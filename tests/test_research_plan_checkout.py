"""Exercise the workflow's actual exact-base step using local shallow Git fixtures."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAN_WORKFLOW = '.github/workflows/research-packages.yml'
BATCH_WORKFLOW = '.github/workflows/research-package-batch.yml'
STEP_NAME = 'Fetch exact automated review base'
DEPTH_EXPRESSION = "${{ github.event_name == 'workflow_dispatch' && '0' || '2' }}"
BASE_EXPRESSION = '${{ github.event.pull_request.base.sha || github.event.before || inputs.base }}'


def fetch_step():
    """Extract this simple actual run block, as the existing CI drift tests do."""
    text = (ROOT / PLAN_WORKFLOW).read_text(encoding='utf-8')
    marker = '      - name: ' + STEP_NAME + '\n'
    if text.count(marker) != 1:
        raise ValueError('expected one exact automated review-base step')
    body = text.split(marker, 1)[1].split('\n      - ', 1)[0]
    marker = '        run: |\n'
    if body.count(marker) != 1:
        raise ValueError('expected one literal Bash run block')
    header, block = body.split(marker, 1)
    lines = block.rstrip('\n').splitlines()
    if not lines or any(line and not line.startswith('          ') for line in lines):
        raise ValueError('unsupported review-base Bash block')
    return header, textwrap.dedent('\n'.join(lines)) + '\n'


def step_environment(base):
    """Use the literal security settings from the step being exercised."""
    header, _ = fetch_step()
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_ALLOW_PROTOCOL='file', GIT_CONFIG_NOSYSTEM='1',
               GIT_CONFIG_GLOBAL=os.devnull, REVIEW_BASE=base)
    for key in ('GIT_NO_REPLACE_OBJECTS', 'GIT_TERMINAL_PROMPT'):
        values = re.findall(r'^          ' + key + r": ['\"]([01])['\"]$", header, re.M)
        if len(values) != 1:
            raise ValueError('expected one literal workflow environment value: ' + key)
        env[key] = values[0]
    return env


class PlanCheckoutSourceContractTests(unittest.TestCase):
    def test_actual_step_uses_exact_event_base_and_source_settings(self):
        text = (ROOT / PLAN_WORKFLOW).read_text(encoding='utf-8')
        header, script = fetch_step()
        self.assertIn("        if: github.event_name != 'workflow_dispatch'\n", header)
        bases = re.findall(r'^          REVIEW_BASE: (.+)$', text, re.M)
        self.assertEqual(bases, [BASE_EXPRESSION, BASE_EXPRESSION])
        self.assertEqual(step_environment('a' * 40)['GIT_NO_REPLACE_OBJECTS'], '1')
        self.assertEqual(step_environment('a' * 40)['GIT_TERMINAL_PROMPT'], '0')
        self.assertIn('set -euo pipefail', script)
        self.assertIn('--no-tags --no-recurse-submodules --depth=1 origin "$REVIEW_BASE"', script)
        self.assertIn('git -c maintenance.auto=false -c gc.auto=0 fetch', script)
        self.assertIn('rev-parse --verify --end-of-options', script)

    def test_dispatch_full_history_and_replay_boundary_remain_explicit(self):
        plan = (ROOT / PLAN_WORKFLOW).read_text(encoding='utf-8')
        batch = (ROOT / BATCH_WORKFLOW).read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'^          fetch-depth: (.+)$', plan, re.M),
                         [DEPTH_EXPRESSION])
        self.assertEqual(re.findall(r'^          fetch-depth: (.+)$', batch, re.M), ['0'])
        self.assertIn("          persist-credentials: false\n", plan)
        self.assertIn("          persist-credentials: false\n", batch)
        self.assertIn("    if: needs.plan.outputs.count != '0'\n", plan)
        events = plan.split('\npermissions:\n', 1)[0]
        self.assertIn('\n  pull_request:\n', events)
        self.assertIn('\n  push:\n    branches: [main]\n', events)
        self.assertNotRegex(events, r"(?m)^\s*['\"]?paths(?:-ignore)?['\"]?\s*:")

    def test_publication_history_checker_still_rejects_shallow_ancestry(self):
        source = (ROOT / 'scripts/check_research_commit.py').read_text(encoding='utf-8')
        self.assertIn("history_git(root, 'rev-parse', '--is-shallow-repository')", source)
        self.assertIn("shallow.stdout.strip() == b'false'", source)
        self.assertIn("history_git(root, 'merge-base', '--is-ancestor', pin, commit)", source)


@unittest.skipUnless(os.name == 'posix' and shutil.which('bash') and shutil.which('git'),
                     'the Ubuntu workflow step requires POSIX Bash and Git')
class PlanCheckoutGitTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.temporary_root = Path(temporary.name)
        self.writer = self.temporary_root / 'writer'
        self.writer.mkdir()
        self.origin = self.temporary_root / 'origin.git'
        self.git(self.temporary_root, 'init', '--bare', '-q', str(self.origin))
        self.git(self.writer, 'init', '-q', '--initial-branch=main')
        self.configure(self.writer)
        for name in ('scripts/research_package.py', PLAN_WORKFLOW, BATCH_WORKFLOW):
            self.write(self.writer, name, (ROOT / name).read_bytes())
        for slug in ('alpha', 'beta'):
            self.write(self.writer, 'inputs/' + slug + '.txt', b'original\n')
            manifest = json.dumps({'inputs': ['inputs/' + slug + '.txt']}) + '\n'
            self.write(self.writer, 'research/' + slug + '/VERIFY.json', manifest.encode())
        self.base = self.commit(self.writer)
        self.write(self.writer, 'inputs/beta.txt', b'earlier push change\n')
        self.middle = self.commit(self.writer)
        self.write(self.writer, 'inputs/alpha.txt', b'latest push change\n')
        self.head = self.commit(self.writer)
        self.git(self.writer, 'tag', 'fixture-base', self.base)
        self.git(self.writer, 'remote', 'add', 'origin', self.origin.as_uri())
        self.git(self.writer, 'push', '-q', 'origin', 'HEAD:refs/heads/main',
                 self.base + ':refs/heads/alternate', 'refs/tags/fixture-base')
        self.git(self.origin, 'symbolic-ref', 'HEAD', 'refs/heads/main')
        self.checkout = self.clone('shallow', depth=2)

    def git(self, root, *args, check=True, env=None):
        if env is None:
            env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
            env.update(GIT_ALLOW_PROTOCOL='file', GIT_TERMINAL_PROMPT='0',
                       GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
        return subprocess.run(['git', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0',
                               *args], cwd=root, env=env, capture_output=True,
                              text=True, check=check, timeout=20)

    def configure(self, root):
        for key, value in (('user.name', 'Fixture'), ('user.email', 'fixture@example.invalid'),
                           ('core.autocrlf', 'false')):
            self.git(root, 'config', key, value)

    def write(self, root, name, raw):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def commit(self, root):
        self.git(root, 'add', '--all')
        self.git(root, 'commit', '-qm', 'fixture')
        return self.git(root, 'rev-parse', 'HEAD').stdout.strip()

    def clone(self, name, depth=None):
        destination = self.temporary_root / name
        args = ['clone', '-q', '--no-local']
        if depth is not None:
            args.extend(['--no-tags', '--single-branch', '--depth=' + str(depth)])
        self.git(self.temporary_root, *args, self.origin.as_uri(), str(destination))
        self.configure(destination)
        return destination

    def unavailable_origin(self, root):
        self.git(root, 'remote', 'set-url', 'origin',
                 (self.temporary_root / 'unavailable.git').as_uri())

    def run_step(self, base, root=None):
        root = root or self.checkout
        before = self.git(root, 'rev-parse', 'HEAD').stdout
        result = subprocess.run(['bash', '--noprofile', '--norc', '-e', '-o', 'pipefail',
                                 '-c', fetch_step()[1]], cwd=root, env=step_environment(base),
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(self.git(root, 'rev-parse', 'HEAD').stdout, before)
        return result

    def selected(self, root, base):
        output = self.temporary_root / 'github-output'
        output.unlink(missing_ok=True)
        result = subprocess.run([sys.executable, '-B', str(root / 'scripts/research_package.py'),
                                 '--changed-since', base, '--matrix-batch-size', '256',
                                 '--github-output', str(output)], cwd=root,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        matrix = json.loads(result.stdout)
        fields = dict(line.split('=', 1) for line in output.read_text().splitlines())
        self.assertEqual(json.loads(fields['matrix']), matrix)
        names = [name for row in matrix['include'] for name in row['packages']]
        self.assertEqual(int(fields['count']), len(names))
        return names

    def assert_stops_before_selector(self, base):
        output = self.temporary_root / 'failure-output'
        output.write_text('existing-output\n', encoding='utf-8')
        entered = self.temporary_root / 'selector-entered'
        env = step_environment(base)
        env['PLAN_FETCH_STEP_SOURCE'] = fetch_step()[1]
        env['PLAN_SELECTOR_ENTERED'] = str(entered)
        selector = [sys.executable, '-B', str(self.checkout / 'scripts/research_package.py'),
                    '--changed-since', base, '--github-output', str(output)]
        # Separate Bash invocations match job-step exit behavior, including exit0.
        driver = 'bash --noprofile --norc -e -o pipefail -c "$PLAN_FETCH_STEP_SOURCE"\n'
        driver += ': > "$PLAN_SELECTOR_ENTERED"\n'
        driver += shlex.join(selector) + '\n'
        before = self.git(self.checkout, 'rev-parse', 'HEAD').stdout
        result = subprocess.run(['bash', '--noprofile', '--norc', '-e', '-o', 'pipefail',
                                 '-c', driver], cwd=self.checkout, env=env,
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse(entered.exists(), 'exact-base step must stop before selector entry')
        self.assertEqual(output.read_text(encoding='utf-8'), 'existing-output\n')
        self.assertEqual(self.git(self.checkout, 'rev-parse', 'HEAD').stdout, before)
        return result

    def test_multicommit_push_fetches_exact_older_base_and_keeps_both_consumers(self):
        self.assertEqual(self.git(self.checkout, 'rev-parse', '--is-shallow-repository').stdout.strip(), 'true')
        self.assertNotEqual(self.git(self.checkout, 'cat-file', '-e', self.base,
                                    check=False).returncode, 0)
        self.assertEqual(self.selected(self.checkout, 'HEAD^'), ['research/alpha'])
        self.assertEqual(self.run_step(self.base).returncode, 0)
        expected = ['research/alpha', 'research/beta']
        self.assertEqual(self.selected(self.writer, self.base), expected)
        self.assertEqual(self.selected(self.checkout, self.base), expected)
        self.assertEqual(self.git(self.checkout, 'rev-parse', self.base + '^{commit}').stdout.strip(), self.base)

    def test_pr_merge_compares_exact_event_base_not_older_common_ancestor(self):
        self.git(self.writer, 'checkout', '-qb', 'feature', self.base)
        self.write(self.writer, 'research/alpha/pr-note.txt', b'PR-only change\n')
        self.commit(self.writer)
        self.git(self.writer, 'checkout', '-q', 'main')
        self.git(self.writer, 'merge', '--no-ff', '-qm', 'fixture merge', 'feature')
        merged = self.git(self.writer, 'rev-parse', 'HEAD').stdout.strip()
        self.git(self.writer, 'push', '-q', 'origin', 'HEAD:refs/heads/main')
        checkout = self.clone('pull-merge', depth=2)
        self.unavailable_origin(checkout)
        self.assertEqual(self.run_step(self.head, checkout).returncode, 0)
        self.assertEqual(self.git(checkout, 'rev-parse', 'HEAD').stdout.strip(), merged)
        self.assertEqual(self.selected(checkout, self.head), ['research/alpha'])
        self.assertEqual(self.selected(self.writer, self.head), ['research/alpha'])
        self.assertEqual(self.selected(self.writer, self.base), ['research/alpha', 'research/beta'])

    def test_available_exact_base_does_not_need_a_remote(self):
        self.unavailable_origin(self.checkout)
        self.assertEqual(self.run_step(self.middle).returncode, 0)
        self.assertEqual(self.selected(self.checkout, self.middle), ['research/alpha'])

    def test_allzero_40_and_64_bases_skip_fetch_and_preserve_select_all(self):
        self.unavailable_origin(self.checkout)
        for size in (40, 64):
            with self.subTest(size=size):
                base = '0' * size
                self.assertEqual(self.run_step(base).returncode, 0)
                self.assertEqual(self.selected(self.checkout, base), ['research/alpha', 'research/beta'])

    def test_bad_or_missing_payload_and_shell_refspec_injection_stop_without_outputs(self):
        marker = self.temporary_root / 'must-not-exist'
        for value in ('', 'HEAD^', 'main', '--upload-pack=evil', 'a' * 39, 'g' * 40,
                      'A' * 40, self.middle + '\n',
                      self.middle + '; touch ' + shlex.quote(str(marker)),
                      self.middle + '$(touch ' + shlex.quote(str(marker)) + ')'):
            with self.subTest(value=value):
                self.assert_stops_before_selector(value)
                self.assertFalse(marker.exists())

    def test_valid_unavailable_commit_stops_without_fallback_or_matrix(self):
        self.assert_stops_before_selector('f' * 40)

    def test_unavailable_remote_stops_when_the_real_base_is_missing(self):
        self.unavailable_origin(self.checkout)
        self.assert_stops_before_selector(self.base)

    def test_blob_object_id_cannot_become_a_comparison_commit(self):
        blob = self.git(self.checkout, 'rev-parse', 'HEAD:inputs/alpha.txt').stdout.strip()
        self.assert_stops_before_selector(blob)

    def test_replacement_ref_is_not_authority_for_a_missing_raw_base(self):
        self.git(self.checkout, 'update-ref', 'refs/replace/' + self.base, self.head)
        # Positive control: ordinary Git can now report the missing original as a commit.
        self.assertEqual(self.git(self.checkout, 'cat-file', '-t', self.base).stdout.strip(), 'commit')
        self.unavailable_origin(self.checkout)
        self.assert_stops_before_selector(self.base)

    def test_replacement_ref_cannot_hide_the_real_base_fetch_and_both_consumers(self):
        self.git(self.checkout, 'update-ref', 'refs/replace/' + self.base, self.head)
        self.assertEqual(self.git(self.checkout, 'cat-file', '-t', self.base).stdout.strip(), 'commit')
        self.assertEqual(self.run_step(self.base).returncode, 0)
        raw_env = step_environment(self.base)
        self.assertEqual(self.git(self.checkout, 'rev-parse', self.base + '^{commit}',
                                  env=raw_env).stdout.strip(), self.base)
        self.assertEqual(self.selected(self.checkout, self.base), ['research/alpha', 'research/beta'])

    def test_targeted_fetch_does_not_import_unrelated_branches_or_tags(self):
        self.assertEqual(self.run_step(self.base).returncode, 0)
        refs = self.git(self.checkout, 'for-each-ref', '--format=%(refname)').stdout.splitlines()
        self.assertNotIn('refs/remotes/origin/alternate', refs)
        self.assertNotIn('refs/tags/fixture-base', refs)

    def test_dispatch_full_checkout_keeps_relative_tag_and_remote_ref_vocabulary(self):
        checkout = self.clone('dispatch-full')
        self.assertEqual(self.git(checkout, 'rev-parse', '--is-shallow-repository').stdout.strip(), 'false')
        for ref, expected in (('HEAD^', ['research/alpha']),
                              ('HEAD~2', ['research/alpha', 'research/beta']),
                              ('fixture-base', ['research/alpha', 'research/beta']),
                              ('origin/alternate', ['research/alpha', 'research/beta'])):
            with self.subTest(ref=ref):
                self.assertEqual(self.selected(checkout, ref), expected)

    def test_missing_dispatch_parent_at_root_still_fails_without_matrix(self):
        checkout = self.clone('dispatch-root')
        self.git(checkout, 'checkout', '-q', '--detach', self.base)
        output = self.temporary_root / 'root-output'
        result = subprocess.run([sys.executable, '-B', str(checkout / 'scripts/research_package.py'),
                                 '--changed-since', 'HEAD^', '--github-output', str(output)],
                                cwd=checkout, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())

    def test_both_shared_workflow_changes_still_invalidate_every_registered_fixture(self):
        for name in (PLAN_WORKFLOW, BATCH_WORKFLOW):
            with self.subTest(name=name):
                base = self.git(self.checkout, 'rev-parse', 'HEAD').stdout.strip()
                path = self.checkout / name
                path.write_bytes(path.read_bytes() + b'\n# changed shared control\n')
                self.commit(self.checkout)
                self.assertEqual(self.selected(self.checkout, base), ['research/alpha', 'research/beta'])


if __name__ == '__main__':
    unittest.main()
