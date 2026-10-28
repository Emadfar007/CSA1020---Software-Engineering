"""Start the saved Jenkins browser release, or seed it once from the verified image."""
import importlib.util
import json
import os
import re


spec = importlib.util.spec_from_file_location('deploy_browser', '/tmp/csa1020-deploy-browser.py')
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


def image_identity(image):
    info = deploy.inspect(image, image=True)
    if not info:
        raise RuntimeError('The browser release image is unavailable.')
    values = dict(value.split('=', 1) for value in info['Config'].get('Env', []) if '=' in value)
    sha, build = values.get('GIT_SHA', ''), values.get('BUILD_NUMBER', '')
    if not re.fullmatch(r'[0-9a-f]{40}', sha) or not re.fullmatch(r'[1-9][0-9]*', build):
        raise RuntimeError('The saved browser release has invalid source/build metadata.')
    deploy.check_identity(info, sha, build)
    return sha, build


def main():
    current = deploy.managed_container(deploy.NAME)
    if current:
        # Keep a newer Jenkins deployment rather than replacing it with the historical seed.
        image = deploy.select_digest([current['Config']['Image']])
        sha, build = image_identity(current['Image'])
        if not current['State']['Running']:
            deploy.docker('start', deploy.NAME)
        deploy.verify_container(deploy.NAME, sha, build)
        deploy.verify_forwarding('http://docker:8000', sha, build)
        action = 'Preserved existing browser deployment'
    else:
        image = deploy.select_digest([os.environ['BOOTSTRAP_IMAGE']])
        print('Seeding the Jenkins browser app from its recorded immutable image.', flush=True)
        deploy.docker('pull', image)
        sha, build = image_identity(image)
        deploy.deploy(image, sha, build, 'http://docker:8000')
        action = 'Seeded browser deployment'
    print(json.dumps({'action':action, 'sourceSha':sha, 'buildNumber':build,
                      'image':image, 'verified':True}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        raise SystemExit('Jenkins browser bootstrap failed: ' + str(error)) from None
