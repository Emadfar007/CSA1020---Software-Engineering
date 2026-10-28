"""Request deployment of a tested image and wait for the private lab's receipt.

Only an ephemeral Actions GITHUB_TOKEN is used. The Codespaces agent connects
outbound to GitHub, so no public deployment endpoint or account token is needed
in the workflow.
"""
import argparse
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPOSITORY = "Emadfar007/CSA1020---Software-Engineering"
CODESPACE = "miserable-cobweb-4j9pjv79r7w7fjrqw"
SPECS = {
    14: ("FocusLane", "coastrider7/csa1020-exp14-focuslane", 8094),
    19: ("Packlight", "coastrider7/csa1020-exp19-packlight", 8099),
}
TERMINAL_FAILURES = {"failure", "error", "inactive"}


class DeploymentError(RuntimeError):
    pass


class GitHubAPI:
    def __init__(self, token):
        if not token:
            raise DeploymentError("GITHUB_TOKEN is required for deployment permission.")
        self.token = token

    def __call__(self, path, method="GET", payload=None):
        req = Request(
            "https://api.github.com/repos/" + REPOSITORY + path,
            data=None if payload is None else json.dumps(payload).encode(),
            method=method,
            headers={"Accept": "application/vnd.github+json",
                     "Authorization": "Bearer " + self.token,
                     "X-GitHub-Api-Version": "2022-11-28",
                     "Content-Type": "application/json",
                     "User-Agent": "CSA1020-browser-deployment"},
        )
        try:
            with urlopen(req, timeout=20) as response:
                return json.load(response)
        except HTTPError as error:
            raise DeploymentError(f"GitHub deployment API returned HTTP {error.code}.") from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise DeploymentError("GitHub deployment API could not be reached or returned invalid JSON.") from None


def encrypt_callback_token(token, public_key):
    """Seal this job's short-lived status token to the lab's public key."""
    if not token or len(token.encode("utf-8")) > 318:
        raise DeploymentError("The temporary deployment token cannot be sealed for the lab.")
    try:
        result = subprocess.run(
            ["openssl", "pkeyutl", "-encrypt", "-pubin", "-inkey", str(public_key),
             "-pkeyopt", "rsa_padding_mode:oaep", "-pkeyopt", "rsa_oaep_md:sha256"],
            input=token.encode("utf-8"), capture_output=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        raise DeploymentError("Could not seal the temporary deployment token with OpenSSL.") from None
    if result.returncode or len(result.stdout) != 384:
        raise DeploymentError("The browser deployment public key must be a valid RSA-3072 key.")
    return base64.b64encode(result.stdout).decode("ascii")


def validate(args):
    if os.environ.get("GITHUB_REPOSITORY", REPOSITORY) != REPOSITORY:
        raise DeploymentError("Deployment is limited to the CSA1020 repository.")
    app, image_repository, port = SPECS[args.experiment]
    if not re.fullmatch(re.escape(image_repository) + r"@sha256:[0-9a-f]{64}", args.image):
        raise DeploymentError("Deploy a SHA-256 digest from this experiment's image repository.")
    if not re.fullmatch(r"[0-9a-f]{40}", args.sha):
        raise DeploymentError("An exact source commit is required.")
    if args.run_id <= 0 or not re.fullmatch(r"[1-9][0-9]*\.[1-9][0-9]*", args.build):
        raise DeploymentError("A valid Actions run and attempt are required.")
    expected_url = f"https://{CODESPACE}-{port}.app.github.dev/"
    if args.url.rstrip("/") + "/" != expected_url:
        raise DeploymentError("The destination must be this experiment's private Codespaces port.")
    if not 0 <= args.wait_seconds <= 600:
        raise DeploymentError("The deployment wait must be between zero and 600 seconds.")
    return app, expected_url


def request_and_wait(args, api, clock=time.monotonic, sleep=time.sleep):
    app, app_url = validate(args)
    callback = encrypt_callback_token(api.token, args.public_key)
    environment = f"codespaces-exp{args.experiment}"
    run_url = f"https://github.com/{REPOSITORY}/actions/runs/{args.run_id}"
    body = {
        "ref": args.sha, "task": "deploy", "auto_merge": False,
        "required_contexts": [], "environment": environment,
        "transient_environment": True, "production_environment": False,
        "description": f"Deploy tested {app} image to the private browser lab",
        "payload": {"protocol": 1, "experiment": args.experiment,
                    "image": args.image, "sourceSha": args.sha,
                    "runId": args.run_id, "buildNumber": args.build,
                    "encryptedCallbackToken": callback},
    }
    deployment = api("/deployments", "POST", body)
    deployment_id = deployment.get("id")
    if (type(deployment_id) is not int or deployment_id <= 0 or
            deployment.get("sha") != args.sha):
        raise DeploymentError("GitHub did not create a deployment for the expected commit.")
    endpoint = f"/deployments/{deployment_id}/statuses"

    def status(state, description):
        return api(endpoint, "POST", {"state": state, "description": description,
                    "environment_url": app_url, "log_url": run_url,
                    "auto_inactive": False})

    status("queued", "Waiting for the running Codespaces lab to verify and deploy this image.")
    deadline = clock() + args.wait_seconds
    print(f"Deployment {deployment_id} queued for {environment}; waiting for its verified result.", flush=True)
    while True:
        states = api(endpoint + "?per_page=1")
        latest = states[0] if isinstance(states, list) and states else {}
        state = latest.get("state", "queued")
        if state == "success":
            if latest.get("environment_url", "").rstrip("/") + "/" != app_url:
                raise DeploymentError("Deployment success did not identify the expected private app URL.")
            return {"deploymentId": deployment_id, "environment": environment,
                    "state": state, "application": app, "url": app_url,
                    "image": args.image, "sourceSha": args.sha,
                    "buildNumber": args.build, "runId": args.run_id,
                    "logUrl": latest.get("log_url", run_url),
                    "verifiedBy": "Private Codespaces deployment agent",
                    "recordedAt": datetime.now(timezone.utc).isoformat()}
        if state in TERMINAL_FAILURES:
            raise DeploymentError("The browser deployment failed. Inspect its GitHub deployment status and lab log.")
        if clock() >= deadline:
            status("failure", "Codespaces lab did not confirm deployment within 600 seconds; resume the lab and retry.")
            raise DeploymentError("Deployment timed out. Resume Codespaces and run 'bash browser-lab/bin/lab start cicd', then rerun this workflow.")
        sleep(min(10, max(0, deadline - clock())))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", type=int, choices=sorted(SPECS), required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--build", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--wait-seconds", type=int, default=600)
    parser.add_argument("--public-key", type=Path,
                        default=Path(__file__).with_name("deployment-public.pem"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    receipt = request_and_wait(args, GitHubAPI(os.environ.get("GITHUB_TOKEN")))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(f"## {receipt['application']} browser deployment\n\n"
                         f"- Result: **verified success**\n- Commit: `{args.sha}`\n"
                         f"- Build: `{args.build}`\n- Image: `{args.image}`\n"
                         f"- Private app: {receipt['url']}\n"
                         f"- Deployment: `{receipt['deploymentId']}`\n\n"
                         "The Codespace must remain running. Monthly free quotas and the zero-spending budget apply.\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    try:
        main()
    except DeploymentError as error:
        raise SystemExit(str(error)) from None
