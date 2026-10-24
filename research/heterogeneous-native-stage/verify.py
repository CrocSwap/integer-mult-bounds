#!/usr/bin/env python3
"""Exact returned-invoice and changed-demand rejection, not solver optimality.

Apache-2.0; substantial OpenAI Codex assistance; retained predecessor credit.
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
    if row['usage'] == 'input':
        if hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Changed source: ' + row['path'])
sys.path.insert(0, str(HERE))
import stage
import price


def main():
    model = stage.build(stage.S.payload(), [1])
    receipt = json.loads((HERE / 'DISCOVERY.json').read_text())
    selected = receipt['selected_nodes']
    paid, helpers = stage.M.invoice(model, selected)
    stage.M.need(paid == {int(k): v for k, v in receipt['paid'].items()} and
                 helpers == {int(k): v for k, v in receipt['helpers'].items()},
                 'Exact returned local bill')
    stage.M.need(not selected and paid == {1:2321, 2:412, 3:510, 4:127, 5:40, 8:8}
                 and helpers == {4:28, 7:7, 8:47, 9:326}, 'Source plus120H1 returned invoice')
    stage.M.need(len(model['eligible_ports']) == 60 and
                 len(model['forced_endpoints']) == 120, 'Every changed main endpoint retained')
    result = price.run()
    stage.M.need(json.loads(json.dumps(result)) == json.loads((HERE / 'RESULT.json').read_text()),
                 'Exact price/certificate receipt reproduced')
    # Prevent a changed-output profile from borrowing the old all-full credit.
    p0, h0 = price.profiles([])
    p1, h1 = price.profiles([0])
    stage.M.need(h1 != h0 and p1 != p0, 'Lost output and changed idle/native work priced')
    stage.M.need(sum(r*n for r,n in h0.items()) - sum(r*n for r,n in h1.items())
                 - sum(r*n for r,n in p0.items()) + sum(r*n for r,n in p1.items()) == 240,
                 'Complete first-stage rank-mass loss240')
    for bad in ([2], [-1], [33]):
        try:
            price.profiles(bad)
        except ValueError:
            pass
        else:
            raise ValueError('Thin/nonexistent native-stage mutation accepted')
    try:
        stage.M.invoice(model, model['forced_endpoints'][:1])
    except ValueError:
        pass
    else:
        raise ValueError('Fixed changed endpoint released')
    print(json.dumps(dict(status='PASS_CHANGED_DEMAND_BILL_AND_RETURNED_INVOICE_REJECTION',
                          eligible_ports=60, forced_endpoints=120,
                          paid=dict(paid), helpers=dict(helpers),
                          all_subset_bound=result['all_subset_bound'],
                          scope='No exact solver optimum, actual signed native word or new kappa.'), sort_keys=True))


if __name__ == '__main__':
    main()
