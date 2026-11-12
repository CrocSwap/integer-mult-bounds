#!/usr/bin/env python3
"""Independent source, spectral arithmetic, local-carry and cost review.

Prepared for Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
This does not import the author's test oracle or full-packet simulator.
"""
from pathlib import Path
import ast
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import itertools
import json
import subprocess
import sys

CANDIDATE = Path(__file__).resolve().parents[2]
DEFAULT = CANDIDATE if (CANDIDATE/'leaf.py').is_file() else CANDIDATE/'worker-c4/research/literal-positive-c-leaf'
PACKAGE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT
ROOT = Path('/workspace/scratch/be42ab5b7196/source')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def spectral_row(k):
    """Walsh spectral diagonal i^popcount, not pair butterflies/products."""
    size = 1 << k
    roots = ((1, 0), (0, 1), (-1, 0), (0, -1))
    ans = []
    for h in range(size):
        a = b = 0
        for frequency in range(size):
            x, y = roots[frequency.bit_count() % 4]
            sign = -1 if (frequency & h).bit_count() % 2 else 1
            a += sign*x
            b += sign*y
        ans.append((Fraction(a, size), Fraction(b, size)))
    return ans


PAIR_ROW = spectral_row(1)


def pair_fields(values):
    z = ((values[0], values[1]), (values[2], values[3]))
    out = []
    for y in (0, 1):
        a = b = Fraction(0)
        for x in (0, 1):
            u, v = mul(PAIR_ROW[x ^ y], z[x])
            a += u
            b += v
        out.extend((a, b))
    return tuple(out)


def encode(n, w):
    return format(n % (1 << w), '0'+str(w)+'b')


class CPU:
    """Sparse dictionary state, separately written local graph interpreter."""
    def __init__(self, program, tapes):
        self.program = program
        self.cells = tapes
        self.positions = [0]*len(tapes)
        self.low = [0]*len(tapes)
        self.high = [0]*len(tapes)
        self.pc = 0
        self.steps = 0
        self.stopped = False
        self.rejected = False

    def run(self, bound, stop_pc=None):
        while not self.stopped and not self.rejected and self.pc != stop_pc:
            require(self.steps < bound, 'independent helper budget')
            insn = self.program[self.pc]
            self.steps += 1
            opcode = insn[0]
            self.pc += 1
            if opcode == 'goto':
                self.pc = insn[1]
            elif opcode == 'halt':
                self.stopped = True
            elif opcode == 'move':
                t, delta = insn[1:]
                self.positions[t] += delta
                self.low[t] = min(self.low[t], self.positions[t])
                self.high[t] = max(self.high[t], self.positions[t])
            elif opcode == 'write':
                t, symbol = insn[1:]
                if symbol == '_':
                    self.cells[t].pop(self.positions[t], None)
                else:
                    self.cells[t][self.positions[t]] = symbol
            elif opcode == 'read':
                t, branches = insn[1:]
                symbol = self.cells[t].get(self.positions[t], '_')
                target = branches.get(symbol)
                if target is None:
                    self.rejected = True
                else:
                    self.pc = target
            else:
                raise ValueError('unexpected local opcode')
        return self


def helper_graph(m, signs):
    builder = m.Builder()
    m.c_component(builder, signs, m.LOUT)
    builder.op('halt')
    builder.mark('reject')
    builder.op('read', m.HEADER, {})
    return builder.finish(('_', '0', '1', '|'))[0]


def helper_case(m, code, row_index, w, numbers, check_cost=True):
    tapes = [{-1: '|'} for _ in range(29)]
    for t, n in zip(m.INPUTS, numbers):
        tapes[t].update(enumerate(encode(n, w)))
    tapes[m.WIDTH].update((j, '1') for j in range(w))
    before = [dict(x) for x in tapes]
    expected = pair_fields(numbers)[row_index]
    ok = expected.denominator == 1 and -(1 << (w-1)) <= expected < (1 << (w-1))
    cpu = CPU(code, tapes).run(1000*(w+1))
    require(cpu.stopped == ok and cpu.rejected != ok, 'spectral helper acceptance')
    if ok:
        output = ''.join(cpu.cells[m.LOUT].get(j, '_') for j in range(w))
        require(output == encode(int(expected), w), 'spectral helper value')
        require(cpu.cells[m.LOUT] == {-1: '|', **dict(enumerate(output))}, 'helper output extent')
        require(all(cpu.cells[t] == before[t] for t in range(29) if t != m.LOUT), 'helper borrow/NUM retirement')
        require(all(x == (w if t == m.LOUT else 0) for t, x in enumerate(cpu.positions)), 'helper head return')
        require(cpu.low[m.NUM] == -1 and cpu.high[m.NUM] == w+2, 'literal numerator width')
        if check_cost:
            require(cpu.steps == 43*w+58, 'exact component tariff')
    else:
        require(cpu.cells[m.LOUT] == before[m.LOUT], 'failed component emitted output')
    return cpu.steps, ok


def spectral_checks():
    report = []
    for k in range(1, 9):
        row = spectral_row(k)
        denom = max(x.denominator for pair in row for x in pair)
        norm = sum(abs(a)+abs(b) for a, b in row)
        require(denom == 1 << ((k+1)//2), 'sharp tensor denominator')
        require(norm == 1 << ((k+1)//2), 'component row norm')
        require(sum(a*a+b*b for a, b in row) == 1, 'unitary kernel row')
        require(tuple(sum(v[part] for v in row) for part in (0, 1)) == (1, 0), 'constant-fibre eigenvalue')
        report.append({'axes': k, 'sharp_denominator': denom, 'component_row_l1': int(norm)})
    # Final exactness is strictly weaker than successive-axis exactness.
    witness = (1, 0, 0, 1)
    row = spectral_row(2)
    final = []
    for y in range(4):
        final.append(tuple(sum(row[x ^ y][part]*witness[x] for x in range(4)) for part in (0, 1)))
    require(final == [(0, 0), (1, 0), (1, 0), (0, 0)], 'final-only witness')
    require(pair_fields((1, 0, 0, 0))[0].denominator == 2, 'first prefix is inexact')
    return report


def geometry_checks():
    count = 0
    records = 0
    for f, p, s, r in itertools.product(range(1, 9), (1, 2, 5), (1, 3), (1, 2)):
        tail = (1 << (8*f))*s*r
        n = p*(1 << f)*tail
        for j in range(f):
            prefix = p*(1 << (f-1-j))
            suffix = s*r*(1 << (8*f+j))
            require(2*prefix*suffix == n, 'axis census')
            if j+1 < f:
                require(prefix % 2 == 0, 'exact prefix halving')
            # Algebraic probes of full physical slots, including interiors and both ends.
            for outer in (0, p-1):
                for coordinate in sorted({0, (1 << f)-1, 1 << j, ((1 << f)-1) ^ (1 << j)}):
                    for rest in sorted({0, tail//2, tail-1}):
                        physical = (outer*(1 << f)+coordinate)*tail+rest
                        block, within = divmod(physical, 2*suffix)
                        side, offset = divmod(within, suffix)
                        mate = block*2*suffix+(1-side)*suffix+offset
                        target = (outer*(1 << f)+(coordinate ^ (1 << j)))*tail+rest
                        require(mate == target, 'physical coefficient pairing')
                        records += 1
            count += 1
    return {'axis_geometries': count, 'full_integer_address_probes': records}


def sources():
    pins = json.loads((PACKAGE/'SOURCES.json').read_text())['files']
    records = []
    for pin in pins:
        data = (PACKAGE/pin['local']).read_bytes()
        require(len(data) == pin['bytes'] and sha(data) == pin['sha256'], 'retained source bytes')
        # Independent Git identity is optional after relocation without repository objects.
        record = {'path': pin['path'], 'commit': pin['commit'], 'sha256': sha(data)}
        if ROOT.exists():
            obj = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', pin['commit']+':'+pin['path']], text=True).strip()
            require(obj == pin['blob'], 'actual commit/path object')
            raw = subprocess.check_output(['git', '-C', str(ROOT), 'cat-file', 'blob', obj])
            require(raw == data, 'actual Git source bytes')
            record['git_blob'] = obj
        records.append(record)
    word = json.loads(gzip.decompress((PACKAGE/'reference/selected-native.json.gz').read_bytes()))
    require(word['program'][24472] == ['MOVE', 415, 3, 99, False], 'actual selected occurrence')
    require(word['frames'][3] == [] and word['frames'][99] == [239], 'actual selected frame edge')
    src = (PACKAGE/'reference/clifford_exact.py').read_text()
    require("def cgate(n,q,sgn=1):" in src, 'source positive C default')
    require('out=out.then(cgate(n,1<<i))' in src, 'source positive Fourier axes')
    require('compiled=rmon.then(fourier(n,range(r))).then(lmon)' in src, 'source central positive kernel')
    # Pinned whole source is authoritative; these checks expose exact relied-on seams.
    return records


def graph_checks(m):
    code, alphabet = m.compile_leaf()
    require(len(code) == 6826 and len(alphabet) == 4, 'frozen graph inventory')
    for insn in code:
        require(insn[0] in ('read', 'write', 'move', 'goto', 'halt'), 'literal language')
        if insn[0] in ('read', 'write', 'move'):
            require(type(insn[1]) is int and 0 <= insn[1] < 29, 'fixed physical tape')
        if insn[0] == 'move':
            require(insn[2] in (-1, 1), 'unit physical move')
        if insn[0] == 'read':
            require(all(s in alphabet and type(pc) is int and 0 <= pc < len(code) for s, pc in insn[2].items()), 'local branches')
        if insn[0] == 'write':
            require(insn[2] in alphabet, 'fixed alphabet write')
        if insn[0] == 'goto':
            require(type(insn[1]) is int and 0 <= insn[1] < len(code), 'fixed target')
    require(m.INPUTS == (23, 24, 25, 26), 'input roles')
    derived = []
    for output in range(4):
        derived.append(tuple(int(2*pair_fields(tuple(int(j == k) for j in range(4)))[output]) for k in range(4)))
    require(tuple(derived) == m.ROWS, 'spectrally derived coefficient rows')
    # Closure is exhaustive only over finite control, not a proof by input sampling.
    transitions = 0
    for signs in derived:
        for carry in (-1, 0, 1, 2):
            for bits in itertools.product((0, 1), repeat=4):
                value = carry+sum(s*b for s, b in zip(signs, bits))
                require(value//2 in (-1, 0, 1, 2), 'finite carry closure')
                require(value == 2*(value//2)+(value % 2), 'exact digit identity')
                transitions += 1
    tree = ast.parse((PACKAGE/'leaf.py').read_text())
    fs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    # Cutoff uses no unary copying, doubling or parameter-sized Python loop.
    calls = {n.func.id for n in ast.walk(fs['gamma_binary']) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    require(not (calls & {'unary_copy', 'double', 'product', 'gamma'}), 'cutoff value expanded')
    require('range' not in calls, 'cutoff graph specialized on a runtime integer')
    table_hash = sha(json.dumps([code, alphabet], sort_keys=True, separators=(',', ':')).encode())
    require(table_hash == 'ac8f5e05a4e0264e94eacb7887b568bead2cce5583607b5047ac560aaf434dc9', 'frozen literal graph hash')
    return {'locations': len(code), 'table_and_alphabet_sha256': table_hash, 'finite_carry_cases': transitions}


def axis_cost_checks(m):
    # Capture construction-time labels; the emitted instructions are unchanged.
    original_builder = m.Builder
    builders = []
    def capture_builder():
        value = original_builder()
        builders.append(value)
        return value
    try:
        m.Builder = capture_builder
        code, _ = m.compile_leaf()
    finally:
        m.Builder = original_builder
    labels = builders[0].labels
    cases = instructions = 0
    for a, u, w in itertools.product((1, 2, 7), (1, 3, 8), (2, 3, 11)):
        n, v = 2*a*u, 4*a*u*w
        tapes = [{-1: '|'} for _ in range(29)]
        for tape, length in ((m.WIDTH, w), (m.PREFIX, a), (m.SUFFIX, u), (m.F, 1)):
            tapes[tape].update((j, '1') for j in range(length))
        tapes[m.A].update((j, '0') for j in range(v))
        tapes[m.MODE][0] = '0'
        cpu = CPU(code, tapes)
        cpu.pc = labels['prefix']
        cpu.run(1000*(v+1), stop_pc=labels['finish'])
        require(cpu.pc == labels['finish'] and not cpu.rejected, 'isolated axis completed')
        require(cpu.steps == 99*v+153*n+48*a+16, 'exact complete-axis census')
        require(cpu.cells[m.B] == {-1: '|', **{j: '0' for j in range(v)}}, 'axis complete output')
        require(cpu.cells[m.A] == {-1: '|'}, 'axis input retirement')
        require(all(cpu.cells[t] == {-1: '|'} for t in (m.LEFT, m.RIGHT, m.LOUT, m.ROUT, *m.INPUTS, m.NUM)), 'axis scratch retirement')
        require(all(pos == (1 if t == m.F else 0) for t, pos in enumerate(cpu.positions)), 'axis local heads')
        cases += 1
        instructions += cpu.steps
    return {'isolated_axis_cost_cases': cases, 'independent_local_transitions': instructions,
            'exact_complete_axis_cost': '99*V + 153*N + 48*A + 16, before next-axis geometry or final commit',
            'scope': 'Isolated guide-driven axis slices, including small generalized guide lengths; these are cost checks, not claims of complete selected m=9 packets.'}


def component_checks(m):
    codes = [helper_graph(m, row) for row in m.ROWS]
    cases = accepts = transitions = 0
    for w in (2, 3):
        for numbers in itertools.product(range(-(1 << (w-1)), 1 << (w-1)), repeat=4):
            for i, code in enumerate(codes):
                steps, ok = helper_case(m, code, i, w, numbers)
                cases += 1
                accepts += ok
                transitions += steps
    for w in (4, 7, 31, 257, 2048):
        low, high = -(1 << (w-1)), (1 << (w-1))-1
        fixtures = ((low, low, low, low), (high, high, high, high), (low, 0, 0, 0),
                    (high, low, high, high), (0, 0, 0, 0), (1, 0, 0, 1))
        for numbers in fixtures:
            for i, code in enumerate(codes):
                steps, ok = helper_case(m, code, i, w, numbers)
                cases += 1
                accepts += ok
                transitions += steps
    # Each mutant changes an emitted local program, not just an expected report.
    controls = []
    original = codes[0]
    parity = next(i for i, insn in enumerate(original) if insn[0] == 'read' and insn[1] == m.NUM and set(insn[2]) == {'0', '1'} and original[insn[2]['0']] == ('write', m.NUM, '_') and original[insn[2]['1']][0] == 'read' and original[insn[2]['1']][2] == {})
    mutant = list(original)
    mutant[parity] = ('read', m.NUM, {'0': original[parity][2]['0'], '1': original[parity][2]['0']})
    try:
        helper_case(m, mutant, 0, 3, (1, 0, 0, 0))
    except ValueError:
        controls.append('odd numerator incorrectly admitted')
    else:
        raise ValueError('parity mutant escaped')
    mutant = helper_graph(m, (1, 1, 1, -1))
    try:
        helper_case(m, mutant, 0, 4, (0, 2, 0, 0))
    except ValueError:
        controls.append('conjugate/wrong C signs')
    else:
        raise ValueError('sign mutant escaped')
    # A harmless extra instruction changes only the exact helper cost census.
    # It is not claimed to refute the generous whole-program asymptotic bound.
    mutant = []
    for insn in original:
        if insn[0] == 'goto':
            mutant.append(('goto', insn[1]+1))
        elif insn[0] == 'read':
            mutant.append(('read', insn[1], {s: target+1 for s, target in insn[2].items()}))
        else:
            mutant.append(insn)
    mutant.insert(0, ('read', m.HEADER, {'|': 1, '_': 1, '0': 1, '1': 1}))
    try:
        helper_case(m, mutant, 0, 3, (0, 0, 0, 0))
    except ValueError as exc:
        require(str(exc) == 'exact component tariff', 'cost mutant failed elsewhere')
        controls.append('functionally unchanged helper cost drift')
    else:
        raise ValueError('cost census mutant escaped')
    return {'complete_component_cases': cases, 'accepted_components': accepts, 'independent_local_transitions': transitions, 'exact_successful_helper_cost': '43*w+57, excluding wrapper halt', 'mutants_detected': controls}


def main():
    records = sources()
    require(sha((PACKAGE/'leaf.py').read_bytes()) == 'bb46c1a55f1119957a52cd61f2cd957f3f7ad1e9b818c54a852bde09a0773744', 'frozen scientific source')
    m = module(PACKAGE/'leaf.py', 'peer_positive_c_leaf')
    require(sha((PACKAGE/'PROOF.md').read_bytes()) == 'c99157c3c43ae490b858cdbce04d85f3661ca5d9752770506d18ec4876c4ed6c', 'reviewed proof')
    result = {'status': 'PASS_SOURCE_SPECTRAL_HELPER_REVIEW', 'proof_sha256': sha((PACKAGE/'PROOF.md').read_bytes()), 'leaf_sha256': sha((PACKAGE/'leaf.py').read_bytes()),
              'sources': records, 'graph': graph_checks(m), 'spectral_tensors': spectral_checks(),
              'geometry': geometry_checks(), 'axis_cost': axis_cost_checks(m), 'component_lowering': component_checks(m),
              'scope': 'Source pins, full exact Walsh-spectral kernels through 8 axes, exact literal component helpers including all width-2 and width-3 inputs. Not full-packet all-f execution; root provides separate dense runtime review.'}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
