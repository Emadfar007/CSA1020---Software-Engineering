"""Start, stop or inspect only this repository's private deployment agent."""
import argparse
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import tempfile
import time


class AgentError(RuntimeError):
    pass


def command(repo, data_root):
    agent = Path(repo) / "browser-lab/ci/deployment_agent.py"
    return "exec python3 " + shlex.quote(str(agent)) + " --data-root " + shlex.quote(str(data_root))


def is_our_command(arguments, repo, data_root):
    """Accept the exact Python invocation, or its brief login-shell bootstrap."""
    if not arguments:
        return False
    expected = str(Path(repo) / "browser-lab/ci/deployment_agent.py")
    executable = Path(arguments[0]).name
    if executable.startswith("python"):
        return arguments[1:] == [expected, "--data-root", str(data_root)]
    return executable == "bash" and arguments[1:] == ["-lic", command(repo, data_root)]


def process_arguments(pid):
    try:
        raw = (Path("/proc") / str(pid) / "cmdline").read_bytes()
    except FileNotFoundError:
        return None
    except OSError:
        raise AgentError("Cannot inspect the recorded agent process; no signal was sent.") from None
    if not raw:
        # A zombie has already exited, even before its parent reaps it.
        return None
    try:
        return [part.decode("utf-8") for part in raw.rstrip(b"\0").split(b"\0")]
    except UnicodeDecodeError:
        raise AgentError("The recorded process identity could not be verified.") from None


def read_pid(path):
    if path.is_symlink():
        raise AgentError("Refusing a symlinked deployment-agent PID file.")
    try:
        value = path.read_text(encoding="ascii").strip()
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError):
        raise AgentError("The private deployment-agent PID file could not be read.") from None
    if not value.isdecimal() or not 1 < int(value) < 2 ** 31:
        raise AgentError("The private deployment-agent PID file is invalid.")
    return int(value)


def verify_keys(repo, data_root):
    private_key = data_root / "private/browser-deployment-key.pem"
    public_key = repo / "browser-lab/ci/deployment-public.pem"
    if not private_key.is_file() or not public_key.is_file():
        raise AgentError("The lab deployment key pair must be provisioned before starting the agent.")
    try:
        private_result = subprocess.run(
            ["openssl", "pkey", "-in", str(private_key), "-pubout", "-outform", "DER"],
            capture_output=True, timeout=10, check=False)
        public_result = subprocess.run(
            ["openssl", "pkey", "-pubin", "-in", str(public_key), "-pubout", "-outform", "DER"],
            capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        raise AgentError("The deployment key pair could not be verified.") from None
    if (private_result.returncode or public_result.returncode or not private_result.stdout or
            private_result.stdout != public_result.stdout):
        raise AgentError("The private lab key does not match the repository's deployment public key.")


def remove_our_pid(path, pid):
    # Do not remove a file that another startup has replaced.
    if read_pid(path) == pid:
        path.unlink(missing_ok=True)


def save_pid(path, pid):
    with tempfile.NamedTemporaryFile(mode="w", encoding="ascii", dir=path.parent, prefix="browser-deployer-", delete=False) as handle:
        handle.write(str(pid) + "\n")
        temporary = Path(handle.name)
    temporary.chmod(0o600)
    temporary.replace(path)


def status(repo, data_root):
    path = data_root / "private/browser-deployer.pid"
    pid = read_pid(path)
    arguments = process_arguments(pid) if pid else None
    if arguments and not is_our_command(arguments, repo, data_root):
        return {"running": False, "pidFileNeedsReview": True, "message": "Recorded PID belongs to another command; no action taken."}
    return {"running": bool(arguments), "pid": pid if arguments else None}


def start(repo, data_root):
    verify_keys(repo, data_root)
    agent = repo / "browser-lab/ci/deployment_agent.py"
    if not agent.is_file():
        raise AgentError("The repository deployment agent is missing.")
    private = data_root / "private"
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    private.chmod(0o700)
    pid_path = private / "browser-deployer.pid"
    pid = read_pid(pid_path)
    if pid:
        arguments = process_arguments(pid)
        if arguments:
            if not is_our_command(arguments, repo, data_root):
                raise AgentError("The recorded PID belongs to another process; it was preserved.")
            return {"running": True, "pid": pid, "alreadyRunning": True}
        remove_our_pid(pid_path, pid)
    log = private / "browser-deployer.log"
    if log.is_symlink():
        raise AgentError("Refusing a symlinked deployment-agent log file.")
    try:
        with log.open("ab", buffering=0) as output:
            log.chmod(0o600)
            process = subprocess.Popen(
                ["bash", "-lic", command(repo, data_root)], cwd=repo,
                stdin=subprocess.DEVNULL, stdout=output, stderr=output,
                start_new_session=True, close_fds=True)
    except OSError:
        raise AgentError("The private deployment agent could not be started.") from None
    save_pid(pid_path, process.pid)
    # A brief check catches immediate configuration/import failures without
    # waiting for a GitHub network poll or keeping the invoking shell alive.
    deadline = time.monotonic() + 1.5
    while time.monotonic() < deadline:
        if process.poll() is not None:
            remove_our_pid(pid_path, process.pid)
            raise AgentError("The deployment agent exited during startup; inspect its private log.")
        time.sleep(0.05)
    arguments = process_arguments(process.pid)
    if not arguments:
        remove_our_pid(pid_path, process.pid)
        raise AgentError("The deployment agent did not remain running.")
    if not is_our_command(arguments, repo, data_root):
        raise AgentError("The started process identity changed unexpectedly; no signal was sent.")
    return {"running": True, "pid": process.pid, "alreadyRunning": False}


def stop(repo, data_root):
    path = data_root / "private/browser-deployer.pid"
    pid = read_pid(path)
    if not pid:
        return {"running": False, "stopped": False}
    arguments = process_arguments(pid)
    if not arguments:
        remove_our_pid(path, pid)
        return {"running": False, "stopped": False}
    # A pidfd keeps the signal bound to this exact process even if its PID is
    # recycled between inspection and SIGTERM. Fail closed on older platforms.
    if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
        raise AgentError("Safe process signaling is unavailable; the agent was not stopped.")
    try:
        descriptor = os.pidfd_open(pid)
    except ProcessLookupError:
        remove_our_pid(path, pid)
        return {"running": False, "stopped": False}
    except OSError:
        raise AgentError("The recorded process could not be safely opened; no signal was sent.") from None
    try:
        arguments = process_arguments(pid)
        if arguments and not is_our_command(arguments, repo, data_root):
            raise AgentError("The recorded PID belongs to another process; no signal was sent.")
        if arguments:
            try:
                signal.pidfd_send_signal(descriptor, signal.SIGTERM)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if process_arguments(pid) is None:
                remove_our_pid(path, pid)
                return {"running": False, "stopped": True}
            time.sleep(0.1)
        return {"running": True, "pid": pid, "stopping": True,
                "message": "SIGTERM sent. Wait for the active deployment to finish, then retry stopping the lab."}
    finally:
        os.close(descriptor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["start", "stop", "status"])
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--data-root", required=True, type=Path)
    args = parser.parse_args()
    if not args.repo.is_absolute() or not args.data_root.is_absolute():
        raise AgentError("The repository and private data root must be absolute paths.")
    os.umask(0o077)
    repo, data_root = args.repo.resolve(), args.data_root.resolve()
    result = {"start": start, "stop": stop, "status": status}[args.action](repo, data_root)
    print(json.dumps(result))
    # The runner uses set -e: do not stop app containers while a deployment
    # operation is still winding down after its SIGTERM request.
    return 2 if args.action == "stop" and result.get("running") else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AgentError as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(1) from None
