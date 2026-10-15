#!/usr/bin/env python3
"""Record which repository paths a verification group reads, and check the
declared CI input manifest against that record.

The CI planner (scripts/plan_verify_groups.py) skips a verification group on
a pull request only when none of the pull request's changed paths match the
group's declared inputs in .github/verify-groups.json. That is sound only if
the declaration is complete. This tool makes the declaration checkable:

* ``--group G`` runs the same command CI runs for group ``G`` under
  ``strace`` and records every tracked file, listed directory, existence
  probe and whole-tree Git query inside the repository. The verification
  outcome is propagated unchanged; tracing adds no claim and removes no check.
* ``--check MANIFEST`` additionally fails when a recorded input is not
  covered by the group's declared patterns (or the ``all`` patterns).
* ``--suggest`` prints a minimal pattern set covering a recording.

Pattern syntax is deliberately small (shared with scripts/plan_verify_groups.py):

* an exact repository path: any change to that file matters;
* ``dir/**`` (``**`` for the whole tree): any change at or below ``dir``;
* ``dir/*`` (``*`` for the repository root): the group listed that
  directory, so an entry added to or removed from it matters, while editing
  an existing entry does not (a read of that entry is recorded separately).

Coverage rules: a recorded file read needs an exact or ``**`` pattern; a
listed directory needs ``dir/*``, ``dir/**`` or an ancestor ``**``; an
existence check of a directory needs ``dir/``, ``dir/*``, ``dir/**`` or an
ancestor ``**``; a probe of a path that does not exist needs an exact
pattern, a ``**`` pattern or a listing pattern on its deepest existing
ancestor; a whole-tree Git query (``git ls-files``, ``git status``,
``git diff``, ...) needs ``**``.

What is deliberately not recorded, and why it is still safe:

* paths outside the repository and ``.git`` internals (``git show REV:path``
  and friends are interpreted from the git command line instead);
* untracked files that ``.gitignore`` ignores (``build/`` outputs, caches):
  a pull request that tracks such a path is an addition the planner cannot
  classify, so it verifies everything;
* probes of names directly at the repository root (GNU make's version-control
  and makefile probes, compiler search paths): an undeclared new root entry
  likewise makes the planner verify everything.

Paths are kept lexical (not symlink-resolved) so that a dependency on a
tracked symlink is recorded on the link; the link's target inside the
repository is recorded as well.

Assumption: a ``stat`` of a directory is an existence check. Directory
metadata (mtime, link count) is not a reproducible input of a fresh CI
checkout, so no verifier here may depend on it; ``git diff --exit-code``
after every group would expose a verifier that did.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / '.github/verify-groups.json'
TRACE_SYSCALLS = '%file,chdir,fchdir,%process'
MAKE_PROBES = {'RCS', 'SCCS', 'GNUmakefile', 'makefile'}

# The commands CI runs per matrix group (see .github/workflows/verify.yml).
GROUP_COMMANDS = {
    'clones': ['python3 -B scripts/replay_historical_check.py skip-clones',
               'python3 -B scripts/replay_historical_check.py split-skip'],
    'ranked-pair-finite': ['make ranked-pair-verify UPSTREAM=build/ranked-pair-upstream'],
}


def group_commands(group):
    return GROUP_COMMANDS.get(group, ['make verify-' + group])


# ---------------------------------------------------------------- strace parsing

_LINE = re.compile(r'^(?P<pid>\d+)\s+(?P<rest>.*)$')
_CALL = re.compile(r'^(?P<name>\w+)\((?P<args>.*)$')
_RESUMED = re.compile(r'^<\.\.\. (?P<name>\w+) resumed>(?P<args>.*)$')
_RESULT = re.compile(r'=\s+(?P<ret>-?\d+|\?)(?:\s|$)')
_FD = re.compile(r'^(?:AT_FDCWD|\d+)<(?P<path>[^>]*)>$')
_SHA = re.compile(r'^[0-9a-f]{40}$')
THIS_CHECKOUT = '<this checkout>'
FORK_CALLS = {'clone', 'clone3', 'fork', 'vfork'}
# Calls whose second (and third) quoted operand is also a path.
TWO_PATH = {'rename': (0, 1), 'link': (0, 1), 'symlink': (1,), 'renameat': (0, 1), 'renameat2': (0, 1),
            'linkat': (0, 1), 'symlinkat': (1,)}
SKIP_CALLS = FORK_CALLS | {'wait4', 'waitid', 'kill', 'exit', 'exit_group', 'execveat', 'getcwd',
                           'arch_prctl', 'tgkill', 'tkill', 'rt_sigreturn', 'prlimit64', 'set_tid_address'}


_ESCAPES = {'n': b'\n', 't': b'\t', 'r': b'\r', 'a': b'\a', 'b': b'\b', 'f': b'\f', 'v': b'\v',
            '\\': b'\\', '"': b'"', "'": b"'", '?': b'?'}


def _unescape(text):
    """Decode strace's C-style string escapes (\\ooo octal, \\xhh, \\n ...) into
    bytes and then with the filesystem encoding, so UTF-8 names survive."""
    out, i = bytearray(), 0
    while i < len(text):
        c = text[i]
        if c != '\\' or i + 1 >= len(text):
            out += c.encode('utf-8', 'surrogateescape'); i += 1
            continue
        n = text[i + 1]
        if n in '01234567':
            j = i + 1
            while j < len(text) and j < i + 4 and text[j] in '01234567':
                j += 1
            out.append(int(text[i + 1:j], 8) & 0xFF); i = j
        elif n == 'x':
            j = i + 2
            while j < len(text) and j < i + 4 and text[j] in '0123456789abcdefABCDEF':
                j += 1
            out.append(int(text[i + 2:j], 16) if j > i + 2 else 0); i = j
        else:
            out += _ESCAPES.get(n, n.encode('utf-8', 'surrogateescape')); i += 2
    return os.fsdecode(bytes(out))


def tokens(args):
    """Split strace argument text into top-level comma-separated tokens."""
    out, depth, cur, i, quote = [], 0, [], 0, False
    while i < len(args):
        c = args[i]
        if quote:
            cur.append(c)
            if c == '\\':
                cur.append(args[i + 1]); i += 1
            elif c == '"':
                quote = False
        elif c == '"':
            quote = True; cur.append(c)
        elif c in '([{':
            depth += 1; cur.append(c)
        elif c in ')]}':
            if depth == 0:
                break  # end of the call's argument list
            depth -= 1; cur.append(c)
        elif c == ',' and depth == 0:
            out.append(''.join(cur).strip()); cur = []
        elif c == '<' and depth == 0 and args.startswith('<unfinished', i):
            break
        else:
            cur.append(c)
        i += 1
    tail = ''.join(cur).strip()
    if tail and not tail.startswith('<unfinished'):
        out.append(tail)
    return out


def string_value(token):
    if token.startswith('"') and token.endswith('"') and len(token) >= 2:
        return _unescape(token[1:-1])
    if token.startswith('"') and token.endswith('...'):  # truncated string
        return None
    return None


def argv_strings(token):
    """Strings of an argv array token such as ``["git", "show", "HEAD:x"]``."""
    if not token.startswith('['):
        return []
    return [s for s in (string_value(t) for t in tokens(token[1:])) if s is not None]


def git_semantics(argv):
    """Inputs implied by a git command line: (paths, tree, directory) where
    paths is a list of repository-relative (path, kind), tree means the whole
    tree of the repository that ``directory`` belongs to (None: the process
    cwd), and ``directory`` is the ``-C`` operand if any."""
    args = argv[1:]
    i, directory = 0, None
    while i < len(args) and args[i].startswith('-'):
        if args[i] == '-C' and i + 1 < len(args):
            directory = args[i + 1] if directory is None else os.path.join(directory, args[i + 1])
            i += 2
            continue
        if args[i] in ('--git-dir', '--work-tree') or args[i].startswith(('--git-dir=', '--work-tree=')):
            # Explicit repository selection bypasses discovery: assume this
            # checkout's whole tree rather than guessing which one it targets.
            return [], True, THIS_CHECKOUT
        if args[i] in ('-c',):
            i += 1
        i += 1
    if i >= len(args):
        return [], False, directory
    sub, rest = args[i], args[i + 1:]
    inert = {'config', 'version', '--version', 'hash-object', 'check-ignore', 'merge-base',
             'fetch', 'init', 'remote', 'describe', 'var', 'help', 'symbolic-ref'}
    if sub == 'rev-parse':
        paths = []
        for arg in rest:
            if ':' in arg and not arg.startswith('-'):
                rev, _, path = arg.partition(':')
                if _SHA.match(rev):
                    continue
                if not path:
                    return [], True, directory
                paths.append((path, 'git'))  # the object id of a live path changes with it
        return paths, False, directory
    if sub in ('show', 'cat-file'):
        if any(a.startswith('--batch') for a in rest):
            return [], True, directory  # requests arrive on stdin, which the trace does not see
        operands = [a for a in rest if not a.startswith('-')]
        if not operands:
            return [], True, directory  # `git show` alone prints the whole HEAD commit
        paths = []
        for arg in operands:
            if ':' in arg:
                rev, _, path = arg.partition(':')
                if _SHA.match(rev):
                    continue  # an immutable object cannot change with the tree
                if path:
                    paths.append((path, 'git'))  # repository-relative, see parse_strace
                else:
                    return [], True, directory
            elif _SHA.match(arg):
                continue
            else:
                return [], True, directory  # a ref alone: a commit, tree or blob of the live history
        return paths, False, directory
    if sub == 'apply':
        if any(a in ('--cached', '--index') or a.startswith('--index') for a in rest):
            return [], True, directory  # the index and object database are not traced
        return [], False, directory  # the patch and the target files are read from the tree: traced
    if sub in inert:
        return [], False, directory
    if sub in ('restore', 'checkout'):
        paths = [(a, 'file') for a in rest if not a.startswith('-')]
        return (paths, False, directory) if paths else ([], True, directory)
    return [], True, directory


def parse_strace(log_lines, start_cwd):
    """Yield (path, kind, syscall) with kind in {'file', 'dir', 'tree', 'gitpath'}.
    ``log_lines`` is a callable returning a fresh iterable of lines (the log
    is read twice: once for the process tree, once for the paths), or a
    string."""
    if isinstance(log_lines, str):
        text = log_lines
        log_lines = lambda: text.splitlines()
    parent = {}
    for line in log_lines():
        m = _LINE.match(line)
        if not m:
            continue
        rest = m.group('rest')
        call = _CALL.match(rest) or _RESUMED.match(rest)
        if call and call.group('name') in FORK_CALLS:
            ret = _RESULT.search(rest)
            if ret and ret.group('ret').isdigit():
                parent[ret.group('ret')] = m.group('pid')
    cwd, pending_chdir, fd_pending = {}, {}, {}

    def current(pid):
        if pid not in cwd:
            cwd[pid] = current(parent[pid]) if pid in parent else start_cwd
        return cwd[pid]

    def resolve(pid, path, base=None):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(base if base else current(pid), path))

    for line in log_lines():
        m = _LINE.match(line)
        if not m:
            continue
        pid, rest = m.group('pid'), m.group('rest')
        call = _CALL.match(rest)
        resumed = _RESUMED.match(rest) if not call else None
        if resumed:
            name = resumed.group('name')
            ret = _RESULT.search(rest)
            if name in FORK_CALLS and ret and ret.group('ret').isdigit():
                cwd.setdefault(ret.group('ret'), current(pid))
            elif name in ('chdir', 'fchdir') and ret and ret.group('ret') == '0' and pid in pending_chdir:
                cwd[pid] = pending_chdir.pop(pid)
            continue
        if not call:
            continue
        name, args = call.group('name'), call.group('args')
        unfinished = args.rstrip().endswith('<unfinished ...>')
        ret = None if unfinished else _RESULT.search(rest)
        toks = tokens(args)
        if name in FORK_CALLS:
            if ret and ret.group('ret').isdigit():
                cwd.setdefault(ret.group('ret'), current(pid))
            continue
        if name in ('chdir', 'fchdir'):
            target = None
            if toks:
                if name == 'chdir':
                    s = string_value(toks[0])
                    target = resolve(pid, s) if s is not None else None
                else:
                    fd = _FD.match(toks[0])
                    target = fd.group('path') if fd else None
            if target is None:
                continue
            if unfinished:
                pending_chdir[pid] = target
            elif ret and ret.group('ret') == '0':
                cwd[pid] = target
            continue
        if name in SKIP_CALLS:
            continue
        if name == 'execve':
            if toks:
                prog = string_value(toks[0])
                if prog is not None:
                    yield resolve(pid, prog), 'file', name
                argv = argv_strings(toks[1]) if len(toks) > 1 else []
                if argv and os.path.basename(argv[0]) == 'git':
                    paths, tree, directory = git_semantics(argv)
                    # The repository git operates on is the one containing the
                    # process cwd, or the -C operand; classify() checks whether
                    # that is this repository or a nested checkout.
                    where = (start_cwd if directory == THIS_CHECKOUT else
                             resolve(pid, directory) if directory else current(pid))
                    if tree:
                        yield where, 'tree', name
                    for path, kind in paths:
                        if kind == 'git':  # REV:path is repository-relative unless ./ or ../
                            yield where + '\0' + path, 'gitpath', name
                        else:
                            yield resolve(pid, path), kind, name
            continue
        # Generic file syscall: quoted operands are paths, each relative to the
        # preceding dirfd operand (``AT_FDCWD<cwd>`` or ``N<path>``) if any.
        operands, base = [], None
        for tok in toks:
            fd = _FD.match(tok)
            if fd:
                base = fd.group('path'); continue
            s = string_value(tok)
            if s is not None:
                operands.append((s, base)); base = None
        if not operands:
            continue
        wanted = TWO_PATH.get(name, (0,))
        kind = 'dir' if 'O_DIRECTORY' in args else 'file'
        for index in wanted:
            if index < len(operands):
                path, b = operands[index]
                yield resolve(pid, path, b), kind, name


# ---------------------------------------------------------------- classification

def git_lines(*args, cwd=ROOT):
    return subprocess.run(['git', *args], cwd=cwd, check=True, stdout=subprocess.PIPE
                          ).stdout.decode().split('\0' if '-z' in args else '\n')


def tracked_files(root=ROOT):
    return set(p for p in git_lines('ls-files', '-z', cwd=Path(root)) if p)


def tracked_dirs(tracked):
    """Every directory that contains a tracked file, at any depth."""
    dirs = set()
    for path in tracked:
        parent = path
        while '/' in parent:
            parent = parent.rsplit('/', 1)[0]
            if parent in dirs:
                break
            dirs.add(parent)
    return dirs


def nearest_tracked(directory, dirs):
    """The directory itself if git knows it, else its deepest ancestor that
    git knows ('' for the root). The planner attributes additions to tracked
    directories only, so declarations must not name runtime-only ones."""
    while directory and directory not in dirs:
        directory = directory.rsplit('/', 1)[0] if '/' in directory else ''
    return directory


def classify(paths, root=ROOT):
    """Split (lexical absolute path, kind) records into tracked files, listed
    directories, existence checks, probes, git tree objects and a
    whole-tree flag."""
    root = Path(root).resolve()
    tracked = tracked_files(root)
    known_dirs = tracked_dirs(tracked)
    inside, tree, subtrees = {}, False, set()

    def this_repository(directory):
        """Is ``directory`` inside this checkout and not a nested repository?"""
        d = Path(os.path.normpath(directory))
        try:
            d.relative_to(root)
        except ValueError:
            return False
        probe = d
        while True:
            if (probe / '.git').exists():
                return probe == root
            if probe == root or probe.parent == probe:
                return probe == root
            probe = probe.parent

    for path, kind in paths:
        if kind == 'tree':
            if this_repository(path):
                tree = True
            continue
        if kind == 'gitpath':
            where, _, rel_path = path.partition('\0')
            if not this_repository(where):
                continue
            if rel_path.startswith(('./', '../')):
                path = os.path.normpath(os.path.join(where, rel_path))
            else:
                path = os.path.normpath(os.path.join(str(root), rel_path))
            try:
                rel = Path(path).relative_to(root).as_posix()
            except ValueError:
                continue
            if rel in known_dirs or rel == '.':
                subtrees.add('' if rel == '.' else rel)  # a tree object: names and hashes of everything below
                continue
            kind = 'file'
        try:
            rel = Path(os.path.normpath(path)).relative_to(root).as_posix()
        except ValueError:
            continue
        if rel == '.':
            rel = ''
        parts = rel.split('/') if rel else []
        if parts and parts[0] == '.git':
            continue
        inside.setdefault(rel, set()).add(kind)
        # Every symbolic link on the lexical path is an input (a link is a
        # tracked entry), and so is the resolved target when it is inside.
        prefix = root
        for part in parts:
            prefix = prefix / part
            if os.path.islink(prefix):
                link_rel = prefix.relative_to(root).as_posix()
                inside.setdefault(link_rel, set()).add('file')
                try:
                    target = Path(os.path.realpath(prefix)).relative_to(root).as_posix()
                    inside.setdefault(target, set()).add('file' if target != rel else kind)
                except ValueError:
                    pass
        if rel:
            real = os.path.realpath(root / rel)
            if real != os.path.normpath(str(root / rel)):
                try:
                    target = Path(real).relative_to(root).as_posix()
                    inside.setdefault(target, set()).add(kind)
                except ValueError:
                    pass
    candidates = [rel for rel in inside if rel and rel not in tracked]
    ignored = set()
    if candidates:
        out = subprocess.run(['git', 'check-ignore', '-z', '--stdin', '--no-index'], cwd=root,
                             input='\0'.join(candidates).encode(), stdout=subprocess.PIPE)
        ignored = set(p for p in out.stdout.decode().split('\0') if p)
    files, dirs, exists, probes = set(), set(), set(), set()
    for rel, kinds in inside.items():
        full = root / rel if rel else root
        if rel in tracked:
            files.add(rel)
        elif rel in ignored:
            continue  # build outputs and caches: tracking one is an undeclared addition, which runs everything
        elif os.path.isdir(full) and not os.path.islink(full):
            # A directory git does not know (created at run time) is declared
            # at its nearest tracked ancestor, which is where the planner
            # attributes additions below it.
            anchored = nearest_tracked(rel, known_dirs)
            if 'dir' in kinds:
                dirs.add(anchored)  # opened as a directory: its entries were listed
            else:
                exists.add(anchored)  # only stat/readlink/access: its existence was checked
        elif not rel or rel in MAKE_PROBES or '/' not in rel:
            continue  # root-level probe: an undeclared new root entry runs everything
        else:
            probes.add(rel)  # missing path, or an untracked unignored file a PR could track
    return sorted(files), sorted(dirs), sorted(probes), tree, sorted(exists), sorted(subtrees)


# ---------------------------------------------------------------- running

def seccomp_supported():
    """strace >= 5.3 can filter unselected syscalls in the kernel, which cuts
    the tracing overhead without changing what is recorded."""
    try:
        probe = subprocess.run(['strace', '--seccomp-bpf', '-f', '-e', 'trace=%file', '-o', os.devnull, '--', 'true'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return probe.returncode == 0
    except OSError:
        return False


def run_traced(commands, cwd=ROOT, env=None):
    """Run shell commands under strace; return (exit_code, log path)."""
    log = Path(cwd) / 'build' / 'verify-trace' / 'strace.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    if log.exists():
        log.unlink()
    # Each command runs in its own subshell from the repository root, so a
    # `cd` in one command cannot change where the next one resolves paths.
    script = ' && '.join('( ' + c + ' )' for c in commands)
    cmd = ['strace', '-f', '-qq', '-s', '65536', '-e', 'signal=none', '-e', 'trace=' + TRACE_SYSCALLS,
           '-o', str(log), '-y'] + (['--seccomp-bpf'] if seccomp_supported() else []) + ['--', 'sh', '-c', script]
    print('TRACE ' + script, flush=True)
    code = subprocess.run(cmd, cwd=cwd, env=env).returncode
    return code, log


RECORDING_VERSION = 5


def record(group, commands, cwd=ROOT):
    code, log = run_traced(commands, cwd)

    def lines():
        if not log.exists():
            return iter(())
        return (line.rstrip('\n') for line in open(log, encoding='utf-8', errors='replace'))
    # Deduplicate while streaming: the log of a large group exceeds 100 MB.
    paths = set((p, k) for p, k, _ in parse_strace(lines, str(Path(cwd).resolve())))
    files, dirs, probes, tree, exists, subtrees = classify(paths, cwd)
    return code, {'group': group, 'commands': commands, 'files': files, 'dirs': dirs, 'exists': exists,
                  'probes': probes, 'subtrees': subtrees, 'tree': tree, 'exit_code': code,
                  'recording_version': RECORDING_VERSION, 'python': sys.version.split()[0]}


# ---------------------------------------------------------------- coverage

def pattern_matches(pattern, path):
    """Does an edit of the existing file ``path`` match ``pattern``?"""
    if pattern == '**':
        return True
    if pattern.endswith('/**'):
        prefix = pattern[:-3]
        return path == prefix or path.startswith(prefix + '/')
    if pattern == '*' or pattern.endswith('/*') or pattern.endswith('/'):
        return False  # listing and existence patterns only cover added or removed entries
    return pattern == path


def dir_covered(pattern, directory):
    """A listed directory needs dir/*, dir/** or an ancestor ** pattern."""
    if pattern == '**':
        return True
    if pattern == '*':
        return directory == ''
    if pattern.endswith('/**'):
        prefix = pattern[:-3]
        return directory == prefix or directory.startswith(prefix + '/')
    if pattern.endswith('/*'):
        return directory == pattern[:-2]
    return False


def exists_covered(pattern, directory):
    """An existence check of a directory needs dir/, or anything that covers
    its listing."""
    if pattern.endswith('/') and not pattern.endswith('/**'):
        return directory == pattern[:-1]
    return dir_covered(pattern, directory)


_TRACKED_DIRS = {}


def anchor(path, root=ROOT):
    """The deepest ancestor directory of a probed path that git knows (it
    contains a tracked file): adding the path, with any missing intermediate
    directories, changes that listing in the tree the planner inspects."""
    key = str(root)
    if key not in _TRACKED_DIRS:
        _TRACKED_DIRS[key] = tracked_dirs(tracked_files(root))
    return nearest_tracked(path.rsplit('/', 1)[0] if '/' in path else '', _TRACKED_DIRS[key])


def probe_covered(pattern, path, root=ROOT):
    """A probed (absent or untracked) path can only be added: exact, ** or a
    listing pattern on its anchor directory all cover that."""
    return pattern_matches(pattern, path) or dir_covered(pattern, anchor(path, root))


def uncovered(recording, patterns, root=ROOT):
    missing = []
    if recording.get('tree') and '**' not in patterns:
        missing.append('**')
    for path in recording['files']:
        if not any(pattern_matches(p, path) for p in patterns):
            missing.append(path)
    for path in recording.get('probes', []):
        if not any(probe_covered(p, path, root) for p in patterns):
            missing.append(path)
    for directory in recording['dirs']:
        if not any(dir_covered(p, directory) for p in patterns):
            missing.append((directory + '/*') if directory else '*')
    for directory in recording.get('exists', []):
        if directory and not any(exists_covered(p, directory) for p in patterns):
            missing.append(directory + '/')
    for directory in recording.get('subtrees', []):
        if not any(p == '**' or (p.endswith('/**') and dir_covered(p, directory)) for p in patterns):
            missing.append((directory + '/**') if directory else '**')
    return missing


DENSE = 4
WALK_FRACTION = 0.5


def suggest(recording, covered_by=(), root=ROOT):
    """Covering patterns: ** for whole-tree queries; dir/** where most of a
    directory's tracked files are read or most of its subdirectories are
    listed (a walk); dir/* for other listings and for probes, at the probe's
    anchor; dir/ for existence checks; exact paths otherwise. Patterns
    already implied by ``covered_by`` (the manifest's ``all`` list) are
    omitted."""
    covered_by = list(covered_by)
    if recording.get('tree'):
        return [] if '**' in covered_by else ['**']
    files = sorted(set(recording['files']))
    by_dir = {}
    for path in files:
        by_dir.setdefault(path.rsplit('/', 1)[0] if '/' in path else '', []).append(path)
    key = str(root)
    if key not in _TRACKED_DIRS:
        _TRACKED_DIRS[key] = tracked_dirs(tracked_files(root))
    tracked_by_dir = {}
    for path in tracked_files(root):
        tracked_by_dir.setdefault(path.rsplit('/', 1)[0] if '/' in path else '', 0)
        tracked_by_dir[path.rsplit('/', 1)[0] if '/' in path else ''] += 1
    chosen = []
    # A directory most of whose tracked files were read is declared whole;
    # a few files out of many stay exact, so unrelated additions to a shared
    # directory (a note, a certificate) do not select the group.
    for d in sorted(d for d, items in by_dir.items()
                    if d and len(items) >= DENSE and len(items) > WALK_FRACTION * tracked_by_dir.get(d, len(items))):
        if not any(dir_covered(c, d) and c.endswith('**') for c in chosen + covered_by):
            chosen.append(d + '/**')
    # A directory most of whose subdirectories are listed was walked: any
    # change below it may add or remove listed entries, so declare it whole.
    listed_children = {}
    for d in recording['dirs']:
        if d:
            listed_children.setdefault(d.rsplit('/', 1)[0] if '/' in d else '', []).append(d)
    for parent, items in sorted(listed_children.items()):
        if not parent or len(items) < DENSE:
            continue
        try:
            total = sum(1 for e in os.scandir(Path(root) / parent) if e.is_dir(follow_symlinks=False))
        except OSError:
            total = len(items)
        if len(items) > WALK_FRACTION * total and not any(
                dir_covered(c, parent) and c.endswith('**') for c in chosen + covered_by):
            chosen.append(parent + '/**')
    chosen = [c for c in chosen if not any(o != c and o.endswith('/**') and dir_covered(o, c[:-3]) for o in chosen)]
    for d in sorted(recording['dirs']):
        if not any(dir_covered(c, d) for c in chosen + covered_by):
            chosen.append((d + '/*') if d else '*')
    for directory in sorted(recording.get('subtrees', [])):
        pattern = (directory + '/**') if directory else '**'
        if not any(c == '**' or (c.endswith('/**') and dir_covered(c, directory)) for c in chosen + covered_by):
            chosen.append(pattern)
    for directory in sorted(recording.get('exists', [])):
        if directory and not any(exists_covered(c, directory) for c in chosen + covered_by):
            chosen.append(directory + '/')
    for path in files:
        if not any(pattern_matches(c, path) for c in chosen + covered_by):
            chosen.append(path)
    for path in sorted(set(recording.get('probes', []))):
        if not any(probe_covered(c, path, root) for c in chosen + covered_by):
            a = anchor(path, root)
            chosen.append((a + '/*') if a else '*')
    return sorted(set(chosen))


def load_manifest(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_recording(path, group):
    """Reject incompatible or incomplete evidence before rechecking coverage."""
    recording = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(recording, dict):
        raise ValueError('Recording must be an object')
    if recording.get('group') != group:
        raise ValueError('Recording group does not match --group')
    if type(recording.get('recording_version')) is not int or recording['recording_version'] != RECORDING_VERSION:
        raise ValueError('Unsupported recording version; record the group again')
    if type(recording.get('exit_code')) is not int:
        raise ValueError('Recording needs an integer exit_code')
    if type(recording.get('tree')) is not bool:
        raise ValueError('Recording needs a boolean tree flag')
    for field in ('commands', 'files', 'dirs', 'exists', 'probes', 'subtrees'):
        values = recording.get(field)
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ValueError('Recording needs a string list for ' + field)
    if not recording['commands']:
        raise ValueError('Recording needs at least one command')
    return recording


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--group', required=True, help='verification group, e.g. community or ranked-pair-finite')
    ap.add_argument('--output', type=Path, help='write the recording as JSON')
    ap.add_argument('--check', type=Path, nargs='?', const=MANIFEST,
                    help='fail unless the manifest covers every recorded input (default manifest: %(default)s)')
    ap.add_argument('--suggest', action='store_true', help='print the minimal covering patterns')
    ap.add_argument('--command', action='append',
                    help='trace this shell command instead of the group default (repeatable, run in order)')
    ap.add_argument('--from-recording', type=Path, help='reuse a recording instead of running the group')
    args = ap.parse_args(argv)

    if args.from_recording:
        try:
            recording = load_recording(args.from_recording, args.group)
        except (OSError, ValueError) as error:
            ap.error(str(error))
        code = recording['exit_code']
    else:
        code, recording = record(args.group, args.command or group_commands(args.group))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(recording, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print('RECORDED group=%s files=%d dirs=%d exists=%d probes=%d subtrees=%d tree=%s' % (
        recording['group'], len(recording['files']), len(recording['dirs']), len(recording.get('exists', [])),
        len(recording.get('probes', [])), len(recording.get('subtrees', [])), recording.get('tree', False)))
    if code != 0:
        print('VERIFICATION_FAILED exit=%d' % code)
        return code
    status = 0
    if args.check:
        manifest = load_manifest(args.check)
        patterns = list(manifest['all']) + list(manifest['groups'][args.group]['paths'])
        missing = uncovered(recording, patterns, ROOT)
        if missing:
            print('UNDECLARED_INPUTS group=%s (add to %s):' % (args.group, args.check))
            for item in missing:
                print('  ' + item)
            status = 2
        else:
            print('PASS_DECLARED_INPUTS_COVER_RECORDING group=' + args.group)
    if args.suggest:
        covered = load_manifest(args.check)['all'] if args.check else ()
        print(json.dumps(suggest(recording, covered, ROOT), indent=1))
    return status


if __name__ == '__main__':
    sys.exit(main())
