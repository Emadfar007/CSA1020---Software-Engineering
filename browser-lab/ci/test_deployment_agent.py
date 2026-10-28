"""Boundaries for accepting trusted requests and restoring a failed deployment."""
from copy import deepcopy
import base64
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location("deployment_agent", Path(__file__).with_name("deployment_agent.py"))
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)

SHA = "a" * 40
IMAGE = "coastrider7/csa1020-exp14-focuslane@sha256:" + "b" * 64
KEYS = b"k" * 32 + b"m" * 32
WRAPPED = b"x" * 384
IV = b"i" * 16
CIPHERTEXT = b"c" * 32


def envelope(ciphertext=CIPHERTEXT, tag=None):
    tag = tag or hmac.new(KEYS[32:], b"CSA1020-CD-v1\0" + WRAPPED + IV + ciphertext, hashlib.sha256).digest()
    packet = {"v": 1, "key": base64.b64encode(WRAPPED).decode(), "iv": base64.b64encode(IV).decode(),
              "ciphertext": base64.b64encode(ciphertext).decode(), "tag": base64.b64encode(tag).decode()}
    return base64.b64encode(json.dumps(packet, separators=(",", ":")).encode()).decode()


PAYLOAD = {"protocol": 1, "experiment": 14, "image": IMAGE, "sourceSha": SHA, "runId": 123, "buildNumber": "8.1",
           "encryptedCallbackToken": envelope()}
DEPLOYMENT = {"id": 42, "environment": "codespaces-exp14", "task": "deploy", "creator": {"login": "github-actions[bot]"},
              "sha": SHA, "ref": SHA, "payload": PAYLOAD}


class API:
    def __init__(self):
        self.run = {"head_branch": "main", "head_sha": SHA, "event": "push", "repository": {"full_name": agent.REPOSITORY},
                    "head_repository": {"full_name": agent.REPOSITORY}, "path": agent.SPECS[14]["workflow"], "run_number": 8, "run_attempt": 1}
        self.jobs = {"jobs": [{"name": agent.SPECS[14]["job"], "conclusion": "success"}]}

    def call(self, path):
        return self.jobs if "/jobs?" in path else self.run


class RequestTests(unittest.TestCase):
    def test_accepts_only_a_matching_successful_main_delivery(self):
        self.assertEqual(agent.validate_request(deepcopy(DEPLOYMENT), 14, API()), PAYLOAD)

    def test_rejects_actor_payload_image_and_revision_substitution(self):
        changes = [
            lambda d: d["creator"].update(login="another-user"),
            lambda d: d["payload"].update(command="run something"),
            lambda d: d["payload"].update(image="coastrider7/other@sha256:" + "b" * 64),
            lambda d: d.update(sha="c" * 40),
            lambda d: d["payload"].update(runId=True),
        ]
        for change in changes:
            with self.subTest(change=change):
                deployment = deepcopy(DEPLOYMENT)
                change(deployment)
                with self.assertRaises(agent.DeploymentError):
                    agent.validate_request(deployment, 14, API())

    def test_rejects_pull_request_wrong_repository_and_wrong_workflow(self):
        for field, value in [("event", "pull_request"), ("head_branch", "feature/change"),
                             ("head_repository", {"full_name": "someone/fork"}), ("path", ".github/workflows/other.yml")]:
            with self.subTest(field=field):
                api = API()
                api.run[field] = value
                with self.assertRaises(agent.DeploymentError):
                    agent.validate_request(deepcopy(DEPLOYMENT), 14, api)

    def test_rejects_failed_or_missing_test_and_publication_job(self):
        for jobs in [[], [{"name": agent.SPECS[14]["job"], "conclusion": "failure"}],
                     [{"name": "Other successful job", "conclusion": "success"}]]:
            api = API()
            api.jobs = {"jobs": jobs}
            with self.subTest(jobs=jobs), self.assertRaises(agent.DeploymentError):
                agent.validate_request(deepcopy(DEPLOYMENT), 14, api)

    def test_rejects_a_build_identity_from_another_attempt(self):
        api = API()
        api.run["run_attempt"] = 2
        with self.assertRaises(agent.DeploymentError):
            agent.validate_request(deepcopy(DEPLOYMENT), 14, api)

    def test_rejects_malformed_or_wrong_size_encrypted_callback(self):
        for value in ["not base64!", base64.b64encode(b"x" * 256).decode(), None]:
            deployment = deepcopy(DEPLOYMENT)
            deployment["payload"]["encryptedCallbackToken"] = value
            with self.subTest(value=value), self.assertRaises(agent.DeploymentError):
                agent.validate_request(deployment, 14, API())

    def test_callback_uses_oaep_sha256_and_keeps_plaintext_in_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            key = Path(directory) / "private/browser-deployment-key.pem"
            key.parent.mkdir()
            key.write_text("private test key")
            token = "ghs_" + "t" * 996
            with patch.object(agent.subprocess, "run", side_effect=[
                    SimpleNamespace(returncode=0, stdout=KEYS, stderr=b""),
                    SimpleNamespace(returncode=0, stdout=token.encode(), stderr=b"")]) as run:
                callback = agent.callback_client(PAYLOAD, directory)
            self.assertEqual(callback.token, token)
            args, kwargs = run.call_args_list[0]
            self.assertIn("rsa_padding_mode:oaep", args[0])
            self.assertIn("rsa_oaep_md:sha256", args[0])
            self.assertEqual(kwargs["input"], WRAPPED)
            decrypt_args, decrypt_kwargs = run.call_args_list[1]
            self.assertIn("-aes-256-cbc", decrypt_args[0])
            self.assertEqual(decrypt_kwargs["input"], CIPHERTEXT)
            self.assertNotIn(token, str(run.call_args_list))

    def test_tampered_callback_is_rejected_before_aes_decryption(self):
        with tempfile.TemporaryDirectory() as directory:
            key = Path(directory) / "private/browser-deployment-key.pem"
            key.parent.mkdir()
            key.touch()
            tampered = {**PAYLOAD, "encryptedCallbackToken": envelope(tag=b"z" * 32)}
            with patch.object(agent.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout=KEYS, stderr=b"")) as run:
                with self.assertRaises(agent.DeploymentError):
                    agent.callback_client(tampered, directory)
                self.assertEqual(run.call_count, 1)

    def test_hybrid_callback_bounds_and_exact_fields_are_enforced(self):
        packet = json.loads(base64.b64decode(PAYLOAD["encryptedCallbackToken"]))
        variants = [{**packet, "extra": "not accepted"}, {**packet, "v": True},
                    {**packet, "iv": base64.b64encode(b"i" * 15).decode()},
                    {**packet, "ciphertext": base64.b64encode(b"c" * 17).decode()},
                    {**packet, "ciphertext": base64.b64encode(b"c" * 8224).decode()}]
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(agent.DeploymentError):
                agent.callback_ciphertext({"encryptedCallbackToken": base64.b64encode(json.dumps(variant).encode()).decode()})

    def test_callback_decryption_failure_does_not_expose_openssl_output(self):
        with tempfile.TemporaryDirectory() as directory:
            key = Path(directory) / "private/browser-deployment-key.pem"
            key.parent.mkdir()
            key.touch()
            with patch.object(agent.subprocess, "run", return_value=SimpleNamespace(returncode=1, stdout=b"sensitive", stderr=b"private failure")):
                with self.assertRaises(agent.DeploymentError) as error:
                    agent.callback_client(PAYLOAD, directory)
            self.assertNotIn("sensitive", str(error.exception))
            self.assertNotIn("private failure", str(error.exception))


def info(image=IMAGE, running=True, label=None):
    return {"Config": {"Image": image, "Labels": {} if label is None else {"com.csa1020.deployment": str(label)}},
            "State": {"Running": running}, "Mounts": [],
            "HostConfig": {"PortBindings": {"8000/tcp": [{"HostIp": "127.0.0.1", "HostPort": "8094"}]}}}


class FakeDocker(agent.DockerRuntime):
    def __init__(self, data_root, fail_live=False):
        super().__init__(data_root)
        self.containers = {agent.SPECS[14]["container"]: info()}
        self.fail_live = fail_live
        self.operations = []

    def inspect(self, name):
        return self.containers.get(name)

    def docker(self, *args, **kwargs):
        self.operations.append(args)
        if args[:2] == ("image", "inspect"):
            return '[{"Config":{"Labels":{"org.opencontainers.image.revision":"' + SHA + '"},"User":"node"}}]'
        if args[0] == "stop":
            self.containers[args[-1]]["State"]["Running"] = False
        elif args[0] == "rename":
            self.containers[args[2]] = self.containers.pop(args[1])
        elif args[0] == "start":
            self.containers[args[1]]["State"]["Running"] = True
        elif args[0] == "rm":
            self.containers.pop(args[-1], None)
        return ""

    def create(self, name, number, payload, publish):
        self.containers[name] = info(payload["image"], label=payload["deploymentId"])

    def wait_verified(self, number, payload, container=None):
        if self.fail_live and container is None:
            raise agent.DeploymentError("Injected post-switch failure")
        return {"passed": True}


class ReplacementTests(unittest.TestCase):
    def test_unrelated_mounts_or_ports_are_not_replaced(self):
        for mutate in [lambda value: value.update(Mounts=[{"Type": "bind", "Source": "/private"}]),
                       lambda value: value["HostConfig"].update(PortBindings={"8000/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8094"}]}),
                       lambda value: value["Config"].update(Image="unrelated/image:latest")]:
            value = info()
            mutate(value)
            with self.assertRaises(agent.DeploymentError):
                agent.DockerRuntime.validate_owned(value, 14)

    def test_success_keeps_previous_container_and_records_the_exact_image(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = FakeDocker(directory)
            receipt = runtime.deploy(14, {**PAYLOAD, "deploymentId": 42})
            self.assertTrue(receipt["passed"])
            self.assertTrue(runtime.containers["focuslane-app-exp14"]["State"]["Running"])
            self.assertFalse(runtime.containers["focuslane-app-exp14-previous"]["State"]["Running"])
            state = Path(directory) / "deployments/14/current.json"
            self.assertIn(IMAGE, state.read_text())
            self.assertNotIn("encryptedCallbackToken", state.read_text())

    def test_live_failure_restores_the_previous_app_and_does_not_save_new_state(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = FakeDocker(directory, fail_live=True)
            original = runtime.containers["focuslane-app-exp14"]
            with self.assertRaises(agent.DeploymentError):
                runtime.deploy(14, {**PAYLOAD, "deploymentId": 42})
            self.assertIs(runtime.containers["focuslane-app-exp14"], original)
            self.assertTrue(original["State"]["Running"])
            self.assertNotIn("focuslane-app-exp14-previous", runtime.containers)
            self.assertFalse((Path(directory) / "deployments/14/current.json").exists())

    def test_a_superseded_request_never_stops_the_existing_app(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = FakeDocker(directory)
            def superseded():
                raise agent.DeploymentError("Superseded")
            with self.assertRaises(agent.DeploymentError):
                runtime.deploy(14, {**PAYLOAD, "deploymentId": 42}, before_switch=superseded)
            self.assertFalse(any(operation[0] == "stop" for operation in runtime.operations))
            self.assertTrue(runtime.containers["focuslane-app-exp14"]["State"]["Running"])


if __name__ == "__main__":
    unittest.main()
