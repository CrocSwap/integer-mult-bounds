#!/usr/bin/env python3
"""Check the source-bound cap on every unchanged installed return phase."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from cap import ReturnCap, inspect, need, weight
sys.path.insert(0, str(ROOT/'research/qq16-finite-handle-charge'))
import verify as predecessor
from observer import snapshot
from kernel import validate


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin '+row['path'])
    predecessor.authenticate()


class Observer:
    def __init__(self, _legacy_size):
        self.handles = {}; self.checks = []; self.exchanges = []; self.examples = []
        self.cap = None; self.controls = 0; self.peak = 0; self.context_weight = 0

    def attach(self, adapter, Tape):
        original = adapter.ReturnProtocol.check_inventory
        exchange = adapter.ReturnProtocol.exchange

        def check(protocol):
            data = snapshot(protocol, Tape, self.handles)
            if self.cap is None:
                self.cap = ReturnCap(protocol, Tape)
                self.rejections(protocol, data)
            self.peak = max(self.peak, self.cap.check(protocol, data))
            bill = validate(data, self.cap.size)
            original(protocol)
            self.checks.append(dict(shapes=[dict(vertices=len(g['rows']), edges=sum(len(r[2]) for r in g['rows']),
                                                  attributes=g['attributes'], tapes=sum(r[0] for r in g['rows']))
                                             for g in data['graphs']], bill=bill))

        def exchanged(roles, old, new):
            result = exchange(roles, old, new)
            self.exchanges.append(True)
            return result

        adapter.ReturnProtocol.check_inventory = check
        adapter.ReturnProtocol.exchange = staticmethod(exchanged)

    def rejections(self, protocol, data):
        runtime = self.cap.owners[0].monomial.compact.binary.native.runtime
        fixed = {id(v) for v in inspect(runtime, self.cap.Tape)[1]}
        control = copy.copy(runtime)
        control.binding = SimpleNamespace(codes=SimpleNamespace(q=2, dimension=2, bits=1))
        control.restore_context((0, 1, 2, 0, 1))
        self.context_weight = weight(inspect((control.context, control.program), self.cap.Tape, fixed)[0]) - 3
        need(self.context_weight <= 43, 'actual restore_context replacement envelope')
        runtime.retained_contexts = [runtime.context]
        try:
            self.reject(lambda: self.cap.check(protocol, snapshot(protocol, self.cap.Tape, self.handles)),
                        'no undeclared retention attribute')
        finally:
            del runtime.retained_contexts
        pool = self.cap.owners[0].pool
        pool.live[-1] = runtime.context
        try:
            self.reject(lambda: self.cap.check(protocol, snapshot(protocol, self.cap.Tape, self.handles)),
                        'no retained lease at external return')
        finally:
            del pool.live[-1]
        saved = self.cap.parameters[0]['owner_cap']
        self.cap.parameters[0]['owner_cap'] = 1
        try:
            self.reject(lambda: self.cap.check(protocol, data), 'derived owner graph cap')
        finally:
            self.cap.parameters[0]['owner_cap'] = saved

    def reject(self, function, reason):
        try:
            function()
        except ValueError as error:
            need(reason in str(error), 'exact semantic rejection: '+str(error))
            self.controls += 1
        else:
            raise ValueError('accepted mutation: '+reason)


def compute():
    authenticate()
    predecessor.Observer = Observer
    observer, original = predecessor.run_actual()
    need(len(observer.checks) == 50 and observer.controls == 3, 'all return phases and semantic controls')
    active = observer.checks[:-1]
    service = [row['shapes'][0] for row in active]
    need(service[0]['edges'] == 5033 and max(row['edges'] for row in service) == 5054,
         'same-owner source first fixture')
    need(len({row['tapes'] for row in service}) == 1, 'constant Tape inventory during growth')
    original.pop('contract_size')
    return dict(status='PASS_QQ16_RETURN_GRAPH_CAP', actual=original,
                cap=observer.cap.size, parameters=observer.cap.parameters,
                list_cap=observer.cap.list_cap, handle_cap=observer.cap.handle_cap,
                observed_snapshot_peak=observer.peak, semantic_rejections=observer.controls,
                service_edge_growth=[5033, 5054], service_tapes=service[0]['tapes'], context_shape_control=observer.context_weight,
                scope='Source-level encoded-graph invariant with finite caller calibration; no full Python-memory, physical frontend, supplier or kappa claim.')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--write', action='store_true'); args = parser.parse_args()
    result = compute()
    path = HERE/'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads(path.read_text()), 'complete deterministic receipt')
    print(result['status'])


if __name__ == '__main__':
    main()
