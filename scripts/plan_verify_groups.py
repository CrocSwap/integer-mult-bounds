#!/usr/bin/env python3
"""Select which verification groups a CI run must execute.

The artifact workflow (.github/workflows/verify.yml) verifies 16 Makefile
groups on three Python versions plus the ranked-pair finite replay and the
formal Lean packages. Running all of that for every pull-request revision is
what saturates the shared runners: most revisions only add a new
``research/<package>/`` directory that no group reads.

This planner keeps every check for anything that can affect it, and skips a
group only when the run's changed paths provably cannot reach it:

* ``.github/verify-groups.json`` declares each group's inputs as exact paths
  or ``dir/**`` prefixes. The declaration is recorded and checked by
  ``scripts/trace_verify_inputs.py``; it is not a guess.
* Any changed path in the manifest's ``all`` list (Makefile, ``scripts/**``,
  the workflow, the manifest itself, the root Git attribute and ignore
  files) runs everything; a nested ``.gitattributes`` or ``.gitignore``
  counts as a change to every path under its directory.
* A changed path that matches no group and is not in ``skip_safe`` is
  *unclassified* and also runs everything. Silence must be declared.
* ``schedule`` and ``workflow_dispatch`` runs, a diff that cannot be computed,
  and pull requests carrying the ``full_label`` label always run everything.

Selected groups keep all Python versions. Every job then runs its commands
under scripts/trace_verify_inputs.py, which fails on inputs the manifest does
not declare, so the declarations are re-validated by every run.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / '.github/verify-groups.json'
ZERO_SHA = '0' * 40
FULL_EVENTS = ('schedule', 'workflow_dispatch')
CLASSES = ('all', 'group', 'skip_safe', 'unclassified')


ANY_ANCESTOR = object()


def directories_changed_by(path, status, base_dirs=None, head_dirs=None):
    """Directories that an added or deleted ``path`` creates or removes: the
    ancestors absent from the base tree (addition) or from the head tree
    (deletion). ANY_ANCESTOR without tree information; None for edits."""
    if status == 'M':
        return None
    dirs = base_dirs if status == 'A' else head_dirs
    if dirs is None:
        return ANY_ANCESTOR
    changed, parent = set(), path
    while '/' in parent:
        parent = parent.rsplit('/', 1)[0]
        if parent not in dirs:
            changed.add(parent)
    return changed


def listing_changed_by(path, status, base_dirs=None, head_dirs=None):
    """Which directory's listing an added or deleted ``path`` changes.

    Adding ``a/b/c.txt`` changes the listing of the deepest ancestor that
    already existed in the base tree (``a`` if ``a/b`` is new, else ``a/b``).
    Deleting changes the listing of the deepest ancestor that still exists
    afterwards. Without tree information, return ANY_ANCESTOR: every ancestor
    listing is then treated as changed (conservative). ``''`` is the root.
    """
    if status == 'M':
        return None
    dirs = base_dirs if status == 'A' else head_dirs
    if dirs is None:
        return ANY_ANCESTOR
    parent = path
    while '/' in parent:
        parent = parent.rsplit('/', 1)[0]
        if parent in dirs:
            return parent
    return ''


def pattern_matches(pattern, path, status='A', listing=ANY_ANCESTOR, created=ANY_ANCESTOR):
    """Does a change of ``status`` (A, M or D as in git diff --name-status) to
    ``path`` match ``pattern``?

    * exact path: any status;
    * ``dir/**`` (``**`` for everything): any status at or below ``dir``;
    * ``dir/*`` (``*`` for the repository root): the group only listed the
      directory, so the change matters only if it adds or removes an entry
      of that directory; ``listing`` names the directory whose listing the
      change alters (see listing_changed_by), or ANY_ANCESTOR when unknown;
    * ``dir/``: the group only checked that the directory exists, so the
      change matters only if it creates or removes that directory;
      ``created`` is the set of directories the change creates or removes
      (see directories_changed_by), or ANY_ANCESTOR when unknown.
    """
    if pattern == '**':
        return True
    if pattern.endswith('/**'):
        prefix = pattern[:-3]
        return path == prefix or path.startswith(prefix + '/')
    if pattern == '*' or pattern.endswith('/*'):
        if status == 'M' or listing is None:
            return False
        directory = '' if pattern == '*' else pattern[:-2]
        if listing is ANY_ANCESTOR or created is ANY_ANCESTOR:
            return directory == '' or path.startswith(directory + '/')
        # The directory whose listing gains or loses an entry, or a directory
        # that the change creates or removes outright (a group that listed it
        # will now find it missing, or newly present).
        return listing == directory or (created is not None and directory in created)
    if pattern.endswith('/'):
        if status == 'M' or created is None:
            return False
        directory = pattern[:-1]
        if created is ANY_ANCESTOR:
            return path.startswith(directory + '/')
        return directory in created
    return pattern == path


def validate_pattern(pattern):
    if not isinstance(pattern, str) or not pattern or pattern.startswith('/') or '\\' in pattern:
        raise ValueError('Bad manifest pattern: ' + repr(pattern))
    if pattern in ('*', '**'):
        return
    body = (pattern[:-3] if pattern.endswith('/**') else pattern[:-2] if pattern.endswith('/*')
            else pattern[:-1] if pattern.endswith('/') else pattern)
    if '*' in body or not body or '..' in body.split('/') or body.endswith('/'):
        raise ValueError('Only exact paths, dir/, dir/* or dir/** are allowed: ' + pattern)


def load_manifest(path=MANIFEST):
    manifest = json.loads(Path(path).read_text(encoding='utf-8'))
    for key in ('python', 'full_label', 'all', 'skip_safe', 'groups'):
        if key not in manifest:
            raise ValueError('Manifest lacks ' + key)
    for pattern in list(manifest['all']) + list(manifest['skip_safe']):
        validate_pattern(pattern)
    for group, spec in manifest['groups'].items():
        if not isinstance(spec.get('paths'), list):
            raise ValueError('Group ' + group + ' needs a paths list')
        for pattern in spec['paths']:
            validate_pattern(pattern)
        job = spec.get('job', 'verify')
        if job not in ('verify', 'ranked-pair-finite', 'formal', 'package'):
            raise ValueError('Group ' + group + ' has unknown job ' + job)
        if job in ('formal', 'package') and not spec.get('package'):
            raise ValueError('Group ' + group + ' needs a package name')
        if job == 'package' and not spec.get('command'):
            raise ValueError('Group ' + group + ' needs a command')
    return manifest


GIT_CONFIG_NAMES = ('.gitattributes', '.gitignore')


def subtree_matches(pattern, directory):
    """Could ``pattern`` match some path at or below ``directory``? Used for
    a nested .gitattributes or .gitignore, whose effect (checkout bytes,
    git's view of untracked files) covers everything under its directory."""
    if pattern == '**' or pattern == '*':
        return True
    body = pattern[:-3] if pattern.endswith('/**') else pattern[:-2] if pattern.endswith('/*') else (
        pattern[:-1] if pattern.endswith('/') else pattern)
    return body == directory or body.startswith(directory + '/') or (
        pattern.endswith('/**') and directory.startswith(body + '/'))


def specific(pattern):
    """Patterns that say something about a particular path. A whole-tree ``**``
    selects its group but does not establish that an otherwise unknown path
    is understood. A listing pattern does: it only ever matches an added or
    removed entry, which no group could have read before (probes and
    listings are recorded), and a removed entry some group did read is also
    covered by that group's exact or ``dir/**`` pattern."""
    return pattern != '**'


def classify(manifest, path, status='A', listing=ANY_ANCESTOR, ignored=False, created=ANY_ANCESTOR):
    """Return (class, groups) for one changed path with its git status letter.

    ``groups`` are every group whose patterns match (they all run). The
    class says whether the path is understood: ``all`` runs everything,
    ``group`` means a specific declared input matched, ``skip_safe`` means
    the path is declared inert, ``unclassified`` means nobody declared it and
    the planner must run everything."""
    name = path.rsplit('/', 1)[-1]
    if name == '.gitmodules' or (name in GIT_CONFIG_NAMES and '/' not in path):
        return 'all', []  # the root attribute and ignore files change checkout bytes and git views everywhere
    if name in GIT_CONFIG_NAMES:
        # A nested one affects every path under its directory: treat the
        # change as touching all of them, with any status.
        directory = path.rsplit('/', 1)[0]
        if any(subtree_matches(p, directory) for p in manifest['all']):
            return 'all', []
        groups = [g for g, spec in manifest['groups'].items()
                  if any(subtree_matches(p, directory) for p in spec['paths'])]
        explained = any(subtree_matches(p, directory) for g, spec in manifest['groups'].items()
                        for p in spec['paths'] if specific(p))
        if explained:
            return 'group', groups
        if any(subtree_matches(p, directory) for p in manifest['skip_safe']):
            return 'skip_safe', groups
        return 'unclassified', groups
    if ignored:
        return 'all', []  # a tracked path that .gitignore would ignore is never a declared input
    if listing == '' or (listing is ANY_ANCESTOR and '/' not in path):
        # A new or removed entry directly at the repository root: make, the
        # import system and compilers probe root names, and the tracer does
        # not record root-level probes, so this always verifies everything.
        return 'all', []
    if any(pattern_matches(p, path, status, listing, created) for p in manifest['all']):
        return 'all', []
    groups = [g for g, spec in manifest['groups'].items()
              if any(pattern_matches(p, path, status, listing, created) for p in spec['paths'])]
    explained = any(pattern_matches(p, path, status, listing, created) for g, spec in manifest['groups'].items()
                    for p in spec['paths'] if specific(p))
    if explained:
        return 'group', groups
    if any(pattern_matches(p, path, status, listing, created) for p in manifest['skip_safe']):
        return 'skip_safe', groups
    return 'unclassified', groups


def split_status(item):
    """``A:path`` / ``M:path`` / ``D:path``; a bare path is treated as added (the
    most conservative status, since it also matches listing patterns)."""
    if len(item) > 2 and item[1] == ':' and item[0] in 'AMD':
        return item[0], item[2:]
    return 'A', item


def plan(manifest, event, changed=None, action=None, label=None, labels=(), diff_error=None,
         force_full=False, base_dirs=None, head_dirs=None, ignored=()):
    """Decide the run. Returns a dict with mode, reason, groups, jobs and the classification.

    ``base_dirs``/``head_dirs`` are the directory sets of the two trees; without
    them, listing patterns are matched conservatively at every ancestor."""
    full_label = manifest['full_label']
    classification = []
    mode, reason = None, None
    if force_full:
        mode, reason = 'full', 'full run requested'
    elif event in FULL_EVENTS:
        mode, reason = 'full', event + ' runs always verify everything'
    elif event == 'pull_request' and action == 'labeled' and label == full_label:
        mode, reason = 'full', 'label ' + full_label + ' requests the full matrix'
    # Other label events must follow the ordinary plan, including any existing
    # full label. An empty successful run would publish the same summary check
    # as a real verification run without establishing its result.
    elif full_label in labels:
        mode, reason = 'full', 'pull request carries ' + full_label
    elif diff_error:
        mode, reason = 'full', 'changed paths unavailable: ' + diff_error
    elif event not in ('pull_request', 'push'):
        mode, reason = 'full', 'unexpected event ' + str(event)
    elif changed is None:
        mode, reason = 'full', 'changed paths were not provided'
    else:
        selected = []
        full_reasons = []
        for item in sorted(set(changed or [])):
            status, path = split_status(item)
            listing = listing_changed_by(path, status, base_dirs, head_dirs)
            created = directories_changed_by(path, status, base_dirs, head_dirs)
            kind, groups = classify(manifest, path, status, listing, path in ignored, created)
            classification.append((status + ':' + path, kind, groups))
            if kind == 'all':
                full_reasons.append(path + ' affects every group')
            elif kind == 'unclassified':
                full_reasons.append(path + ' is not declared as an input or as inert')
            elif kind == 'symlink':
                full_reasons.append(path + ' is or was a symbolic link')
            for g in groups:
                if g not in selected:
                    selected.append(g)
        if full_reasons:
            mode, reason = 'full', '; '.join(full_reasons[:5])
        elif selected:
            mode, reason = 'selected', 'changed paths reach %d group(s)' % len(selected)
        else:
            mode, reason = 'none', 'no changed path is an input of any verification group'
    order = list(manifest['groups'])
    if mode == 'full':
        groups = order
    elif mode == 'selected':
        groups = [g for g in order if g in selected]
    else:
        groups = []
    specs = manifest['groups']
    job_of = lambda g: specs[g].get('job', 'verify')
    matrix_groups = [g for g in groups if job_of(g) == 'verify']
    jobs = sorted({job_of(g) for g in groups} - {'verify'})
    include = [{'python-version': v, 'group': g} for g in matrix_groups for v in manifest['python']]
    formal = [{'package': specs[g]['package']} for g in groups if job_of(g) == 'formal']
    packages = [{'python-version': v, 'package': specs[g]['package'], 'command': specs[g]['command'],
                 'artifact': specs[g].get('artifact', '')}
                for g in groups if job_of(g) == 'package' for v in specs[g].get('python', manifest['python'])]
    return {
        'mode': mode, 'reason': reason, 'groups': groups, 'matrix_groups': matrix_groups,
        'jobs': jobs, 'include': include, 'formal': formal, 'packages': packages,
        'classification': classification,
    }


SYMLINK_MODE = '120000'
GITLINK_MODE = '160000'


def git_changed(base, head='HEAD', cwd=ROOT):
    """``STATUS:path`` for every path changed between two commits, plus the
    set of paths that are or were symbolic links or submodule pointers.
    Renames and copies are reported as a delete plus an add; type changes
    count as both."""
    if base == ZERO_SHA:
        raise ValueError('base is the all-zero SHA (new branch or force push)')
    out = subprocess.run(['git', 'diff', '--no-renames', '--raw', '-z', base, head], cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if out.returncode != 0:
        raise ValueError(out.stderr.decode(errors='replace').strip() or 'git diff failed')
    fields = out.stdout.decode().split('\0')
    changed, links = [], set()
    i = 0
    while i + 1 < len(fields) and fields[i]:
        meta, path = fields[i], fields[i + 1]
        i += 2
        parts = meta.lstrip(':').split()  # src_mode dst_mode src_sha dst_sha status
        if len(parts) < 5:
            raise ValueError('unexpected git diff --raw record: ' + meta)
        status = parts[4][0]
        if SYMLINK_MODE in (parts[0], parts[1]) or GITLINK_MODE in (parts[0], parts[1]):
            links.add(path)  # symbolic links and submodule pointers always verify everything
        if status in ('A', 'M', 'D'):
            changed.append(status + ':' + path)
        else:  # T (type change), U, X or anything unexpected: treat as add + delete
            changed += ['A:' + path, 'D:' + path]
    return changed, links


def git_ignored(paths, cwd=ROOT):
    """Paths among ``paths`` that .gitignore rules would ignore."""
    if not paths:
        return set()
    out = subprocess.run(['git', 'check-ignore', '-z', '--stdin', '--no-index'], cwd=cwd,
                         input='\0'.join(paths).encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if out.returncode not in (0, 1):
        raise ValueError(out.stderr.decode(errors='replace').strip() or 'git check-ignore failed')
    return set(p for p in out.stdout.decode().split('\0') if p)


def git_dirs(rev, cwd=ROOT):
    """Every directory of a tree, as paths relative to the root."""
    out = subprocess.run(['git', 'ls-tree', '-r', '-d', '--name-only', '-z', rev], cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if out.returncode != 0:
        raise ValueError(out.stderr.decode(errors='replace').strip() or 'git ls-tree failed')
    return set(p for p in out.stdout.decode().split('\0') if p)


def summary_markdown(result, event):
    lines = ['## Verification plan', '',
             '- Event: `%s`' % event, '- Mode: **%s**' % result['mode'], '- Reason: %s' % result['reason']]
    if result['groups']:
        lines.append('- Groups: ' + ', '.join('`%s`' % g for g in result['groups']))
    if result['jobs']:
        lines.append('- Extra jobs: ' + ', '.join('`%s`' % j for j in result['jobs']))
    lines.append('- Matrix jobs: %d verify, %d formal, %d package' % (
        len(result['include']), len(result['formal']), len(result['packages'])))
    if result['classification']:
        lines += ['', '| Changed path | Class | Groups |', '|---|---|---|']
        for path, kind, groups in result['classification'][:300]:
            lines.append('| `%s` | %s | %s |' % (path, kind, ', '.join(groups)))
        if len(result['classification']) > 300:
            lines.append('| … %d more | | |' % (len(result['classification']) - 300))
    return '\n'.join(lines) + '\n'


def write_outputs(result, path):
    with open(path, 'a', encoding='utf-8') as out:
        out.write('matrix=' + json.dumps({'include': result['include']}, separators=(',', ':')) + '\n')
        out.write('count=%d\n' % len(result['include']))
        out.write('formal=' + json.dumps({'include': result['formal']}, separators=(',', ':')) + '\n')
        out.write('formal_count=%d\n' % len(result['formal']))
        out.write('packages=' + json.dumps({'include': result['packages']}, separators=(',', ':')) + '\n')
        out.write('package_count=%d\n' % len(result['packages']))
        out.write('groups=' + ','.join(result['groups']) + '\n')
        out.write('jobs=' + ','.join(result['jobs']) + '\n')
        out.write('mode=' + result['mode'] + '\n')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--manifest', type=Path, default=MANIFEST)
    ap.add_argument('--event', required=True, help='GitHub event name')
    ap.add_argument('--action', default=None, help='GitHub event action, e.g. labeled')
    ap.add_argument('--label', default=None, help='label name for labeled events')
    ap.add_argument('--labels', default='[]', help='JSON list of the pull request labels')
    ap.add_argument('--diff', nargs=2, metavar=('BASE', 'HEAD'), help='compute changed paths with git')
    ap.add_argument('--changed', nargs='*', help='changed paths (instead of --diff)')
    ap.add_argument('--full', action='store_true', help='force the full matrix')
    ap.add_argument('--github-output', type=Path)
    ap.add_argument('--summary', type=Path, help='append a Markdown summary (e.g. $GITHUB_STEP_SUMMARY)')
    args = ap.parse_args(argv)

    manifest = load_manifest(args.manifest)
    changed, diff_error, base_dirs, head_dirs, ignored = args.changed, None, None, None, set()
    if args.diff:
        try:
            changed, links = git_changed(args.diff[0], args.diff[1])
            if links:
                diff_error = 'symbolic links or submodules changed: ' + ', '.join(sorted(links)[:5])
            base_dirs, head_dirs = git_dirs(args.diff[0]), git_dirs(args.diff[1])
            ignored = git_ignored([split_status(c)[1] for c in changed])
        except ValueError as error:
            changed, diff_error = None, str(error)
    labels = json.loads(args.labels) if args.labels else None
    result = plan(manifest, args.event, changed, action=args.action or None, label=args.label or None,
                  labels=labels if isinstance(labels, list) else [], diff_error=diff_error,
                  force_full=args.full, base_dirs=base_dirs, head_dirs=head_dirs, ignored=ignored)
    print('PLAN mode=%s groups=%d verify_jobs=%d formal_jobs=%d package_jobs=%d extra=%s reason=%s' % (
        result['mode'], len(result['groups']), len(result['include']), len(result['formal']),
        len(result['packages']), ','.join(result['jobs']) or '-', result['reason']))
    for path, kind, groups in result['classification']:
        print('  %-12s %s%s' % (kind, path, (' -> ' + ','.join(groups)) if groups else ''))
    if args.github_output:
        write_outputs(result, args.github_output)
    if args.summary:
        with open(args.summary, 'a', encoding='utf-8') as out:
            out.write(summary_markdown(result, args.event))
    return 0


if __name__ == '__main__':
    sys.exit(main())
