"""Deploy the tested immutable image in Jenkins' dedicated browser-lab Docker engine."""
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib import parse, request


REPOSITORY = 'coastrider7/csa1020-exp13-releaseharbor'
NAME = 'releaseharbor-browser-exp13'
PREVIOUS = NAME + '-previous'
CANARY = NAME + '-canary'
LABEL = 'csa1020.experiment'


def docker(*arguments, check=True):
    result = subprocess.run(['docker', *arguments], capture_output=True, text=True, timeout=120)
    if check and result.returncode:
        raise RuntimeError('Docker operation failed: ' + arguments[0])
    return result


def inspect(name, image=False):
    result = docker(*(['image', 'inspect'] if image else ['container', 'inspect']), name, check=False)
    if result.returncode:
        return None
    return json.loads(result.stdout)[0]


def select_digest(digests):
    pattern = re.compile(re.escape(REPOSITORY) + r'@sha256:[0-9a-f]{64}')
    if not isinstance(digests, list):
        raise RuntimeError('Published image digests must be a list.')
    matches = [value for value in digests if isinstance(value, str) and pattern.fullmatch(value)]
    if len(matches) != 1:
        raise RuntimeError('Exactly one published digest is required for this experiment.')
    return matches[0]


def check_identity(info, sha, build):
    if not info or info.get('Config', {}).get('Labels', {}).get('org.opencontainers.image.revision') != sha:
        raise RuntimeError('Published image source label does not match this build.')
    values = dict(value.split('=', 1) for value in info['Config'].get('Env', []) if '=' in value)
    if values.get('GIT_SHA') != sha or values.get('BUILD_NUMBER') != build:
        raise RuntimeError('Published image source/build metadata does not match this build.')
    if info['Config'].get('User') in ('', 'root', '0', '0:0', None):
        raise RuntimeError('The browser runtime must use the image non-root user.')


def managed_container(name):
    info = inspect(name)
    if info is None:
        return None
    if info.get('Config', {}).get('Labels', {}).get(LABEL) != '13':
        raise RuntimeError('A reserved container name is occupied by an unmanaged container.')
    if any(mount.get('Type') != 'tmpfs' for mount in info.get('Mounts', [])):
        raise RuntimeError('A managed stateless app unexpectedly has persistent mounts; it was preserved.')
    return info


def runtime_arguments(name, image, publish=False):
    arguments = ['run', '-d', '--name', name, '--restart', 'no',
                 '--label', LABEL + '=13', '--label', 'csa1020.managed=browser-cd',
                 '--read-only', '--tmpfs', '/tmp:rw,noexec,nosuid,size=32m',
                 '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
                 '--memory', '256m', '--cpus', '1', '--pids-limit', '256',
                 '--health-interval', '10s', '--health-timeout', '5s',
                 '--health-start-period', '5s', '--health-retries', '3',
                 '-e', 'PORT=8000', '-e', 'APP_MODE=browser-lab']
    if publish:
        # The dedicated DinD service forwards this port to loopback-only 8091 in Codespaces.
        arguments += ['-p', '8000:8000']
    else:
        arguments += ['--network', 'none']
    return arguments + [image]


VERIFY_SCRIPT = r"""
const assert = require('node:assert/strict');
(async () => {
  const base = 'http://127.0.0.1:8000';
  const health = await fetch(base + '/healthz', {signal:AbortSignal.timeout(5000)});
  assert.equal(health.status, 200);
  const version = (await (await fetch(base + '/api/version')).json()).data;
  assert.equal(version.application, 'ReleaseHarbor');
  assert.equal(version.gitSha, process.env.EXPECTED_SHA);
  assert.equal(String(version.buildNumber), process.env.EXPECTED_BUILD);
  const checks = Object.fromEntries(['tests','codeReview','build','dependencies','secrets','access','backup','monitoring','rollback','runbook','notes','support'].map(key => [key,true]));
  const body = {releaseName:'Automatic browser deployment',version:'1.0.0',owner:'Demo team',releaseDate:'2026-11-02',checks};
  const post = payload => fetch(base + '/api/assess', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(5000)});
  const ready = await post(body);
  assert.equal(ready.status,200);
  const result = (await ready.json()).data;
  assert.equal(result.score,100); assert.equal(result.blockers.length,0);
  assert.equal((await post({...body,version:'invalid'})).status,400);
  console.log(JSON.stringify(version));
})().catch(() => process.exit(1));
"""


def verify_container(name, sha, build, wait=60):
    deadline = time.monotonic() + wait
    while True:
        result = docker('exec', '-e', 'EXPECTED_SHA=' + sha, '-e', 'EXPECTED_BUILD=' + build,
                        name, 'node', '-e', VERIFY_SCRIPT, check=False)
        if result.returncode == 0:
            return json.loads(result.stdout)
        if time.monotonic() >= deadline:
            raise RuntimeError('The new container failed its HTTP behavior or source/build identity checks.')
        time.sleep(2)


def verify_forwarding(base, sha, build, wait=45):
    deadline = time.monotonic() + wait
    while True:
        try:
            with request.urlopen(base + '/healthz', timeout=8) as response:
                assert response.status == 200
            with request.urlopen(base + '/api/version', timeout=8) as response:
                version = json.load(response)['data']
            assert version['application'] == 'ReleaseHarbor' and version['gitSha'] == sha
            assert str(version['buildNumber']) == build
            return version
        except (OSError, ValueError, KeyError, AssertionError):
            if time.monotonic() >= deadline:
                raise RuntimeError('The forwarded browser application did not match this build.') from None
            time.sleep(2)


def valid_browser_url(value):
    try:
        parts = parse.urlsplit(value)
        return (parts.scheme == 'https' and bool(parts.hostname) and
                parts.hostname.endswith('-8091.app.github.dev') and not parts.username and
                not parts.password and not parts.port and parts.path in ('', '/') and
                not parts.query and not parts.fragment)
    except ValueError:
        return False


def deploy(image, sha, build, base):
    old = managed_container(NAME)
    stale_canary = managed_container(CANARY)
    if stale_canary:
        docker('rm', '-f', CANARY)
    docker(*runtime_arguments(CANARY, image))
    try:
        verify_container(CANARY, sha, build)
    finally:
        docker('rm', '-f', CANARY, check=False)

    previous = managed_container(PREVIOUS)
    if previous:
        if previous.get('State', {}).get('Running'):
            raise RuntimeError('The previous-release container is unexpectedly running; it was preserved.')
        docker('rm', PREVIOUS)
    was_running = bool(old and old['State']['Running'])
    renamed = False
    try:
        if old:
            if was_running:
                docker('stop', '--time', '20', NAME)
            docker('rename', NAME, PREVIOUS)
            renamed = True
        docker(*runtime_arguments(NAME, image, publish=True))
        verify_container(NAME, sha, build)
        version = verify_forwarding(base, sha, build)
    except Exception:
        if not old or renamed:
            failed = managed_container(NAME)
            if failed:
                docker('rm', '-f', NAME)
        if renamed:
            docker('rename', PREVIOUS, NAME)
        if was_running:
            docker('start', NAME)
        raise
    return version, old['Config']['Image'] if old else None


def main():
    if os.environ.get('IMAGE_REPOSITORY') != REPOSITORY:
        raise RuntimeError('Unexpected experiment image repository.')
    sha, build = os.environ['SOURCE_SHA'], os.environ['BUILD_NUMBER']
    if not re.fullmatch(r'[0-9a-f]{40}', sha) or not re.fullmatch(r'[1-9][0-9]*', build):
        raise RuntimeError('Invalid source SHA or Jenkins build number.')
    base = os.environ.get('CLOUD_URL', 'http://docker:8000').rstrip('/')
    if base != 'http://docker:8000':
        raise RuntimeError('The deployment must use the dedicated Jenkins Docker engine.')
    browser = os.environ.get('BROWSER_APP_URL') or os.environ.get('LAB_APP_URL', '')
    if not valid_browser_url(browser):
        raise RuntimeError('Configure the private Codespaces BROWSER_APP_URL for port 8091.')
    image = select_digest(json.loads(Path('reports/image-digests.json').read_text()))
    docker('pull', image)
    info = inspect(image, image=True)
    check_identity(info, sha, build)
    tested = inspect(os.environ['RELEASE_IMAGE'], image=True)
    if not tested or tested['Id'] != info['Id']:
        raise RuntimeError('The pushed immutable image is not the runtime image tested by this build.')
    version, previous = deploy(image, sha, build, base)
    report = {'cloud':'GitHub Codespaces', 'deploymentTarget':'private-browser-lab',
              'url':browser.rstrip('/'), 'internalUrl':base, 'image':image,
              'sourceSha':sha, 'buildNumber':build, 'verifiedVersion':{'data':version},
              'healthHttpStatus':200, 'functionalChecksPassed':True,
              'previousImageRetained':previous, 'rollbackAvailable':previous is not None}
    Path('reports/cloud-deployment.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Verified automatic browser deployment: ' + sha[:12] + ' / Jenkins build ' + build)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        Path('reports').mkdir(exist_ok=True)
        Path('reports/browser-deployment-failure.json').write_text(json.dumps({
            'deploymentTarget':'private-browser-lab', 'passed':False,
            'reason':str(error), 'note':'The preceding release is retained; failed replacement triggers restoration. Inspect the running container if Docker itself failed.'
        }, indent=2) + '\n')
        raise SystemExit('Browser deployment failed: ' + str(error)) from None
