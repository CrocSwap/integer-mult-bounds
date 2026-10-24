#!/usr/bin/env python3
"""Check the reduced interfaces with exact reverse ordered columns."""
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
SOURCE = LANES / 'new-core-transfer-20261017/bipartite-eight-transfer-20261018'
EIGHT = LANES / 'controller-followthrough-20261017/bipartite-eight-20261018'
PREVIOUS = LANES / 'new-core-transfer-20261017/structured-centres-transfer-20261018'
PINS = {
    'producer': '84b1156a0c58ced62ee5834a92d02147346032f7a8beb181b3efe35a539d86f1',
    'eight': 'c147770b253d8b33a18ba6edb766ab505d203ba8ecd16507764d9a8c1c98e1c1',
    'previous_review': 'fade8160a807a2687a007a67dec3f21cfe4ebcc1840130c6650e4e2acbc6fa3b',
    'interpreter': 'd55b2bcdce6764fb97d38bae212840047a739ecf20f17d180f3435e613e2df90',
}
path = REVIEW / 'structured-transfer-review-20261018/check.py'
if sha256(path.read_bytes()).hexdigest() != PINS['interpreter']:
    raise ValueError('Pinned independent reverse interpreter')
spec = importlib.util.spec_from_file_location('independent_s24_reverse', path)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
prior.INPUTS[str(path.relative_to(LANES.parent))] = {'sha256':PINS['interpreter']}
need, read, frozen = prior.need, prior.read, prior.frozen
atom, add, line = prior.atom, prior.add, prior.left
apply, multiply = prior.matrix_apply, prior.matrix_product


def identity(n=112):
    return [{p:Q(1)} for p in range(n)]


def sparse(raw):
    return [{int(p):Q(c) for p,c in row.items() if Q(c)} for row in raw]


def inverse(matrix):
    n = len(matrix)
    rows = [dict(row) for row in matrix]
    result = identity(n)
    determinant = Q(1)
    for col in range(n):
        pivot = next((row for row in range(col,n) if rows[row].get(col,0)),None)
        need(pivot is not None, 'Exact nonzero rational pivot')
        if pivot != col:
            rows[col],rows[pivot] = rows[pivot],rows[col]
            result[col],result[pivot] = result[pivot],result[col]
            determinant *= -1
        scale = rows[col][col]
        determinant *= scale
        rows[col] = {p:c/scale for p,c in rows[col].items()}
        result[col] = {p:c/scale for p,c in result[col].items()}
        for row in range(n):
            if row == col or not rows[row].get(col,0):
                continue
            factor = -rows[row][col]
            for target,source in ((rows[row],rows[col]),(result[row],result[col])):
                for p,c in source.items():
                    value = target.get(p,0)+factor*c
                    if value:
                        target[p] = value
                    else:
                        target.pop(p,None)
    need(rows == identity(n), 'Complete exact elimination')
    return result,determinant


def embedded_principal(matrix, subset):
    result = identity()
    for p in subset:
        result[p] = {q:c for q,c in matrix[p].items() if q in subset}
    return result


def derive(J, selected):
    S = set(selected)
    U = set(range(112))-S
    need(all(J[p].get(q,0)==J[q].get(p,0) for p in range(112) for q in range(112)),
         'Actual response is symmetric')
    L = embedded_principal(J,S)
    H = embedded_principal(J,U)
    Li,detL = inverse(L)
    Hi,detH = inverse(H)
    C = identity()
    upper,lower = identity(),identity()
    selected_inverse = identity()
    for p in range(112):
        if p in S:
            C[p] = {q:-c for q,c in J[p].items() if q in S}
            selected_inverse[p] = {q:-c for q,c in Li[p].items()}
            upper[p].update({q:-c for q,c in J[p].items() if q in U})
        else:
            C[p].update({q:-c for q,c in J[p].items() if q in S})
            lower[p].update({q:c for q,c in J[p].items() if q in S})
    N,detC = inverse(C)
    A = multiply(upper,multiply(Hi,C))
    Ai,_ = inverse(A)
    need(multiply(lower,selected_inverse)==N, 'Two-step suffix equals full C inverse')
    need(multiply(Ai,multiply(upper,Hi))==N, 'Long suffix equals full C inverse')
    for a,b in ((L,Li),(Li,L),(H,Hi),(Hi,H),(C,N),(N,C),(A,Ai),(Ai,A)):
        need(multiply(a,b)==identity(), 'Both exact matrix inverse orders')
    for matrix in (L,Li,H,Hi,C,N,A,Ai):
        need(all(c.denominator & (c.denominator-1)==0 for row in matrix for c in row.values()),
             'All complete scalar maps are dyadic')
    return dict(J=J,L=L,Li=Li,H=H,Hi=Hi,C=C,N=N,A=A,Ai=Ai,upper=upper,
                lower=lower,selected_inverse=selected_inverse,U=U,
                determinants={'L':str(detL),'H':str(detH),'C':str(detC)})


def compiled_program(program, c):
    need(program['events']==program['prefix']+program['input_exchange']+
         program['retained_core']+program['suffix'], 'Complete serialized native word')
    pre,pre_price = prior.boundary(program['prefix']+program['input_exchange'],0)
    post,post_price = prior.boundary(program['suffix'],1)
    core,bill = prior.core(program['retained_core'],c,program['orientation'])
    operations = [('operator',p,p+1) for p in range(112)]+pre
    operations += [('operator',p,-p-1) for p in range(112)]+core
    operations += [('operator',112+p,-p-1) for p in range(112)]+post
    operations += [('operator',112+p,p+1) for p in range(112)]
    return operations,pre_price+post_price+bill['dyadic_real_primitives']


def gauge_map(matrix, events, offset=0):
    result = [atom(i) for i in range(640)]
    result[offset:offset+112] = apply(matrix,result[offset:offset+112])
    if any(e['kind']=='clear' for e in events):
        result[632] = {}
    return result


def cross_events(J, selected, lower):
    result = []
    S = set(selected)
    for p in range(112):
        for q,c in sorted(J[p].items()):
            if ((p not in S and q in S) if lower else (p in S and q not in S)):
                result.append({'kind':'add','target':p,'source':q,
                               'coefficient':str(c if lower else -c),'frame':1})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    out = parser.parse_args().out
    need(not out.exists(), 'New output directory')
    need(shutil.disk_usage(HERE).free>=3*1024**3, 'At least 3 GiB free disk')
    freeze = frozen(SOURCE,'FREEZE.json',PINS['producer'])
    frozen(EIGHT,'FREEZE.json',PINS['eight'])
    frozen(REVIEW/'structured-transfer-review-20261018','FREEZE.json',PINS['previous_review'])
    previous_freeze = frozen(PREVIOUS,'FREEZE.json',prior.PINS['transfer'])
    packet = read(SOURCE/'run-normal/REDUCED-INTERFACES-PROGRAMS.json.gz',
                  freeze['payload_decompressed_sha256'],True)
    eight = read(EIGHT/'BIPARTITE-EIGHT-PROGRAM.json.gz',
                 '0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee',True)
    previous = read(PREVIOUS/'scaled-normal/STRUCTURED-TRANSFER-PROGRAMS.json.gz',
                    previous_freeze['payload_decompressed_sha256']['scaled'],True)
    structured = read(LANES/'controller-followthrough-20261017/structured-centres/STRUCTURED-CENTRES-PROGRAM.json.gz',
                      '2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1',True)
    clean = read(LANES/'new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz',prior.PINS['clean'],True)
    bridge = read(PREVIOUS/'NATIVE-GEOMETRY-BRIDGE.json')
    reports,controls = {},{}
    need(set(packet['families'])=={'eight','twenty_four'}, 'Both complete construction families')
    for family,data in packet['families'].items():
        need(family in ('eight','twenty_four'), 'Known literal family')
        selected = data['selected_S']
        J = sparse(eight['response']) if family=='eight' else [
            {p:-c for p,c in row.items()} for row in sparse(structured['response'])]
        need(selected==(eight['selected_ports'] if family=='eight' else previous['selected_S']),
             'Actual source selection')
        matrices = derive(J,selected)
        U = matrices['U']
        need(data['ordinary_U']==sorted(U), 'Actual ordinary ports')
        expected = prior.expected_maps(selected,J,matrices['H'],matrices['Hi'],
                                       matrices['A'],matrices['Ai'],U)
        expected['long_normalized_backward'] = expected['normalized_backward']
        expected['short_normalized_backward'] = expected['normalized_backward']
        family_report = {'determinants':matrices['determinants'],'providers':{}}
        need(set(data['providers'])=={'base','extra'}, 'Both actual providers')
        for provider,item in data['providers'].items():
            c = item['canonical']
            phase_path = REVIEW/provider/'CANONICAL-WORD.json.gz'
            need(sha256(phase_path.read_bytes()).hexdigest()==
                 bridge['providers'][provider]['phase_canonical_compressed_sha256'],
                 'Exact canonical phase-provider bytes')
            phase_c = read(phase_path,zipped=True)
            need(c==phase_c==previous['providers'][provider]['canonical']==clean['providers'][provider]['canonical'],
                 'Actual canonical geometry is unchanged')
            prior.physical_frames(c)
            words = item['local_words']
            native_source = eight['providers'][provider] if family=='eight' else previous['providers'][provider]
            need(c==native_source['canonical'], 'Source response uses this exact canonical geometry')
            for program in item['programs'].values():
                direction = program['orientation']
                source_core = native_source['programs'][direction] if family=='eight' else next(
                    v['retained_core'] for v in native_source['programs'].values() if v['orientation']==direction)
                need(program['retained_core']==source_core, 'Exact complete source core')
                need([e for e in source_core if prior.native(e)] ==
                     [e for e in clean['providers'][provider]['programs'][direction] if prior.native(e)],
                     'Exact retained native records and phase dependency')
            gauge_checks = {}
            for name,events in words.items():
                matrix_name = {'long_normalizer_X':'N','short_normalizer_X':'N',
                               'lower_X':'lower','upper_X':'upper','ordinary_Y':'H',
                               'ordinary_inverse_X':'Hi','selected_inverse_X':'selected_inverse'}[name]
                offset = 112 if name=='ordinary_Y' else 0
                operations,price = prior.boundary(events,0 if offset else 1)
                check = prior.reverse(operations,gauge_map(matrices[matrix_name],events,offset))
                check['dyadic_real_primitives'] = price
                gauge_checks[name] = check
            if family=='eight':
                need(all(e['target']<224 and e.get('source',0)<224 and e['kind'] in ('add','scale')
                         for events in words.values() for e in events), 'Eight-port gauges use no owned field')
                need(words['short_normalizer_X']==words['selected_inverse_X']+words['lower_X'],
                     'Selected inverse precedes the lower update')
                need(words['lower_X']==cross_events(J,selected,True) and
                     words['upper_X']==cross_events(J,selected,False), 'Actual complete cross shears')
                need(len(words['lower_X'])==len(words['upper_X'])==144 and
                     all(abs(Q(e['coefficient']))==Q(1,2) for name in ('lower_X','upper_X') for e in words[name]),
                     'Exact cross-shear count and coefficients')
                prior_gauges = previous['providers'][provider]['gauge_words']
                had_y = []
                for event in prior_gauges['hadamard_X']:
                    event = dict(event,target=event['target']+112,frame=0)
                    if 'source' in event:
                        event['source'] += 112
                    had_y.append(event)
                need(words['ordinary_Y'][-352:]==had_y and
                     words['ordinary_inverse_X'][-352:]==prior_gauges['hadamard_inverse_X'],
                     'Both paid Hadamard words retain their 32 physical exchanges')
                expected_costs = dict(raw_backward=87568,raw_forward=87776,balanced_backward=91264,
                                      balanced_forward=91472,diagonal_backward=92704,
                                      long_normalized_backward=99472,short_normalized_backward=89200)
                gauge_costs = dict(long_normalizer_X=11904,short_normalizer_X=1632,lower_X=1440,
                                   upper_X=1440,ordinary_Y=3696,ordinary_inverse_X=3696,selected_inverse_X=192)
            else:
                expected_costs = dict(long_normalized_backward=96012,short_normalized_backward=89592)
                gauge_costs = dict(long_normalizer_X=8028,short_normalizer_X=1608)
                need(item['programs']['long_normalized_backward']==
                     previous['providers'][provider]['programs']['normalized_backward'],
                     'The prior complete 24-port long word is unchanged')
            need({name:r['dyadic_real_primitives'] for name,r in gauge_checks.items()}==gauge_costs,
                 'All independently counted gauge invoices')
            need(set(item['programs'])==set(expected_costs), 'Every declared complete word is present')
            checks = {}
            for name,program in item['programs'].items():
                need(program['input_exchange']==prior.selected_exchange(selected,0),
                     'Literal physical input exchanges')
                prefix = words['ordinary_Y'] if name=='balanced_forward' else []
                suffix = (words['ordinary_inverse_X'] if name=='balanced_backward' else
                          words['ordinary_inverse_X']+words['upper_X'] if name=='diagonal_backward' else
                          words['long_normalizer_X'] if name=='long_normalized_backward' else
                          words['short_normalizer_X'] if name=='short_normalized_backward' else
                          prior.selected_exchange(selected,1) if program['orientation']=='forward' else [])
                need(program['prefix']==prefix and program['suffix']==suffix, 'Exact local word composition')
                operations,price = compiled_program(program,c)
                check = prior.reverse(operations,expected[name],private=True)
                need(price==expected_costs[name], 'Complete independent scalar invoice')
                if name.endswith('normalized_backward'):
                    for p in range(112):
                        x_part = {key:value for key,value in expected[name][p].items() if key[1]<112}
                        need(x_part==(line(atom(p),p,1) if p in selected else atom(p)),
                             'Full original-X block is exactly diag(Q,I)')
                    if name=='short_normalized_backward':
                        mistaken = deepcopy(expected[name])
                        ai_y = apply(matrices['Ai'],[atom(112+p) for p in range(112)])
                        for p in range(112):
                            mistaken[p] = line(atom(p),p,1) if p in selected else atom(p)
                            add(mistaken[p],line(ai_y[p],p,-1) if p in selected else
                                {key:-v for key,v in ai_y[p].items()})
                        need(mistaken!=expected[name], 'The borrowed-source Q order is material')
                        try:
                            prior.reverse(operations,mistaken,private=True)
                        except ValueError:
                            controls[family+'/'+provider+'/wrong_Q_order_rejected'] = True
                        else:
                            raise ValueError('Wrong Q order in the normalized borrowed term')
                if program['orientation']=='backward':
                    need(all(line(expected[name][112+p],p,-1)==atom(p) for p in selected),
                         'Every productive selected physical Y is original X')
                check.update(dyadic_real_primitives=price,native_mass=5073,native_children=3507,
                             logical_helpers_restored=408,owned_zero_outputs=8)
                checks[name] = check
            if family=='eight':
                bad = deepcopy(item['programs']['short_normalized_backward'])
                bad['suffix'] = words['lower_X']+words['selected_inverse_X']
                bad['events'] = bad['prefix']+bad['input_exchange']+bad['retained_core']+bad['suffix']
                operations,_ = compiled_program(bad,c)
                try:
                    prior.reverse(operations,expected['short_normalized_backward'],private=True)
                except ValueError:
                    controls[provider+'/old_selected_query_rejected'] = True
                else:
                    raise ValueError('The lower shear used the old selected fields')
            family_report['providers'][provider] = {'programs':checks,'gauges':gauge_checks,
                                                    'long_short_full_map_equal':True}
            print(family,provider,'complete maps, frames, restoration and invoices PASS',flush=True)
        reports[family] = family_report
    result = {'status':'PASS_INDEPENDENT_REDUCED_SELECTED_INTERFACES','complete_words_checked':18,
              'families':reports,'negative_controls':controls,
              'method':'Reverse ordered columns with exact rational block inversion; no producer import.',
              'scope':'Complete local words. Native phases inherit exact unchanged reviewed records. No global controller, hosting, precision, supplier or kappa claim.',
              'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    out.mkdir(parents=True)
    (out/'REVIEW.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (out/'INPUTS.json').write_text(json.dumps(prior.INPUTS,indent=2,sort_keys=True)+'\n')
    print(result['status'],flush=True)


if __name__=='__main__':
    main()
