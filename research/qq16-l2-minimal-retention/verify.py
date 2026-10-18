#!/usr/bin/env python3
"""Exact ordered QQ16 L2 retention identities. Apache-2.0.

Ross Richardson with substantial OpenAI Codex assistance.
No predecessor executable is imported. The algebra is a rational free-group
ring: distinct port/chart maps need not commute or satisfy any extra relation.
Native reads, retention implementation and full supplier costs are not checked.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
MEMBER = 't16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz'
MEMBER_SHA = 'a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518'
PACKET = 'research/joint-query/certificate.json.gz'
ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_bytes(root=ROOT):
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    data = {}
    for item in pins['files']:
        if item['usage'] == 'input':
            raw = (root / item['path']).read_bytes()
            need(sha(raw) == item['sha256'], 'source hash: ' + item['path'])
            data[item['path']] = raw
    return data


def xor_apply(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def sources(data):
    packet = json.loads(gzip.decompress(data[PACKET]))
    need(packet['F_contract'] == 'f=R_s x. X_U=x_U-K_s,U f; X_A=P_s,A ell_s,T x; X_T=P_s,T f. Y_U=y_U+X_U; Y_A+X_A=y_A+x_A; Y_T+X_T=y_T+x_T.',
         'pinned conserved forward contract')
    need(packet['B_contract'] == 'u=E_t y; a=ell_s,T x; b=R_s u. Y_A=u_A; Y_U=y_U+K_s,U a; Y_T=u_T-P_s,T(b+11a). X_U=x_U-y_U; X_A=x_A+y_A-u_A; X_T=P_s,T(b+12a).',
         'pinned conserved backward contract')
    need(tuple(packet['A_ports']) == A and tuple(packet['T_ports']) == T
         and tuple(packet['U_ports']) == U, 'actual port partition')
    r = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet['R_rows']]
    need(len(r) == 8, 'eight query coordinates')
    need(all(Q(packet['K_rows'][p].get(str(i), 0)) == r[i][p] / 4
             for p in range(112) for i in range(8)), 'K=R transpose/4')
    for ports, gram in ((A, 4), (T, 4), (U, 48)):
        need(all(sum(r[i][p] * r[j][p] for p in ports) == (gram if i == j else 0)
                 for i in range(8) for j in range(8)), 'selected/ordinary Gram')
    with tarfile.open(fileobj=io.BytesIO(data[ARCHIVE]), mode='r:gz') as ar:
        members = [m for m in ar.getmembers() if m.name == MEMBER]
        need(len(members) == 1 and members[0].isfile(), 'unique template member')
        raw = ar.extractfile(members[0]).read()
        need(sha(raw) == MEMBER_SHA, 'template hash')
        template = json.loads(gzip.decompress(raw))
    need(template['recipe'][:2] == [
        {'kind': 'local', 'pair': 0, 'reverse': False, 'stage': 0},
        {'kind': 'local', 'pair': 0, 'reverse': True, 'stage': 1}], 'immediate F0/B1 cut')
    # Bind 224 positive-stage logical symbols to the actual port-specific
    # owner maps. Logical D uses the owner component, not native translation.
    bindings = []
    unit = tuple(1 << i for i in range(73))
    program = packet['programs']['B_1_2']
    for p in range(112):
        maps = [e[2] for e in program if e[0] == 'cover_map' and e[1] == ['L', 112 + p]]
        need(len(maps) == 4, 'four Y alignments per port')
        for stage, offset in ((2, 0), (1, 2)):
            entry, back = [packet['map_registry'][maps[offset + i]] for i in (0, 1)]
            g, h = [tuple(v['owner_right_matrix_columns']) for v in (entry, back)]
            need(len(g) == len(h) == 73 and all(0 <= c < 2**73 for c in g + h), 'owner dimensions')
            need(tuple(xor_apply(g, c) for c in h) == unit
                 and tuple(xor_apply(h, c) for c in g) == unit, 'both owner inverse orders')
            a, b = [v['payload_translation_at_identity_owner'] for v in (entry, back)]
            need(a ^ xor_apply(g, b) == 0 and b ^ xor_apply(h, a) == 0, 'native inverse translations')
            bindings.append([stage, p, maps[offset], maps[offset + 1]])
    return r, bindings


def word_reduce(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def add(*terms):
    """A row maps (independent array id, ordered map word) to a rational."""
    out = {}
    for factor, row in terms:
        if factor:
            for key, value in row.items():
                out[key] = out.get(key, Q(0)) + factor * value
    return {k: v for k, v in out.items() if v}


def move(letter, row):
    if letter == 0:
        return dict(row)
    out = {}
    for (var, word), value in row.items():
        key = (var, word_reduce((letter,) + word))
        out[key] = out.get(key, Q(0)) + value
    return {k: v for k, v in out.items() if v}


def variable(i):
    return {(i, ()): Q(1)}


def pair():
    return ({p: variable(p) for p in range(112)},
            {p: variable(112 + p) for p in range(112)})


def route(stage, port):
    return 0 if stage == 0 else 1 + (stage - 1) * 112 + port


class Algebra:
    def __init__(self, r):
        self.r = r

    def query(self, rows, ports, stage=0):
        routed = {p: move(route(stage, p), rows[p]) for p in ports}
        return [add(*[(self.r[i][p], routed[p]) for p in ports]) for i in range(8)]

    def inject(self, q, ports, stage=0):
        return {p: move(-route(stage, p), add(*[(self.r[i][p] / 4, q[i]) for i in range(8)]))
                for p in ports}

    def forward(self, x, y):
        f = self.query(x, range(112))
        kf = self.inject(f, U + T)
        a = self.inject(self.query(x, T), A)
        xx = {p: add((1, x[p]), (-1, kf[p])) for p in U} | a | {p: kf[p] for p in T}
        yy = {p: add((1, y[p]), (1, xx[p])) for p in U}
        yy |= {p: add((1, x[p]), (1, y[p]), (-1, xx[p])) for p in A + T}
        return xx, yy

    def forward_inverse(self, xx, yy):
        f = self.query(xx, T)
        c = self.query(xx, A)
        kf = self.inject(f, U)
        x = {p: add((1, xx[p]), (1, kf[p])) for p in U} | self.inject(c, T)
        b = self.query(x, U)
        x |= self.inject([add((1, f[i]), (-1, b[i]), (-1, c[i])) for i in range(8)], A)
        y = {p: add((1, yy[p]), (-1, xx[p])) for p in U}
        y |= {p: add((1, xx[p]), (1, yy[p]), (-1, x[p])) for p in A + T}
        return x, y

    def observe(self, x, y):
        """Input is post-F0. Blocks: retained x_A,x_T,y_T; live C,V,Z."""
        k = self.inject(self.query(x, T, 1), U, 1)
        e = self.inject(self.query(y, U + T, 2), A, 2)
        return ({p: x[p] for p in A}, {p: x[p] for p in T}, {p: y[p] for p in T},
                {p: add((1, x[p]), (-1, y[p])) for p in U},
                {p: add((1, y[p]), (1, k[p])) for p in U},
                {p: add((1, y[p]), (1, e[p])) for p in A})

    def decode(self, obs, fault=None):
        xa, xt, yt, c, v, z = obs
        k = self.inject(self.query(xt, T, 1), U, 1)
        y = {p: add((1, v[p]), (0 if fault == 'omit_current_driver' else
                                 1 if fault == 'wrong_current_sign' else -1, k[p])) for p in U}
        x = dict(xa) | dict(xt) | {p: add((1, c[p]), (1, y[p])) for p in U}
        y |= dict(yt)
        stage = 1 if fault == 'future_chart_is_current_chart' else 2
        q = self.query(y, U if fault == 'omit_future_T' else U + T, stage)
        e = self.inject(q, A, stage)
        y |= {p: add((1, z[p]), (1 if fault == 'wrong_logger_sign' else -1, e[p])) for p in A}
        return x, y


def free_observations():
    blocks, count = [], 0
    for ports in (A, T, T, U, U, A):
        blocks.append({p: variable(count + i) for i, p in enumerate(ports)})
        count += len(ports)
    need(count == 224, '224 independent observations')
    return tuple(blocks)


def residual(want, got):
    for block, (a, b) in enumerate(zip(want, got)):
        for p in sorted(a):
            row = add((1, b[p]), (-1, a[p]))
            if row:
                (var, word), value = sorted(row.items())[0]
                return {'block': block, 'port': p, 'input_array': var,
                        'word': list(word), 'coefficient': str(value), 'row_terms': len(row)}
    return None


def require_equal(want, got, label):
    need(want == got, label + ': ' + str(residual(want, got)))


def rejected(want, got, label):
    witness = residual(want, got)
    need(witness is not None, 'ineffective semantic control: ' + label)
    return witness


def scalar_projection(row):
    """Positive specialization D=I; this alone would lose ordered coverage."""
    return add(*[(q, variable(i)) for (i, _), q in row.items()])


def run():
    data = source_bytes()
    r, bindings = sources(data)
    model = Algebra(r)
    inputs = pair()
    after = model.forward(*inputs)
    require_equal(inputs, model.forward_inverse(*after), 'F0 left inverse')
    require_equal(inputs, model.forward(*model.forward_inverse(*inputs)), 'F0 right inverse')
    observed = model.observe(*inputs)
    require_equal(inputs, model.decode(observed), 'post-F0 left inverse')
    free = free_observations()
    require_equal(free, model.observe(*model.decode(free)), 'post-F0 right inverse')
    complete = model.observe(*after)
    require_equal(inputs, model.forward_inverse(*model.decode(complete)), 'complete input recovery')
    require_equal(free, model.observe(*model.forward(*model.forward_inverse(*model.decode(free)))),
                  'complete observation recovery')
    controls = {}
    for fault in ('omit_current_driver', 'wrong_current_sign', 'omit_future_T',
                  'wrong_logger_sign', 'future_chart_is_current_chart'):
        wrong = model.decode(observed, fault)
        controls[fault] = rejected(inputs, wrong, fault)
        if fault == 'future_chart_is_current_chart':
            need(all(scalar_projection(wrong[b][p]) == inputs[b][p]
                     for b in range(2) for p in range(112)), 'chart fault hidden by D=I')
    drops = []
    for b in range(3):
        for p in observed[b]:
            bad = [dict(block) for block in observed]
            bad[b][p] = {}
            drops.append({'block': b, 'port': p,
                          'witness': rejected(inputs, model.decode(tuple(bad)), 'retained coordinate omission')})
    bad = [dict(block) for block in observed]
    bad[4] = {p: {} for p in U}
    controls['discard_live_Y2_U'] = rejected(inputs, model.decode(tuple(bad)), 'missing new live read')
    bad[4] = dict(inputs[1])
    controls['use_pre_B1_Y_U'] = rejected(inputs, model.decode(tuple(bad)), 'incorrect live cut')
    bad = [dict(block) for block in observed]
    bad[5] = {p: {} for p in A}
    controls['discard_live_Y2_A'] = rejected(inputs, model.decode(tuple(bad)), 'missing live logger')
    reversed_rows = tuple({p: dict(reversed(list(row.items()))) for p, row in reversed(list(block.items()))}
                          for block in observed)
    require_equal(inputs, model.decode(reversed_rows), 'term and port reorder')
    split_rows = tuple({p: add((Q(1, 3), row), (Q(2, 3), row)) for p, row in block.items()}
                       for block in observed)
    require_equal(inputs, model.decode(split_rows), 'equivalent rational splitting')
    return {'status': 'PASS_QQ16_L2_MINIMAL_RETENTION', 'no_new_kappa': True,
            'source_sha256': {k: sha(v) for k, v in sorted(data.items())},
            'template_member': {MEMBER: MEMBER_SHA}, 'registered_route_pairs': bindings,
            'input_arrays': 224, 'live_arrays': 200, 'retained_arrays': 24,
            'predecessor_L2_retained_arrays': 32, 'retained_blocks': ['x1_A', 'x1_T', 'y1_T'],
            'live_blocks': ['X2_U', 'Y2_U', 'Y2_A'],
            'algebra': 'Q free-group ring on 224 invertible chart/port symbols; D0=I',
            'identities': ['F0^-1 F0=I', 'F0 F0^-1=I', 'decode observe=I',
                           'observe decode=I', 'full decoder full observation=I',
                           'full observation full decoder=I'],
            'lower_bound': 'For finite array dimension n>0, (200+q)n>=224n; hence q>=24',
            'semantic_faults': controls, 'retained_coordinate_omissions': drops,
            'positive_controls': ['reordered terms/ports', 'rational splitting'],
            'chart_fault_invisible_at_identity_specialization': True,
            'scope': 'Information lemma at immediate post-B1; native reads, cost, cleanup and later cuts not admitted'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-result', action='store_true')
    args = ap.parse_args()
    result = run()
    encoded = json.dumps(result, sort_keys=True, indent=2) + '\n'
    path = HERE / 'RESULT.json'
    if args.write_result:
        with path.open('x') as f:
            f.write(encoded)
    else:
        need(path.read_text() == encoded, 'missing or mismatching committed result')
    print(result['status'], 'retained=24 live=200 inputs=224 identities=6 faults=32 no_new_kappa')


if __name__ == '__main__':
    main()
