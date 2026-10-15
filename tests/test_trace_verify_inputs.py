"""Recorded verification inputs must be parsed, classified and covered correctly."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('trace_verify_inputs', ROOT / 'scripts/trace_verify_inputs.py')
tracer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracer)

LOG = '''100 execve("/usr/bin/sh", ["sh", "-c", "make verify-x"], 0x1 /* 3 vars */) = 0
100 openat(AT_FDCWD</repo>, "Makefile", O_RDONLY|O_CLOEXEC) = 3</repo/Makefile>
100 openat(AT_FDCWD</repo>, ".", O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 4</repo>
100 vfork( <unfinished ...>
101 execve("/usr/bin/python3", ["python3", "scripts/x.py"], 0x2 /* 3 vars */) = 0
101 newfstatat(AT_FDCWD</repo>, "scripts/x.py", {st_mode=S_IFREG|0644, st_size=10, ...}, 0) = 0
100 <... vfork resumed>) = 101
101 chdir("certificates") = 0
101 openat(AT_FDCWD</repo/certificates>, "alpha.json", O_RDONLY|O_CLOEXEC) = 3</repo/certificates/alpha.json>
101 openat(AT_FDCWD</repo/certificates>, "../notes", O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 5</repo/notes>
101 openat(5</repo/notes>, "deep.tex", O_RDONLY|O_CLOEXEC) = 6</repo/notes/deep.tex>
101 newfstatat(AT_FDCWD</repo/certificates>, "missing.json", 0x7ffd, 0) = -1 ENOENT (No such file or directory)
101 openat(AT_FDCWD</repo/certificates>, "/repo/build/out.json", O_WRONLY|O_CREAT|O_TRUNC|O_CLOEXEC, 0666) = 7</repo/build/out.json>
101 openat(AT_FDCWD</repo/certificates>, "/usr/lib/python3/json/__init__.py", O_RDONLY|O_CLOEXEC) = 8</usr/lib/python3/json/__init__.py>
101 readlink("/repo/scripts/x.py", 0x7ffd, 4096) = -1 EINVAL (Invalid argument)
101 <... openat resumed>) = 9
101 exit_group(0) = ?
100 +++ exited with 0 +++
'''


class Parsing(unittest.TestCase):
    def test_paths_resolve_against_each_process_cwd(self):
        seen = {(p, k) for p, k, _ in tracer.parse_strace(LOG, '/repo')}
        self.assertIn(('/repo/Makefile', 'file'), seen)
        self.assertIn(('/repo', 'dir'), seen)
        self.assertIn(('/repo/scripts/x.py', 'file'), seen)
        self.assertIn(('/repo/certificates/alpha.json', 'file'), seen)   # after chdir in the child
        self.assertIn(('/repo/notes', 'dir', ), seen)
        self.assertIn(('/repo/notes/deep.tex', 'file'), seen)           # relative to an open directory fd
        self.assertIn(('/repo/certificates/missing.json', 'file'), seen)
        self.assertIn(('/repo/build/out.json', 'file'), seen)
        self.assertIn(('/usr/lib/python3/json/__init__.py', 'file'), seen)
        self.assertNotIn(('/repo/certificates/scripts/x.py', 'file'), seen)
        self.assertIn(('/repo/scripts/x.py', 'file'), seen)  # readlink operand

    def test_child_inherits_cwd_before_parent_resume_line(self):
        log = ('1 chdir("sub") = 0\n1 vfork( <unfinished ...>\n2 openat(AT_FDCWD</r/sub>, "f", O_RDONLY) = 3\n'
               '1 <... vfork resumed>) = 2\n')
        self.assertIn(('/r/sub/f', 'file'), {(p, k) for p, k, _ in tracer.parse_strace(log, '/r')})


class Classification(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@x', GIT_COMMITTER_NAME='t',
                   GIT_COMMITTER_EMAIL='t@x', GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
        git = lambda *a: subprocess.run(['git', *a], cwd=self.root, env=env, check=True, stdout=subprocess.PIPE)
        git('init', '-q')
        (self.root / 'certificates').mkdir()
        (self.root / 'certificates/alpha.json').write_text('{}')
        (self.root / 'Makefile').write_text('all:\n')
        (self.root / '.gitignore').write_text('build/\n__pycache__/\n')
        git('add', '.'); git('commit', '-qm', 'base')
        (self.root / 'build').mkdir(); (self.root / 'build/out.json').write_text('x')
        (self.root / 'certificates/untracked.json').write_text('{}')
        (self.root / 'certificates/__pycache__').mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_tracked_files_listed_dirs_and_probes(self):
        r = str(self.root)
        paths = [(r + '/Makefile', 'file'), (r + '/certificates/alpha.json', 'file'), (r, 'dir'),
                 (r + '/certificates', 'dir'), (r + '/certificates/missing.json', 'file'),
                 (r + '/build/out.json', 'file'), (r + '/certificates/untracked.json', 'file'),
                 (r + '/certificates/__pycache__/x.pyc', 'file'), (r + '/.git/index', 'file'),
                 ('/usr/lib/python3/json.py', 'file'), (r + '/RCS', 'dir'), (r + '/SCCS', 'file'),
                 (r + '/-lc', 'file'), (r + '/algorithm', 'file'), (r + '/certificates', 'file')]
        files, dirs, probes, tree, exists, subtrees = tracer.classify(paths, self.root)
        self.assertEqual(files, ['Makefile', 'certificates/alpha.json'])
        self.assertEqual(dirs, ['', 'certificates'])
        self.assertEqual(exists, [])
        # ignored outputs, caches, .git, system files, make's VCS probes and root-level probes are dropped;
        # an untracked but unignored file and a missing path inside the repo are kept.
        self.assertEqual(probes, ['certificates/missing.json', 'certificates/untracked.json'])
        self.assertFalse(tree)
        files, dirs, probes, tree, exists, subtrees = tracer.classify([(r + '/build', 'dir'), (r + '/build/out.json', 'file')], self.root)
        self.assertEqual((files, dirs, probes, exists), ([], [], [], []))  # ignored directories are not listings

    def test_existence_checks_are_not_listings(self):
        r = str(self.root)
        files, dirs, probes, tree, exists, subtrees = tracer.classify(
            [(r + '/certificates', 'file'), (r, 'file'), (r + '/certificates', 'dir')], self.root)
        self.assertEqual((dirs, exists), (['certificates'], ['']))  # listed wins over a bare stat; root stat is existence
        files, dirs, probes, tree, exists, subtrees = tracer.classify([(r + '/certificates', 'file')], self.root)
        self.assertEqual((dirs, exists), ([], ['certificates']))

    def test_runtime_directories_are_declared_at_their_tracked_ancestor(self):
        r = str(self.root)
        (self.root / 'certificates/scratch').mkdir()
        files, dirs, probes, tree, exists, subtrees = tracer.classify(
            [(r + '/certificates/scratch', 'dir'), (r + '/certificates/scratch/input.json', 'file')], self.root)
        self.assertEqual(dirs, ['certificates'])  # git does not know scratch; additions below it change certificates
        self.assertEqual(probes, ['certificates/scratch/input.json'])
        self.assertEqual(tracer.anchor('certificates/scratch/input.json', self.root), 'certificates')
        self.assertEqual(tracer.anchor('nowhere/deep/x', self.root), '')

    def test_git_tree_objects_are_subtrees(self):
        r = str(self.root)
        files, dirs, probes, tree, exists, subtrees = tracer.classify(
            [(r + '\0certificates', 'gitpath'), (r + '\0certificates/alpha.json', 'gitpath')], self.root)
        self.assertEqual((files, subtrees), (['certificates/alpha.json'], ['certificates']))
        rec = {'group': 'g', 'commands': [], 'files': [], 'dirs': [], 'probes': [], 'subtrees': ['certificates']}
        self.assertEqual(tracer.uncovered(rec, ['certificates/*'], self.root), ['certificates/**'])
        self.assertEqual(tracer.suggest(rec, root=self.root), ['certificates/**'])

    def test_escaped_utf8_and_dash_names_survive(self):
        r = str(self.root)
        (self.root / 'certificates/caf\u00e9.json').write_text('{}')
        subprocess.run(['git', 'add', 'certificates/caf\u00e9.json'], cwd=self.root, check=True)
        self.assertEqual(tracer._unescape('caf\\303\\251.json'), 'caf\u00e9.json')
        self.assertEqual(tracer._unescape('a\\nb\\x41\\"'), 'a\nbA"')
        files, dirs, probes, tree, exists, subtrees = tracer.classify(
            [(r + '/certificates/caf\u00e9.json', 'file'), (r + '/certificates/-dashed.json', 'file')], self.root)
        self.assertEqual(files, ['certificates/caf\u00e9.json'])
        self.assertEqual(probes, ['certificates/-dashed.json'])

    def test_tracked_cache_files_and_tree_queries_are_kept(self):
        r = str(self.root)
        (self.root / 'certificates/__pycache__/keep.pyc').write_text('x')
        subprocess.run(['git', 'add', '-f', 'certificates/__pycache__/keep.pyc'], cwd=self.root, check=True,
                       stdout=subprocess.PIPE)
        files, dirs, probes, tree, exists, subtrees = tracer.classify([(r + '/certificates/__pycache__/keep.pyc', 'file'), (r, 'tree')], self.root)
        self.assertEqual(files, ['certificates/__pycache__/keep.pyc'])
        self.assertTrue(tree)

    def test_git_in_a_nested_checkout_or_outside_is_not_this_tree(self):
        r = str(self.root)
        nested = self.root / 'build/upstream'
        nested.mkdir(parents=True)
        subprocess.run(['git', 'init', '-q'], cwd=nested, check=True)
        files, dirs, probes, tree, exists, subtrees = tracer.classify(
            [(r + '/build/upstream', 'tree'), ('/elsewhere', 'tree'), (r + '/build/upstream\0certificates/alpha.json', 'gitpath'),
             (r + '/certificates\0Makefile', 'gitpath'), (r + '/certificates\0./alpha.json', 'gitpath')], self.root)
        self.assertFalse(tree)
        self.assertEqual(files, ['Makefile', 'certificates/alpha.json'])
        files, dirs, probes, tree, exists, subtrees = tracer.classify([(r + '/certificates', 'tree')], self.root)
        self.assertTrue(tree)

    def test_symlink_records_link_and_target(self):
        r = str(self.root)
        os.symlink('alpha.json', self.root / 'certificates/link.json')
        os.symlink('certificates', self.root / 'linkdir')
        subprocess.run(['git', 'add', 'certificates/link.json', 'linkdir'], cwd=self.root, check=True)
        files, dirs, probes, tree, exists, subtrees = tracer.classify([(r + '/certificates/link.json', 'file')], self.root)
        self.assertEqual(files, ['certificates/alpha.json', 'certificates/link.json'])
        files, dirs, probes, tree, exists, subtrees = tracer.classify([(r + '/linkdir/alpha.json', 'file')], self.root)
        self.assertEqual(files, ['certificates/alpha.json', 'linkdir'])  # the directory link and the real input


class GitSemantics(unittest.TestCase):
    def test_show_of_a_tree_path_is_that_path(self):
        self.assertEqual(tracer.git_semantics(['git', 'show', 'HEAD:certificates/x.json']),
                         ([('certificates/x.json', 'git')], False, None))
        self.assertEqual(tracer.git_semantics(['git', '-c', 'core.quotepath=off', 'show', 'HEAD:a/b']),
                         ([('a/b', 'git')], False, None))
        self.assertEqual(tracer.git_semantics(['git', 'cat-file', '-p', 'HEAD:a/b']), ([('a/b', 'git')], False, None))
        self.assertEqual(tracer.git_semantics(['git', '-C', 'up', 'ls-tree', '-r', 'HEAD']), ([], True, 'up'))
        self.assertEqual(tracer.git_semantics(['git', 'rev-parse', 'HEAD:certificates/x.json']),
                         ([('certificates/x.json', 'git')], False, None))
        self.assertEqual(tracer.git_semantics(['git', 'rev-parse', 'HEAD:']), ([], True, None))
        self.assertEqual(tracer.git_semantics(['git', '--git-dir=/x/.git', 'show', 'HEAD'])[1:], (True, tracer.THIS_CHECKOUT))

    def test_object_paths_carry_the_git_directory(self):
        log = ('7 chdir("sub") = 0\n'
               '7 execve("/usr/bin/git", ["git", "show", "HEAD:certificates/x.json"], 0x1 /* 3 vars */) = 0\n'
               '7 execve("/usr/bin/git", ["git", "-C", "../up", "ls-files"], 0x1 /* 3 vars */) = 0\n')
        seen = {(p, k) for p, k, _ in tracer.parse_strace(log, '/r')}
        self.assertIn(('/r/sub\0certificates/x.json', 'gitpath'), seen)
        self.assertIn(('/r/up', 'tree'), seen)

    def test_immutable_objects_and_inert_commands(self):
        sha = '0123456789abcdef0123456789abcdef01234567'
        self.assertEqual(tracer.git_semantics(['git', 'show', sha + ':certificates/x.json'])[:2], ([], False))
        for argv in (['git', 'rev-parse', 'HEAD'], ['git', 'cat-file', '-e', sha], ['git', 'hash-object', 'f'],
                     ['git', 'apply', '--check', '--directory=upstream', 'patches/x.patch'], ['git', 'fetch', 'x'],
                     ['git', 'cat-file', '-p', sha + ':certificates/x.json'], ['git', '-C', 'up', 'rev-parse', 'HEAD']):
            self.assertEqual(tracer.git_semantics(argv)[:2], ([], False), argv)

    def test_whole_tree_commands(self):
        for argv in (['git', 'ls-files', '-z'], ['git', 'status', '--porcelain'], ['git', 'diff', '--exit-code'],
                     ['git', 'show', 'HEAD'], ['git', 'show'], ['git', 'ls-tree', 'HEAD'], ['git', '--git-dir=x', 'log'],
                     ['git', 'rev-list', 'HEAD'],
                     ['git', 'clone', '.', '/tmp/x'], ['git', 'frobnicate'], ['git', 'cat-file', '--batch'],
                     ['git', 'cat-file', '--batch-check'], ['git', 'cat-file', '-p', 'HEAD'],
                     ['git', 'apply', '--cached', 'p.patch'], ['git', 'apply', '--index', 'p.patch']):
            self.assertEqual(tracer.git_semantics(argv)[:2], ([], True), argv)
        self.assertEqual(tracer.git_semantics(['git', 'restore', 'certificates/x.json']),
                         ([('certificates/x.json', 'file')], False, None))


class Tokens(unittest.TestCase):
    def test_tokens_respect_quotes_and_nesting(self):
        self.assertEqual(tracer.tokens('AT_FDCWD</r>, "a, b", O_RDONLY|O_CLOEXEC) = 3'),
                         ['AT_FDCWD</r>', '"a, b"', 'O_RDONLY|O_CLOEXEC'])
        self.assertEqual(tracer.tokens('"/usr/bin/git", ["git", "show", "HEAD:x,y"], 0x1 /* 3 vars */) = 0'),
                         ['"/usr/bin/git"', '["git", "show", "HEAD:x,y"]', '0x1 /* 3 vars */'])
        self.assertEqual(tracer.argv_strings('["git", "show", "HEAD:x,y"]'), ['git', 'show', 'HEAD:x,y'])
        self.assertEqual(tracer.tokens('"x" <unfinished ...>'), ['"x"'])

    def test_two_path_calls_record_destinations(self):
        log = ('7 rename("build/tmp.json", "certificates/out.json") = 0\n'
               '7 renameat2(AT_FDCWD</r>, "a", AT_FDCWD</r>, "b", RENAME_NOREPLACE) = 0\n'
               '7 symlinkat("target", AT_FDCWD</r>, "linkname") = 0\n')
        seen = {(p, k) for p, k, _ in tracer.parse_strace(log, '/r')}
        self.assertEqual(seen, {('/r/build/tmp.json', 'file'), ('/r/certificates/out.json', 'file'),
                                ('/r/a', 'file'), ('/r/b', 'file'), ('/r/linkname', 'file')})

    def test_git_execve_and_fchdir(self):
        log = ('7 execve("/usr/bin/git", ["git", "ls-files", "-z"], 0x1 /* 3 vars */) = 0\n'
               '8 fchdir(5</r/sub>) = 0\n8 openat(AT_FDCWD</r/sub>, "f", O_RDONLY) = 3\n'
               '9 chdir("deep" <unfinished ...>\n9 <... chdir resumed>) = 0\n9 stat("g", 0x1) = 0\n')
        seen = {(p, k) for p, k, _ in tracer.parse_strace(log, '/r')}
        self.assertIn(('/r', 'tree'), seen)
        self.assertIn(('/usr/bin/git', 'file'), seen)
        self.assertIn(('/r/sub/f', 'file'), seen)
        self.assertIn(('/r/deep/g', 'file'), seen)
        log2 = '9 chdir("sub") = 0\n9 execve("/usr/bin/git", ["git", "--git-dir=/elsewhere/.git", "show", "HEAD"], 0x1 /* 3 vars */) = 0\n'
        self.assertIn(('/r', 'tree'), {(p, k) for p, k, _ in tracer.parse_strace(log2, '/r')})
        # the parser also accepts a callable producing lines, as record() streams the log
        self.assertIn(('/r', 'tree'), {(p, k) for p, k, _ in tracer.parse_strace(lambda: iter(log2.splitlines()), '/r')})


class Coverage(unittest.TestCase):
    RECORDING = {'group': 'g', 'commands': [], 'files': ['Makefile', 'certificates/alpha.json', 'notes/a.tex'],
                 'dirs': ['', 'certificates', 'references/pkg'], 'probes': ['references/pkg/missing.json'],
                 'tree': False}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@x', GIT_COMMITTER_NAME='t',
                   GIT_COMMITTER_EMAIL='t@x', GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
        subprocess.run(['git', 'init', '-q'], cwd=self.root, env=env, check=True)
        for d in ('certificates', 'notes', 'references/pkg', 'research/p1', 'research/p2', 'research/p3',
                  'research/p4', 'research/p5', 'research/p6', 'research/p7', 'research/p8', 'tests/sub'):
            (self.root / d).mkdir(parents=True)
            (self.root / d / 'tracked.txt').write_text('x')  # every directory is known to git
        subprocess.run(['git', 'add', '.'], cwd=self.root, env=env, check=True)
        subprocess.run(['git', 'commit', '-qm', 'base'], cwd=self.root, env=env, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_dir_coverage(self):
        self.assertTrue(tracer.dir_covered('certificates/*', 'certificates'))
        self.assertTrue(tracer.dir_covered('certificates/**', 'certificates'))
        self.assertTrue(tracer.dir_covered('references/**', 'references/pkg'))
        self.assertTrue(tracer.dir_covered('*', ''))
        self.assertTrue(tracer.dir_covered('**', 'anything'))
        self.assertFalse(tracer.dir_covered('certificates/*', 'certificates/sub'))
        self.assertFalse(tracer.dir_covered('certificates/alpha.json', 'certificates'))
        self.assertFalse(tracer.dir_covered('*', 'certificates'))

    def test_file_reads_need_exact_or_recursive_patterns(self):
        self.assertTrue(tracer.pattern_matches('notes/**', 'notes/a.tex'))
        self.assertTrue(tracer.pattern_matches('Makefile', 'Makefile'))
        self.assertFalse(tracer.pattern_matches('notes/*', 'notes/a.tex'))  # listing does not cover an edit
        self.assertFalse(tracer.pattern_matches('*', 'Makefile'))

    def test_uncovered_and_suggest(self):
        patterns = ['Makefile', 'certificates/alpha.json', 'notes/**', '*', 'certificates/*', 'references/**']
        self.assertEqual(tracer.uncovered(self.RECORDING, patterns, self.root), [])
        missing = tracer.uncovered(self.RECORDING, ['Makefile', 'notes/**', 'references/**'], self.root)
        self.assertEqual(missing, ['certificates/alpha.json', '*', 'certificates/*'])
        suggested = tracer.suggest(self.RECORDING, covered_by=['Makefile'], root=self.root)
        self.assertEqual(suggested, ['*', 'certificates/*', 'certificates/alpha.json', 'notes/a.tex',
                                     'references/pkg/*'])  # the probe is covered by its parent's listing
        self.assertEqual(tracer.uncovered(self.RECORDING, suggested + ['Makefile'], self.root), [])

    def test_suggest_coarsens_directories_whose_files_are_mostly_read(self):
        # tests/ has one tracked file in the fixture: reading five files there is "most of it"
        rec = {'group': 'g', 'commands': [], 'files': ['tests/t%d.py' % i for i in range(5)] + ['tests/sub/x.py'],
               'dirs': ['tests'], 'probes': []}
        self.assertEqual(tracer.suggest(rec, root=self.root), ['tests/**'])
        # notes/ with many tracked files: reading four of them stays exact plus the listing
        for i in range(20):
            (self.root / ('notes/n%d.tex' % i)).write_text('x')
        subprocess.run(['git', 'add', 'notes'], cwd=self.root, check=True)
        tracer._TRACKED_DIRS.clear()
        rec = {'group': 'g', 'commands': [], 'files': ['notes/n%d.tex' % i for i in range(4)], 'dirs': ['notes'], 'probes': []}
        self.assertEqual(tracer.suggest(rec, root=self.root),
                         ['notes/*', 'notes/n0.tex', 'notes/n1.tex', 'notes/n2.tex', 'notes/n3.tex'])

    def test_suggest_coarsens_walked_directories_but_not_a_few_listed_children(self):
        walked = {'group': 'g', 'commands': [], 'files': [], 'probes': [],
                  'dirs': ['research'] + ['research/p%d' % i for i in range(1, 9)]}
        self.assertEqual(tracer.suggest(walked, root=self.root), ['research/**'])
        few = {'group': 'g', 'commands': [], 'files': [], 'probes': [],
               'dirs': ['research', 'research/p1', 'research/p2', 'research/p3', 'research/p4']}
        self.assertEqual(tracer.suggest(few, root=self.root),
                         ['research/*', 'research/p1/*', 'research/p2/*', 'research/p3/*', 'research/p4/*'])

    def test_probe_is_anchored_at_its_deepest_existing_ancestor(self):
        rec = {'group': 'g', 'commands': [], 'files': [], 'dirs': ['certificates'],
               'probes': ['certificates/missing.json', 'research/x/missing.json', 'notes/deep/er/missing.h']}
        self.assertEqual(tracer.uncovered(rec, ['certificates/*'], self.root), ['research/x/missing.json', 'notes/deep/er/missing.h'])
        self.assertEqual(tracer.suggest(rec, root=self.root), ['certificates/*', 'notes/*', 'research/*'])
        self.assertEqual(tracer.uncovered(rec, ['certificates/*', 'notes/*', 'research/*'], self.root), [])

    def test_existence_coverage(self):
        rec = {'group': 'g', 'commands': [], 'files': [], 'dirs': [], 'probes': [], 'exists': ['research', 'notes']}
        self.assertEqual(tracer.uncovered(rec, ['notes/**'], self.root), ['research/'])
        self.assertEqual(tracer.uncovered(rec, ['research/', 'notes/*'], self.root), [])
        self.assertEqual(tracer.suggest(rec, root=self.root), ['notes/', 'research/'])
        self.assertFalse(tracer.pattern_matches('research/', 'research/x/y'))

    def test_whole_tree_dependency(self):
        rec = {'group': 'g', 'commands': [], 'files': ['Makefile'], 'dirs': [''], 'probes': [], 'tree': True}
        self.assertEqual(tracer.uncovered(rec, ['Makefile', '*'], self.root), ['**'])
        self.assertEqual(tracer.uncovered(rec, ['**'], self.root), [])
        self.assertEqual(tracer.suggest(rec, root=self.root), ['**'])
        self.assertEqual(tracer.suggest(rec, covered_by=['**'], root=self.root), [])


class Commands(unittest.TestCase):
    def test_group_commands_match_the_workflow(self):
        self.assertEqual(tracer.group_commands('community'), ['make verify-community'])
        self.assertEqual(tracer.group_commands('clones'),
                         ['python3 -B scripts/replay_historical_check.py skip-clones',
                          'python3 -B scripts/replay_historical_check.py split-skip'])
        self.assertEqual(tracer.group_commands('ranked-pair-finite'),
                         ['make ranked-pair-verify UPSTREAM=build/ranked-pair-upstream'])


class SavedRecordings(unittest.TestCase):
    def recording(self):
        return dict(group='clones', commands=tracer.group_commands('clones'),
                    files=[], dirs=[], exists=[], probes=[], subtrees=[], tree=False,
                    exit_code=0, recording_version=tracer.RECORDING_VERSION)

    def recheck(self, recording):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'recording.json'
            path.write_text(json.dumps(recording), encoding='utf-8')
            return subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/trace_verify_inputs.py'),
                                   '--group', 'clones', '--from-recording', str(path), '--check'],
                                  cwd=ROOT, capture_output=True, text=True)

    def test_successful_recording_can_be_rechecked(self):
        result = self.recheck(self.recording())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS_DECLARED_INPUTS_COVER_RECORDING group=clones', result.stdout)

    def test_partial_recording_keeps_verification_failure(self):
        recording = self.recording()
        recording['exit_code'] = 7
        result = self.recheck(recording)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertIn('VERIFICATION_FAILED exit=7', result.stdout)
        self.assertNotIn('PASS_DECLARED_INPUTS', result.stdout)

    def test_wrong_group_old_schema_and_incomplete_evidence_reject(self):
        mutations = [('group', 'community'), ('recording_version', tracer.RECORDING_VERSION - 1),
                     ('recording_version', True), ('exit_code', False), ('tree', 'false'),
                     ('files', 'Makefile'), ('probes', [None]), ('commands', [])]
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                recording = self.recording()
                recording[field] = value
                result = self.recheck(recording)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn('PASS_DECLARED_INPUTS', result.stdout)
        for field in ('exit_code', 'dirs', 'subtrees'):
            with self.subTest(missing=field):
                recording = self.recording()
                del recording[field]
                result = self.recheck(recording)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn('PASS_DECLARED_INPUTS', result.stdout)


if __name__ == '__main__':
    unittest.main()
