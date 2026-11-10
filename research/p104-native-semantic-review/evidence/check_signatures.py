"""Current compiler output, checked independently on all exact task signatures.

This is not an all-column dense replay. The separate retained literal Pauli
interpreter plus exact dense zero column determine each individual Clifford,
including phase. Every recipe is emitted by the actual current compiler.
"""
from pathlib import Path
from functools import lru_cache
from hashlib import sha256
import argparse
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('signature_map_compare', HERE/'compare_maps.py')
B = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = B
spec.loader.exec_module(B)


def run(comparison=None):
    B.authenticate()
    comparison = B.run() if comparison is None else comparison
    sys.path.insert(0, str(HERE/'vendor/current'))
    C = B.load('signature_actual_current_compiler', 'current/prefix_clifford.py')
    V = B.load('signature_independent_literal', 'literal.py')
    D = B.load('signature_independent_dense', 'dense.py')
    w = B.read('inputs/CURRENT-WORD.json.gz')

    @lru_cache(None)
    def chart(i):
        return C.canonical_frame(9, tuple(w['frames'][i]))

    @lru_cache(None)
    def frame(i):
        return V.frame(tuple(w['frames'][i]), 9)

    @lru_cache(None)
    def emit(kind, a, b, q):
        if kind == 'internal':
            op = chart(a).adjoint().then(chart(b))
        elif kind == 'main_in':
            op = C.cgate(9, q, 1).adjoint().then(chart(a))
        else:
            B.need(kind == 'main_out', 'actual native task kind')
            op = chart(a).adjoint().then(C.cgate(9, q, -1).then(C.fourier(9)))
        recipe, _ = C.lower_child(op)
        return recipe

    @lru_cache(None)
    def signature(circuit):
        tab = V.tableau(circuit)
        real, imag, den = D.dense_column(D.compile_circuit(circuit), 0)
        B.need(sum(a*a+b*b for a,b in zip(real,imag)) == 1 << (2*den),
               'exact nonzero normalized zero column')
        return tab, den, tuple((j,a,b) for j,(a,b) in enumerate(zip(real,imag)) if a or b)

    matched = {tuple(t['current']): t for t in comparison['matched']}
    unmatched = {tuple(t['current']): t for t in comparison['unmatched']}
    records = []
    recipes = {}
    adapters = {}
    for task in B.inventory(w):
        kind, a, b, q = task
        recipe = emit('internal' if kind in ('move','helper') else kind, a, b, q)
        if kind in ('move','helper'):
            expected = V.adjoint(frame(a)) + frame(b)
            recipes[a,b] = recipe
        elif kind == 'main_in':
            expected = V.adjoint((('C',q,1),)) + frame(a)
            adapters[kind,a,q] = recipe
        else:
            expected = V.adjoint(frame(a)) + (('C',q,-1),) + V.fourier(9)
            adapters[kind,a,q] = recipe
        actual = V.recipe(recipe)
        got, want = signature(actual), signature(expected)
        B.need(got == want, 'actual current emitted recipe full signed phase signature '+str(task))
        item = matched.get(task, unmatched.get(task))
        B.need(item is not None and recipe['rank'] == item['rank'], 'actual current recipe preserves paid rank')
        digest = sha256(json.dumps(got,separators=(',',':')).encode()).hexdigest()
        B.need(digest == item['normal_form_sha256'], 'actual output agrees with independently compared normal form')
        records.append({'task':list(task), 'rank':recipe['rank'], 'normal_form_sha256':digest,
                        'recipe_sha256':sha256(json.dumps(recipe,sort_keys=True,separators=(',',':')).encode()).hexdigest()})

    # Match the ordering of the literal current native(w,C,V) payload exactly.
    payload = [[a,b,recipes[a,b]] for a,b in sorted(recipes)]
    for r,q in zip(w['live'],w['ports']):
        payload.append(adapters['main_in',w['initial'][r],q])
        payload.append(adapters['main_out',w['final'][r+112],q])
    B.need(len(recipes)==2939 and len(records)==3184 and len(adapters)==208,
           'entire actual current internal and intrinsic-adapter inventory')
    first = emit('internal', *next(iter(recipes)), 0)
    actual = V.recipe(first)
    wrong = actual + (('phase',1),)
    B.need(signature(actual)[0] == signature(wrong)[0] and signature(actual) != signature(wrong),
           'current-output phase-only fault is rejected independently')
    return {'schema':'all-current-emitted-native-signatures/1',
            'status':'PASS_ALL_CURRENT_EMITTED_RECIPES_EXACT_PHASE_SIGNATURES',
            'typed_tasks':len(records), 'internal_frame_pairs':len(recipes), 'intrinsic_main_adapters':len(adapters),
            'matched_typed_tasks':len(matched), 'unmatched_typed_tasks':len(unmatched),
            'actual_recipe_emissions':emit.cache_info().misses,
            'exact_signatures_evaluated':signature.cache_info().misses,
            'recipe_payload_sha256':sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'records':records, 'phase_only_control_rejected':True,
            'scope':'Actual current compiler outputs, independently checked via all18 signed Pauli images and the complete exact nonzero U|0> vector. Individual Clifford equality implies every literal columnwise tensor power; it does not tensorize a scalar operator sum. No full512-column replay of unchanged maps, no historical suite or scientific admission.'}


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    r=run();raw=json.dumps(r,sort_keys=True,indent=2)+'\n';path=HERE/'SIGNATURES.json'
    if a.write:path.write_text(raw)
    else:B.need(path.read_text()==raw,'read-only current emitted-signature receipt')
    print(json.dumps({k:r[k] for k in ('status','typed_tasks','internal_frame_pairs','intrinsic_main_adapters','recipe_payload_sha256')},sort_keys=True))
