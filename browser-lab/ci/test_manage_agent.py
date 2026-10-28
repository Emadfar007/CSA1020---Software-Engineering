"""The lifecycle helper must never signal a PID belonging to another command."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("manage_agent", Path(__file__).with_name("manage_agent.py"))
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repository"
        self.data = self.root / "private-data"
        self.pidfile = self.data / "private/browser-deployer.pid"
        self.pidfile.parent.mkdir(parents=True)
        self.pidfile.write_text("12345\n")
        self.arguments = ["python3", str(self.repo / "browser-lab/ci/deployment_agent.py"), "--data-root", str(self.data)]

    def test_only_exact_repository_agent_and_data_root_are_accepted(self):
        self.assertTrue(manager.is_our_command(self.arguments, self.repo, self.data))
        self.assertTrue(manager.is_our_command(["bash", "-lic", manager.command(self.repo, self.data)], self.repo, self.data))
        self.assertFalse(manager.is_our_command(["python3", "-c", self.arguments[1]], self.repo, self.data))
        self.assertFalse(manager.is_our_command([*self.arguments[:-1], "/another/private-data"], self.repo, self.data))
        self.assertFalse(manager.is_our_command(["bash", "-c", "echo " + self.arguments[1]], self.repo, self.data))

    def test_status_does_not_remove_or_signal_an_unrelated_pid(self):
        with patch.object(manager, "process_arguments", return_value=["unrelated-process"]):
            result = manager.status(self.repo, self.data)
        self.assertFalse(result["running"])
        self.assertTrue(result["pidFileNeedsReview"])
        self.assertTrue(self.pidfile.exists())

    def test_stop_refuses_an_unrelated_process_without_sending_a_signal(self):
        with patch.object(manager, "process_arguments", return_value=["unrelated-process"]), \
             patch.object(manager.os, "pidfd_open", return_value=77, create=True), \
             patch.object(manager.signal, "pidfd_send_signal", create=True) as send, \
             patch.object(manager.os, "close"):
            with self.assertRaises(manager.AgentError):
                manager.stop(self.repo, self.data)
            send.assert_not_called()
        self.assertTrue(self.pidfile.exists())

    def test_stop_signals_only_the_validated_pidfd_and_removes_pid_after_exit(self):
        with patch.object(manager, "process_arguments", side_effect=[self.arguments, self.arguments, None]), \
             patch.object(manager.os, "pidfd_open", return_value=77, create=True), \
             patch.object(manager.signal, "pidfd_send_signal", create=True) as send, \
             patch.object(manager.os, "close") as close:
            result = manager.stop(self.repo, self.data)
            send.assert_called_once_with(77, manager.signal.SIGTERM)
            close.assert_called_once_with(77)
        self.assertFalse(result["running"])
        self.assertFalse(self.pidfile.exists())

    def test_key_mismatch_prevents_startup_without_exposing_key_material(self):
        private = self.data / "private/browser-deployment-key.pem"
        public = self.repo / "browser-lab/ci/deployment-public.pem"
        public.parent.mkdir(parents=True)
        private.write_text("private fixture")
        public.write_text("public fixture")
        with patch.object(manager.subprocess, "run", side_effect=[
                SimpleNamespace(returncode=0, stdout=b"first-public-key"),
                SimpleNamespace(returncode=0, stdout=b"different-public-key")]), \
             patch.object(manager.subprocess, "Popen") as spawn:
            with self.assertRaises(manager.AgentError) as error:
                manager.start(self.repo, self.data)
            spawn.assert_not_called()
            self.assertNotIn("private fixture", str(error.exception))

    def test_cli_stop_fails_until_the_agent_has_finished_exiting(self):
        arguments = ["manage_agent.py", "stop", "--repo", str(self.repo), "--data-root", str(self.data)]
        for result, expected in [({"running": True, "stopping": True}, 2), ({"running": False}, 0)]:
            with self.subTest(result=result), patch("sys.argv", arguments), \
                 patch.object(manager, "stop", return_value=result), patch("builtins.print"):
                self.assertEqual(manager.main(), expected)


if __name__ == "__main__":
    unittest.main()
