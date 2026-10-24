#!/usr/bin/env python3
"""Check live-field line recipes and complete forward words independently."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import shutil


HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent
LANES = REVIEW.parent
SOURCE = LANES / 'new-core-transfer-20261017/forward-eight-phase-20261018'
REDUCED = LANES / 'new-core-transfer-20261017/bipartite-eight-transfer-20261018'
EIGHT = LANES / 'controller-followthrough-20261017/bipartite-eight-20261018'
PINS = {
    'producer': 'af400bac97eeb1231b30e6ee74ccf7ffc818133c555d7232c2b60234dd04fc42',
    'reduced': '84b1156a0c58ced62ee5834a92d02147346032f7a8beb181b3efe35a539d86f1',
    'reduced_review': 'a5c4619ba3e3a627f136dadda4b3c2e94ca0653acc4943f66a9ceab595218f9e',
    'eight': 'c147770b253d8b33a18ba6edb766ab505d203ba8ecd16507764d9a8c1c98e1c1',
    'interpreter': 'd55b2bcdce6764fb97d38bae212840047a739ecf20f17d180f3435e613e2df90',
    'child_definition': '087ad4cc683e5caf1f2a8cd62d5f65c9b4dde2636593b417f8f5099a29875c8b',
}
path = REVIEW / 'structured-transfer-review-20261018/check.py'
if sha256(path.read_bytes()).hexdigest() != PINS['interpreter']:
    raise ValueError('Pinned independent reverse interpreter')
spec = importlib.util.spec_from_file_location('independent_forward_reverse',path)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
prior.INPUTS[str(path.relative_to(LANES.parent))] = {'sha256':PINS['interpreter']}
need,read,frozen = prior.need,prior.read,prior.frozen
atom,add,line = prior.atom,prior.add,prior.left


def plus(a,b):
    return a[0]+b[0],a[1]+b[1]


def times(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def power(a,n):
    result = (1,0)
    for _ in range(n):
        result = times(result,a)
    return result


def permutation(record):
    need(set(record)=={'matrix_rows','offset','quadratic_rows','linear_Z4','phase'},
         'Complete serialized monomial record')
    need(record['offset']==record['phase']==0 and record['quadratic_rows']==[0]*9 and
         record['linear_Z4']==[0]*9, 'Exact pure permutation with zero phase')
    rows = record['matrix_rows']
    need(len(rows)==9 and all(isinstance(r,int) and 0<=r<512 for r in rows), 'Nine-bit binary matrix')
    images = [sum(((r & value).bit_count()%2)<<bit for bit,r in enumerate(rows)) for value in range(512)]
    need(sorted(images)==list(range(512)), 'Exact binary permutation')
    return images


def apply_recipe(values,left,right):
    moved = [(0,0)]*512
    for source,target in enumerate(right):
        moved[target] = values[source]
    child = [plus(times((1,1),moved[z]),times((1,-1),moved[z^1])) for z in range(512)]
    result = [(0,0)]*512
    for source,target in enumerate(left):
        result[target] = child[source]
    return result


def native_lines(records,selected,labels):
    need(len(records)==8 and [r['port'] for r in records]==selected, 'Eight ordered actual recipes')
    full = [times(power((1,1),9-z.bit_count()),power((1,-1),z.bit_count())) for z in range(512)]
    results = {}
    for entry in records:
        p,v,recipe = entry['port'],entry['label'],entry['recipe']
        need(v==labels[p] and entry['power']==1 and entry['exact_circuit']==[['C',v,1]],
             'Actual positive spatial line')
        need(recipe['rank']==1, 'One rank-one native child')
        left,right = permutation(recipe['left']),permutation(recipe['right'])
        need(left[1]==v and all(left[right[z]]==right[left[z]]==z for z in range(512)),
             'Exact inverse wrappers and actual child direction')
        for source in range(512):
            column = [(0,0)]*512
            column[source] = (1,0)
            actual = apply_recipe(column,left,right)
            expected = [(0,0)]*512
            expected[source],expected[source^v] = (1,1),(1,-1)
            need(actual==expected, 'Every exact spatial column, including global phase')
            # FULL has denominator 2^9. Both products below have denominator 2^10.
            full_column = [full[z^source] for z in range(512)]
            q_full = apply_recipe(full_column,left,right)
            full_q = [plus(times((1,1),full[z^source]),times((1,-1),full[z^source^v]))
                      for z in range(512)]
            need(q_full==full_q, 'Every exact FULL commutation column')
        zero = [(0,0)]*512;zero[0]=(1,0)
        actual = apply_recipe(zero,left,right)
        negative = [(0,0)]*512;negative[0],negative[v]=(1,-1),(1,1)
        need(actual!=negative and [(-a,-b) for a,b in actual]!=actual,
             'Wrong line sign and wrong global sign both reject')
        results[p] = {'label':v,'rank':1,'pure_permutation_wrappers':2,
                      'exact_spatial_columns':512,'exact_FULL_commutation_columns':512,
                      'nonzero_recipe_coefficients_checked':1024,
                      'inverse_line_rejected':True,'global_minus_sign_rejected':True}
        print('native line',p,'all spatial and FULL columns PASS',flush=True)
    return results


def subtraction(J,selected):
    direct,scaled = [],[]
    S = set(selected)
    for p in selected:
        scaled.append({'kind':'scale','target':p,'coefficient':'2','frame':1})
        need(len(J[p])==20 and all(abs(c)==Q(1,2) for c in J[p].values()),
             'Twenty actual half-coefficients per selected row')
        for q,c in sorted(J[p].items()):
            source = 112+q if q in S else q
            direct.append({'kind':'add','target':p,'source':source,'coefficient':str(-c),'frame':1})
            scaled.append({'kind':'add','target':p,'source':source,'coefficient':str(-2*c),'frame':1})
        scaled.append({'kind':'scale','target':p,'coefficient':'1/2','frame':1})
    return direct,scaled


def expected_map(J,selected,balanced):
    result = [atom(i) for i in range(640)]
    S = set(selected)
    for p in range(112):
        if p in S:
            result[p] = line(atom(p),p,1)
        else:
            result[112+p] = {} if balanced else atom(112+p)
            for q,c in J[p].items():
                if q in S:
                    add(result[112+p],line(atom(112+q),q,-1),c)
                else:
                    add(result[112+p],atom(q),c)
                    if balanced:
                        add(result[112+p],atom(112+q),c)
    result[632:] = [{} for _ in range(8)]
    return result


def compile_complete(program,c,selected,recipes):
    prefix = program['prefix']+program['input_exchange']
    need(program['events']==prefix+program['retained_core']+program['output_exchange']+program['phase_suffix'],
         'Complete serialized forward word')
    pre,pre_price = prior.boundary(prefix,0)
    output,output_price = prior.boundary(program['output_exchange'],1)
    core,bill = prior.core(program['retained_core'],c,'forward')
    suffix = program['phase_suffix']
    children = []
    for p,event in zip(selected,suffix[:8]):
        need(event=={'kind':'data_line','target':p,'port':p,'power':1,'frame':1,'recipe':recipes[p]},
             'Direct live selected-X call at the actual FULL frame')
        children.append(('operator',p,p+1))
    need(len(children)==8 and all(e['kind'] in ('add','scale') and e['target']<224 and
                                  e.get('source',0)<224 for e in suffix[8:]),
         'Eight native calls followed by scalar data operations only')
    scalar,scalar_price = prior.boundary(suffix[8:],1)
    initial = [('operator',p,p+1) for p in range(112)]+pre
    initial += [('operator',p,-p-1) for p in range(112)]+core
    initial += [('operator',112+p,-p-1) for p in range(112)]+output
    final = [('operator',112+p,p+1) for p in range(112)]
    operations = initial+children+scalar+final
    price = pre_price+output_price+scalar_price+bill['dyadic_real_primitives']
    profile = Counter(bill['profile']);profile[1] += 8
    need(dict(profile)=={1:2441,2:724,3:228,4:102,5:20}, 'Complete native profile')
    return operations,price,initial,children,scalar,final


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    out = parser.parse_args().out
    need(not out.exists(), 'New output directory')
    need(shutil.disk_usage(HERE).free>=3*1024**3, 'At least 3 GiB free disk')
    freeze = frozen(SOURCE,'FREEZE.json',PINS['producer'])
    reduced_freeze = frozen(REDUCED,'FREEZE.json',PINS['reduced'])
    frozen(REVIEW/'reduced-transfer-review-20261018','FREEZE.json',PINS['reduced_review'])
    source_freeze = frozen(EIGHT,'FREEZE.json',PINS['eight'])
    child_path = LANES/'interface-proof/verify_native_lift.py'
    need(sha256(child_path.read_bytes()).hexdigest()==PINS['child_definition'], 'Pinned source child convention')
    prior.INPUTS[str(child_path.relative_to(LANES.parent))] = {'sha256':PINS['child_definition']}
    packet = read(SOURCE/'scaled-normal/FORWARD-EIGHT-PROGRAMS.json.gz',
                  freeze['payload_decompressed_sha256']['scaled-normal'],True)
    reduced = read(REDUCED/'run-normal/REDUCED-INTERFACES-PROGRAMS.json.gz',
                   reduced_freeze['payload_decompressed_sha256'],True)
    source = read(EIGHT/'BIPARTITE-EIGHT-PROGRAM.json.gz',source_freeze['payload_decompressed_sha256'],True)
    selected = packet['selected_S']
    need(selected==source['selected_ports']==[0,7,15,36,42,46,79,89], 'Actual selected set')
    need(packet['ordinary_U']==sorted(set(range(112))-set(selected)), 'Actual ordinary set')
    labels = source['providers']['base']['canonical']['ports']
    native_checks = native_lines(packet['line_recipes'],selected,labels)
    recipes = {r['port']:r['recipe'] for r in packet['line_recipes']}
    J = [{int(p):Q(c) for p,c in row.items()} for row in source['response']]
    direct,scaled = subtraction(J,selected)
    need(packet['direct_subtraction']==direct and packet['scaled_subtraction']==scaled and
         packet['suffix'][8:]==scaled, 'Exact literal current-data subtraction')
    scalar_expected = [atom(i) for i in range(640)]
    for p in selected:
        for q,c in J[p].items():
            add(scalar_expected[p],atom(112+q if q in selected else q),-c)
    direct_ops,direct_price = prior.boundary(direct,1)
    scaled_ops,scaled_price = prior.boundary(scaled,1)
    prior.reverse(direct_ops,scalar_expected)
    prior.reverse(scaled_ops,scalar_expected)
    need((len(direct),direct_price,len(scaled),scaled_price)==(160,1600,176,1312),
         'Both scalar implementations and full invoices')
    reports = {}
    need(set(packet['providers'])=={'base','extra'}, 'Both actual providers')
    for provider,item in packet['providers'].items():
        c = item['canonical']
        original = reduced['families']['eight']['providers'][provider]
        need(c==original['canonical']==source['providers'][provider]['canonical'] and c['ports']==labels,
             'Exact retained canonical geometry and intrinsic labels')
        need(sorted(c['frames'][1])==[1<<i for i in range(9)], 'Actual FULL coordinate axes')
        prior.physical_frames(c)
        need(set(item['programs'])=={'raw_forward','balanced_forward'}, 'Both complete forward words')
        cases = {}
        for name,program in item['programs'].items():
            old = original['programs'][name]
            need(all(program[key]==old[key] for key in ('prefix','input_exchange','retained_core')) and
                 program['output_exchange']==old['suffix'] and program['phase_suffix']==packet['suffix'],
                 'Exact old complete word with one appended phase suffix')
            operations,price,before,children,scalars,after = compile_complete(program,c,selected,recipes)
            expected = expected_map(J,selected,name=='balanced_forward')
            check = prior.reverse(operations,expected,private=True)
            need(price==(92784 if name=='balanced_forward' else 89088), 'Complete scalar invoice')
            need(all(line(expected[112+p],p,-1)==line(atom(112+p),p,-1) for p in selected),
                 'Physical selected Y remains the arbitrary current q d')
            mutations = {
                'omit_positive_line':before+scalars+after,
                'inverse_line':before+[('operator',p,-p-1) for p in selected]+scalars+after,
                'omit_subtraction':before+children+after,
            }
            controls = []
            for label,changed in mutations.items():
                try:
                    prior.reverse(changed,expected,private=True)
                except ValueError:
                    controls.append(label)
                else:
                    raise ValueError('Boundary mutation accepted: '+label)
            check.update(dyadic_real_primitives=price,native_rank_mass=5081,native_children=3515,
                         new_rank_one_children=8,new_pure_permutation_wrappers=16,
                         new_owned_fields=0,new_private_fields=0,helpers_restored=408,
                         owned_zero_outputs=8,boundary_mutations_rejected=controls)
            cases[name] = check
            print(provider,name,'full map, arbitrary d, frames and invoice PASS',flush=True)
        reports[provider] = cases
    result = {'status':'PASS_INDEPENDENT_DIRECT_LIVE_EIGHT_PHASE','native_lines':native_checks,
              'complete_programs':reports,'complete_words_checked':4,
              'direct_scalar_price':direct_price,'scaled_scalar_price':scaled_price,
              'native_recipe_spatial_columns':4096,'FULL_commutation_spatial_columns':4096,
              'method':'Independent Gaussian-integer spatial matrices and reverse free-operator columns; no producer or native Clifford interpreter import.',
              'scope':'Exact local live-field calls and complete words. All 8 new children and 16 wrappers are explicit. Global hosting, routed composition, descriptor costs, exterior phase, recursive precision and the supplier remain open.',
              'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    out.mkdir(parents=True)
    (out/'REVIEW.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (out/'INPUTS.json').write_text(json.dumps(prior.INPUTS,indent=2,sort_keys=True)+'\n')
    print(result['status'],flush=True)


if __name__=='__main__':
    main()
