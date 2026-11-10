"""Passive review-text binding. Never execute a predecessor or target module."""
from pathlib import Path
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(condition, message):
    if condition is not True:
        raise RuntimeError(message)


def pointer(value, path):
    for key in path.split('/')[1:]:
        value = value[int(key)] if type(value) is list else value[key]
    return value


def inspect_scope(documents, claims):
    rows = claims['resolved']
    need([row['id'] for row in rows] == [
        'G12-CAUGHT-PRIMARY', 'G12-SOURCE-BOUNDARY', 'G12-NO-NEW-FINANCIAL-API'],
        'claim identity/order changed')
    for row in rows:
        need(pointer(documents[row['input']], row['pointer']) == row['source_text'],
             'source text transcription differs')
    need('already-caught P' in rows[0]['source_text'] and
         'No broader allocation-equivalence proof or new authority framework is required.' in rows[0]['source_text'],
         'original narrow review instruction missing')
    need('already-caught primary' in rows[1]['source_text'] and
         'not a universal allocation-equivalence proof' in rows[1]['source_text'],
         'static/runtime source boundary missing')
    need('do not require construction of a new enclosing financial/accounting API' in rows[2]['source_text'] and
         'complete source work/cost bill' in rows[2]['source_text'],
         'original financial/API distinction missing')
    need(claims['conditional_PR6347_witnesses_withdrawn'] is False and
         claims['new_runtime_or_activity_acceptance'] is False,
         'unearned acceptance or witness retraction')
    need(claims['original_weighted_activity_percent'] == 43.5 and
         claims['original_complete_activities'] == 22 and
         claims['original_activity_denominator'] == 49 and
         claims['stage_gate_percent'] == 20 and claims['overall_milestone_percent'] == 10,
         'original denominators/credit changed')
    need(claims['costs'] == 'OPEN_NOT_ZERO', 'unknown costs erased')


def rejected(action, label):
    try:
        action()
    except (RuntimeError, KeyError, IndexError):
        return
    raise RuntimeError('tamper accepted: ' + label)


def main():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    docs = {}
    for row in sources['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'live source pin differs')
        docs[row['path']] = json.loads(raw)
    claims = json.loads((HERE / 'CLAIMS.json').read_text())
    inspect_scope(docs, claims)
    count = 0
    # Change both the evidence transcription and decoded source: the scope
    # anchors still reject a matching but materially broadened contract.
    for index, before, after in [
        (0, 'No broader allocation-equivalence proof or new authority framework is required.',
         'A broader allocation-equivalence proof is required.'),
        (1, 'not a universal allocation-equivalence proof', 'a universal allocation-equivalence proof'),
        (2, 'do not require construction', 'require construction'),
    ]:
        bad_docs, bad_claims = copy.deepcopy(docs), copy.deepcopy(claims)
        row = bad_claims['resolved'][index]
        changed = row['source_text'].replace(before, after)
        need(changed != row['source_text'], 'tamper placement failed')
        row['source_text'] = changed
        parts = row['pointer'].split('/')[1:]
        parent = bad_docs[row['input']]
        for key in parts[:-1]:
            parent = parent[int(key)] if type(parent) is list else parent[key]
        parent[parts[-1]] = changed
        rejected(lambda: inspect_scope(bad_docs, bad_claims), str(index))
        count += 1
    for key in ('conditional_PR6347_witnesses_withdrawn', 'new_runtime_or_activity_acceptance'):
        bad = copy.deepcopy(claims)
        bad[key] = True
        rejected(lambda: inspect_scope(docs, bad), key)
        count += 1
    bad = copy.deepcopy(claims)
    bad['resolved'][0]['source_text'] += ' unbound transcription'
    rejected(lambda: inspect_scope(docs, bad), 'transcription')
    count += 1
    print('PASS_G12_ORIGINAL_CONTRACT_SCOPE source_inputs=3 tamper_controls=' + str(count) +
          ' target_execution=false original_acceptance=false')


if __name__ == '__main__':
    main()
