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


def apply_pr148_retention(item, receipt, coverage):
    """Index PR1572's source-only evidence without granting PR148 review.

    Thiago Goulart's retained proof resolves the old fourteen-file source gap.
    Its checker remains the authority for the authenticated trees and payloads;
    this projection checks the receipt's head and coverage before indexing it.
    A later head or a later review's remaining question is never overwritten.
    """
    head = '975c3cf5d4ee0c90d5a76500d431bfc59102bb72'
    package = 'research/pr148-source-retention/'
    if (item['number'] != 148 or receipt['head_commit'] != head
            or coverage['head_commit'] != head
            or receipt['status'] != 'PASS_PR148_SOURCE_RETENTION'):
        raise ValueError('PR148 retention receipt belongs to a different source')
    rows = coverage['rows']
    paths = [r['path'] for r in rows]
    counts = dict(collections.Counter(r['storage']['kind'] for r in rows))
    direct = sorted(r['path'] for r in rows if r['direct_change'])
    recovered = sorted(r['path'] for r in rows if r['storage']['kind'] == 'recovered')
    if (len(paths) != len(set(paths)) or len(paths) != 114
            or receipt['comparison_changed_paths'] != len(paths)
            or counts != {'main-file': 96, 'pr181-archive': 4, 'recovered': 14}
            or receipt['coverage'] != counts
            or direct != receipt['direct_changed_paths'] or len(direct) != 11
            or recovered != receipt['recovered_paths']):
        raise ValueError('PR148 retention receipt has inconsistent coverage')
    item['source_retention'] = dict(
        head=head, applies_to_current_head=item['current_head'] == head,
        receipt=package + 'RESULT.json', coverage=package + 'COVERAGE.json',
        location=package, status='complete_historical_source_retention',
        scope='Source bytes and author-delta classification only; no whole-PR mathematical review or closure.')
    evidence = dict(head=head, evidence=package + 'README.md',
                    scope='PR1572 (Thiago Goulart / Tuafo) authenticates all 114 PR148 changed paths: '
                          '96 main, 4 PR181 archive, 14 recovered; 11 direct author changes. '
                          'Source coverage only; Rohan Gupta / gupt1156 retains construction credit.',
                    kind='source_retention')
    if evidence not in item['evidence']:
        item['evidence'].append(evidence)
    old_question = ('Whole-current-PR incorporation is not established: 14 changed paths lack byte-identical '
                    'coverage in main or its checked PR181 archive. Distinguish later equivalent edits, '
                    'unique content and historical implementations before closure.')
    if item['current_head'] == head and item.get('unresolved_question') == old_question:
        item['unresolved_question'] = (
            'PR1572 resolves the historical 14-path source gap and authenticates all 114 changed paths. '
            'Whole-PR mathematical review remains open: inspect the 11-file direct author delta and '
            'reconstruct the complete historical paired-cube verification from the pinned PR148 tree '
            'before any incorporation or closure decision. Source retention is not that execution.')


def apply_independent_parent_evidence(item, companion, source_path):
    """Append scoped evidence without changing any later review or closure decision."""
    if item['number'] != companion['number'] or item['current_head'] != companion['head']:
        raise ValueError('Independent parent evidence belongs to a different head')
    evidence = dict(head=companion['head'], evidence=source_path,
                    scope=companion['scope'], kind='independent_consolidation')
    if evidence not in item['evidence']:
        item['evidence'].append(evidence)


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
            mentions[int(number)].append(p.relative_to(ROOT).as_posix())

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
        'research/community-frontier890-audit/DISPOSITIONS.json',
        'research/community-batch932-audit/DISPOSITIONS.json',
        'research/community-batch952-audit/DISPOSITIONS.json',
        'research/community-batch970-audit/DISPOSITIONS.json',
        'research/community-batch1047-audit/DISPOSITIONS.json',
        'research/community-batch1099-audit/DISPOSITIONS.json',
        'research/pr-reconciliation100-20261013/DISPOSITIONS.json',
        'research/community-historical-five-audit/DISPOSITIONS.json',
        'research/community-reconciliation92-audit/DISPOSITIONS.json',
        'research/community-reconciliation-next100-audit/DISPOSITIONS.json',
        'research/community-reconciliation-third100-audit/DISPOSITIONS.json',
        'research/community-reconciliation-fourth100-audit/DISPOSITIONS.json',
        'research/community-pilot20-audit/DISPOSITIONS.json',
        'research/community-efficient100-audit/DISPOSITIONS.json',
                        'research/community-efficient200-audit/DISPOSITIONS.json',
        'research/community-efficient300-audit/DISPOSITIONS.json',
                        'research/community-efficient400-audit/DISPOSITIONS.json',
        'research/community-efficient500-audit/DISPOSITIONS.json',
        'research/community-efficient600-audit/DISPOSITIONS.json',
        'research/community-efficient700-audit/DISPOSITIONS.json',
        'research/community-efficient800-audit/DISPOSITIONS.json',
        'research/community-efficient900-audit/DISPOSITIONS.json',
        'research/community-efficient1000-audit/DISPOSITIONS.json',
        'research/community-efficient1100-audit/DISPOSITIONS.json',
        'research/community-efficient1200-audit/DISPOSITIONS.json',
        'research/community-efficient1300-audit/DISPOSITIONS.json',
        'research/community-efficient1400-audit/DISPOSITIONS.json',
        'research/community-efficient1500-audit/DISPOSITIONS.json',
                        'research/community-efficient1600-audit/DISPOSITIONS.json',
                        'research/community-efficient1700-audit/DISPOSITIONS.json',
        'research/community-efficient1800-audit/DISPOSITIONS.json',
        'research/community-efficient1900-audit/DISPOSITIONS.json',
        'research/community-efficient2000-audit/DISPOSITIONS.json',
        'research/community-efficient2100-audit/DISPOSITIONS.json',
        'research/community-efficient2200-audit/DISPOSITIONS.json',
        'research/community-efficient2300-audit/DISPOSITIONS.json',
        'research/community-efficient2400-audit/DISPOSITIONS.json',
        'research/community-efficient2500-audit/DISPOSITIONS.json',
        'research/community-efficient2600-audit/DISPOSITIONS.json',
        'docs/research/pr-intake-decisions.json',
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
    # Companion replays supplement old heads without granting whole-PR closure.
    companion_path = 'research/community-batch970-audit/COMPANION-REVIEWS.json'
    if (ROOT / companion_path).exists():
        indexed = {p['number']: p for p in result}
        for companion in load(companion_path)['pull_requests']:
            item = indexed[companion['number']]
            if item['current_head'] != companion['head']:
                raise ValueError('Companion replay belongs to a different parent head')
            item.setdefault('companion_reviews', []).append(companion)
            item['evidence'].append(dict(head=companion['head'], evidence=companion_path,
                                        scope=companion['scope'], kind='scoped_companion_review'))
            # A later whole-head review supersedes the old companion's carry-forward.
            # Keep the historical evidence without resurrecting its resolved question.
            if not item.get('review_completion', {}).get('required_execution_complete', False):
                item['unresolved_question'] = companion['remaining']
    for extra_parent_path in (
            'research/community-efficient300-audit/PARENT-EVIDENCE.json',
            'research/pr116-evidence-reconciliation/PARENT-EVIDENCE.json'):
        if (ROOT / extra_parent_path).exists():
            indexed = {p['number']: p for p in result}
            for companion in load(extra_parent_path)['pull_requests']:
                apply_independent_parent_evidence(indexed[companion['number']], companion,
                                                  extra_parent_path)
    retention_path = 'research/pr148-source-retention/'
    if (ROOT / retention_path / 'RESULT.json').exists():
        item = next(p for p in result if p['number'] == 148)
        apply_pr148_retention(item, load(retention_path + 'RESULT.json'),
                              load(retention_path + 'COVERAGE.json'))
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
    lines += ['', '[100-PR historical reconciliation](community-reconciliation100-review.md): exact-head coverage and individual carry-forward tasks; it is not 100 completed mathematical audits.',
              '[Five early contributions](community-historical-five-review.md): #2/#4/#8/#9/#12 retained with complete historical sources and focused replays.',
              '[Remaining 92 contributions](community-reconciliation92-review.md): source retention, scoped review and closure receipts; #122 awaits its missing parent circuit/profile.',
              '[Previous 100 contributions, #153–#303](community-reconciliation-next100-review.md): individual scope and explicit remaining obligations.', '[Third 100 contributions, #304–#421](community-reconciliation-third100-review.md): constructions, research and verification with source-bound execution.', '[Fourth 100 contributions, #423–#668](community-reconciliation-fourth100-review.md): full-source reconciliation and scoped execution, with blockers retained.', '', '## Remaining priorities', '',
              '1. Resolve the explicit remaining questions on partially reviewed or changed heads; consult the latest family disposition before repeating a replay.',
              '2. Continue with a frozen chunk of live, non-draft, unreviewed PRs. Compare current heads with published reviews and exclude submissions awaiting a concrete revision.',
              '3. Keep source retention, scoped execution, publication and actual GitHub closure separate. Preserve research, verification and parallel contribution credit even when a result is superseded.',
              '4. Build formal connections to the actual finite constructions; abstract theorem builds alone do not instantiate the selected multiplication algorithm.', '',
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
