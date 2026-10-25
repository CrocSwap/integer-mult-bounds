"""Verify the prepared-helper construction and complete conditional bound.

Scratch-net with substantial OpenAI Codex assistance. Apache-2.0.
Native/caller/pricing machinery retains its source authors and notices.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256, sha1
from pathlib import Path
import gzip
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import closure, load, need, read
from construct import construct
import prepared


def reject(fn):
    try:
        fn()
    except ValueError as error:
        return str(error)
    raise ValueError('A semantic corruption was accepted')


def controls(word):
    out = {}
    mutations = {
        "missing_initialization": (["INIT",573,3], None),
        "wrong_second_reconstruction": (["ADD",573,710,"2",603], ["ADD",573,710,"4",603]),
        "missing_owned_cleanup": (["CLEAR",573,603], None),
        "missing_owned_reset": (["CLEAR",573,3], None),
        "wrong_delivery_frame": (["COPY",573,572,"1",595], ["COPY",573,572,"1",603]),
    }
    for name,(old,new) in mutations.items():
        bad = deepcopy(word)
        need(bad['program'].count(old) == 1, 'Unique control site '+name)
        at = bad['program'].index(old)
        if new is None:
            bad['program'].pop(at)
        else:
            bad['program'][at] = new
        out[name] = reject(lambda: prepared.replay(bad))
    return out


def source_relations(source):
    """Derive each replacement relation before specializing any input."""
    rows = [{r:Q(1)} for r in range(758)]
    sites = {13670:[(573,1),(572,-1),(732,2)],
             13691:[(573,1),(572,-1),(710,-2)]}
    checked = []
    for i,e in enumerate(source['program']):
        if i in sites:
            row = {}
            for r,q in sites[i]:
                prepared.add(row,rows[r],Q(q))
            need(row == {573:Q(-2)}, 'Exact source-version relation '+str(i))
            checked.append({'source_event':i,'combination':sites[i],
                            'original_input_relation':[[573,'-2']]})
        op,r = e[:2]
        if op in ('INIT','CLEAR'):
            rows[r] = {}
        elif op == 'SCALE':
            rows[r] = {k:Q(e[-2])*v for k,v in rows[r].items()}
        elif op == 'COPY':
            rows[r] = {k:Q(e[-2])*v for k,v in rows[e[2]].items()}
        elif op == 'ADD':
            prepared.add(rows[r],rows[e[2]],Q(e[-2]))
        else:
            need(op == 'MOVE','Known source opcode')
    need(len(checked) == 2,'Both causal relations')
    return checked


def run():
    pins = read(HERE/'SOURCES.json')
    for pin in pins['external_inputs']:
        raw = (HERE/pin['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'Source SHA256 '+pin['local_path'])
        need(sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest() == pin['git_blob'],
             'Source Git blob '+pin['local_path'])
    price = (HERE/'inputs/pr5599-pricing.py').read_text()
    for old,new in read(HERE/'PRICING-EDITS.json'):
        need(price.count(old) == 1, 'Unique declared price edit '+old)
        price = price.replace(old,new)
    need(price == (HERE/'pricing.py').read_text(), 'Declared pricing changes only')
    source = read(HERE/'inputs/pr5599-WORD.json.gz')
    relations = source_relations(source)
    word = construct(source)
    local = prepared.replay(word)
    columns = prepared.reverse_columns(word)
    rejected = controls(word)
    print('PASS prepared construction, all 758 endpoints, transpose and five controls', flush=True)
    with closure() as root:
        L = load(HERE/'inputs/pr5599-local.py','local')
        L.ROOT = root
        parent = L.replay(source)
        delta = Counter(local['paid']); delta.subtract(parent['paid'])
        need({r:n for r,n in delta.items() if n} == {1:-2}, 'Exact paid deletion')
        targets = Counter(parent['helpers']); targets[2] -= 1
        need(dict(targets) == local['helpers'], 'One rank-two target is retired')
        old_maps = {(e[2],e[3]) for e in source['program'] if e[0] == 'MOVE'}
        new_maps = {(e[2],e[3]) for e in word['program'] if e[0] == 'MOVE'}
        need(new_maps <= old_maps, 'No new paid native map')
        # The inherited native evaluator checks all remaining maps, every main
        # adapter and every original helper endpoint. Remove the retired target
        # and its two unused external normalizers from the complete new bill.
        native = L.native(word)
        need(native['helpers'] == parent['helpers'], 'Original native endpoint inventory')
        native['helpers'][2] -= 1
        native['helper_normalizers'] -= 2
        native['retired_helper'] = 573
        print('PASS every remaining native map and exact phase', flush=True)
        C = load(root/'research/p104-productive-controller/caller.py','prepared_caller')
        caller = C.construct()
        need(caller == read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Exact full caller')
        physical = C.physical(caller,word)
        P = load(HERE/'pricing.py','prepared_pricing')
        result = P.run(local,native,caller,physical)
        print('PASS complete invoice, two moment engines, compiler and all outer predicates', flush=True)
        bad = deepcopy(local); bad['paid'][1] -= 1
        rejected['omitted_paid_job'] = reject(lambda:P.assemble(bad,native,caller,physical))
        bad = deepcopy(local); bad['helpers'][2] += 1
        rejected['retired_target_still_credited'] = reject(lambda:P.assemble(bad,native,caller,physical))
        E = L.load(root/'research/higher-moment-strictification/verify.py','prepared_intervals')
        new_t = {int(r):n for r,n in result['targets'].items()}
        new_p = {int(r):n for r,n in result['paid'].items()}
        old_t,old_p = dict(new_t),dict(new_p)
        old_t[2] += 18; old_p[1] += 36
        parent_interval = [Q('.00309839352211'),Q('.00309839352212')]
        signs = []
        for k in parent_interval:
            a,b = E.moment(old_t,1-k),E.moment(old_p,1-k)
            signs.append((a[0]-b[1],a[1]-b[0]))
        need(signs[0][0] > 0 > signs[1][1], 'Exact predecessor crossing reproduced')
        lo,hi = map(Q,result['raw_root_interval'])
        gain = [lo-parent_interval[1],hi-parent_interval[0]]
        need(gain[0] > 0, 'Strict increase over predecessor raw crossing')
        at = 1-P.TESTED
        two = E.power(2,at)
        local_gain = (2-two[1],2-two[0])
        need(local_gain[0] > 0, 'Full local paid-minus-target trade is profitable')
    receipt = P.encode(dict(status='PASS_P104_PREPARED_SPLIT_KAPPA_00309871',
        source_commit='0644592d421b375c221045954fdf13932575ffa8',
        local_paid_delta={1:-2},local_target_delta={2:-1},
        local=local,source_relations=relations,transpose=columns,native=native,physical=physical,
        parent_raw_interval=parent_interval,raw_gain_interval=gain,
        local_moment_gain=local_gain,controls=rejected,complete_cost=result,
        limits=['The five inherited framework assumptions remain.',
                'The complete uniform compiler word and rounded multiplier are not materialized.',
                'No independent human review, proof-kernel acceptance or selected promotion is claimed.']))
    return receipt,word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    receipt,word = run()
    for name,data in [('RESULT.json',receipt),('WORD.json.gz',word)]:
        path = HERE/name
        if args.write:
            raw = (json.dumps(data,sort_keys=True,indent=None if name.endswith('.gz') else 2)+'\n').encode()
            path.write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
        else:
            need(read(path) == data, 'Saved semantic artifact '+name)
    print(receipt['status'],flush=True)
    print(json.dumps({k:receipt['complete_cost'][k] for k in
                     ('kappa','raw_root_interval','productive_fields','paid_calls')},sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
