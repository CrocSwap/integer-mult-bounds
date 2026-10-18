"""Live-checkout inputs of the selected replay must stay pinned; its workflow should trigger on them."""
from contextlib import redirect_stdout
from hashlib import sha256
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selected_ci_inputs', ROOT / 'scripts/check_selected_ci_inputs.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
RECORD = json.loads((ROOT / 'certificates/selected-result.json').read_bytes())
SELECTED_1094 = RECORD['reproduce'] == 'make frontier1094-verify'


def quiet_main(argv):
    with redirect_stdout(io.StringIO()):
        return guard.main(argv)


class CurrentTree(unittest.TestCase):
    def test_hard_checks_pass(self):
        result = guard.check(ROOT)
        self.assertEqual(result['pin_drift'], [])
        self.assertEqual(result['record_failures'], {})
        self.assertEqual(quiet_main(['--root', str(ROOT)]), 0)

    def test_live_pins_are_outside_the_fast_inventory(self):
        record, manifest, pins = guard.live_pins(ROOT)
        for rel in pins:
            self.assertNotIn(rel, manifest['files'])
            self.assertNotIn(rel, record['proof_supplements'])

    @unittest.skipUnless(SELECTED_1094, 'expectations below describe the #1094 selection')
    def test_frontier1094_shape(self):
        _, _, pins = guard.live_pins(ROOT)
        self.assertEqual(len(pins), 35)
        # One pin each that only INPUTS.json main or only UPSTREAM-PINS.json supplies.
        self.assertIn('research/complex-k492-owner-repair/vendor/joint_prefix/code/build_joint_prefix.py', pins)
        self.assertIn('research/community-k492-audit/pr622/replay/baseline558/complex-global/base/'
                      'split-centres/CLIFFORD-RECIPES.json', pins)
        result = guard.check(ROOT)
        self.assertEqual(result['driver_closure'], [
            'scripts/historical-ci-inputs/verify_hpe_lean_binding.py',
            'scripts/verify_frontier1042.py', 'scripts/verify_frontier1094.py', 'scripts/verify_frontier741.py',
            'scripts/verify_frontier741_bindings.py', 'scripts/verify_frontier741_bridge_coverage.py',
            'scripts/verify_frontier799.py', 'scripts/verify_frontier799_bindings.py',
            'scripts/verify_hpe_lean_binding.py',
            'scripts/verify_replay_coverage.py', 'scripts/verify_selected_result.py'])
        self.assertIn('certificates/checkpoints/frontier1042.json', result['named_records'])
        self.assertEqual(result['workflow'], '.github/workflows/frontier1094.yml')

    @unittest.skipUnless(SELECTED_1094, 'expectations below describe the #1094 selection')
    def test_frontier1094_required_paths(self):
        record, manifest, pins = guard.live_pins(ROOT)
        target, script = guard.driver(record, ROOT)
        scripts, named = guard.closure(script, ROOT)
        records = guard.named_records(named, ROOT)
        _, record_files = guard.check_records(records, ROOT)
        required = set(guard.required_paths(record, manifest, pins, scripts, named, record_files,
                                            '.github/workflows/frontier1094.yml'))
        for path in ('research/complex-t16-rare-pattern-exchanges/README.md',  # #1094-only root inventory
                     'certificates/checkpoints/frontier1042.json',           # named by the driver closure
                     'research/community-frontier1042-audit/ASSEMBLY.json',  # checkpoint certificate
                     'research/community-frontier1042-audit/SELECTED-SOURCE.json',
                     'scripts/verify_replay_coverage.py', *pins):
            self.assertIn(path, required)

    @unittest.skipUnless(SELECTED_1094, 'trigger coverage is enforced for the #1094 workflow only')
    def test_frontier1094_workflow_triggers_complete(self):
        result = guard.check(ROOT)
        self.assertIsNone(result['coverage_error'])
        self.assertEqual(result['uncovered'], dict(push=[], pull_request=[]))
        self.assertEqual(quiet_main(['--root', str(ROOT), '--require-triggers']), 0)


class ExitCodes(unittest.TestCase):
    def outcome(self, argv=(), **changes):
        result = dict(pin_drift=[], record_failures={}, coverage_error=None,
                      uncovered=dict(push=[], pull_request=[]))
        result.update(changes)
        with mock.patch.object(guard, 'check', return_value=result):
            return quiet_main(['--root', str(ROOT), *argv])

    def test_hard_failures(self):
        self.assertEqual(self.outcome(), 0)
        self.assertEqual(self.outcome(pin_drift=['x']), 1)
        self.assertEqual(self.outcome(record_failures={'r': 'changed'}), 1)

    def test_triggers_are_advisory_unless_required(self):
        gaps = dict(uncovered=dict(push=[], pull_request=['x']))
        self.assertEqual(self.outcome(**gaps), 0)
        self.assertEqual(self.outcome(['--require-triggers'], **gaps), 1)
        error = dict(coverage_error='Unsupported', uncovered=None)
        self.assertEqual(self.outcome(**error), 0)
        self.assertEqual(self.outcome(['--require-triggers'], **error), 1)


class Skeleton(unittest.TestCase):
    """A minimal copy holding the files the pin and trigger checks read, derived from the record."""

    @classmethod
    def setUpClass(cls):
        record, manifest, pins = guard.live_pins(ROOT)
        if not pins:
            raise unittest.SkipTest('the selected record has no live-checkout pins')
        target, script = guard.driver(record, ROOT)
        scripts, named = guard.closure(script, ROOT)
        cls.workflow = guard.replay_workflow(target, script, ROOT).relative_to(ROOT).as_posix()
        cls.manifest_path = record['source_manifest']
        cls.target, cls.script = target, script
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        names = {'certificates/selected-result.json', cls.manifest_path, 'Makefile', cls.workflow,
                 *pins, *scripts, *named}
        names |= {r + '/' + n for r in manifest['package_roots'] for n in guard.PIN_FILES
                  if (ROOT / r / n).is_file()}
        for name in names:
            target_path = cls.root / name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target_path)
        cls.pins = sorted(pins)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def edit(self, name, change):
        path = self.root / name
        original = path.read_bytes()
        path.write_bytes(change(original))
        self.addCleanup(path.write_bytes, original)

    def uncovered_pins(self):
        text = (self.root / self.workflow).read_text()
        return {event: [p for p in self.pins if not guard.triggers(guard.event_paths(text, event), p)]
                for event in guard.EVENTS}

    def append_to_pull_request_paths(self, line):
        def change(b):
            lines = b.decode().split('\n')
            head = next(i for i, x in enumerate(lines) if x.strip() == 'pull_request:')
            items = [i for i in range(head + 1, len(lines)) if lines[i].lstrip().startswith('- ')]
            last = max(i for i in items if all(lines[j].strip() == '' or lines[j].lstrip().startswith(('- ', '#'))
                                               or guard.key(lines[j]) == 'paths' for j in range(head + 1, i)))
            prefix = lines[last][:guard.indent(lines[last])]
            return '\n'.join(lines[:last + 1] + [prefix + line] + lines[last + 1:]).encode()
        self.edit(self.workflow, change)

    def test_skeleton_matches_repository(self):
        self.assertEqual(guard.live_pins(self.root)[2], guard.live_pins(ROOT)[2])
        if SELECTED_1094:
            self.assertEqual(self.uncovered_pins(), dict(push=[], pull_request=[]))

    def test_every_single_byte_pin_change_is_rejected(self):
        _, _, pins = guard.live_pins(self.root)
        for rel in self.pins:
            with self.subTest(pin=rel):
                path = self.root / rel
                original = path.read_bytes()
                path.write_bytes(original + b'\n')
                try:
                    self.assertEqual(guard.drift(pins, self.root), [rel])
                finally:
                    path.write_bytes(original)
        self.assertEqual(guard.drift(pins, self.root), [])

    def test_missing_pinned_file_is_rejected(self):
        rel = self.pins[0]
        path = self.root / rel
        original = path.read_bytes()
        path.unlink()
        self.addCleanup(path.write_bytes, original)
        self.assertEqual(guard.drift(guard.live_pins(self.root)[2], self.root), [rel])

    @unittest.skipUnless(SELECTED_1094, 'baseline coverage holds for the #1094 workflow')
    def test_later_negated_pull_request_pattern_is_reported(self):
        rel = self.pins[0]
        self.append_to_pull_request_paths("- '!" + rel + "'")
        self.assertEqual(self.uncovered_pins(), dict(push=[], pull_request=[rel]))

    def test_unsupported_trigger_filters_fail_closed(self):
        for extra in ("paths-ignore:\n      - 'research/**'", 'types: [closed]',
                      "branches: [release]", "tags:\n      - 'v*'"):
            with self.subTest(extra=extra):
                original = (self.root / self.workflow).read_text()
                text = original.replace('  pull_request:\n', '  pull_request:\n    ' + extra + '\n', 1)
                self.assertNotEqual(text, original)
                with self.assertRaises(ValueError):
                    guard.event_paths(text, 'pull_request')

    def test_quoted_and_branch_filtered_keys_are_read(self):
        text = (self.root / self.workflow).read_text()
        quoted = text.replace('  pull_request:\n    paths:\n', "  pull_request:\n    'paths':\n", 1)
        self.assertNotEqual(quoted, text)
        self.assertEqual(guard.event_paths(quoted, 'pull_request'), guard.event_paths(text, 'pull_request'))
        self.assertEqual(guard.event_paths(text, 'push'), guard.event_paths(text, 'pull_request'))

    def test_conflicting_live_pins_are_rejected(self):
        rel = self.pins[0]
        manifest = guard.read(self.root / self.manifest_path)
        roots = [r for r in manifest['package_roots'] if (self.root / r / 'data/UPSTREAM-PINS.json').is_file()
                 and rel in guard.read(self.root / r / 'data/UPSTREAM-PINS.json')]
        if len(roots) < 2:
            self.skipTest('no live pin shared by two roots')
        def conflict(b):
            value = json.loads(b)
            value[rel] = '0' * 64
            return json.dumps(value).encode()
        self.edit(roots[-1] + '/data/UPSTREAM-PINS.json', conflict)
        with self.assertRaisesRegex(ValueError, 'Conflicting live pins'):
            guard.live_pins(self.root)

    def test_pin_paths_must_stay_in_the_repository(self):
        manifest = guard.read(self.root / self.manifest_path)
        owner = next(r for r in manifest['package_roots'] if (self.root / r / 'data/UPSTREAM-PINS.json').is_file())
        for bad in ('../outside.json', '/etc/hosts', 'research/./x.json'):
            with self.subTest(path=bad):
                def escape(b, bad=bad):
                    value = json.loads(b)
                    value[bad] = '2' * 64
                    return json.dumps(value).encode()
                path = self.root / owner / 'data/UPSTREAM-PINS.json'
                original = path.read_bytes()
                path.write_bytes(escape(original))
                try:
                    with self.assertRaisesRegex(ValueError, 'Invalid repository path'):
                        guard.live_pins(self.root)
                finally:
                    path.write_bytes(original)

    def test_inside_root_pin_must_match_inventory(self):
        manifest = guard.read(self.root / self.manifest_path)
        owner = next(r for r in manifest['package_roots'] if (self.root / r / 'data/UPSTREAM-PINS.json').is_file())
        member = next(f for f in manifest['files'] if f.startswith(owner + '/'))
        def wrong(b):
            value = json.loads(b)
            value[member] = '1' * 64
            return json.dumps(value).encode()
        self.edit(owner + '/data/UPSTREAM-PINS.json', wrong)
        with self.assertRaisesRegex(ValueError, 'selected source inventory'):
            guard.live_pins(self.root)

    def test_replay_workflow_detection(self):
        other = self.root / '.github/workflows/other.yml'
        self.addCleanup(lambda: other.unlink() if other.exists() else None)
        other.write_text('# mentions ' + self.script + ' and make ' + self.target + '\nname: other\n'
                         'on:\n  push:\njobs:\n  j:\n    steps:\n      - name: run ' + self.script + '\n'
                         '        run: echo unrelated\n')
        self.assertEqual(guard.replay_workflow(self.target, self.script, self.root).name, Path(self.workflow).name)
        for command in ('      - run: python -B ' + self.script + ' --work x\n',
                        '      - run: |\n          make ' + self.target + '\n'):
            with self.subTest(command=command):
                other.write_text('name: other\non:\n  push:\njobs:\n  j:\n    steps:\n' + command)
                with self.assertRaisesRegex(ValueError, 'Expected one workflow'):
                    guard.replay_workflow(self.target, self.script, self.root)


class Records(unittest.TestCase):
    def test_changed_checkpoint_certificate_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'scripts').mkdir()
            shutil.copyfile(ROOT / 'scripts/verify_selected_result.py', root / 'scripts/verify_selected_result.py')
            package = root / 'supplier'
            package.mkdir()
            (package / 'proof.md').write_text('frozen proof\n')
            digest = sha256((package / 'proof.md').read_bytes()).hexdigest()
            cert = root / 'certificate.json'
            cert.write_text('{"kappa":"1/1000"}')
            (root / 'manifest.json').write_text(json.dumps({'format': 'repository-packages-sha256-v1',
                                                            'package_roots': ['supplier'],
                                                            'files': {'supplier/proof.md': digest}}))
            record = dict(kappa='1/1000', decimal='0.001', certificate='certificate.json',
                          certificate_sha256=sha256(cert.read_bytes()).hexdigest(),
                          source_manifest='manifest.json', proof='supplier/proof.md',
                          review='supplier/proof.md', validation='certificate.json',
                          proof_supplements={'supplier/proof.md': digest})
            (root / 'certificates').mkdir()
            (root / 'certificates/checkpoint.json').write_text(json.dumps(record))
            self.assertEqual(guard.named_records(['certificates/checkpoint.json'], root), ['certificates/checkpoint.json'])
            failures, files = guard.check_records(['certificates/checkpoint.json'], root)
            self.assertEqual(failures, {})
            self.assertEqual(files, {'certificate.json', 'manifest.json', 'supplier/proof.md'})
            cert.write_text('{"kappa":"1/1000"} ')
            failures, _ = guard.check_records(['certificates/checkpoint.json'], root)
            self.assertIn('certificates/checkpoint.json', failures)


class Globs(unittest.TestCase):
    def test_branch_exclusions_apply_in_order(self):
        cases = [
            (['main', '!main'], False),
            (['main', '!m*'], False),
            (['main', '!**'], False),
            (['main', '!m*', 'main'], True),
            (['main', '!release/**'], True),
            (['release', 'main'], True),
            (['m*'], False),
            ([], False),
        ]
        for event in guard.EVENTS:
            for patterns, included in cases:
                for block in (False, True):
                    branches = ('\n' + ''.join('      - ' + json.dumps(p) + '\n' for p in patterns)
                                if block and patterns else ' ' + json.dumps(patterns) + '\n')
                    text = 'on:\n  ' + event + ':\n    branches:' + branches + '    paths: ["research/**"]\n'
                    with self.subTest(event=event, patterns=patterns, block=block):
                        if included:
                            self.assertEqual(guard.event_paths(text, event), ['research/**'])
                        else:
                            with self.assertRaisesRegex(ValueError, 'branch filter excludes main'):
                                guard.event_paths(text, event)

    def test_unsupported_branch_globs_fail_closed(self):
        for event in guard.EVENTS:
            for pattern in ('!m?in', '!m[ab]in', 'release/+'):
                text = ('on:\n  ' + event + ':\n    branches: ' + json.dumps(['main', pattern]) + '\n')
                with self.subTest(event=event, pattern=pattern), self.assertRaisesRegex(ValueError, 'Unsupported glob syntax'):
                    guard.event_paths(text, event)

    def test_github_path_filter_semantics(self):
        cases = [
            (['research/a/**'], 'research/a/b/c.json', True),
            (['research/a/*'], 'research/a/b/c.json', False),
            (['research/**/c.json'], 'research/c.json', True),
            (['research/**'], 'scripts/x.py', False),
            (['research/**', '!research/a/**'], 'research/a/x', False),
            (['!research/a/**', 'research/**'], 'research/a/x', True),
            ([], 'anything', True),
            (None, 'anything', False),
        ]
        for patterns, name, expected in cases:
            with self.subTest(patterns=patterns, name=name):
                self.assertEqual(guard.triggers(patterns, name), expected)

    def test_unsupported_syntax_fails_closed(self):
        for pattern in ('research/[ab]/**', 'scripts/verify_?.py', 'research/CORE-23+.json', 'a/{b,c}'):
            with self.subTest(pattern=pattern), self.assertRaises(ValueError):
                guard.triggers([pattern], 'research/a/x')
        with self.assertRaises(ValueError):
            guard.event_paths("on: [push]\n", 'push')

    def test_event_reader(self):
        text = ("name: x\non:\n  workflow_dispatch:\n  push:\n    branches: [main]\n    paths:\n"
                "      - 'a/**'\n      # note\n      - \"b.py\"\n  pull_request:\njobs:\n  j:\n")
        self.assertEqual(guard.event_paths(text, 'push'), ['a/**', 'b.py'])
        self.assertEqual(guard.event_paths(text, 'pull_request'), [])
        self.assertIsNone(guard.event_paths(text, 'schedule'))


class BranchFilterCLI(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = root = Path(temporary.name)
        (root / 'scripts').mkdir()
        shutil.copyfile(ROOT / 'scripts/verify_selected_result.py', root / 'scripts/verify_selected_result.py')
        # Naming the record in the driver makes the real CLI authenticate its
        # certificate, inventory and proof as well as calculating trigger coverage.
        (root / 'scripts/replay.py').write_text("record = 'certificates/selected-result.json'\n", encoding='utf-8')
        (root / 'Makefile').write_text('replay-verify:\n\tpython scripts/replay.py\n', encoding='utf-8')
        (root / 'supplier').mkdir()
        proof = b'frozen proof\n'
        (root / 'supplier/proof.md').write_bytes(proof)
        certificate = b'{"kappa":"1/1000"}'
        (root / 'certificate.json').write_bytes(certificate)
        manifest = {'format': 'repository-packages-sha256-v1', 'package_roots': ['supplier'],
                    'files': {'supplier/proof.md': sha256(proof).hexdigest()}}
        (root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        (root / 'certificates').mkdir()
        record = {'source_manifest': 'manifest.json', 'certificate': 'certificate.json',
                  'reproduce': 'make replay-verify', 'kappa': '1/1000', 'decimal': '0.001',
                  'certificate_sha256': sha256(certificate).hexdigest(), 'proof': 'supplier/proof.md',
                  'proof_supplements': manifest['files'], 'review': 'supplier/proof.md', 'validation': 'certificate.json'}
        (root / 'certificates/selected-result.json').write_text(json.dumps(record), encoding='utf-8')
        (root / '.github/workflows').mkdir(parents=True)

    def test_excluded_main_fails_only_when_triggers_are_required(self):
        # Execute the real CLI on a complete small fixture, without mocks.
        workflow = self.root / '.github/workflows/replay.yml'
        command = [sys.executable, '-B', str(ROOT / 'scripts/check_selected_ci_inputs.py'), '--root', str(self.root)]
        for event in guard.EVENTS:
            for patterns, code in ((['main', '!m*'], 1), (['main', '!m*', 'main'], 0)):
                text = 'on:\n'
                for kind in guard.EVENTS:
                    text += '  ' + kind + ':\n'
                    if kind == event:
                        text += '    branches: ' + json.dumps(patterns) + '\n'
                text += 'jobs:\n  replay:\n    steps:\n      - run: python scripts/replay.py\n'
                workflow.write_text(text, encoding='utf-8')
                for required in (False, True):
                    with self.subTest(event=event, patterns=patterns, required=required):
                        result = subprocess.run(command + (['--require-triggers'] if required else []),
                                                check=False, capture_output=True, text=True, timeout=30)
                        self.assertEqual(result.returncode, code if required else 0, result.stdout + result.stderr)
                        marker = 'FAIL_SELECTED_CI_INPUTS' if required and code else 'PASS_SELECTED_CI_INPUTS'
                        self.assertEqual(result.stdout.splitlines()[-1], marker)
                        if code:
                            self.assertIn(event + ' branch filter excludes main', result.stdout)
                        else:
                            self.assertNotIn('ADVISORY:', result.stdout)


if __name__ == '__main__':
    unittest.main()
