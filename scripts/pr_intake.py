#!/usr/bin/env python3
"""Plan delta-only maintainer intake. Never execute PR code or mutate GitHub."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = 'CrocSwap/integer-mult-bounds'
STATE = ROOT / 'docs/research/pr-intake-state.json'
POLICY_VERSION = 1
STATUSES = {'pending_review', 'ready_to_integrate', 'waiting_revision', 'deferred_replay'}
SHA = re.compile(r'[0-9a-f]{40}')


def command(argv):
    return subprocess.check_output(argv, cwd=ROOT, text=True)


def validate_state(state):
    if state.get('schema_version') != 1:
        raise ValueError('unsupported intake state schema')
    seen = set()
    for row in state['pull_requests']:
        n = row['number']
        if not isinstance(n, int) or n <= 0 or n in seen:
            raise ValueError('invalid or duplicate PR number')
        seen.add(n)
        if not SHA.fullmatch(row['head']) or row['status'] not in STATUSES:
            raise ValueError(f'invalid state for PR {n}')
        if not row['reason'] or not row['evidence']:
            raise ValueError(f'missing reason/evidence for PR {n}')
        if not isinstance(row['watch_paths'], dict) or not isinstance(row['watch_prs'], dict):
            raise ValueError(f'invalid wake dependencies for PR {n}')
        for p in row['watch_paths']:
            if Path(p).is_absolute() or '..' in Path(p).parts:
                raise ValueError('watch paths must be repository relative')


def plan(state, live, tree, wake=(), limit=100):
    """Unchanged waits are dormant; unfinished review remains visible and actionable."""
    validate_state(state)
    if not 1 <= limit <= 100:
        raise ValueError('review chunks must contain between 1 and 100 decisions')
    previous = {r['number']: r for r in state['pull_requests']}
    current = {r['number']: r for r in live}
    if len(current) != len(live):
        raise ValueError('duplicate PR in live snapshot')
    rows = []
    for n, pr in sorted(current.items()):
        if not SHA.fullmatch(pr['headRefOid']):
            raise ValueError(f'invalid live head for PR {n}')
        old = previous.get(n)
        changes = []
        if old:
            if old['head'] != pr['headRefOid']:
                changes.append('head changed')
            if old.get('policy_version') != POLICY_VERSION:
                changes.append('intake policy changed')
            changes += [f'main path changed: {p}' for p, oid in old['watch_paths'].items()
                        if tree.get(p) != oid]
            changes += [f'dependency PR changed/left open queue: {p}'
                        for p, oid in old['watch_prs'].items()
                        if current.get(int(p), {}).get('headRefOid') != oid]
        if pr['isDraft']:
            lane = 'draft'
        elif n in wake:
            lane = 'reactivated'
            changes.append('explicit maintainer wake')
        elif not old:
            lane = 'new'
        elif changes:
            lane = 'reactivated'
        elif old['status'] in ('waiting_revision', 'deferred_replay'):
            lane = old['status']
        else:
            lane = old['status']
        rows.append(dict(number=n, head=pr['headRefOid'], title=pr['title'], lane=lane,
                         changes=changes, reason=old['reason'] if old else 'No cached intake decision.',
                         evidence=old['evidence'] if old else []))
    priorities = {'ready_to_integrate': 0, 'reactivated': 1, 'new': 2, 'pending_review': 3}
    actionable = sorted((r for r in rows if r['lane'] in priorities),
                        key=lambda r: (priorities[r['lane']], r['number']))
    return dict(schema_version=1, policy_version=POLICY_VERSION,
                scope='Scheduling only. No approval, scientific validation, merge or closure.',
                counts=dict(Counter(r['lane'] for r in rows)), open_count=len(rows),
                actionable_count=len(actionable), selected=actionable[:limit],
                remaining_actionable=len(actionable[limit:]), pull_requests=rows,
                no_longer_open=sorted(set(previous) - set(current)))


def tree_at(base):
    # One Git traversal, not one process per file or PR. Includes directory IDs.
    raw = subprocess.check_output(['git', 'ls-tree', '-r', '-t', '-z', base], cwd=ROOT)
    result = {}
    for item in raw.split(b'\0'):
        if item:
            metadata, path = item.split(b'\t', 1)
            result[path.decode()] = metadata.decode().split()[2]
    return result


def fetch_live():
    fields = 'number,title,headRefOid,isDraft,url,author'
    data = json.loads(command(['gh', 'pr', 'list', '--repo', REPO, '--state', 'open',
                               '--limit', '10000', '--json', fields]))
    if len(data) >= 10000:
        raise ValueError('live query reached its cap; paginate before planning')
    return data


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'record'])
    parser.add_argument('--state', type=Path, default=STATE)
    parser.add_argument('--base', default='origin/main')
    parser.add_argument('--live-json', type=Path, help='Offline/reused snapshot; no freshness implied')
    parser.add_argument('--refresh', action='store_true', help='Fetch canonical main before live read')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--limit', type=int, default=100)
    parser.add_argument('--wake', type=int, action='append', default=[])
    parser.add_argument('--number', type=int)
    parser.add_argument('--head', help='Required reviewed head when recording; must match live')
    parser.add_argument('--status', choices=sorted(STATUSES))
    parser.add_argument('--reason')
    parser.add_argument('--evidence', action='append', default=[])
    parser.add_argument('--watch-path', action='append', default=[])
    parser.add_argument('--watch-pr', type=int, action='append', default=[])
    args = parser.parse_args()
    if args.refresh and args.live_json:
        parser.error('--refresh cannot imply freshness for an offline snapshot')
    if args.refresh:
        command(['git', 'fetch', '--no-tags', 'https://github.com/' + REPO + '.git',
                 '+refs/heads/main:refs/remotes/origin/main'])
    state = json.loads(args.state.read_text())
    validate_state(state)
    live = json.loads(args.live_json.read_text()) if args.live_json else fetch_live()
    base = command(['git', 'rev-parse', args.base]).strip()
    tree = tree_at(base)
    if args.action == 'plan':
        if not args.output:
            parser.error('plan requires --output (outside the repository is recommended)')
        result = plan(state, live, tree, args.wake, args.limit)
        result.update(base=base, observed_at=datetime.now(timezone.utc).isoformat(),
                      live_source='offline snapshot' if args.live_json else 'GitHub open PR query',
                      live=live)
        dump(args.output, result)
        print(json.dumps({k: result[k] for k in ('counts', 'open_count', 'actionable_count',
                                                'remaining_actionable')}))
        print('Selected: ' + ', '.join('#' + str(r['number']) for r in result['selected']))
        return
    if not all((args.number, args.head, args.status, args.reason, args.evidence)):
        parser.error('record requires --number, --head, --status, --reason, --evidence')
    current = {r['number']: r for r in live}
    if current.get(args.number, {}).get('headRefOid') != args.head:
        parser.error('review head does not match snapshot; do not cache stale review')
    for p in args.watch_path + [e for e in args.evidence if not e.startswith('https://')]:
        if Path(p).is_absolute() or '..' in Path(p).parts:
            parser.error('evidence/watch paths must be repository relative')
    paths = sorted(set(args.watch_path + [e for e in args.evidence if not e.startswith('https://')]))
    for p in paths:
        if p not in tree:
            parser.error('watched source missing at base: ' + p)
    for n in args.watch_pr:
        if n not in current:
            parser.error('watched PR is not open: ' + str(n))
    row = dict(number=args.number, head=args.head, status=args.status, reason=args.reason,
               evidence=args.evidence, policy_version=POLICY_VERSION, baseline=base,
               watch_paths={p: tree[p] for p in paths},
               watch_prs={str(n): current[n]['headRefOid'] for n in args.watch_pr})
    state['pull_requests'] = sorted([r for r in state['pull_requests'] if r['number'] != args.number]
                                   + [row], key=lambda r: r['number'])
    validate_state(state)
    dump(args.state, state)
    print(f'Recorded scheduling state for #{args.number}; ledger/approval unchanged.')


if __name__ == '__main__':
    main()
