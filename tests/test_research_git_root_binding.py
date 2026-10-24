"""Real repository boundaries for shared publication and source readers.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Credit the package-local Git environment policy in the PR2530 source-partner
 audit and the shared stored-object, history and export regression authors.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_research_commit as publication
import export_research_package as exporter
import find_overlap as overlap
import new_research_package as scaffold
import research_package as package
sys.path.pop(0)


class GitRootBindingTests(unittest.TestCase):
    package = 'research/fixture'

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='git-root-binding-')
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name)
        # Fixture setup must not itself be redirected by the donor's shell.
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        self.env.update(GIT_AUTHOR_NAME='JoyboyBrian',
                        GIT_AUTHOR_EMAIL='122925040+JoyboyBrian@users.noreply.github.com',
                        GIT_COMMITTER_NAME='JoyboyBrian',
                        GIT_COMMITTER_EMAIL='122925040+JoyboyBrian@users.noreply.github.com')
        self.environment = patch.dict(os.environ, self.env, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.root = self.make_repo('intended', b'intended source\n')
        self.foreign = self.make_repo('foreign', b'foreign source\n')
        self.head = self.git(self.root, 'rev-parse', 'HEAD').decode().strip()
        self.foreign_head = self.git(self.foreign, 'rev-parse', 'HEAD').decode().strip()
        self.redirect = {'GIT_DIR': str(self.foreign / '.git'),
                         'GIT_WORK_TREE': str(self.foreign)}

    def git(self, root, *args):
        return subprocess.run(['git', *args], cwd=root, env=self.env,
                              capture_output=True, check=True, timeout=15).stdout

    def commit(self, root):
        self.git(root, 'add', '.')
        self.git(root, '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                 '-c', 'maintenance.auto=false', '-c', 'gc.auto=0', 'commit', '-qm', 'fixture')

    def make_repo(self, name, payload):
        root = self.parent / name
        root.mkdir()
        self.git(root, 'init', '-q')
        self.git(root, 'config', 'core.autocrlf', 'false')
        files = {'input.txt': payload, 'certificates/selected-result.json': b'{}',
                 'docs/research/agent-task-catalog.json': json.dumps({
                     'priority_revision': 7, 'tracks': [{'tasks': [
                         {'id': 'fixture', 'question': 'Bind the requested repository'}]}]}).encode()}
        for path, raw in files.items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        self.commit(root)
        target = scaffold.create(root, 'fixture', 'fixture', 'Fixture', ['input.txt'])
        task = json.loads((target / 'TASK.json').read_bytes())
        task.update(bottleneck_link='Source binding', stop_rule='Bounded fixture',
                    outcome='completed', evidence='Real repository boundary fixture',
                    ai_assistance='OpenAI Codex', open_questions=[],
                    no_open_questions_reason='Only publication transport is checked')
        (target / 'TASK.json').write_text(json.dumps(task))
        manifest = json.loads((target / 'VERIFY.json').read_bytes())
        manifest['status'] = 'ready'
        manifest['commands'][0]['checks'] = 'Source binding fixture'
        (target / 'VERIFY.json').write_text(json.dumps(manifest))
        self.commit(root)
        return root

    def test_dirty_publication_cannot_pass_against_foreign_head(self):
        # The intended dirty tree exactly matches the foreign publication. This
        # formerly passed, instead of comparing with the intended HEAD.
        shutil.copytree(self.foreign / self.package, self.root / self.package, dirs_exist_ok=True)
        shutil.copyfile(self.foreign / 'input.txt', self.root / 'input.txt')
        with self.assertRaisesRegex(ValueError, 'working/commit bytes differ'):
            publication.check(self.root, self.package)
        for redirect in ({'GIT_DIR': self.redirect['GIT_DIR']}, self.redirect):
            with self.subTest(redirect=redirect), patch.dict(os.environ, redirect):
                with self.assertRaisesRegex(ValueError, 'working/commit bytes differ'):
                    publication.check(self.root, self.package)

    def test_export_and_history_stay_in_requested_repository(self):
        with patch.dict(os.environ, self.redirect):
            result = publication.check(self.root, self.package, check_source_history=True)
            self.assertEqual(result['commit'], self.head)
            receipt = exporter.export(self.root, self.package, 'HEAD', self.parent / 'bundle.tar')
            self.assertEqual(receipt['commit'], self.head)
            with tarfile.open(self.parent / 'bundle.tar') as archive:
                self.assertEqual(archive.extractfile('input.txt').read(), b'intended source\n')
            self.assertEqual(exporter.check_bundle(self.parent / 'bundle.tar'), receipt)
            self.assertEqual(publication.history_git(self.root, 'rev-parse', 'HEAD').stdout.strip(),
                             self.head.encode())

    def test_foreign_live_pins_do_not_validate(self):
        shutil.copytree(self.foreign / self.package, self.root / self.package, dirs_exist_ok=True)
        shutil.copyfile(self.foreign / 'input.txt', self.root / 'input.txt')
        with patch.dict(os.environ, self.redirect):
            with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                package.validate(self.root, self.package)

    def test_every_reader_and_scaffold_uses_local_objects(self):
        name = 'input.txt'
        oid = self.git(self.root, 'rev-parse', 'HEAD:' + name).decode().strip()
        expected = [(oid, b'intended source\n')]
        with patch.dict(os.environ, self.redirect):
            self.assertEqual(list(package.git_source_rows(self.root, 'HEAD', [name])), expected)
            self.assertEqual(list(package.git_blobs(self.root, ['HEAD:' + name])), expected)
            self.assertEqual(list(package._git_blob_batch(self.root, ['HEAD:' + name], False)), expected)
            self.assertEqual(package.git(self.root, 'show', 'HEAD:' + name), expected[0][1])
            package.validate(self.root, self.package)
            created = scaffold.create(self.root, 'second', 'fixture', 'Fixture', [name])
            self.assertEqual(json.loads((created / 'SOURCES.json').read_bytes())['base_commit'], self.head)

    def test_head_inventory_planning_and_overlap_cannot_use_foreign_notes(self):
        path = self.root / 'research/local-only/README.md'
        path.parent.mkdir()
        path.write_text('local note')
        self.commit(self.root)
        head = self.git(self.root, 'rev-parse', 'HEAD').decode().strip()
        with patch.dict(os.environ, self.redirect):
            self.assertIn('research/local-only/README.md', package.tracked_input_paths(self.root))
            self.assertIn(self.package, package.plan(self.root, ['input.txt']))
            coverage, warnings = overlap.local_coverage(self.root, overlap.local_records(self.root))
            self.assertEqual(coverage['head'], head)
            self.assertTrue(coverage['complete_head_inventory'])
            self.assertEqual(warnings, [])

    def test_redirecting_environment_does_not_break_linked_worktree(self):
        linked = self.parent / 'linked'
        self.git(self.root, 'worktree', 'add', '--detach', str(linked), self.head)
        self.assertTrue((linked / '.git').is_file())
        with patch.dict(os.environ, self.redirect):
            self.assertEqual(publication.check(linked, self.package, check_source_history=True)['commit'], self.head)
            package.validate(linked, self.package)
            self.assertEqual(package.git(linked, 'show', 'HEAD:input.txt'), b'intended source\n')

    def test_other_repository_selection_channels_are_not_inherited(self):
        variants = [
            {'GIT_COMMON_DIR': str(self.foreign / '.git')},
            {'GIT_OBJECT_DIRECTORY': str(self.foreign / '.git/objects')},
            {'GIT_INDEX_FILE': str(self.parent / 'absent-index')},
            {'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'core.bare', 'GIT_CONFIG_VALUE_0': 'true'},
            {'GIT_CONFIG_PARAMETERS': "'core.bare'='true'"},
        ]
        for env in variants:
            with self.subTest(env=env), patch.dict(os.environ, env):
                self.assertEqual(publication.check(self.root, self.package, check_source_history=True)['commit'], self.head)

    def test_parent_and_verifier_environments_are_unchanged(self):
        with patch.dict(os.environ, self.redirect):
            before = dict(os.environ)
            package.git(self.root, 'show', 'HEAD:input.txt')
            self.assertEqual(dict(os.environ), before)
            # Repository isolation is not applied to package command processes.
            output = self.parent / 'child.json'
            command = 'import os,json,pathlib;pathlib.Path(' + repr(str(output)) + ').write_text(json.dumps({k:os.environ[k] for k in ("GIT_DIR","GIT_WORK_TREE")}))'
            package.run_command([sys.executable, '-I', '-B', '-c', command], self.root, 5)
            self.assertEqual(json.loads(output.read_text()), self.redirect)


if __name__ == '__main__':
    unittest.main()
