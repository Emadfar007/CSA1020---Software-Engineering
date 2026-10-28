"""Guards for immutable publication and preservation during browser deployment."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location('deploy_browser', Path(__file__).parents[1] / 'deploy-browser.py')
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)
DIGEST = deploy.REPOSITORY + '@sha256:' + 'a' * 64
OLD = {'State': {'Running': True}, 'Config': {'Image': 'previous-digest'}}


class BrowserDeploymentTests(unittest.TestCase):
    def test_digest_must_be_one_exact_published_repository_digest(self):
        self.assertEqual(deploy.select_digest([DIGEST]), DIGEST)
        for values in ([DIGEST, DIGEST], [], ['other/repository@sha256:' + 'a' * 64],
                       [deploy.REPOSITORY + ':latest'], [deploy.REPOSITORY + '@sha256:xyz'], {}):
            with self.subTest(values=values), self.assertRaises(RuntimeError):
                deploy.select_digest(values)

    def test_reserved_names_with_unrelated_or_persistent_data_are_preserved(self):
        records = [
            {'Config': {'Labels': {}}, 'Mounts': []},
            {'Config': {'Labels': {deploy.LABEL: '13'}}, 'Mounts': [{'Type': 'volume'}]},
            {'Config': {'Labels': {deploy.LABEL: '13'}}, 'Mounts': [{'Type': 'bind'}]},
        ]
        for record in records:
            with self.subTest(record=record), patch.object(deploy, 'inspect', return_value=record):
                with self.assertRaises(RuntimeError):
                    deploy.managed_container(deploy.NAME)

    def test_image_identity_requires_sha_build_and_non_root_user(self):
        record = {'Config': {'User': 'node', 'Labels': {'org.opencontainers.image.revision': 'b' * 40},
                             'Env': ['GIT_SHA=' + 'b' * 40, 'BUILD_NUMBER=9']}}
        deploy.check_identity(record, 'b' * 40, '9')
        with self.assertRaises(RuntimeError):
            deploy.check_identity(record, 'c' * 40, '9')
        with self.assertRaises(RuntimeError):
            deploy.check_identity(record, 'b' * 40, '10')
        record['Config']['User'] = 'root'
        with self.assertRaises(RuntimeError):
            deploy.check_identity(record, 'b' * 40, '9')

    def test_browser_url_cannot_contain_credentials_or_another_destination(self):
        self.assertTrue(deploy.valid_browser_url('https://lab-name-8091.app.github.dev/'))
        for value in ('http://lab-name-8091.app.github.dev', 'https://evil.example',
                      'https://lab-name-8094.app.github.dev/',
                      'https://user:secret@lab-name-8091.app.github.dev/',
                      'https://lab-name-8091.app.github.dev/?token=secret',
                      'https://lab-name-8091.app.github.dev:bad/'):
            with self.subTest(value=value):
                self.assertFalse(deploy.valid_browser_url(value))

    def test_failed_canary_never_stops_the_running_release(self):
        with patch.object(deploy, 'managed_container', side_effect=[OLD, None]), \
             patch.object(deploy, 'docker') as command, \
             patch.object(deploy, 'verify_container', side_effect=RuntimeError('canary failed')):
            with self.assertRaisesRegex(RuntimeError, 'canary failed'):
                deploy.deploy(DIGEST, 'b' * 40, '9', 'http://docker:8000')
        self.assertFalse(any(call.args[0] in ('stop', 'rename') for call in command.call_args_list))

    def test_failed_new_release_restores_the_previous_running_container(self):
        with patch.object(deploy, 'managed_container', side_effect=[OLD, None, None, {'Config': {'Image': DIGEST}}]), \
             patch.object(deploy, 'docker') as command, \
             patch.object(deploy, 'verify_container', side_effect=[{}, RuntimeError('new release failed')]):
            with self.assertRaisesRegex(RuntimeError, 'new release failed'):
                deploy.deploy(DIGEST, 'b' * 40, '9', 'http://docker:8000')
        calls = [call.args for call in command.call_args_list]
        self.assertIn(('rename', deploy.NAME, deploy.PREVIOUS), calls)
        self.assertIn(('rm', '-f', deploy.NAME), calls)
        self.assertIn(('rename', deploy.PREVIOUS, deploy.NAME), calls)
        self.assertIn(('start', deploy.NAME), calls)

    def test_rename_failure_restarts_the_old_container_without_deleting_it(self):
        def command(*arguments, **options):
            if arguments == ('rename', deploy.NAME, deploy.PREVIOUS):
                raise RuntimeError('rename failed')
        with patch.object(deploy, 'managed_container', side_effect=[OLD, None, None]), \
             patch.object(deploy, 'docker', side_effect=command) as process, \
             patch.object(deploy, 'verify_container', return_value={}):
            with self.assertRaisesRegex(RuntimeError, 'rename failed'):
                deploy.deploy(DIGEST, 'b' * 40, '9', 'http://docker:8000')
        calls = [call.args for call in process.call_args_list]
        self.assertIn(('start', deploy.NAME), calls)
        self.assertNotIn(('rm', '-f', deploy.NAME), calls)


if __name__ == '__main__':
    unittest.main()
