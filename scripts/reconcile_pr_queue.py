#!/usr/bin/env python3
"""Build a review index from pinned historical records; never mutate GitHub.

The starting snapshot stays fixed. Explicit decisions can record later publication
and closure, but historical queue inclusion alone is never a completed review.
"""
import collections
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'research/pr-reconciliation-20261012'


def read(path):
    return json.loads((ROOT / path).read_text())


def build():
    snapshot = read(AUDIT.relative_to(ROOT) / 'starting-snapshot.json')
    rows = {}
    sources = {}

    def load(path):
        p = ROOT / path
        sources[path] = hashlib.sha256(p.read_bytes()).hexdigest()
        return json.loads(p.read_text())

    def add(number, head, evidence, scope, kind='review'):
        if not re.fullmatch('[0-9a-f]{40}', head or ''):
            return
        item = dict(head=head, evidence=evidence, scope=scope, kind=kind)
        history = rows.setdefault(int(number), [])
        if item not in history:
            history.append(item)

    for name in ('community-followup-validation.json', 'community-round2-validation.json',
                 'community-round3-validation.json', 'community-round4-validation.json',
                 'community-round5-validation.json', 'community-round6-validation.json'):
        path = 'docs/research/' + name
        d = load(path)
        for key in ('reviewed_heads', 'reviewed_construction_heads'):
            for number, head in d.get(key, {}).items():
                if isinstance(head, str):
                    add(number, head, path, d.get('scope', 'Scoped historical review; see receipt for limitations.'))
        for number, obj in d.get('pull_requests', {}).items():
            add(number, obj.get('head'), path, obj.get('disposition', d.get('scope', 'Scoped historical review.')))
        for key, obj in d.items():
            if re.fullmatch('pr[0-9]+', key) and isinstance(obj, dict):
                add(key[2:], obj.get('head', obj.get('commit')), path,
                    obj.get('disposition', d.get('scope', 'Scoped historical checks; consult receipt.')))

    path = 'research/overnight-pr-review-20261009/dispositions.json'
    for obj in load(path):
        # These rows distinguish triage from execution. Preserve that distinction.
        add(obj['number'], obj.get('head'), path,
            obj.get('disposition', '') + ': ' + obj.get('reason', ''), 'triage_or_review')
    path = 'research/community-round8-audit/validation.json'
    d = load(path)
    for number, obj in d['heads'].items():
        add(number, obj['head'], path, d['local'].get('pr' + number, 'Dependency review; consult scoped receipt.'))
    path = 'research/community-round9-audit/review-ledger.json'
    for obj in load(path)['prs']:
        if obj['disposition'] == 'prior-snapshot-scope-only':
            continue
        add(obj['number'], obj.get('head'), path,
            obj['disposition'] + ': ' + obj.get('review_note', ''), 'review')
    path = 'docs/research/community-pr210-integration.json'
    d = load(path)
    add(210, d['source_head'], path, d['status'], 'integration')
    path = 'docs/research/community-pr279-integration.json'
    d = load(path)
    for number, head in d['source_prs'].items():
        add(number, head, path, d['scope'], 'integration')
    path = 'docs/research/research-notes-20261011.json'
    for obj in load(path)['prs']:
        add(obj['number'], obj['source_head'], path, obj['scope'], 'integration')
    path = 'docs/research/community-pr531-integration.json'
    d = load(path)
    for number, head in d['reviewed_heads'].items():
        add(number, head, path, d['scope'], 'integration')

    path = 'docs/research/community-formal-20261012-integration.json'
    if (ROOT / path).exists():
        d = load(path)
        for number, head in d['reviewed_heads'].items():
            add(number, head, path, d['checks'].get('pr' + number, 'Scoped dependency replay; see receipt.'), 'integration')

    # Markdown links locate older context, without upgrading a mention to an audit.
    mentions = collections.defaultdict(list)
    for p in sorted((ROOT / 'docs/research').glob('*.md')):
        if p.name == 'pr-ledger.md':
            continue
        text = p.read_text()
        for number in set(re.findall(r'(?:pull/|\bPR\s*#?|#)([0-9]+)\b', text)):
            mentions[int(number)].append(str(p.relative_to(ROOT)))

    decisions = load('research/pr-reconciliation-20261012/decisions.json')['decisions']
    ending_path = 'research/pr-reconciliation-20261012/ending-snapshot.json'
    ending = load(ending_path) if (ROOT / ending_path).exists() else None
    live = {p['number']: p for p in ending['open_pull_requests']} if ending else {}
    active = {442, 484, 509, 516, 520}
    result = []
    for pr in sorted(snapshot['pull_requests'], key=lambda x: x['number']):
        n = pr['number']
        history = rows.get(n, [])
        exact = [h for h in history if h['head'] == pr['headRefOid']]
        if exact:
            status = 'partially_reviewed'
            question = 'Historical scoped review exists; establish full current-content coverage and disposition before closure.'
        elif history:
            status = 'changed_since_review'
            question = 'Review the changes between the recorded historical head(s) and the current head; old evidence does not approve those changes.'
        else:
            status = 'unreviewed'
            question = 'No exact-head substantive review established by the indexed records; inspect the contribution and its dependencies.'
        if n in active:
            status = 'partially_reviewed'
            question = 'Finish the active formalization/construction/tooling batch and publish its scoped evidence.'
        item = dict(number=n, url=pr['url'], title=pr['title'], contributor=pr['author'],
                    draft=pr['isDraft'], starting_head=pr['headRefOid'], current_head=pr['headRefOid'],
                    previously_reviewed_heads=sorted({h['head'] for h in history if h['kind'] != 'triage_or_review'}),
                    historical_assessment_heads=sorted({h['head'] for h in history}),
                    evidence=history, historical_mentions=mentions.get(n, []),
                    disposition=status, integration_location=[], github_state='OPEN',
                    unresolved_question=question, closure=None)
        if str(n) in decisions:
            decision = decisions[str(n)]
            if decision.get('starting_head') != pr['headRefOid']:
                raise ValueError(f'#{n}: decision belongs to a different starting head')
            item.update(decision)
        if n in live:
            item['current_head'] = live[n]['headRefOid']
            item['github_state'] = 'OPEN'
            item['current_head_observed_in'] = ending_path
            if item['current_head'] != item['starting_head']:
                item['changed_during_round'] = True
                item['unresolved_question'] = ('The head changed during reconciliation. Review current head '
                    + item['current_head'] + '; earlier metadata/source inspection does not establish coverage of this update.')
                if history:
                    item['disposition'] = 'changed_since_review'
        elif item.get('closure'):
            item['current_head_observed_in'] = 'research/pr-reconciliation-20261012/closure-receipts.json'
        result.append(item)
    if len(result) != len({p['number'] for p in result}):
        raise ValueError('Duplicate PR in starting snapshot')
    if set(map(int, decisions)) - {p['number'] for p in result}:
        raise ValueError('Decision outside the fixed snapshot')
    # Later family rounds extend the inventory without rewriting the original
    # 446-PR snapshot or changing an original row's starting head/attribution.
    family_paths = [p for p in (
        'research/community-family533-audit/DISPOSITIONS.json',
        'research/community-family588-audit/DISPOSITIONS.json',
        'research/community-hyperplane599-audit/DISPOSITIONS.json',
        'research/community-cold617-audit/DISPOSITIONS.json',
        'research/community-k492-audit/DISPOSITIONS.json',
        'research/community-frontier741-audit/DISPOSITIONS.json',
        'research/community-frontier799-audit/DISPOSITIONS.json',
    ) if (ROOT / p).exists()]
    family_path = family_paths[-1] if family_paths else None
    for family_path in family_paths:
        family = load(family_path)
        indexed = {p['number']: p for p in result}
        for decision in family['pull_requests']:
            n = decision['number']
            if n not in indexed:
                pr = decision['metadata']
                item = dict(number=n, url=f'https://github.com/CrocSwap/integer-mult-bounds/pull/{n}',
                            title=pr['title'], contributor=pr['author'], draft=pr['isDraft'],
                            starting_head=pr['headRefOid'], current_head=pr['headRefOid'],
                            previously_reviewed_heads=[], historical_assessment_heads=[], evidence=[],
                            historical_mentions=[], integration_location=[], github_state='OPEN', closure=None)
                result.append(item)
                indexed[n] = item
            item = indexed[n]
            for key in ('reviewed_head', 'current_head', 'disposition', 'integration_location', 'github_state',
                        'unresolved_question', 'closure', 'review_completion', 'verification_evidence'):
                if key in decision:
                    item[key] = decision[key]
            item['current_head_observed_in'] = family_path
            item['reconciliation_evidence'] = list(dict.fromkeys(item.get('reconciliation_evidence', []) + [family_path]))
            item['evidence'].append(dict(head=decision['reviewed_head'], evidence=family_path,
                                         scope=decision['scope'], kind='integration_or_partial_review'))
        result.sort(key=lambda p: p['number'])
    counts = dict(sorted(collections.Counter(p['disposition'] for p in result).items()))
    output = dict(schema_version=1, snapshot='research/pr-reconciliation-20261012/starting-snapshot.json',
                  starting_main=snapshot['published_main'], starting_open_count=len(snapshot['pull_requests']),
                  inventory_count=len(result), family_round=family_path,
                  family_rounds=family_paths,
                  counts=counts, source_sha256=sources,
                  scope='Reconciliation index, not blanket mathematical verification. Partial includes triage or scoped checks; mentions alone are not review. Integrated archives are distinguished from active implementations. No automatic closures.',
                  pull_requests=result)
    if ending:
        output['ending_snapshot'] = ending_path
        output['remaining_from_start'] = ending['remaining_from_start']
        output['new_arrivals_outside_round'] = [p['number'] for p in ending['new_arrivals']]
        output['github_dispositions'] = dict(sorted(collections.Counter(p['github_state'] for p in result).items()))
    dest = ROOT / 'docs/research/pr-ledger.json'
    dest.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
    lines = ['# PR review and integration ledger', '',
             'The immutable starting snapshot contains **%d PRs**. Explicit later family rounds extend the current inventory to **%d**; unrelated arrivals remain outside the round.' % (len(snapshot['pull_requests']), len(result)), '',
             '[Machine-readable ledger](pr-ledger.json) · [Starting snapshot](../../research/pr-reconciliation-20261012/starting-snapshot.json)', '',
             'The ledger separates historical review from integration. A prior snapshot or a mention in a note does not certify a contribution. '
             '“Partially reviewed” includes scoped review and triage with their original limitations; “changed since review” means the present head lacks matching recorded coverage. '
             'Archived incorporation preserves a historical implementation and attribution without making it the selected result.', '',
             '| Disposition | Count |', '|---|---:|']
    lines += [f'| {k.replace("_", " ")} | {v} |' for k, v in counts.items()]
    if ending:
        states = collections.Counter(p['github_state'] for p in result)
        lines += ['', f'The earlier reconciliation closing snapshot had {ending["remaining_from_start"]} starting PRs still open and {ending["open_count"]} total open. '
                  'These are historical counts, not a live queue measurement. Later dispositions are recorded below.']
    if family_paths:
        lines += ['', '[Earlier family review](community-family533-review.md) · '
                  '[Earlier dispositions](../../research/community-family533-audit/DISPOSITIONS.json)', '',
                  'The earlier construction family #533–#537 and formal connections #513/#528 are covered there, '
                  'including the #503/#510 bit dependency. #463 has only its vendored pipeline subset reviewed.']
    if 'research/community-family588-audit/DISPOSITIONS.json' in family_paths:
        lines += ['', '[Family through #588](community-family588-review.md) · '
                  '[Exact-head dispositions](../../research/community-family588-audit/DISPOSITIONS.json)', '',
                  'This frozen round covers #543/#545/#555 and related construction, research and tooling packages '
                  'through #588. Each disposition distinguishes completed checks, publication and remaining obligations. '
                  'The separate formalization PRs and later arrivals are not approved by this round.']
    lines += ['', '## Remaining priorities', '',
              '1. Follow the new Linux CI for the published #442/#484/#509/#516/#520 batch; the [scoped review](community-formal-20261012-review.md) records completed local checks.',
              '2. Follow the explicit construction-family dispositions and remaining obligations; do not repeat completed foundation replays without a source/input change.',
              '3. Review #525’s checkpoint/ceiling and #529/#532’s distinct construction mechanisms; retain parallel credit.',
              '4. Reconcile #210/#279 updates with their earlier incorporated heads; audit #236’s source-package integration separately from its already published review receipts.',
              '5. Continue finite-instance connections for formal interfaces; abstract theorem builds do not instantiate all current physical constructions.', '',
              '## Starting PR inventory', '',
              'Each evidence link leads to the original scoped assessment. The JSON records exact heads, unresolved questions, integration locations and closure receipts.', '',
              '| PR | Contributor | Disposition | Evidence or remaining question |', '|---|---|---|---|']
    for p in result:
        refs = sorted({e['evidence'] for e in p['evidence']})
        if p.get('reconciliation_evidence'):
            refs.extend(p['reconciliation_evidence'])
        if refs:
            detail = ' · '.join(f'[record {i+1}](../../{f})' for i, f in enumerate(dict.fromkeys(refs)))
        else:
            detail = 'No exact-head review established; inspect contribution and dependencies.'
        lines.append(f'| [#{p["number"]}]({p["url"]}) | {p["contributor"]["login"]} | {p["disposition"].replace("_", " ")} | {detail} |')
    (ROOT / 'docs/research/pr-ledger.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(dict(total=len(result), counts=counts), indent=2))


if __name__ == '__main__':
    build()
