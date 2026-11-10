#!/usr/bin/env python3
"""Source-pinned opt-in raw candidate prefilter; Git keeps every path policy.

Armin Pourshafeie/apoursh, ToikY/6357 and Nick Petalas/6428 retain credit.
New bounded adapter: ToikY with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
MANIFEST_SHA = 'e4d812801ed232f58117f51343b7409b67059bd10c500acfef2a2da8f697f2b9'
CHUNK = 512 * 1024
MAX_ARGUMENT_BYTES = 64 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def decode(raw):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def bad(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad)


def authenticated():
    manifest = (HERE / 'SOURCE-PINS.json').read_bytes()
    require(hashlib.sha256(manifest).hexdigest() == MANIFEST_SHA, 'source manifest SHA256')
    pins = decode(manifest)['files']
    require(set(pins) == {'predecessor.py', 'reuse.py', 'README-6428.md', 'research_package.py'}, 'four exact sources')
    raw = {}
    for name, pin in pins.items():
        value = (HERE / 'sources' / name).read_bytes()
        require(len(value) == pin['bytes'], 'source length: ' + name)
        require(hashlib.sha256(value).hexdigest() == pin['sha256'], 'source SHA256: ' + name)
        blob = b'blob ' + str(len(value)).encode() + b'\0' + value
        require(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'source Git blob: ' + name)
        raw[name] = value
    return raw


def helper_module(raw):
    tree = ast.parse(raw, filename='frozen/research_package.py')
    wanted = {'_GIT_REDIRECT_VARS', '_GIT_CONFIG_PREFIXES', 'git_source_env'}
    selected = []
    for node in tree.body:
        names = {t.id for t in node.targets if isinstance(t, ast.Name)} if isinstance(node, ast.Assign) else set()
        if isinstance(node, ast.FunctionDef):
            names = {node.name}
        if names & wanted:
            selected.append(node)
    require(len(selected) == 3, 'exact canonical helper declarations')
    module = types.ModuleType('research_package')
    module.__dict__['os'] = os
    exec(compile(ast.Module(body=selected, type_ignores=[]), 'frozen/git_source_env', 'exec'), module.__dict__)
    return module


def load_source(name, raw=None):
    require(name in ('predecessor', 'reuse'), 'bounded source module selection')
    raw = authenticated() if raw is None else raw
    helper = helper_module(raw['research_package.py'])
    old = sys.modules.get('research_package')
    module = types.ModuleType('private_pinned_' + name)
    module.__file__ = str(HERE / 'sources' / (name + '.py'))
    try:
        sys.modules['research_package'] = helper
        exec(compile(raw[name + '.py'], module.__file__, 'exec'), module.__dict__)
    finally:
        if old is None:
            sys.modules.pop('research_package', None)
        else:
            sys.modules['research_package'] = old
    return module


def seam(args):
    if len(args) < 9 or args[:5] != ('grep', '-I', '-l', '-z', '-F') or args[-1] != '--':
        return None
    patterns = args[5:-2]
    if len(patterns) % 2 or not patterns:
        return None
    needles = []
    for flag, digest in zip(patterns[::2], patterns[1::2]):
        if flag != '-e' or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            return None
        needles.append(digest.encode('ascii'))
    revision = args[-2]
    if len(revision) not in (40, 64) or any(c not in '0123456789abcdef' for c in revision):
        return None
    return revision, needles


def tree_aliases(root, revision, git):
    prefix = git(root, 'rev-parse', '--show-prefix', check=False)
    require(prefix.returncode == 0 and not prefix.stdout.strip(), 'repository-root context required')
    for key in ('grep.recurseSubmodules', 'submodule.recurse'):
        config = git(root, 'config', '--bool', '--get-all', key, check=False)
        require(config.returncode in (0, 1), 'unsupported recursive configuration')
        require(all(x == b'false' for x in config.stdout.splitlines()), 'recursive configuration enabled')
    result = git(root, 'ls-tree', '-r', '-z', '--full-tree', revision, check=False)
    require(result.returncode == 0 and len(result.stdout) <= 8 * 1024 * 1024, 'tree listing fallback')
    entries = []
    for row in result.stdout.split(b'\0'):
        if not row:
            continue
        header, path = row.split(b'\t', 1)
        mode, kind, oid = header.split()
        require(kind != b'commit', 'gitlink traversal requires original search')
        require(kind == b'blob' and mode in (b'100644', b'100755', b'120000'), 'unsupported tree mode')
        if mode != b'120000':
            entries.append((path.decode('utf-8'), oid.decode('ascii')))
    require(len(entries) <= 10000, 'tree path bound')
    return entries


def stream_hits(root, oids, needles, env, metrics, chunk_size=CHUNK):
    hits = set()
    with tempfile.TemporaryFile() as errors:
        with subprocess.Popen(['git', '--no-replace-objects', 'cat-file', '--batch'], cwd=root,
                              env=env(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors) as process:
            try:
                for oid in oids:
                    process.stdin.write(oid.encode('ascii') + b'\n')
                    process.stdin.flush()
                    header = process.stdout.readline(256).split()
                    require(len(header) == 3 and header[0].decode('ascii') == oid and header[1] == b'blob', 'blob batch header')
                    remaining = int(header[2])
                    require(remaining >= 0, 'blob size')
                    metrics['unique_blob_reads'] += 1
                    carry, matched = b'', False
                    while remaining:
                        data = process.stdout.read(min(chunk_size, remaining))
                        require(data, 'truncated blob payload')
                        remaining -= len(data)
                        metrics['prefilter_payload_bytes'] += len(data)
                        window = carry + data
                        if not matched and any(needle in window for needle in needles):
                            matched = True
                        carry = window[-63:]
                    require(process.stdout.read(1) == b'\n', 'blob framing newline')
                    if matched:
                        hits.add(oid)
                process.stdin.close()
                require(process.wait(timeout=30) == 0, 'blob reader exit')
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)
    return hits


class Prefilter:
    def __init__(self, module, max_argument_bytes=MAX_ARGUMENT_BYTES, chunk_size=CHUNK):
        require(type(chunk_size) is int and 1 <= chunk_size <= CHUNK, 'bounded stream chunk')
        require(type(max_argument_bytes) is int and max_argument_bytes > 0, 'positive argument bound')
        self.original = module.git
        self.env = module.git_source_env
        self.limit = max_argument_bytes
        self.chunk = chunk_size
        self.metrics = {'unique_blob_reads': 0, 'prefilter_payload_bytes': 0,
                        'regular_tree_paths': 0, 'unique_tree_blobs': 0,
                        'candidate_aliases': 0, 'final_grep_pathspecs': 0, 'fallbacks': []}

    def candidates(self, root, revision, needles):
        entries = tree_aliases(root, revision, self.original)
        oids = list(dict.fromkeys(oid for _path, oid in entries))
        self.metrics['regular_tree_paths'] = len(entries)
        self.metrics['unique_tree_blobs'] = len(oids)
        hits = stream_hits(root, oids, needles, self.env, self.metrics, self.chunk)
        return [path for path, oid in entries if oid in hits]

    def __call__(self, root, *args, check=True, data=None):
        parsed = seam(args)
        if parsed is None or check is not False or data is not None:
            return self.original(root, *args, check=check, data=data)
        try:
            paths = self.candidates(root, *parsed)
            self.metrics['candidate_aliases'] = len(paths)
            require(paths, 'empty candidate set delegates original exit/error behavior')
            extended = ('--literal-pathspecs',) + args + tuple(paths)
            size = sum(len(x.encode('utf-8')) + 1 for x in extended)
            require(size <= self.limit, 'argument bound')
            result = self.original(root, *extended, check=False)
            require(result.returncode in (0, 1), 'restricted grep error')
            self.metrics['final_grep_pathspecs'] = len(paths)
            return result
        except (ValueError, OSError, UnicodeError, subprocess.SubprocessError) as error:
            self.metrics['fallbacks'].append(str(error))
            return self.original(root, *args, check=check, data=data)


@contextmanager
def installed(module, **options):
    adapter = Prefilter(module, **options)
    module.git = adapter
    try:
        yield adapter
    finally:
        module.git = adapter.original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('predecessor', 'reuse', 'prefilter'))
    options, rest = parser.parse_known_args()
    module = load_source('predecessor' if options.mode == 'predecessor' else 'reuse')
    if options.mode == 'prefilter':
        with installed(module):
            return module.main(rest)
    return module.main(rest)


if __name__ == '__main__':
    sys.exit(main())
