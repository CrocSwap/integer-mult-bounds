#!/usr/bin/env python3
"""Cancel queued or running pull-request runs that a newer commit of the same
pull request has superseded.

Runs created before a workflow gained a concurrency group keep their old
definition, so a backlog of superseded runs can only be cleared explicitly.
This script is deliberately narrow:

* only ``pull_request`` runs are candidates; pushes, scheduled and manually
  dispatched runs are never touched;
* a run is superseded only if its head commit is no longer the pull
  request's current head commit (read from the pull request itself, not
  from whichever runs are listed). Runs for the current head (a re-run, a
  label-requested full run) are kept;
* the pull request is identified by number when the API provides it, and
  otherwise (fork pull requests) by looking up the single open pull request
  for the run's head repository and branch; ambiguous or unknown identities
  are skipped;
* a ``--created`` window is required because the API lists at most the
  newest 1000 runs per query.

Everything goes through the GitHub REST API via ``gh``; no pull-request
code is checked out. Dry run by default; pass ``--cancel`` to act.
"""
import argparse
import json
import subprocess
import sys
import urllib.parse


def api(path):
    out = subprocess.run(['gh', 'api', '--paginate', path], check=True, stdout=subprocess.PIPE)
    text = out.stdout.decode()
    decoder = json.JSONDecoder()
    items, pos = [], 0
    while pos < len(text):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text):
            break
        obj, pos = decoder.raw_decode(text, pos)
        items.append(obj)
    return items


def list_runs(repo, status, created):
    runs = []
    for page in api('repos/%s/actions/runs?status=%s&created=%s&per_page=100' % (repo, status, created)):
        runs += page.get('workflow_runs', [])
    return runs


def identify(repo, run, cache):
    """(workflow path, pull request number) or None when not unambiguous."""
    prs = run.get('pull_requests') or []
    if len(prs) == 1:
        return run['path'], prs[0]['number']
    if len(prs) > 1:
        return None
    head_repo = (run.get('head_repository') or {}).get('full_name')
    branch = run.get('head_branch')
    if not head_repo or not branch:
        return None
    key = (head_repo, branch)
    if key not in cache:
        owner = head_repo.split('/')[0]
        found = []
        query = urllib.parse.urlencode({'state': 'open', 'head': owner + ':' + branch, 'per_page': 100})
        for page in api('repos/%s/pulls?%s' % (repo, query)):
            found += [pr for pr in page
                      if (pr.get('head') or {}).get('ref') == branch
                      and ((pr.get('head') or {}).get('repo') or {}).get('full_name') == head_repo]
        cache[key] = found[0]['number'] if len(found) == 1 else None
    number = cache[key]
    return (run['path'], number) if number is not None else None


def current_head(repo, number, cache):
    """The pull request's head commit right now, from the pull request itself
    rather than from whichever runs happen to be listed."""
    if number not in cache:
        pages = api('repos/%s/pulls/%d' % (repo, number))
        cache[number] = pages[0].get('head', {}).get('sha') if pages else None
    return cache[number]


def superseded(runs, identities, heads):
    """Runs to cancel: active runs whose head commit is no longer the pull
    request's head commit."""
    cancel = []
    for run in runs:
        if run['event'] != 'pull_request':
            continue
        identity = identities.get(run['id'])
        if identity is None:
            continue
        head = heads.get(identity[1])
        if head and run['head_sha'] != head:
            cancel.append(run)
    return cancel


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo', required=True, help='owner/name')
    ap.add_argument('--created', required=True,
                    help='GitHub created filter, e.g. 2026-10-14T00:00:00Z..2026-10-14T06:00:00Z (the API lists '
                         'at most the newest 1000 runs per query, so use windows for a deep backlog)')
    ap.add_argument('--workflow', action='append', default=[],
                    help='workflow file name to consider (repeatable); default: every workflow')
    ap.add_argument('--cancel', action='store_true', help='actually cancel (default: report only)')
    ap.add_argument('--limit', type=int, default=0, help='cancel at most this many runs (0 = no limit)')
    args = ap.parse_args(argv)
    if args.limit < 0:
        ap.error('--limit must be nonnegative')

    runs = []
    for status in ('queued', 'in_progress', 'waiting', 'pending'):
        runs += list_runs(args.repo, status, args.created)
    if args.workflow:
        wanted = set(args.workflow)
        runs = [r for r in runs if r['path'].rsplit('/', 1)[-1] in wanted]
    seen, unique = set(), []
    for run in runs:
        if run['id'] not in seen and run['event'] == 'pull_request':
            seen.add(run['id']); unique.append(run)
    cache, identities, unidentified, heads = {}, {}, 0, {}
    for run in unique:
        identity = identify(args.repo, run, cache)
        if identity is None:
            unidentified += 1
        else:
            identities[run['id']] = identity
    head_cache = {}
    for identity in set(identities.values()):
        heads[identity[1]] = current_head(args.repo, identity[1], head_cache)
    targets = superseded(unique, identities, heads)
    if args.limit:
        targets = targets[:args.limit]
    print('pull-request runs considered: %d; without an unambiguous pull request (kept): %d; superseded: %d'
          % (len(unique), unidentified, len(targets)))
    for number, head in sorted(heads.items()):
        if head is None:
            print('pull request #%d: current head unknown; its runs are kept' % number)
    failed = []
    for run in targets:
        print('%s run %d %s PR #%d head %s created %s (%s)' % (
            'CANCEL' if args.cancel else 'would cancel', run['id'], run['path'].rsplit('/', 1)[-1],
            identities[run['id']][1], run['head_sha'][:8], run['created_at'], run['status']))
        if args.cancel:
            result = subprocess.run(
                ['gh', 'api', '-X', 'POST', 'repos/%s/actions/runs/%d/cancel' % (args.repo, run['id'])],
                check=False, stdout=subprocess.DEVNULL)
            if result.returncode:
                failed.append(run['id'])
    if failed:
        print('Cancellation failed for run(s): ' + ', '.join(map(str, failed)), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
