"""Pull trusted Actions deployment requests into the private, running browser lab.

Only the two named, stateless demonstration containers are replaced. GitHub's
Codespaces token stays in this process; it is never mounted into an app image.
"""
from __future__ import annotations

import argparse
import base64
import binascii
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

REPOSITORY = "Emadfar007/CSA1020---Software-Engineering"
API_ROOT = "https://api.github.com"
SPECS = {
    14: {"application": "FocusLane", "container": "focuslane-app-exp14", "port": 8094,
         "imageRepository": "coastrider7/csa1020-exp14-focuslane",
         "workflow": ".github/workflows/experiment-14-cd.yml", "job": "Test and publish FocusLane"},
    19: {"application": "Packlight", "container": "packlight-app-exp19", "port": 8099,
         "imageRepository": "coastrider7/csa1020-exp19-packlight",
         "workflow": ".github/workflows/experiment-19-cicd.yml", "job": "Test and publish Packlight"},
}
PAYLOAD_KEYS = {"protocol", "experiment", "image", "sourceSha", "runId", "buildNumber", "encryptedCallbackToken"}
TERMINAL = {"success", "failure", "error", "inactive"}


def log(event, **fields):
    print(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "event": event, **fields}), flush=True)


class DeploymentError(RuntimeError):
    """A deliberately short error that is safe to publish as a status."""


class GitHub:
    def __init__(self, token):
        if not token:
            raise DeploymentError("A repository-scoped GitHub token is required in the Codespace.")
        self.token = token

    def call(self, path, data=None):
        if not path.startswith(f"/repos/{REPOSITORY}/"):
            raise DeploymentError("GitHub request is outside the experiment repository.")
        headers = {"Authorization": "Bearer " + self.token, "Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "CSA1020-private-browser-deployer"}
        request = Request(API_ROOT + path, headers=headers,
                          data=None if data is None else json.dumps(data).encode(),
                          method="GET" if data is None else "POST")
        try:
            with urlopen(request, timeout=25) as response:
                return json.load(response)
        except HTTPError as error:
            raise DeploymentError(f"GitHub API returned HTTP {error.code}.") from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise DeploymentError("GitHub API could not be reached or returned invalid JSON.") from None

    def list_deployments(self, number):
        query = urlencode({"environment": f"codespaces-exp{number}", "task": "deploy", "per_page": 20})
        return self.call(f"/repos/{REPOSITORY}/deployments?{query}")

    def latest_status(self, deployment_id):
        statuses = self.call(f"/repos/{REPOSITORY}/deployments/{deployment_id}/statuses?per_page=1")
        return statuses[0]["state"] if statuses else "queued"

    def status(self, deployment_id, state, description, url, run_id):
        return self.call(f"/repos/{REPOSITORY}/deployments/{deployment_id}/statuses", {
            "state": state, "description": description[:140], "environment_url": url,
            "log_url": f"https://github.com/{REPOSITORY}/actions/runs/{run_id}",
            "auto_inactive": state == "success",
        })


def validate_request(deployment, number, api):
    """Authenticate the request against GitHub's run and job records, not its text."""
    if number not in SPECS or deployment.get("environment") != f"codespaces-exp{number}":
        raise DeploymentError("Unexpected deployment environment.")
    if deployment.get("task") != "deploy" or deployment.get("creator", {}).get("login") != "github-actions[bot]":
        raise DeploymentError("Only GitHub Actions can request browser deployments.")
    if type(deployment.get("id")) is not int or deployment["id"] <= 0:
        raise DeploymentError("Invalid deployment identity.")
    payload = deployment.get("payload")
    if not isinstance(payload, dict) or set(payload) != PAYLOAD_KEYS:
        raise DeploymentError("Unexpected deployment payload fields.")
    if type(payload.get("protocol")) is not int or payload["protocol"] != 1:
        raise DeploymentError("Unsupported deployment protocol.")
    if type(payload.get("experiment")) is not int or payload["experiment"] != number:
        raise DeploymentError("Deployment experiment does not match its environment.")
    sha = payload.get("sourceSha", "")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise DeploymentError("Invalid source revision.")
    if deployment.get("sha") != sha or deployment.get("ref") != sha:
        raise DeploymentError("Deployment and payload revisions do not match.")
    image = payload.get("image", "")
    prefix = re.escape(SPECS[number]["imageRepository"])
    if not isinstance(image, str) or not re.fullmatch(prefix + r"@sha256:[0-9a-f]{64}", image):
        raise DeploymentError("Only the experiment's immutable Docker Hub image is accepted.")
    if type(payload.get("runId")) is not int or payload["runId"] <= 0:
        raise DeploymentError("Invalid Actions run identity.")
    if not isinstance(payload.get("buildNumber"), str) or not re.fullmatch(r"[1-9][0-9]*\.[1-9][0-9]*", payload["buildNumber"]):
        raise DeploymentError("Invalid Actions build identity.")
    callback_ciphertext(payload)
    run = api.call(f"/repos/{REPOSITORY}/actions/runs/{payload['runId']}")
    if (run.get("head_branch") != "main" or run.get("head_sha") != sha or
            run.get("event") not in {"push", "workflow_dispatch"} or
            run.get("repository", {}).get("full_name") != REPOSITORY or
            run.get("head_repository", {}).get("full_name") != REPOSITORY or
            str(run.get("path", "")).split("@", 1)[0] != SPECS[number]["workflow"]):
        raise DeploymentError("Actions run is not a trusted main-branch delivery.")
    if payload["buildNumber"] != f"{run.get('run_number')}.{run.get('run_attempt')}":
        raise DeploymentError("Actions run and requested build identities do not match.")
    jobs = api.call(f"/repos/{REPOSITORY}/actions/runs/{payload['runId']}/jobs?filter=latest&per_page=100")
    matching = [job for job in jobs.get("jobs", []) if job.get("name") == SPECS[number]["job"]]
    if len(matching) != 1 or matching[0].get("conclusion") != "success":
        raise DeploymentError("The required test-and-publication job has not succeeded.")
    return dict(payload)


def callback_ciphertext(payload):
    encrypted = payload.get("encryptedCallbackToken")
    if not isinstance(encrypted, str) or len(encrypted) > 1024:
        raise DeploymentError("Invalid encrypted deployment callback.")
    try:
        ciphertext = base64.b64decode(encrypted, validate=True)
    except (binascii.Error, ValueError):
        raise DeploymentError("Invalid encrypted deployment callback.") from None
    if len(ciphertext) != 384:
        raise DeploymentError("The callback must use the lab's RSA-3072 public key.")
    return ciphertext


def callback_client(payload, data_root):
    """Decrypt a short-lived job token only after native-token validation succeeds."""
    key = Path(data_root) / "private/browser-deployment-key.pem"
    if not key.is_file():
        raise DeploymentError("The private browser deployment key is unavailable.")
    try:
        result = subprocess.run([
            "openssl", "pkeyutl", "-decrypt", "-inkey", str(key),
            "-pkeyopt", "rsa_padding_mode:oaep", "-pkeyopt", "rsa_oaep_md:sha256",
        ], input=callback_ciphertext(payload), capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        raise DeploymentError("The encrypted callback could not be opened.") from None
    if result.returncode:
        raise DeploymentError("The encrypted callback could not be opened.")
    try:
        token = result.stdout.decode("ascii")
    except UnicodeDecodeError:
        raise DeploymentError("The encrypted callback did not contain a valid job token.") from None
    if not 20 <= len(token) <= 4096 or any(character.isspace() or ord(character) < 33 or ord(character) > 126 for character in token):
        raise DeploymentError("The encrypted callback did not contain a valid job token.")
    return GitHub(token)


def read_http(port, path, payload=None):
    request = Request(f"http://127.0.0.1:{port}{path}",
                      data=None if payload is None else json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=8) as response:
            body = response.read()
            return response.status, body.decode() if path == "/" else json.loads(body)
    except HTTPError as error:
        return error.code, json.load(error)


def verify_contract(request, number, payload):
    """Check the actual running API and a useful application calculation."""
    spec = SPECS[number]
    status, page = request("/")
    if status != 200 or spec["application"].lower() not in page.lower():
        raise DeploymentError("The application page did not load.")
    if request("/healthz")[0] != 200:
        raise DeploymentError("The application health check failed.")
    status, version = request("/api/version")
    version = version.get("data", version) if isinstance(version, dict) else {}
    if (status != 200 or version.get("application") != spec["application"] or
            version.get("gitSha", version.get("git_sha")) != payload["sourceSha"] or
            str(version.get("buildNumber", version.get("build_number"))) != payload["buildNumber"]):
        raise DeploymentError("The running application has the wrong source or build identity.")
    if number == 14:
        body = {"planName": "Automatic deployment check", "startDate": "2026-11-02", "dailyMinutes": 90,
                "horizonDays": 3, "subjects": [
                    {"id": "math", "name": "Mathematics", "minutes": 90, "priority": "medium"},
                    {"id": "cs", "name": "Computer Science", "minutes": 120, "priority": "high"},
                    {"id": "writing", "name": "Writing", "minutes": 45, "priority": "low"}]}
        status, result = request("/api/plan", body)
        result = result.get("data", {})
        if (status != 200 or result.get("plannedMinutes") != 255 or result.get("remainingMinutes") != 0 or
                [day.get("plannedMinutes") for day in result.get("days", [])] != [90, 90, 75] or
                result["days"][0]["sessions"][0].get("subjectId") != "cs"):
            raise DeploymentError("The study-planning calculation failed.")
        if request("/api/plan", {**body, "dailyMinutes": 0})[0] != 400:
            raise DeploymentError("Invalid study input was accepted.")
        return {"version": version, "plannedMinutes": 255, "dailyMinutes": [90, 90, 75], "invalidInputHttpStatus": 400}
    body = {"days": 4, "travelers": 2, "climate": "rainy", "activity": "trail", "laundry": False}
    status, result = request("/api/packing-list", body)
    items = {item["name"]: item["quantity"] for group in result.get("categories", []) for item in group.get("items", [])}
    if (status != 200 or result.get("total_items") != 47 or items.get("First aid kit") != 1 or
            items.get("Rain jacket") != 2 or sum(items.values()) != 47):
        raise DeploymentError("The packing-list calculation failed.")
    if request("/api/packing-list", {**body, "days": 0})[0] != 400:
        raise DeploymentError("Invalid trip input was accepted.")
    return {"version": version, "packingItems": 47, "invalidInputHttpStatus": 400}


NODE_REQUEST = r"""
const [path, raw] = process.argv.slice(1);
(async()=>{
  const response=await fetch('http://127.0.0.1:8000'+path,{method:raw==='null'?'GET':'POST',
    headers:{'Content-Type':'application/json'},body:raw==='null'?undefined:raw,signal:AbortSignal.timeout(5000)});
  const text=await response.text();
  console.log(JSON.stringify([response.status,path==='/'?text:JSON.parse(text)]));
})().catch(()=>{process.stderr.write('Application request failed.');process.exit(1)});
"""
PYTHON_REQUEST = r"""
import json,sys,urllib.request,urllib.error
path,raw=sys.argv[1:]
req=urllib.request.Request('http://127.0.0.1:8000'+path,data=None if raw=='null' else raw.encode(),headers={'Content-Type':'application/json'})
try:
    response=urllib.request.urlopen(req,timeout=5)
except urllib.error.HTTPError as error:
    response=error
with response:
    text=response.read().decode()
    print(json.dumps([response.status,text if path=='/' else json.loads(text)]))
"""


class DockerRuntime:
    def __init__(self, data_root):
        self.data_root = Path(data_root)

    def docker(self, *args, timeout=180):
        try:
            result = subprocess.run(["docker", *args], check=False, capture_output=True, text=True, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            raise DeploymentError("The Docker operation could not complete.") from None
        if result.returncode:
            raise DeploymentError("The Docker operation failed; inspect the private lab log.")
        return result.stdout

    def inspect(self, name):
        try:
            result = subprocess.run(["docker", "container", "inspect", name], capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            raise DeploymentError("Could not inspect the managed application container.") from None
        if result.returncode:
            return None
        return json.loads(result.stdout)[0]

    @staticmethod
    def validate_owned(info, number):
        spec = SPECS[number]
        config, host = info.get("Config", {}), info.get("HostConfig", {})
        mounts = info.get("Mounts") or []
        unsafe_mount = any(mount.get("Type") != "tmpfs" or mount.get("Destination") != "/tmp" for mount in mounts)
        if (not str(config.get("Image", "")).startswith(spec["imageRepository"] + "@sha256:") or
                unsafe_mount or host.get("Binds") or host.get("Privileged")):
            raise DeploymentError("Refusing to replace a container outside this stateless experiment.")
        bindings = host.get("PortBindings", {})
        expected = [{"HostIp": "127.0.0.1", "HostPort": str(spec["port"])}]
        if bindings != {"8000/tcp": expected}:
            raise DeploymentError("The managed container has unexpected port bindings.")

    def running(self, number):
        info = self.inspect(SPECS[number]["container"])
        if info:
            self.validate_owned(info, number)
        return bool(info and info.get("State", {}).get("Running"))

    def create(self, name, number, payload, publish):
        arguments = ["run", "-d", "--name", name, "--restart", "no", "--read-only",
                     "--tmpfs", "/tmp:rw,noexec,nosuid,size=32m", "--cap-drop", "ALL",
                     "--security-opt", "no-new-privileges:true", "--memory", "256m", "--cpus", "1",
                     "--pids-limit", "256", "--label", f"com.csa1020.deployment={payload['deploymentId']}",
                     "-e", "PORT=8000", "-e", "APP_MODE=browser-lab"]
        if publish:
            arguments += ["-p", f"127.0.0.1:{SPECS[number]['port']}:8000"]
        else:
            arguments += ["--network", "none"]
        self.docker(*arguments, payload["image"])

    def inside_request(self, container, number, path, payload=None):
        raw = json.dumps(payload)
        runtime = ["node", "-e", NODE_REQUEST] if number == 14 else ["python", "-c", PYTHON_REQUEST]
        return json.loads(self.docker("exec", container, *runtime, path, raw, timeout=15))

    def wait_verified(self, number, payload, container=None):
        deadline = time.monotonic() + 75
        while True:
            try:
                if container:
                    request = lambda path, body=None: self.inside_request(container, number, path, body)
                else:
                    request = lambda path, body=None: read_http(SPECS[number]["port"], path, body)
                return verify_contract(request, number, payload)
            except (DeploymentError, OSError, ValueError, KeyError, TypeError, IndexError):
                if time.monotonic() >= deadline:
                    raise DeploymentError("The deployed application failed its HTTP contract or identity checks.") from None
                time.sleep(2)

    def save_state(self, number, receipt):
        directory = self.data_root / "deployments" / str(number)
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = directory / "current.json.tmp"
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(directory / "current.json")
        (directory / f"deployment-{receipt['deploymentId']}.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    def deploy(self, number, payload, before_switch=None):
        # Callback credentials, including their ciphertext, never enter receipts or app containers.
        payload = {key: value for key, value in payload.items() if key != "encryptedCallbackToken"}
        spec = SPECS[number]
        name, previous = spec["container"], spec["container"] + "-previous"
        canary = name + "-candidate-" + str(payload["deploymentId"])
        old = self.inspect(name)
        if not old or not old.get("State", {}).get("Running"):
            raise DeploymentError("Start this experiment's browser lab profile before deploying.")
        self.validate_owned(old, number)
        self.docker("pull", payload["image"], timeout=240)
        image = json.loads(self.docker("image", "inspect", payload["image"]))[0]
        config = image.get("Config", {})
        if config.get("Labels", {}).get("org.opencontainers.image.revision") != payload["sourceSha"]:
            raise DeploymentError("The pulled image revision does not match the tested commit.")
        if str(config.get("User", "")).split(":", 1)[0] in {"", "root", "0"}:
            raise DeploymentError("The application image must run as a non-root user.")
        stopped = renamed = False
        try:
            self.create(canary, number, payload, publish=False)
            self.wait_verified(number, payload, container=canary)
            if before_switch:
                before_switch()
            self.docker("rm", "-f", canary)
            older = self.inspect(previous)
            if older:
                self.validate_owned(older, number)
                if older.get("State", {}).get("Running"):
                    raise DeploymentError("A previous deployment is still running; review it before replacement.")
                self.docker("rm", previous)
            self.docker("stop", "--timeout", "20", name)
            stopped = True
            self.docker("rename", name, previous)
            renamed = True
            self.create(name, number, payload, publish=True)
            checks = self.wait_verified(number, payload)
            receipt = {**payload, "application": spec["application"], "container": name, "port": spec["port"],
                       "previousImage": old["Config"]["Image"], "checks": checks, "passed": True,
                       "deployedAt": datetime.now(timezone.utc).isoformat()}
            self.save_state(number, receipt)
            return receipt
        except Exception:
            if renamed:
                current = self.inspect(name)
                if current:
                    if current.get("Config", {}).get("Labels", {}).get("com.csa1020.deployment") != str(payload["deploymentId"]):
                        raise DeploymentError("Rollback refused an unexpected replacement container.") from None
                    self.validate_owned(current, number)
                    self.docker("rm", "-f", name)
                self.docker("rename", previous, name)
                self.docker("start", name)
            elif stopped:
                self.docker("start", name)
            raise
        finally:
            candidate = self.inspect(canary)
            if candidate and candidate.get("Config", {}).get("Labels", {}).get("com.csa1020.deployment") == str(payload["deploymentId"]):
                self.docker("rm", "-f", canary)


def latest_actions_request(api, number):
    deployments = api.list_deployments(number)
    return next((item for item in deployments if item.get("creator", {}).get("login") == "github-actions[bot]"), None)


def process_once(api, runtime, codespace):
    for number in SPECS:
        deployment = latest_actions_request(api, number)
        if not deployment or api.latest_status(deployment["id"]) in TERMINAL:
            continue
        # An inactive profile must not be started by a polling deployment agent.
        if not runtime.running(number):
            continue
        url = f"https://{codespace}-{SPECS[number]['port']}.app.github.dev/"
        run_id = deployment.get("payload", {}).get("runId", 0) if isinstance(deployment.get("payload"), dict) else 0
        callback = None
        try:
            payload = validate_request(deployment, number, api)
            callback = callback_client(payload, runtime.data_root)
            payload.pop("encryptedCallbackToken")
            payload["deploymentId"] = deployment["id"]
            callback.status(deployment["id"], "in_progress", "Verifying and deploying the tested image in the private browser lab.", url, payload["runId"])

            def still_current():
                latest = latest_actions_request(api, number)
                if not latest or latest.get("id") != deployment["id"]:
                    raise DeploymentError("A newer deployment request superseded this delivery.")
                if api.latest_status(deployment["id"]) in TERMINAL:
                    raise DeploymentError("The workflow cancelled or ended this deployment request.")

            receipt = runtime.deploy(number, payload, before_switch=still_current)
            callback.status(deployment["id"], "success", "Browser app verified: source, build identity and application behavior match.", url, payload["runId"])
            log("deployed", experiment=number, deploymentId=deployment["id"], sourceSha=payload["sourceSha"], url=url)
        except (DeploymentError, OSError, ValueError, KeyError, TypeError, IndexError):
            # Do not expose exception bodies, command output, tokens or API responses.
            if callback:
                callback.status(deployment["id"], "failure", "Browser deployment failed validation; the previous app was preserved or restored.", url, run_id)
            log("deployment_failed", experiment=number, deploymentId=deployment["id"])


@contextmanager
def single_agent(data_root):
    import fcntl
    directory = Path(data_root) / "deployments"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (directory / "agent.lock").open("w") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise DeploymentError("The browser deployment agent is already running.") from None
        yield


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--data-root", default=os.environ.get("LAB_DATA_DIR", "/workspaces/.lab-data"))
    parser.add_argument("--interval", type=int, default=15)
    args = parser.parse_args()
    codespace = os.environ.get("CODESPACE_NAME", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", codespace) or not 5 <= args.interval <= 300:
        raise DeploymentError("Run this agent in the existing Codespace with an interval of 5 to 300 seconds.")
    if not Path(args.data_root).is_absolute():
        raise DeploymentError("The private deployment data directory must be absolute.")
    os.umask(0o077)
    api = GitHub(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    runtime = DockerRuntime(args.data_root)
    stopped = threading.Event()
    for number in (signal.SIGTERM, signal.SIGINT):
        signal.signal(number, lambda *_: stopped.set())
    with single_agent(args.data_root):
        log("agent_started", repository=REPOSITORY, intervalSeconds=args.interval)
        while not stopped.is_set():
            try:
                process_once(api, runtime, codespace)
            except (DeploymentError, OSError, ValueError, KeyError, TypeError):
                log("poll_failed", message="Check Codespaces token access and the private deployment log.")
                if args.once:
                    return 1
            if args.once:
                return 0
            stopped.wait(args.interval)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DeploymentError as error:
        log("agent_error", message=str(error))
        raise SystemExit(1) from None
