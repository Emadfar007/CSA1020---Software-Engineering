"""Deployment protocol checks: no network or credentials are used."""
from argparse import Namespace
import base64
import hashlib
import hmac
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import request_deployment as protocol


def arguments(**overrides):
    values = dict(experiment=14,
                  image="coastrider7/csa1020-exp14-focuslane@sha256:" + "a" * 64,
                  sha="b" * 40, run_id=123, build="4.1",
                  url=f"https://{protocol.CODESPACE}-8094.app.github.dev/",
                  wait_seconds=30, public_key=Path("deployment-public.pem"))
    values.update(overrides)
    return Namespace(**values)


class FakeAPI:
    def __init__(self, states=None, sha="b" * 40):
        self.states = states or []
        self.sha = sha
        self.calls = []
        self.token = "fixture-job-token"

    def __call__(self, path, method="GET", payload=None):
        self.calls.append((path, method, payload))
        if path == "/deployments":
            return {"id": 17, "sha": self.sha}
        if method == "POST":
            return payload
        return self.states


class DeploymentProtocolTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(protocol, "encrypt_callback_token", return_value="sealed-fixture")
        self.encrypt = patcher.start()
        self.addCleanup(patcher.stop)

    def test_request_binds_exact_commit_image_and_run(self):
        args = arguments()
        api = FakeAPI([{"state": "success", "environment_url": args.url}])
        receipt = protocol.request_and_wait(args, api)
        body = api.calls[0][2]
        self.assertEqual(body["ref"], args.sha)
        self.assertFalse(body["auto_merge"])
        self.assertFalse(body["production_environment"])
        self.assertTrue(body["transient_environment"])
        self.assertEqual(body["environment"], "codespaces-exp14")
        self.assertEqual(body["payload"], {"protocol": 1, "experiment": 14,
                         "image": args.image, "sourceSha": args.sha,
                         "runId": 123, "buildNumber": "4.1",
                         "encryptedCallbackToken": "sealed-fixture"})
        self.encrypt.assert_called_once_with("fixture-job-token", args.public_key)
        self.assertEqual(receipt["deploymentId"], 17)
        self.assertEqual(receipt["state"], "success")
        self.assertEqual(api.calls[1][2]["state"], "queued")

    def test_rejects_cross_experiment_or_mutable_image_before_api(self):
        for image in ["coastrider7/csa1020-exp14-focuslane:latest",
                      "coastrider7/csa1020-exp19-packlight@sha256:" + "a" * 64]:
            api = FakeAPI()
            with self.assertRaises(protocol.DeploymentError):
                protocol.request_and_wait(arguments(image=image), api)
            self.assertEqual(api.calls, [])

    def test_rejects_other_repo_or_public_destination(self):
        with patch.dict(protocol.os.environ, {"GITHUB_REPOSITORY": "other/repo"}):
            with self.assertRaises(protocol.DeploymentError):
                protocol.validate(arguments())
        with self.assertRaises(protocol.DeploymentError):
            protocol.validate(arguments(url="https://example.com/"))

    def test_cannot_accept_created_deployment_for_another_commit(self):
        api = FakeAPI(sha="c" * 40)
        with self.assertRaises(protocol.DeploymentError):
            protocol.request_and_wait(arguments(), api)
        self.assertEqual(len(api.calls), 1)

    def test_controller_failure_fails_the_workflow(self):
        with self.assertRaises(protocol.DeploymentError):
            protocol.request_and_wait(arguments(), FakeAPI([{"state":"failure"}]))

    def test_success_must_name_the_expected_private_port(self):
        with self.assertRaises(protocol.DeploymentError):
            protocol.request_and_wait(arguments(), FakeAPI([
                {"state":"success", "environment_url":"https://example.com/"}]))

    def test_offline_lab_times_out_and_marks_request_failed(self):
        api = FakeAPI([{"state":"queued"}])
        with self.assertRaises(protocol.DeploymentError):
            protocol.request_and_wait(arguments(wait_seconds=0), api,
                                      clock=lambda: 100, sleep=lambda _: None)
        self.assertEqual(api.calls[-1][1], "POST")
        self.assertEqual(api.calls[-1][2]["state"], "failure")


class CallbackEncryptionTests(unittest.TestCase):
    def test_seals_large_job_token_using_authenticated_hybrid_envelope(self):
        token = "x" * 1000
        keys, iv, cipher, wrapped = bytes(range(64)), bytes(range(16)), b"c" * 1008, b"w" * 384
        with patch.object(protocol.secrets, "token_bytes", side_effect=[keys, iv]), \
                patch.object(protocol.subprocess, "run", side_effect=[
                    subprocess.CompletedProcess([], 0, cipher, b""),
                    subprocess.CompletedProcess([], 0, wrapped, b"")]) as run:
            result = protocol.encrypt_callback_token(token, Path("public.pem"))
        packet = json.loads(base64.b64decode(result))
        self.assertEqual(set(packet), {"v", "key", "iv", "ciphertext", "tag"})
        self.assertEqual(packet["v"], 1)
        self.assertEqual(base64.b64decode(packet["key"]), wrapped)
        self.assertEqual(base64.b64decode(packet["iv"]), iv)
        self.assertEqual(base64.b64decode(packet["ciphertext"]), cipher)
        expected_tag = hmac.new(keys[32:], b"CSA1020-CD-v1\0" + wrapped + iv + cipher,
                                hashlib.sha256).digest()
        self.assertEqual(base64.b64decode(packet["tag"]), expected_tag)
        aes_call, rsa_call = run.call_args_list
        self.assertEqual(aes_call.kwargs["input"], token.encode())
        self.assertIn("-aes-256-cbc", aes_call.args[0])
        self.assertIn(keys[:32].hex(), aes_call.args[0])
        self.assertIn(iv.hex(), aes_call.args[0])
        self.assertEqual(rsa_call.kwargs["input"], keys)
        self.assertNotIn(token, rsa_call.args[0])
        self.assertIn("rsa_padding_mode:oaep", rsa_call.args[0])
        self.assertIn("rsa_oaep_md:sha256", rsa_call.args[0])

    def test_invalid_key_cannot_send_a_deployment_request(self):
        with patch.object(protocol.subprocess, "run", return_value=
                          subprocess.CompletedProcess([], 1, b"", b"invalid key")):
            with self.assertRaises(protocol.DeploymentError):
                protocol.encrypt_callback_token("fixture-job-token", Path("invalid.pem"))

    def test_rejects_empty_or_oversized_token_before_launching_openssl(self):
        with patch.object(protocol.subprocess, "run") as run:
            for token in ("", "x" * 8193):
                with self.assertRaises(protocol.DeploymentError):
                    protocol.encrypt_callback_token(token, Path("public.pem"))
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
