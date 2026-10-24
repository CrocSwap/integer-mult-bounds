#!/usr/bin/env python3
"""Source-bound signed-invoice examples, exchange cap and independent reuse audit."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import budget
import census


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_comparator():
    path = ROOT/'scripts/compare_recursive_invoices.py'
    spec = importlib.util.spec_from_file_location('invoice_order', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_invoice(c):
    word = json.loads(gzip.decompress((HERE/'source/ACTUAL-WORD.json.gz').read_bytes()))
    ctrl = json.loads((HERE/'source/CONTROLLER.json').read_bytes())
    original = json.loads((HERE/'source/INVOICE.json').read_bytes())
    can = word['canonical']
    frames = can['frames']
    need((can['v'], can['h'], ctrl['pairs'], ctrl['prefix_pairs'], ctrl['ambient_rank'])
         == (112,9,16,7,145), 'Pinned rank conventions and caller')
    helpers = Counter(len(frames[can['final'][i]])-len(frames[can['start'][i]]) for i in range(224,632))
    need(min(helpers) > 0, 'Productive helper target ranks')
    local = Counter({int(r): n for r,n in c['orientations']['forward']['paid_profile'].items()})
    need(local == Counter({int(r):n for r,n in c['orientations']['backward']['paid_profile'].items()}), 'Both local paid profiles')
    for direction in word['programs'].values():
        centres = [e for e in direction if e[0]=='center']
        need(len(centres)==8 and all(e[-1]==8 for e in centres), 'Eight original H8 centre slots')
        need(all(e[-1]!=8 for e in direction if e[0]=='climb'), 'All original H8 jobs are centres')
    paid, targets, events, directions = Counter(), Counter(), Counter(), Counter()
    for event in ctrl['physical_events']:
        kind = event[0]
        events[kind] += 1
        if kind == 'LOCAL':
            directions[bool(event[3])] += 1
            paid.update(local)
            targets.update(helpers)
        elif kind == 'QUERY_SHEAR':
            paid[1] += 112
        elif kind == 'IDLE':
            need(event[2] and len(set(event[2]))==len(event[2]), 'Distinct whole-idle stages')
            paid[8*len(event[2])] += 224
        else:
            need(kind in ('ADD','SIGNED_SWAP'), 'Known whole-caller event')
    for diagonal in ctrl['diagonal']:
        need(len(diagonal)==34 and diagonal[0] in (-1,1) and all(t in (0,1) for t in diagonal[1:]), 'Main output rank convention')
        targets[1+8*sum(diagonal[1:])] += 112
    need(events['LOCAL']==18 and directions==Counter({True:16,False:2}), '16 backward and two forward invocations')
    need(paid == Counter({int(r):n for r,n in original['paid'].items()}), 'Independently rebuilt complete paid invoice')
    need(targets == Counter({int(r):n for r,n in original['targets'].items()}), 'Independently rebuilt complete target invoice')
    return targets, paid


def invoice(targets, paid, module):
    return {'schema': module.SCHEMA,
        'contract': {'model':'mixed-target-unnormalized-power-v1',
            'rank_semantics':'H_r has raw tariff r^(1-C), with surrendered productive fields debited',
            'ambient_rank':145,
            'boundary':'complete p16/a7 unit before the retained mixed-target compiler'},
        'paid':{str(r):n for r,n in sorted(paid.items()) if n},
        'targets':{str(r):n for r,n in sorted(targets.items()) if n}}


def run():
    manifest = json.loads((HERE/'SOURCES.json').read_bytes())
    for row in manifest['retained_exports']:
        need(sha256((HERE/row['local_path']).read_bytes()).hexdigest()==row['sha256'], 'Retained source: '+row['local_path'])
    c = census.run()
    targets, paid = source_invoice(c)
    module = load_comparator()
    original = invoice(targets, paid, module)
    examples = {}
    for count in (0,16,128,144):
        t,p = budget.exchange(targets, paid, count)
        candidate = invoice(t,p,module)
        report = module.compare_invoices(original,candidate)
        need(report['classification']==('equal' if count==0 else 'uniformly_better'), 'Signed target-debit comparison')
        path = HERE/'examples'/('source.json' if count==0 else f'exchange-{count}.json')
        need(json.loads(path.read_bytes())==candidate, 'Exact committed example invoice')
        examples[str(count)] = report
    split = invoice(targets,paid,module)
    split['paid']['4'] -= 1
    split['paid']['2'] += 2
    need(module.compare_invoices(original,split)['classification']=='uniformly_worse', 'Scalar-saving H4 split loses')
    need(json.loads((HERE/'examples/h4-split.json').read_bytes())==split, 'Committed split example')
    b = budget.run()
    result = {'status':'PASS_SIGNED_INVOICE_PREFLIGHT_AND_SCOPED_CENTRE_EXHAUSTION',
        'source_reconstruction':{'local_jobs_each_orientation':3298,'backward_invocations':16,'forward_invocations':2,
            'original_centre_slots':144,'rank_surplus':752},
        'signed_comparisons':examples,'budget':b,'census':c,
        'scope':'Exact histogram order and this fixed exchange family; independent fixed-eight formal-row census. No new supplier or selected-frontier change.'}
    # JSON object keys are strings, including the census's integer rank keys.
    return json.loads(json.dumps(result))


if __name__=='__main__':
    result = run()
    expected = json.loads((HERE/'RESULT.json').read_bytes())
    need(result==expected, 'Deterministic committed receipt')
    print('PASS_SIGNED_INVOICE_PREFLIGHT_AND_SCOPED_CENTRE_EXHAUSTION')
