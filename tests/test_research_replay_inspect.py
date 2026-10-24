"""Real terminal controls for inherited inspection at the replay boundary."""
import importlib.util
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('inspect_replay', ROOT / 'scripts/research_package.py')
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class ReplayEnvironmentTests(unittest.TestCase):
    def test_windows_dispatch_receives_sanitized_copy_without_changing_arguments(self):
        argv = [sys.executable, '-i', '-O', '-c', 'print(1)']
        with patch.dict(os.environ, PYTHONINSPECT='1', REPLAY_SENTINEL='retained'):
            before = dict(os.environ)
            with patch.object(package.os, 'name', 'nt'), patch.object(package, 'run_windows_command', return_value=0) as launch:
                package.run_command(argv, ROOT, 3)
            actual, cwd, timeout, env = launch.call_args.args
            self.assertEqual(actual, argv)
            self.assertEqual((cwd, timeout), (ROOT, 3))
            self.assertNotIn('PYTHONINSPECT', env)
            self.assertEqual(env['REPLAY_SENTINEL'], 'retained')
            self.assertEqual(dict(os.environ), before)


@unittest.skipIf(os.name == 'nt', 'POSIX pseudo-terminal control; native Windows not covered')
class TerminalReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='replay-inspect-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = 'print("VERIFIER_ENTERED", flush=True)\nraise ValueError("REAL_VERIFIER_FAILURE")\n'
        (self.root / 'fixture.py').write_text(self.source, encoding='utf8')

    def driver(self, entry, flags=(), helper='run_python_replay'):
        return (
            'import os, sys\nfrom pathlib import Path\n'
            f'sys.path.insert(0, {str(ROOT / "scripts")!r})\n'
            'import research_package as runner\n'
            'before = dict(os.environ)\n'
            f'runner.{helper}([sys.executable, *{list(flags)!r}, *{entry!r}], Path({str(self.root)!r}), 3)\n'
            'if dict(os.environ) != before: raise ValueError("parent environment changed")\n'
            'print("RUNNER_ACCEPTED", flush=True)\n')

    def terminal(self, code, inspect='1', input_line=None):
        import pty
        master, slave = pty.openpty()
        # -I isolates only the driver. The registered child still sees the
        # ambient setting unless its real launch boundary removes it.
        argv = [sys.executable, '-I', '-B', *(['-O'] if sys.flags.optimize else []), '-c', code]
        env = dict(os.environ, PYTHONINSPECT=inspect)
        process = None
        try:
            process = subprocess.Popen(argv, cwd=self.root, env=env, stdin=slave,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = b''
            eof_sent = input_sent = False
            deadline = time.monotonic() + 8
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    self.fail('outer terminal fixture exceeded its bound')
                ready, _, _ = select.select([process.stdout], [], [], .1)
                if ready:
                    output += os.read(process.stdout.fileno(), 65536)
                if input_line is not None and b'CHILD_INPUT>' in output and not input_sent:
                    os.write(master, input_line.encode('utf8') + b'\n')
                    input_sent = True
                if b'>>> ' in output and not eof_sent:
                    # Ordinary terminal EOF, without executing any replacement
                    # success command in the interactive interpreter.
                    os.write(master, b'\x04')
                    eof_sent = True
            remainder, _ = process.communicate(timeout=2)
            return process.returncode, (output + remainder).decode('utf8', 'replace')
        finally:
            if process is not None:
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=5)
            os.close(master)
            os.close(slave)

    def test_failure_preserved_for_file_module_and_command_in_both_modes(self):
        entries = [[str(self.root / 'fixture.py')], ['-m', 'fixture'], ['-c', self.source]]
        for flags in ([], ['-O']):
            for entry in entries:
                with self.subTest(flags=flags, entry=entry[0]):
                    status, output = self.terminal(self.driver(entry, flags))
                    self.assertNotEqual(status, 0, output)
                    self.assertIn('REAL_VERIFIER_FAILURE', output)
                    self.assertIn('verification command exited 1', output)
                    self.assertNotIn('RUNNER_ACCEPTED', output)
                    self.assertNotIn('>>> ', output)

    def test_shared_run_command_preserves_failure_and_clean_control(self):
        for inspect in ('', '1'):
            with self.subTest(inspect=inspect):
                status, output = self.terminal(self.driver(['-c', self.source], helper='run_command'), inspect)
                self.assertNotEqual(status, 0, output)
                self.assertNotIn('RUNNER_ACCEPTED', output)

    def test_success_keeps_stdin_parent_and_descendant_environment(self):
        source = (
            'import os, subprocess, sys\n'
            'print("CHILD_INPUT>", flush=True)\n'
            'if input() != "payload": raise ValueError("stdin changed")\n'
            'if "PYTHONINSPECT" in os.environ: raise ValueError("ambient inspection retained")\n'
            'subprocess.run([sys.executable,"-c",'
            '"import os; assert \'PYTHONINSPECT\' not in os.environ"], check=True)\n'
            'print("CHILD_OK", flush=True)\n')
        status, output = self.terminal(self.driver(['-c', source]), input_line='payload')
        self.assertEqual(status, 0, output)
        self.assertIn('CHILD_OK', output)
        self.assertIn('RUNNER_ACCEPTED', output)
        self.assertNotIn('>>> ', output)

    def test_explicit_interactive_flag_remains_explicit(self):
        status, output = self.terminal(self.driver(['-c', 'print("EXPLICIT",flush=True)'], ['-i']), inspect='')
        self.assertEqual(status, 0, output)
        self.assertIn('>>> ', output)
        self.assertIn('RUNNER_ACCEPTED', output)

    def test_registered_package_never_prints_pass_for_failed_verifier(self):
        # Use the actual package generator and validator, not a stubbed manifest.
        sys.path.insert(0, str(ROOT / 'scripts'))
        try:
            import new_research_package as scaffold
        finally:
            sys.path.pop(0)
        package.git(self.root, 'init', '-q')
        for key, value in [('user.name', 'Fixture'), ('user.email', 'fixture@example.invalid'), ('core.autocrlf', 'false')]:
            package.git(self.root, 'config', key, value)
        (self.root / 'docs/research').mkdir(parents=True)
        (self.root / 'certificates').mkdir()
        (self.root / 'docs/research/agent-task-catalog.json').write_text(json.dumps({
            'priority_revision': 2, 'tracks': [{'tasks': [{'id': 'fixture', 'question': 'Check replay', 'acceptance_gate': 'Reject failure'}]}]}))
        (self.root / 'certificates/selected-result.json').write_text('{}')
        package.git(self.root, 'add', '.')
        package.git(self.root, '-c', 'maintenance.auto=false', 'commit', '-qm', 'fixture')
        target = scaffold.create(self.root, 'fixture', 'fixture', 'Fixture', ['fixture.py'])
        task_path = target / 'TASK.json'
        task = json.loads(task_path.read_text())
        task.update(bottleneck_link='Replay status', stop_rule='One failing fixture', outcome='partial',
                    evidence='Real terminal control', ai_assistance='Fixture',
                    open_questions=[dict(question='Native Windows?', why_it_matters='Portability',
                                         first_step='Run native control', blocked_by='Unavailable host')])
        task_path.write_text(json.dumps(task))
        manifest_path = target / 'VERIFY.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['status'] = 'ready'
        manifest['commands'][0]['checks'] = 'Failing registered fixture'
        manifest_path.write_text(json.dumps(manifest))
        (target / 'verify.py').write_text(self.source)
        code = ('import sys\nfrom pathlib import Path\n'
                f'sys.path.insert(0, {str(ROOT / "scripts")!r})\n'
                'import research_package as runner\n'
                f'runner.run_package(Path({str(self.root)!r}), "research/fixture")\n')
        status, output = self.terminal(code)
        self.assertNotEqual(status, 0, output)
        self.assertIn('CHECK Failing registered fixture', output)
        self.assertIn('REAL_VERIFIER_FAILURE', output)
        self.assertNotIn('PASS_REGISTERED_RESEARCH_PACKAGE', output)
        self.assertNotIn('>>> ', output)


if __name__ == '__main__':
    unittest.main()
