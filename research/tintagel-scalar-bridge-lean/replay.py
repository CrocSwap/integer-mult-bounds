#!/usr/bin/env python3
"""Offline packet replay: hash-locked selected-AST recognition and Lean checks.
Upstream Python is parsed as data and never imported or executed. The selected
recognizer is not exhaustive; its fixed whole-source digest is essential.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = '5fe7174cd3a6580a74e4c1bf8fa7b426e8673f1c285603bf3076d4e758d70731'
SOURCE_BLOB = '626a28614b07066528fd5f189d87cffa5015ac60'

def dump(x):
    return ast.dump(x, include_attributes=False)

def parse_block(s):
    return ast.parse(s).body

def match(node, s):
    expected = parse_block(s)
    got = node if isinstance(node, list) else [node]
    assert [dump(x) for x in got] == [dump(x) for x in expected], 'AST mismatch: ' + s[:90]

def functions(tree):
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

def assign_name(n, name):
    return isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)

def get_assign(body, name):
    return next(n for n in body if assign_name(n, name))

STAGES = "stages = [(0, 'F', 1), (1, 'B', 1), (2, 'F', 1)] + [x for p in range(2, k + 1) for x in ((2 * p - 1, 'B', p), (2 * p, 'F', p))]"

LOOP = """for t, kind, p in stages:
    for r in 'XY':
        climb((r, p), stage_in(t, r), True)
        climb((r, p), stage_out(t, r), False)
    log.append((kind, p))
    for q in range(2, k + 1):
        if t == 2 * q - 3:
            for r in 'XY': climb((r, q), cur[(r, q - 1)], True)
            gate(('X', q - 1), ('X', q), 1)
            gate(('Y', q), ('Y', q - 1), -1)
        if t == 2 * q - 2:
            for r in 'XY': climb((r, q), cur[(r, q - 1)], True)
            gate(('Y', q), ('Y', q - 1), 1)
            gate(('X', q - 1), ('X', q), -1)
"""

CLEANUP = """for q in range(k, 1, -1):
    gate(('Y', q - 1), ('Y', q), -1)
    gate(('X', q), ('X', q - 1), 1)
"""

SCALAR = """for op in log:
    if op[0] == 'F': S[('Y', op[1])] = sp.expand(S[('Y', op[1])] + S[('X', op[1])])
    elif op[0] == 'B': S[('X', op[1])] = sp.expand(S[('X', op[1])] - S[('Y', op[1])])
    else: S[op[1]] = sp.expand(S[op[1]] + op[3] * S[op[2]])
"""

def recognize(text):
    tree = ast.parse(text)
    fs = functions(tree)
    b = fs['check'].body
    match(fs['qS'], """def qS(blocks, h, l=0):
    return frozenset((c, j) for c in blocks for j in range(h) if j != l)
""")
    for name, expected in {
        'stage_in': """def stage_in(t, role):
    if t == 0: return frozenset([('b0', l)]) if role == 'X' else frozenset()
    base = B0 if role == 'X' else B0 - {('b0', l)}
    return base | qS(F[:t - 1], h, l)
""",
        'stage_out': """def stage_out(t, role):
    if t == 0: return B0 if role == 'X' else B0 - {('b0', l)}
    return stage_in(t, role) | qS([F[t - 1]], h, l)
""",
        'gate': """def gate(dst, src, sign):
    assert cur[dst] == cur[src], ('gate at unequal frames', dst, src)
    log.append(('G', dst, src, sign))
""",
        'climb': """def climb(key, new, idle_flag):
    old = cur[key]
    assert old <= new, ('not nested', key, len(old), len(new))
    if new != old:
        if idle_flag: idle[key].append(len(new) - len(old))
        else: inv_moves[key] += len(new) - len(old)
    cur[key] = new
""",
    }.items():
        match(next(n for n in b if isinstance(n, ast.FunctionDef) and n.name == name), expected)
    match(get_assign(b, 'stages'), STAGES)
    stage_loop = next(n for n in b if isinstance(n, ast.For) and isinstance(n.iter, ast.Name) and n.iter.id == 'stages')
    match(stage_loop, LOOP)
    idx = b.index(stage_loop)
    match(b[idx + 1], 'for key in cur: climb(key, final[key[0]], True)')
    match(b[idx + 2], CLEANUP)
    match(next(n for n in b if isinstance(n, ast.For) and isinstance(n.iter, ast.Name) and n.iter.id == 'log'), SCALAR)
    match(get_assign(b, 'final'), "final = {'X': allc, 'Y': allc - {('b0', l)}}")
    # Literals extracted from the recognized AST, not from hand-entered trace data.
    initial = ast.literal_eval(get_assign(b, 'stages').value.left)
    branch = stage_loop.body[2].body
    def gate_spec(expr):
        call = expr.value
        assert isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'gate'
        def addr(node):
            role, pair = node.elts
            assert isinstance(pair, (ast.Name, ast.BinOp))
            return (ast.literal_eval(role), 0 if isinstance(pair, ast.Name) else -ast.literal_eval(pair.right))
        return (addr(call.args[0]), addr(call.args[1]), ast.literal_eval(call.args[2]))
    guards = [(ast.literal_eval(n.test.comparators[0].right), [gate_spec(e) for e in n.body[1:]]) for n in branch]
    end = [gate_spec(e) for e in b[idx + 2].body]
    assert len(guards) == 2 and all(len(gs) == 2 for _, gs in guards) and len(end) == 2
    return {'initial_stages': initial, 'guards': guards, 'cleanup': end,
            'source_lines': {'stages': get_assign(b, 'stages').lineno,
                             'chronology': stage_loop.lineno, 'cleanup': b[idx+2].lineno}}

def source_trace(k, schema):
    assert k >= 1
    stages = list(schema['initial_stages']) + [(t, kind, p) for p in range(2, k+1) for t,kind in ((2*p-1, 'B'), (2*p, 'F'))]
    out = []
    def gates(q, gs):
        for dst,src,sign in gs:
            out.append(('G', (dst[0],q+dst[1]), (src[0],q+src[1]), sign))
    for t,kind,p in stages:
        out.append((kind,p,t))
        for q in range(2,k+1):
            for offset,gs in schema['guards']:
                if t == 2*q-offset: gates(q,gs)
    for q in range(k,1,-1): gates(q,schema['cleanup'])
    return out

def generate_lean(trace):
    lines=['import IndexedBridge', '', 'namespace Tintagel.Abelian',
           'variable {A : Type u} (G : Abelian A)', '',
           '/-- Literal source operations after hash-locked selected-AST recognition. Stage-indexed',
           'invocations permit distinct implementations; all share the same live helpers. -/',
           'def sourceB3With {H : Type v} (I : Nat → Invocation G H)',
           '    (p1 p2 p3 : Pair A) (h : H) : List (Pair A) × H :=']
    for i,op in enumerate(trace):
        if op[0]=='G':
            _,(dr,dp),(sr,sp),sg=op
            pos=1 if dr=='X' else 2; srcpos=1 if sr=='X' else 2
            changed=f'G.{"add" if sg==1 else "sub"} p{dp}.{pos} p{sp}.{srcpos}'
            pair=f'({changed}, p{dp}.2)' if pos==1 else f'(p{dp}.1, {changed})'
            lines.append(f'  let p{dp} := {pair} -- source operation {i+1}: {op!r}')
        else:
            kind,p,t=op
            lines.extend([f'  let r{i} := (I {t}).{"fwd" if kind=="F" else "bwd"} (p{p}, h) -- stage {t}',
                          f'  let p{p} := r{i}.1',f'  let h := r{i}.2'])
    lines += ['  ([p1, p2, p3], h)', '',
      'theorem sourceB3_is_indexed_chain {H : Type v} (I : Nat → Invocation G H)',
      '    (p q r : Pair A) (h : H) :',
      '    sourceB3With G I p q r h = indexedChain G I p [q,r] h := rfl', '',
      'theorem sourceB3_reduces_to_canonical {H : Type v} (I : Nat → Invocation G H)',
      '    (p q r : Pair A) (h : H) :',
      '    sourceB3With G I p q r h = (G.correct3 p q r, h) := by',
      '  simp only [sourceB3With, ' + ', '.join(f'(I {op[2]}).{"fwd_spec" if op[0]=="F" else "bwd_spec"}' for op in trace if op[0]!='G') + ']',
      '  rfl', '',
      'theorem sourceB3_all_inputs {H : Type v} (I : Nat → Invocation G H)',
      '    (p q r : Pair A) (h : H) :',
      '    sourceB3With G I p q r h = ([G.quarter p, G.quarter q, G.quarter r], h) := by',
      '  rw [sourceB3_reduces_to_canonical, b3_identity]', '',
      'theorem sourceB3_correlated_signed_endpoint {H : Type v} {Ω : Type w}',
      '    (I : Nat → Invocation G H) (p q r : Ω → Pair A) (h : Ω → H) (ω : Ω) :',
      '    let z := sourceB3With G I (p ω) (q ω) (r ω) (h ω)',
      '    (z.1.map G.signedExchange, z.2) = ([p ω, q ω, r ω], h ω) := by',
      '  simp only [sourceB3_all_inputs, List.map_cons, List.map_nil, signed_exchange_quarter]',
      '', 'end Tintagel.Abelian', '']
    for n in ('sourceB3_is_indexed_chain','sourceB3_reduces_to_canonical','sourceB3_all_inputs','sourceB3_correlated_signed_endpoint'):
        lines.append('#print axioms Tintagel.Abelian.'+n)
    return '\n'.join(lines)+'\n'

def main():
    if not __debug__:
        raise SystemExit('Run without Python -O: recognition uses assertions.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean', required=True, type=Path,
                        help='Absolute path to an already installed Lean 4.33.0 binary, not an elan shim.')
    parser.add_argument('--receipt', type=Path, help='Optional output JSON path; no proof source is modified.')
    args = parser.parse_args()
    lean = args.lean.expanduser().resolve(strict=True)
    if not args.lean.is_absolute():
        raise SystemExit('--lean must name an absolute installed binary path.')
    version = subprocess.run([str(lean), '--version'], check=True, capture_output=True, text=True, timeout=30).stdout.strip()
    if 'version 4.33.0,' not in version:
        raise SystemExit('Expected installed Lean 4.33.0; no installation is attempted.')
    raw = (HERE / 'sources/bridged.py.txt').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, 'Source digest mismatch'
    assert hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == SOURCE_BLOB
    schema = recognize(raw.decode())
    trace = source_trace(3, schema)
    generated = generate_lean(trace).encode()
    assert generated == (HERE / 'SourceBound.lean').read_bytes(), 'Generated B3 term differs from the submitted target'
    pin = json.loads((HERE / 'evidence/source-binding.json').read_text())
    assert json.loads(json.dumps(trace)) == pin['b3_trace']
    assert pin['source']['sha256'] == SOURCE_SHA256 and pin['source']['git_blob_sha1'] == SOURCE_BLOB
    expected = pin['expected_new_theorem_axioms']
    accepted = []
    failures = []
    all_axioms = []
    with tempfile.TemporaryDirectory(prefix='tintagel-scalar-replay-') as tmp:
        work = Path(tmp)
        for name in ('BridgeChain', 'IndexedBridge', 'SourceBound'):
            shutil.copyfile(HERE / (name + '.lean'), work / (name + '.lean'))
        env = {k: v for k, v in os.environ.items() if not k.startswith(('LEAN', 'LAKE'))}
        env['LEAN_PATH'] = str(work)
        def run(name, argv, success):
            r = subprocess.run([str(lean), '-t', '0', *argv], cwd=work, env=env,
                               capture_output=True, text=True, timeout=60)
            log = (r.stdout + r.stderr).replace(str(work) + '/', '')
            assert (r.returncode == 0 if success else r.returncode != 0 and 'error:' in log), (name, log)
            if success:
                assert 'sorryAx' not in log
                all_axioms.extend(s for s in log.splitlines() if s.startswith("'Tintagel."))
            result = {'target': name, 'returncode': r.returncode,
                      'diagnostic_sha256': hashlib.sha256(log.encode()).hexdigest()}
            if not success:
                result['first_error'] = next(s for s in log.splitlines() if 'error:' in s)
            return result
        for name in ('BridgeChain', 'IndexedBridge', 'SourceBound'):
            accepted.append(run(name, ['-o', name + '.olean', name + '.lean'], True))
        good = (work / 'SourceBound.lean').read_text()
        lines = good.splitlines()
        start = next(i for i,s in enumerate(lines) if '-- source operation 16:' in s)
        mutations = {
            'ChangedTwinSign': good.replace('G.sub p2.2 p1.2', 'G.add p2.2 p1.2', 1),
            'AscendingCleanup': '\n'.join(lines[:start] + lines[start+2:start+4] + lines[start:start+2] + lines[start+4:]) + '\n',
            'UnsignedEndpoint': good.replace('(z.1.map G.signedExchange, z.2)', '(z.1.map (fun p => (p.2, p.1)), z.2)', 1),
            'ChangedStageIndex': good.replace('(I 2).fwd (p1, h)', '(I 4).fwd (p1, h)', 1),
            'DroppedHelperThread': good.replace('  let h := r0.2\n', '', 1),
        }
        for name, text in mutations.items():
            assert text != good
            text = '\n'.join(s for s in text.splitlines() if not s.startswith('#print')) + '\n'
            (work / (name + '.lean')).write_text(text)
            failures.append(run(name, [name + '.lean'], False))
    assert len(all_axioms) == 22
    for name, axioms in expected.items():
        line = next(s for s in all_axioms if s.startswith("'Tintagel.Abelian." + name + "'"))
        assert (line.endswith('depends on axioms: [' + ', '.join(axioms) + ']') if axioms else
                line.endswith('does not depend on any axioms')), line
    receipt = {
        'status': 'PASS', 'lean_version': version,
        'lean_executable_sha256': hashlib.sha256(lean.read_bytes()).hexdigest(),
        'clean_temporary_build': True, 'trust_level': 0,
        'source_sha256': SOURCE_SHA256, 'source_git_blob_sha1': SOURCE_BLOB,
        'hash_locked_selected_ast_recognition': True, 'generated_target_byte_identical': True,
        'accepted_targets': accepted, 'rejected_negative_controls': failures,
        'transitive_axiom_reports': all_axioms,
        'proof_sha256': {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest()
                         for n in ('BridgeChain.lean', 'IndexedBridge.lean', 'SourceBound.lean')},
        'boundary': 'No upstream Python executed. Recognition is selected and hash-locked, not an exhaustive or verified Python semantics. Physical-provider obligations remain separate.'
    }
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'compiled_targets': len(accepted),
                      'transitive_axiom_reports': len(all_axioms),
                      'lean_negative_controls_rejected': len(failures)}))

if __name__ == '__main__':
    main()
