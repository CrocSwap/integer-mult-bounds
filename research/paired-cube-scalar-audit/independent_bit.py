"""Exact finite F2 operator audit of the physical paired-cube bit schedule.

Apache-2.0; written with OpenAI Codex assistance. Pure standard library,
no imports from the producer or its checker. Raw witness conventions and
chronology follow fd25adb7fbaa12ee761d02c733c54d1d2a7687ee. Integer bitsets
encode coefficients of EVERY source and independent physical dirty variable.
This proves this finite scalar map only, not frame/phase or all-size claims.
"""
import argparse
import ctypes
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import time


class AuditError(ValueError):
    pass


class IdentityError(AuditError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


class Budget:
    """Time/private-memory guard; resource measurement adapted from R6 audit."""
    def __init__(self, seconds=300, memory_bytes=4*1024**3):
        self.start = time.monotonic()
        self.seconds, self.memory_bytes, self.peak = seconds, memory_bytes, 0
        self.steps = 0
        if os.name == 'nt':
            from ctypes import wintypes
            class Counters(ctypes.Structure):
                _fields_ = [('cb', wintypes.DWORD), ('faults', wintypes.DWORD)] + [
                    (n, ctypes.c_size_t) for n in ('peak_working', 'working',
                    'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile',
                    'peak_pagefile', 'private')]
            self.counters = Counters()
            self.counters.cb = ctypes.sizeof(Counters)
            self.psapi = ctypes.WinDLL('psapi', use_last_error=True)
            self.psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,
                ctypes.POINTER(Counters), wintypes.DWORD]
            self.psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            self.kernel.GetCurrentProcess.restype = wintypes.HANDLE
        self.sample()

    def sample(self):
        require(time.monotonic()-self.start <= self.seconds, 'wall budget exceeded')
        if os.name == 'nt':
            require(self.psapi.GetProcessMemoryInfo(self.kernel.GetCurrentProcess(),
                ctypes.byref(self.counters), self.counters.cb), 'memory measurement failed')
            self.peak = max(self.peak, self.counters.private, self.counters.peak_pagefile)
        else:
            import resource
            peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            self.peak = max(self.peak, int(peak) if sys.platform == 'darwin' else int(peak)*1024)
        require(self.peak <= self.memory_bytes, 'memory budget exceeded')

    def tick(self):
        self.steps += 1
        if self.steps % 1024 == 0:
            self.sample()

    def report(self):
        self.sample()
        return dict(elapsed_seconds=time.monotonic()-self.start,
                    measured_peak_bytes=self.peak, memory_budget_bytes=self.memory_bytes,
                    wall_budget_seconds=self.seconds, workers=1, steps=self.steps,
                    memory_metric='Windows private/peak pagefile bytes; Unix peak resident bytes')


def isint(x):
    return type(x) is int


class Protocol:
    def __init__(self, graph, word, kchron, budget):
        self.budget = budget
        self.v = graph['v']
        require(isint(self.v) and self.v > 0, 'source dimension')
        self.ops = [tuple(x) for x in word['ops']]
        require(all(len(x) == 3 and all(isint(n) and n >= 0 for n in x)
                    and x[0] != x[1] for x in self.ops), 'operation format')
        self.sources = {int(s): r for s, r in word['sources'].items()}
        require(set(self.sources) == set(range(self.v)) and
                len(set(self.sources.values())) == self.v, 'source bijection')
        self.roots = graph['roots']
        self.rootroles = word['rootroles']
        require(len(self.roots) == len(self.rootroles), 'root correspondence')
        require(all(r['kind'] in ('center', 'side') for r in self.roots), 'root kind')
        require(all(isint(t) and 0 <= t < self.v for r in self.roots
                    for t in r['targets']), 'target index')
        roles = [n for op in self.ops for n in op[:2]] + list(self.sources.values()) + self.rootroles
        require(all(isint(r) and r >= 0 for r in roles), 'role index')
        self.R = max(roles)+1
        phase = word['phase1']
        require(len(set(phase)) == len(phase) and
                all(isint(i) and 0 <= i < len(self.ops) for i in phase), 'phase indices')
        early = sorted(phase)
        earlyset = set(early)
        self.order = early + [i for i in range(len(self.ops)) if i not in earlyset]
        self.cut = len(early)
        self.position = {i: p for p, i in enumerate(self.order)}
        touched = set()
        role_ops = [[] for _ in range(self.R)]
        for p, i in enumerate(self.order):
            for s in self.ops[i][:2]:
                role_ops[s].append(i)
                if p < self.cut:
                    touched.add(s)
        require(all(row == sorted(row) for row in role_ops), 'per-role order')
        gauges = word['gauges']
        gauge_roles = [g['role'] for g in gauges]
        require(len(set(gauge_roles)) == len(gauge_roles) and all(
            isint(s) and 0 <= s < self.R and role_ops[s] and s not in touched
            and s not in self.sources.values() for s in gauge_roles), 'gauge roles')
        reads = {int(s): p for s, p in word.get('reads', {}).items()}
        require(set(reads) <= set(gauge_roles), 'read roles')
        self.when = {}
        for k, g in enumerate(reversed(gauges)):
            s = g['role']; p = reads.get(s, self.cut)
            require(isint(p) and self.cut <= p <= self.position[role_ops[s][0]], 'read window')
            self.when[s] = (p, k)
        self.pairs = [tuple(pair) for pair in word.get('pairs', [])]
        require(all(len(pair) == 2 and all(isint(s) and 0 <= s < self.R for s in pair)
                    for pair in self.pairs), 'pair format')
        donors = {a for a, b in self.pairs}; recipients = {b for a, b in self.pairs}
        require(len(donors) == len(recipients) == len(self.pairs) and
                not donors & recipients, 'disjoint pair matching')
        for a, b in self.pairs:
            require(role_ops[a] and a not in self.rootroles and b in self.when and
                    self.position[role_ops[a][-1]] < self.when[b][0], 'pair lifetime')
        self.slot = list(range(self.R))
        for a, b in self.pairs:
            self.slot[b] = a
        require(all(self.slot[a] != self.slot[b] for a, b, _ in self.ops), 'aliased gate ports')
        self.physical = sorted(set(self.slot))
        self.response = [0]*self.R
        for r, s in zip(self.roots, self.rootroles):
            for t in r['targets']:
                self.response[s] ^= 1 << t
        # Transpose of the ORIGINAL logical gate word in its native execution order.
        for i in reversed(self.order):
            a, b, _ = self.ops[i]
            self.response[b] ^= self.response[a]
            budget.tick()
        self.entries = kchron['entries']
        self.deliveries = {}
        for e in self.entries:
            c, d, j = e['carrier'], e['passive'], e['deliver_after_root']
            require(isint(c) and isint(d) and c != d and 0 <= c < self.v and 0 <= d < self.v,
                    'K source index')
            require(isint(j) and 0 <= j < len(self.roots) and self.roots[j]['kind'] == 'side',
                    'K delivery root')
            require(all(isint(t) and 0 <= t < self.v for t in e['receivers']), 'K receiver')
            self.deliveries.setdefault(j, []).append(e)

    def run(self, mutation=None, role=None):
        budget = self.budget
        X = [1 << t for t in range(self.v)]
        initial = {s: 1 << (self.v+j) for j, s in enumerate(self.physical)}
        z = dict(initial)
        Y = [0]*self.v
        at = {}
        for s in sorted(self.when, key=self.when.get):
            if mutation == 'omit_read' and s == role:
                continue
            p = self.when[s][0]
            if mutation == 'premature_read' and s == role:
                p = self.cut
            if mutation == 'read_position_as_index':
                p = self.position[p]
            at.setdefault(p, []).append(s)

        def read(s):
            mask = self.response[s]
            value = z[self.slot[s]]
            while mask:
                bit = mask & -mask
                Y[bit.bit_length()-1] ^= value
                mask ^= bit
                budget.tick()

        def gate(i):
            a, b, _ = self.ops[i]
            z[self.slot[a]] ^= z[self.slot[b]]
            budget.tick()

        for s in range(self.R):
            if s not in self.when:
                read(s)
        for leaf, s in self.sources.items():
            z[self.slot[s]] ^= X[leaf]
        for i in self.order[:self.cut]:
            gate(i)
        for r, s in zip(self.roots, self.rootroles):
            if r['kind'] == 'center':
                for t in r['targets']:
                    Y[t] ^= z[self.slot[s]]
        for p in range(self.cut, len(self.order)):
            for s in at.get(p, ()):
                read(s)
            gate(self.order[p])
        for j, (r, s) in enumerate(zip(self.roots, self.rootroles)):
            if r['kind'] == 'side':
                for t in r['targets']:
                    Y[t] ^= z[self.slot[s]]
                for e in self.deliveries.get(j, ()):
                    c, d = e['carrier'], e['passive']
                    X[c] ^= X[d]
                    for t in e['receivers']:
                        Y[t] ^= X[d] if mutation == 'wrong_K_injection' else X[c]
        # Match native forward entry-list source restoration, and CHECK it.
        for e in self.entries:
            X[e['carrier']] ^= X[e['passive']]
        for i in self.order if mutation == 'wrong_inverse_order' else reversed(self.order):
            gate(i)
        for leaf, s in self.sources.items():
            z[self.slot[s]] ^= X[leaf]
        for t, value in enumerate(X):
            if value != 1 << t:
                raise IdentityError('source restoration failure at %s' % t)
        for s in self.physical:
            if z[s] != initial[s]:
                raise IdentityError('dirty restoration failure at physical role %s' % s)
        for t, value in enumerate(Y):
            if value != 1 << t:
                delta = value ^ (1 << t)
                col = (delta & -delta).bit_length()-1
                raise IdentityError('target identity failure at target %s, basis column %s' % (t, col))
        budget.sample()
        return dict(target_rows=self.v, source_rows_restored=self.v,
                    physical_dirty_rows_restored=len(self.physical),
                    independent_basis_columns=self.v+len(self.physical),
                    logical_roles=self.R, physical_roles=len(self.physical),
                    operations=len(self.ops), phase_one_operations=self.cut,
                    pairs=len(self.pairs), gauge_reads=len(self.when),
                    unpaired_gauge_reads=sum(s not in {b for a, b in self.pairs} for s in self.when),
                    explicit_late_reads=sum(p > self.cut for p, k in self.when.values()),
                    K_deliveries=len(self.entries))


def check(raw_graph, raw_word, raw_kchron, *, controls=False, seconds=300, memory_bytes=4*1024**3):
    """Accept parsed RAW witness objects; hashes belong in caller's source manifest."""
    budget = Budget(seconds, memory_bytes)
    protocol = Protocol(raw_graph, raw_word, raw_kchron, budget)
    result = protocol.run()
    rejected = {}
    if controls:
        recipients = {b for a, b in protocol.pairs}
        paired = next((b for a, b in protocol.pairs if protocol.response[b]), None)
        unpaired = next((s for s in protocol.when if s not in recipients and protocol.response[s]), None)
        late = next((b for a, b in protocol.pairs if protocol.response[b] and
                    protocol.when[b][0] > protocol.cut and any(
                    protocol.ops[i][0] == a for i in protocol.order[protocol.cut:protocol.when[b][0]])), None)
        require(paired is not None and unpaired is not None and late is not None and
                protocol.entries, 'required negative-control witnesses absent')
        mutations = [('omitted_paired_read', 'omit_read', paired),
                     ('omitted_unpaired_read', 'omit_read', unpaired),
                     ('premature_paired_read', 'premature_read', late),
                     ('read_position_as_index', 'read_position_as_index', None),
                     ('wrong_K_injection', 'wrong_K_injection', None),
                     ('wrong_inverse_order', 'wrong_inverse_order', None)]
        for name, mutation, role in mutations:
            try:
                protocol.run(mutation, role)
            except IdentityError as error:
                rejected[name] = dict(role=role, reason=str(error))
            else:
                raise AuditError('negative control accepted: '+name)
    return dict(status='computed_pass', scalar_identity=result,
                rejected_controls=rejected, resource=budget.report(),
                scope='exact finite F2 scalar operator over all source/physical-dirty columns; frame, phase, cost and all-size proofs excluded')


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, 'duplicate JSON key')
        obj[key] = value
    return obj


def load(path):
    data = path.read_bytes()
    if path.suffix == '.gz':
        data = gzip.decompress(data)
    return json.loads(data, object_pairs_hook=unique_object)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('graph', type=Path)
    parser.add_argument('word', type=Path)
    parser.add_argument('kchron', type=Path)
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    result = check(load(args.graph), load(args.word), load(args.kchron), controls=args.controls)
    result['raw_input_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (args.graph, args.word, args.kchron)}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
