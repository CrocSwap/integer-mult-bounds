# SPDX-License-Identifier: Apache-2.0
"""Shared helpers for the PR #2530 audit: one failure type and the pinned-input reader.

Every PR input is read with `git -C <repo> show <commit>:<path>` at a pinned commit and must match a pinned git
blob id (and, where listed, a sha256) before it is parsed; a pinned tree is listed by reading and re-hashing every
tree object below it (`git cat-file tree`, recursively), so a listing is accepted only if it hashes to the pinned
tree id.  PR content is data only: it is decoded as JSON, gzip, tar or text and never imported or executed.

Git environment (git_env): the repository-redirecting variables (GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE,
GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_NAMESPACE, GIT_CEILING_DIRECTORIES, GIT_COMMON_DIR) and
the command-line config injections (GIT_CONFIG_PARAMETERS, GIT_CONFIG_COUNT, GIT_CONFIG_KEY_*, GIT_CONFIG_VALUE_*)
are removed, GIT_NO_REPLACE_OBJECTS=1 is set, so every git call reads exactly the --repo repository's own objects,
and GIT_NO_LAZY_FETCH=1 is set, so that in a partial clone `git show` fails on a missing object instead of fetching
it (honoured by recent git; older git ignores it).  The reader is read-only.  The only write is the documented --fetch (ensure_commits), which runs
`git fetch` with --no-write-fetch-head, --no-tags, --no-recurse-submodules, --no-prune, an empty --refmap and
-c gc.auto=0 -c maintenance.auto=false -c fetch.writeCommitGraph=false -c core.logAllRefUpdates=false
-c core.hooksPath=/dev/null, so it writes only the fetched objects and the namespaced ref refs/audit/pr<N> (no
FETCH_HEAD, no other ref, no reflog, no commit-graph, no gc or maintenance, no hook); it needs git >= 2.29
(--no-write-fetch-head); a failed fetch is reported with git's own error message.

Control bookkeeping: every negative-control helper of the scopes calls attempt() before it runs its mutant, and every
positive control calls positive(<id>) after it has passed, so verify.py prints attempted and rejected negative
controls from separate counters and the positive controls actually executed.
Standard library only; Python 3.8-compatible syntax.
"""
import gzip
import hashlib
import json
import os
import subprocess


class AuditFail(Exception):
    """A failed audit check (the message names the check)."""


def need(ok, msg):
    if not ok:
        raise AuditFail(msg)


# Negative controls attempted (names, in order) and positive controls executed (ids, in order); see reset_controls.
ATTEMPTED, POSITIVES = [], []


def reset_controls():
    del ATTEMPTED[:]
    del POSITIVES[:]


def attempt(name):
    """Called by every negative-control helper before it runs its mutant."""
    ATTEMPTED.append(name)


def positive(pid):
    """Called after a positive control has passed."""
    POSITIVES.append(pid)


def git_blob_id(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# Environment variables that would make git read or write a repository other than `git -C <repo>`.
GIT_REDIRECT_VARS = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY',
                     'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_NAMESPACE', 'GIT_CEILING_DIRECTORIES', 'GIT_COMMON_DIR')
# Environment variables that inject configuration as if given with `git -c` (prefixes end with '_').
GIT_CONFIG_INJECTION_VARS = ('GIT_CONFIG_PARAMETERS', 'GIT_CONFIG_COUNT')
GIT_CONFIG_INJECTION_PREFIXES = ('GIT_CONFIG_KEY_', 'GIT_CONFIG_VALUE_')
# `git -c` settings and options of the one writing call (--fetch): objects and refs/audit/pr<N> only.
FETCH_CONFIG = ('gc.auto=0', 'maintenance.auto=false', 'fetch.writeCommitGraph=false', 'core.logAllRefUpdates=false',
                'core.hooksPath=/dev/null')
FETCH_OPTIONS = ('-q', '--no-tags', '--no-write-fetch-head', '--no-recurse-submodules', '--no-prune', '--refmap=')


def git_env():
    """A copy of os.environ without GIT_REDIRECT_VARS and the config-injection variables, with
    GIT_NO_REPLACE_OBJECTS=1 (refs/replace is ignored) and GIT_NO_LAZY_FETCH=1 (no on-demand fetch of missing
    objects in a partial clone)."""
    env = dict(os.environ)
    for name in list(env):
        if name in GIT_REDIRECT_VARS or name in GIT_CONFIG_INJECTION_VARS or name.startswith(GIT_CONFIG_INJECTION_PREFIXES):
            del env[name]
    env['GIT_NO_REPLACE_OBJECTS'] = '1'
    env['GIT_NO_LAZY_FETCH'] = '1'
    return env


def _git(repo, args, config=()):
    cmd = ['git']
    for kv in config:
        cmd += ['-c', kv]
    return subprocess.run(cmd + ['-C', repo] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=git_env())


def commit_present(repo, commit):
    return _git(repo, ['cat-file', '-e', commit + '^{commit}']).returncode == 0


def audit_ref(pr):
    return 'refs/audit/pr%d' % pr


def anchored(repo, commit, ref):
    """commit is present and reachable from ref (so git gc keeps it)."""
    return commit_present(repo, commit) and _git(repo, ['merge-base', '--is-ancestor', commit, ref]).returncode == 0


def ensure_commits(repo, commits, fetch, remote):
    """commits: {pr_number: sha}.  Without fetch a missing commit is an error and nothing is written.  With fetch,
    a missing commit is fetched from the remote's refs/pull/N/head and, if the PR head has moved past it, by its
    sha, each time into the namespaced ref refs/audit/prN of the target repository (forced update), so that the
    fetched commit stays reachable from a ref and survives git gc; it must then be present and reachable from
    refs/audit/prN.  The fetch writes the fetched objects and refs/audit/prN only (FETCH_CONFIG, FETCH_OPTIONS;
    git >= 2.29).  If the commit is still missing, the failure message carries the last fetch's exit code and stderr
    (for example an unknown option on older git, or a network error).  Returns the PR numbers fetched."""
    need(_git(repo, ['rev-parse', '--git-dir']).returncode == 0, '%s is not a git repository (use --repo)' % repo)
    fetched = []
    for pr in sorted(commits):
        sha = commits[pr]
        if commit_present(repo, sha):
            continue
        need(fetch, 'commit %s of PR #%d is absent from %s; rerun with --fetch' % (sha[:12], pr, repo))
        ref = audit_ref(pr)
        last = None
        for src in ('refs/pull/%d/head' % pr, sha):
            last = _git(repo, ['fetch'] + list(FETCH_OPTIONS) + [remote, '+%s:%s' % (src, ref)], FETCH_CONFIG)
            if anchored(repo, sha, ref):
                fetched.append(pr)
                break
        need(anchored(repo, sha, ref), 'could not fetch commit %s of PR #%d from %s into %s (last git fetch: exit %d, '
             'stderr %r)' % (sha[:12], pr, remote, ref, last.returncode, last.stderr.decode('utf-8', 'replace')[-400:]))
    return fetched


class PinnedInputs(object):
    """Reader for the pinned input table {key: (pr, commit, path, git_blob, sha256 or None)}.

    raw() returns the verified bytes; json() the parsed JSON (gunzipped for *.gz).  Parsed objects are cached and
    shared, so callers must treat them as read-only (controls deep-copy before mutating)."""

    def __init__(self, repo, table):
        self.repo, self.table = repo, table
        self._raw, self._json, self.used = {}, {}, {}

    def raw(self, key):
        if key not in self._raw:
            pr, commit, path, blob, sha = self.table[key]
            p = _git(self.repo, ['rev-parse', '--verify', '-q', commit + ':' + path])
            need(p.returncode == 0, 'input %s: %s:%s not found' % (key, commit[:12], path))
            need(p.stdout.decode().strip() == blob, 'input %s: tree entry is not the pinned blob %s' % (key, blob))
            p = _git(self.repo, ['show', commit + ':' + path])
            need(p.returncode == 0, 'input %s: git show failed: %s' % (key, p.stderr.decode()[:200]))
            data = p.stdout
            need(git_blob_id(data) == blob, 'input %s: git blob id mismatch' % key)
            digest = sha256(data)
            need(sha is None or digest == sha, 'input %s: sha256 mismatch' % key)
            self._raw[key] = data
            self.used[key] = dict(pr=pr, commit=commit, path=path, git_blob=blob, sha256=digest, bytes=len(data))
        return self._raw[key]

    def json(self, key):
        if key not in self._json:
            data = self.raw(key)
            if self.table[key][2].endswith('.gz'):
                data = gzip.decompress(data)
            self._json[key] = json.loads(data.decode('utf-8'))
        return self._json[key]

    def text(self, key):
        return self.raw(key).decode('utf-8')

    def show_blob(self, commit, path, blob):
        """Bytes of commit:path for a file listed by tree(); the blob id is re-verified."""
        p = _git(self.repo, ['show', commit + ':' + path])
        need(p.returncode == 0 and git_blob_id(p.stdout) == blob, 'git show %s:%s is not blob %s' % (commit[:12], path, blob))
        return p.stdout

    def _tree_object(self, tree_id):
        """Raw content of a tree object, re-hashed against its id (fail-closed listing)."""
        p = _git(self.repo, ['cat-file', 'tree', tree_id])
        need(p.returncode == 0, 'git cat-file tree %s failed' % tree_id)
        data = p.stdout
        need(hashlib.sha1(b'tree %d\0' % len(data) + data).hexdigest() == tree_id, 'tree object %s does not hash to its id'
             % tree_id)
        return data

    def _tree_files(self, tree_id, prefix, out, key):
        data, i = self._tree_object(tree_id), 0
        while i < len(data):
            sp, nul = data.index(b' ', i), data.index(b'\0', i)
            mode, name, oid = data[i:sp].decode(), data[sp + 1:nul].decode('utf-8'), data[nul + 1:nul + 21].hex()
            i = nul + 21
            if mode == '40000':
                self._tree_files(oid, prefix + name + '/', out, key)
            else:
                need(mode in ('100644', '100755'), 'tree %s: non-regular entry %r (mode %s)' % (key, prefix + name, mode))
                out[prefix + name] = oid
        return out

    def tree(self, key):
        """A pinned tree entry {key: (pr, commit, path, tree_id, None)}: returns {relative path: blob id} of every
        regular file below it, after checking that commit:path is the pinned tree object; every tree object read is
        re-hashed against its id."""
        pr, commit, path, tree_id, _ = self.table[key]
        p = _git(self.repo, ['rev-parse', '--verify', '-q', commit + ':' + path])
        need(p.returncode == 0 and p.stdout.decode().strip() == tree_id, 'tree %s is not the pinned tree %s' % (key, tree_id))
        out = self._tree_files(tree_id, '', {}, key)
        self.used[key] = dict(pr=pr, commit=commit, path=path, git_tree=tree_id, files=len(out))
        return out
