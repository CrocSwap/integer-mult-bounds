"""Separate transition semantics for the physical child-shape producer.

Author-side OpenAI Codex-assisted review. Apache-2.0. No source Machine/Tape
interpreter is executed. The all-size theorem requires its written proof.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
GUARD = {-9: 6, -4: 3, -1: 4}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


class Reject(ValueError):
    pass


class Walker:
    def __init__(self, program, cells, heads):
        self.rows, self.pc = program.instructions, program.entry
        self.cells, self.heads = [dict(c) for c in cells], list(heads)
        self.steps = 0
        self.visited = [set() for _ in cells]
        self.written = [set() for _ in cells]

    def run(self, ceiling):
        while self.steps < ceiling:
            row = self.rows[self.pc]
            self.steps += 1
            if row[0] == 'halt':
                return self
            if row[0] == 'reject':
                raise Reject(row[1])
            if row[0] == 'goto':
                self.pc = row[1]
                continue
            tape, position = row[1], self.heads[row[1]]
            self.visited[tape].add(position)
            if row[0] == 'branch':
                self.pc = dict(row[2]).get(self.cells[tape].get(position, 0), row[3])
                continue
            if row[0] == 'write':
                self.written[tape].add(position)
                if row[2]:
                    self.cells[tape][position] = row[2]
                else:
                    self.cells[tape].pop(position, None)
            elif row[0] == 'move':
                need(row[2] in (-1, 1), 'unit step')
                self.heads[tape] += row[2]
                self.visited[tape].add(self.heads[tape])
            else:
                raise ValueError('Unsupported literal instruction')
            self.pc += 1
        raise RuntimeError('External reviewer cap exceeded')


def packet(values):
    values = list(values)
    return {**GUARD, 0: 1, **{i+1: x for i, x in enumerate(values)}, len(values)+1: 2}


def binary(value):
    return packet(3 + ((value >> i) & 1) for i in range(value.bit_length()))


def check_prefix(run):
    need(all(not positions or min(positions) >= 0 for positions in run.visited), 'protected prefix never read')
    need(all(not positions or min(positions) >= 0 for positions in run.written), 'protected prefix never written')
    for tape in run.cells:
        need(all(tape.get(i) == v for i, v in GUARD.items()), 'ancestor guard preserved')


def run():
    source = json.loads((HERE/'SOURCE.json').read_text())
    for row in source['files']:
        b = (HERE/row['path']).read_bytes()
        need(len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256'], 'exact sealed source bytes before import')
    candidate = HERE.parent/'shape/producer.py'
    if candidate.is_file():
        need(candidate.read_bytes() == (HERE/'snapshot/producer.py').read_bytes(), 'independent snapshot equals active adjacent shape producer')
    spec = importlib.util.spec_from_file_location('reviewed_shape_producer', HERE/'snapshot/producer.py')
    p = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = p
    spec.loader.exec_module(p)
    cases, linked_cases = [], []
    for L in (2, 3, 4, 9):
        program, consumer = p.build(L), p.retire_delivered(L)
        need(program.tapes == 9, 'nine fixed tapes')
        for H in (1, 2, 3, 5):
            for Ac in (1, 2, 3, 8):
                for Rp in (1, 2, 4, 5):
                    A, Rc = L*H*Ac, H*Rp
                    cells, heads = [dict(GUARD) for _ in range(11)], [0]*11
                    for role, value in ((0, A), (1, H), (2, Rp)):
                        cells[role], heads[role] = binary(value), 1
                    before = [dict(c) for c in cells]
                    out = Walker(program, cells, heads).run(2000*A*L*Rp)
                    check_prefix(out)
                    for i in (0, 1, 2):
                        need(out.cells[i] == before[i] and out.heads[i] == 1 and not out.written[i], 'borrowed input unchanged')
                    for i, value in ((3, Ac), (4, Rc)):
                        need(out.cells[i] == binary(value) and out.heads[i] == 1, 'exact generated binary child shape')
                    for i in (5, 6, 7, 8, 9, 10):
                        need(out.cells[i] == GUARD and out.heads[i] == 0, 'all temporary work physically erased')
                    retired = Walker(consumer, out.cells, out.heads).run(2000*A*L*Rp)
                    check_prefix(retired)
                    need(retired.cells == before and retired.heads == heads, 'delivered grants have a charged final consumer')
                    cases.append([L,H,Ac,Rp,out.steps,sum(map(len,out.visited)),retired.steps])
        linked = p.linked_split(L)
        need(linked.tapes == L+11, 'fixed linked port count')
        for H, Ac, Rp in ((1,1,1),(2,1,3),(3,2,2),(5,1,1)):
            A, Rc = L*H*Ac, H*Rp
            for pattern in (0,1):
                bits = [((i*i+19*i+7) ^ (i>>2))&1 if pattern else i&1 for i in range(A*Rp)]
                cells, heads = [dict(GUARD) for _ in range(L+11)], [0]*(L+11)
                for role, value in ((0,A),(1,H),(2,Rp)):
                    cells[role], heads[role] = binary(value), 1
                cells[L+9], heads[L+9] = packet(3+b for b in bits), 1
                before = [dict(c) for c in cells]
                out = Walker(linked,cells,heads).run(2000*A*L*Rp)
                check_prefix(out)
                for bank in range(L):
                    wanted = [bits[(a*L+bank)*Rc+r] for a in range(Ac) for r in range(Rc)]
                    need(out.cells[9+bank] == packet(3+b for b in wanted) and out.heads[9+bank] == 1, 'generated grants feed literal child split without callback')
                for role in (0,1,2,L+9):
                    need(out.cells[role] == before[role] and out.heads[role] == 1 and not out.written[role], 'linked borrowed input preserved')
                need(out.cells[3] == binary(Ac) and out.cells[4] == binary(Rc), 'child grant packets retained for matching merge')
                for role in (5,6,7,8,L+10):
                    need(out.cells[role] == GUARD and out.heads[role] == 0, 'linked scratch blank including markers')
                retired = Walker(p.retire_delivered(L, linked=True), out.cells, out.heads).run(2000*A*L*Rp)
                check_prefix(retired)
                need(retired.cells == before and retired.heads == heads, 'all delivered child copies and grants physically consumed')
                linked_cases.append([L,H,Ac,Rp,pattern,out.steps,retired.steps])
    program = p.build(3)
    original, heads = [dict(GUARD) for _ in range(9)], [0]*9
    for i, n in enumerate((18,2,3)):
        original[i], heads[i] = binary(n), 1
    controls = []
    for label in ('nondivisible','zero_H','noncanonical_H','occupied_output','bad_R_bit'):
        cells = [dict(c) for c in original]
        if label == 'nondivisible':
            cells[0] = binary(17)
        elif label == 'zero_H':
            cells[1] = packet([3])
        elif label == 'noncanonical_H':
            cells[1] = packet([3,4,3])
        elif label == 'occupied_output':
            cells[3][0] = 4
        else:
            cells[2][1] = 5
        try:
            Walker(program,cells,heads).run(200000)
        except Reject:
            controls.append(label)
        else:
            raise ValueError('Invalid shape accepted: '+label)
    digest = lambda rows: hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
    return {'status':'PASS_INDEPENDENT_PHYSICAL_CHILD_SHAPE', 'producer_cases':len(cases), 'linked_split_cases':len(linked_cases), 'invalid_controls':controls, 'producer_receipt_sha256':digest(cases), 'linked_receipt_sha256':digest(linked_cases), 'max_steps_per_root_volume':max(row[4]/(row[0]**2*row[1]*row[2]*row[3]) for row in cases), 'internal_author_side_review_only':True}


if __name__ == '__main__':
    print(json.dumps(run(),sort_keys=True))
