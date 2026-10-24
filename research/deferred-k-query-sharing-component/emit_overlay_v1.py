#!/usr/bin/env python3
"""One exact balanced-T occurrence overlay; original emitter/native bodies unchanged.
Producer only: output remains pending independent verification. No source evaluator,
checker, native, phase or price engine is imported. Chris R / Clear1nsight with
substantial OpenAI Codex assistance; Apache-2.0. Original peer/source credit retained.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

PINS={
 'base_packet':'7f26477b561114e1189d1ac7e00fd5cf5b1aea4881433619c931c12c01eb1ffd',
 'base_result':'9a895a972a523ef7a96dccdd31d357d8c6503db961bc8a3d37d13204b47a729d',
 'base_custody':'a94e060c654b4e3765fd71e1966f51c0b214a585a3ae6f9f4ae5aa5815764c1a',
 'identity_audit':'227397cd725bf55c97a9d760899360e68daca76257060c614dbea687855928a2',
 'identity_sources':'8aee92044ee72e19edbd61dbdc44f98401d7a0bc590cc90bc372cd5865067e9a',
 'q_audit':'fb60187fea8346539abb61a08b1c525825cc84bd7c2847eb44a7c9590f3abee3',
 'q_binding':'d1b2918c00a0987c763593b9383ee239bdce5a54ad6bec3bf1d1670661eed6e7'}
E_FIELDS=[f'y{i}' for i in range(112)]+[f'h{j}' for j in range(8)]
K_FIELDS=[f'k{j}' for j in range(8)]

def need(ok,message):
    if not ok:raise ValueError(message)

def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def inputs(manifest_path):
    manifest_path=manifest_path.resolve();m=json.loads(manifest_path.read_bytes());rows={r['role']:r for r in m['inputs']}
    need(set(rows)==set(PINS),'this producer requires exactly its seven frozen source roles')
    data={}
    for role,want in PINS.items():
        row=rows[role];p=manifest_path.parent/row['frozen']
        need(not p.is_symlink() and p.resolve().is_relative_to(manifest_path.parent),'source path escaped frozen root')
        raw=p.read_bytes();need(len(raw)==row['bytes'] and sha256(raw).hexdigest()==want==row['sha256'],'source hash/length changed: '+role)
        data[role]=json.loads(raw) if p.suffix=='.json' else raw
    need(data['base_result']['packet_sha256']==PINS['base_packet'],'base result binds different packet')
    need(data['base_result']['status']=='PASS_INDEPENDENT_LITERAL_BOUNDARY_MAIN_INVERSE_UNDER_RETAINED_NATIVE_ABI','base independent main/source pass missing')
    need(data['base_result']['all_owned_zero_returns'] and data['base_result']['both_main_inverse_products'],'base owned/main coverage missing')
    need(not data['base_result']['optional_current_source_120_queries_installed'],'base must not already contain the currentQ120 layer')
    need(data['base_custody']['packet']['sha256']==PINS['base_packet'] and data['base_custody']['status']=='PASS_STATIC_LITERAL_SOURCE_BINDINGS','base custody mismatch')
    return m,data

def old_episode(j,sign):
    c=f'c{j+1}';h=f'h{j}';k=f'k{j}'
    return [dict(op='CLEAR',field=c,owned=True),dict(op='ZERO_RETAG',field=c,chart='exact current frame of '+h,premise='immediately preceding owned CLEAR'),
            dict(op='COPY',dst=c,src=h,owned_zero_destination=True),dict(op='GAUSSIAN_Q',field=c,rank=1,axis=0,sign=1,paid=True),
            dict(op='ADD',dst=k,src=c,coefficient=str(sign)),dict(op='CLEAR',field=c,owned=True),
            dict(op='ZERO_RETAG',field=c,chart='ground',premise='immediately preceding owned CLEAR')]

def bind_base(base):
    need(base['original_count']==632 and base['main_original_count']==240 and base['remaining_helper_count']==392,'wrong original/helper interface')
    need(base['stage_geometry']['source9_to_stage_axes']==[0,9,10,11,12,13,14,15,16] and base['stage_geometry']['logical_ambient_axes']==25,'wrong frozen stage geometry')
    need(base['owned']['fields']==[f'c{i}' for i in range(9)] and base['owned']['all9_arbitrary_entry'] and base['owned']['all9_zero_exit'],'nine-owned ABI changed')
    need(base['raw_forward_promoted_main_ABI']['k']=='D*k','promoted-k source premise changed')
    need(base['remaining_helper_profile']=={'4':28,'7':7,'8':39,'9':318},'helper debit/profile changed')
    fs=base['forward_segments'];ivs=base['inverse_segments']
    need(len(fs)==len(ivs)==11,'frozen segment cardinality changed')
    need(fs[0]['kind']==ivs[10]['kind']=='QUERY_OLD_H' and fs[0]['label']=='query_original_h' and ivs[10]['label']=='query_recovered_OLD_h','wrong removal occurrence')
    need(fs[0]['operations']==sum((old_episode(j,-1) for j in range(8)),[]) and ivs[10]['operations']==sum((old_episode(j,1) for j in range(8)),[]),'old-query episode/lifetime differs')
    need(sum(s['kind']=='QUERY_OLD_H' for s in fs)==sum(s['kind']=='QUERY_OLD_H' for s in ivs)==1,'more than named old-query occurrence present')
    need(fs[1]['kind']=='COMMON_K_FRAME_ENTRY' and fs[5]['kind']=='COMMON_K_FRAME_EXIT' and fs[4]['kind']=='COMMON_FRAME_SHEAR_W' and fs[4]['sign']==1,'source Z/K extraction anchors changed')
    entry={x['field']:x for x in fs[1]['operations']};exit={x['field']:x for x in fs[5]['operations']}
    need(set(entry)==set(exit)==set(E_FIELDS),'source actual K words incomplete')
    M={}
    for op in fs[4]['operations']:
        need(op['op']=='ADD' and op['dst'].startswith('y') and op['src'].startswith('h'),'unexpected source W primitive')
        i=int(op['dst'][1:]);j=int(op['src'][1:]);value=2*F(op['coefficient'])
        need(0<=i<112 and 0<=j<8 and value in (-1,1) and (i,j) not in M,'source M coefficient not exact signed unit')
        M[i,j]=int(value)
    need(len(M)==448 and all(sum(i==r for i,j in M)==4 for r in range(112)),'source M inventory changed')
    return entry,exit,M

def moved_monomial(record,field):
    op=deepcopy(record);need(op['op']=='MONOMIAL','expected actual source monomial word');op['field']=field
    return op

def correction(entry,exit,M,sign):
    ops=[]
    for j in range(8):
        for _ in range(13):ops.append(dict(op='ADD',dst=f'k{j}',src=f'h{j}',coefficient=str(sign)))
    for j in range(8):ops.append(moved_monomial(entry[f'h{j}'],f'k{j}'))
    for i in range(112):
        ops.extend([dict(op='CLEAR',field='c0',owned=True),dict(op='ZERO_RETAG',field='c0',chart=f'exact current frame of y{i}',premise='immediately preceding owned CLEAR'),dict(op='COPY',dst='c0',src=f'y{i}',owned_zero_destination=True),moved_monomial(entry[f'y{i}'],'c0')])
        for j in range(8):
            if (i,j) in M:
                coefficient=sign*M[i,j]
                ops.append(dict(op='ADD',dst=f'k{j}',src='c0',coefficient=str(coefficient)))
                ops.append(dict(op='ADD',dst=f'k{j}',src='c0',coefficient=str(F(coefficient,2))))
        ops.extend([dict(op='CLEAR',field='c0',owned=True),dict(op='ZERO_RETAG',field='c0',chart='ground',premise='immediately preceding owned CLEAR')])
    for j in range(8):ops.append(moved_monomial(exit[f'h{j}'],f'k{j}'))
    return dict(label='deferred_K_strict_subtract' if sign<0 else 'deferred_K_strict_undo',kind='DEFERRED_K_STRICT',sign=sign,
        source_version='CURRENT_SOURCE_Q120 output E; never q^-1E or oldh',source_stage='s=1, raw common physical exit coordinates',
        source_read_only=True,scratch='c0',borrow='owned zero; CLEAR before every read; zero return; no overlap with native/scalar lowering',
        weighted_ADD_before_lowering=456,unit_half_ADD_after_lowering=1000,operations=ops)

def queries(inverse=False):
    ops=[]
    for field in E_FIELDS:
        ops.append(dict(op='GAUSSIAN_Q',field=field,rank=1,axis=0,sign=1,paid=True,absolute_phase=0))
        if inverse:ops.append(dict(op='MONOMIAL',field=field,word=[['X',1]],source_word9=[['X',1]],absolute_phase=0,phase=0))
    return dict(label='current_source_Q120_inverse' if inverse else 'current_source_Q120',kind='CURRENT_SOURCE_Q120',inverse=inverse,
        input_version='current E, after strict K undo' if inverse else 'actual returned Vprime after native aliases and H postdivision',
        physical_placement=dict(axis=0,rank=1,pre_alias=[],post_alias=[],aliases='literal identity in canonical physical current exit coordinates; NOT K conjugation',spectators=list(range(1,25)),source_proof_sha256=PINS['q_audit']),
        inverse_translation='after each positiveQ: central X(mask1), absolute multiplier+1/exponent0' if inverse else None,operations=ops)

def count(segments):return dict(sorted(Counter(op['op'] for segment in segments for op in segment['operations']).items()))

def emit(m,data):
    base=data['base_packet'];entry,exit,M=bind_base(base);out=deepcopy(base)
    out['schema']='deferred-k-current-query-component/1';out['status']='EMITTED_AWAITING_INDEPENDENT_VERIFICATION'
    out['base_packet_sha256']=PINS['base_packet'];out['base_result_sha256']=PINS['base_result'];out['base_source_custody_sha256']=PINS['base_custody'];out['root_identity_sha256']=PINS['identity_audit'];out['source_q_proof_sha256']=PINS['q_audit']
    out['overlay_dependencies']=deepcopy(m['inputs']);out['forward_segments']=deepcopy(base['forward_segments'][1:])+[queries(),correction(entry,exit,M,-1)]
    out['inverse_segments']=[correction(entry,exit,M,1),queries(True)]+deepcopy(base['inverse_segments'][:10])
    out['forward_counts']=count(out['forward_segments']);out['inverse_counts']=count(out['inverse_segments'])
    out['producer_census_not_independent']=True
    out['producer_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    out['current_source_120_queries_installed']=True
    out['base_boundary_counts_before_inherited_aliases']=deepcopy(base['boundary_counts_before_inherited_aliases'])
    def external_without_aliases(direction):
        counts=deepcopy(out[direction+'_counts']);counts['MONOMIAL']-=800
        counts.pop('PROVIDER_5402' if direction=='forward' else 'PROVIDER_5411_INVERSE')
        return counts
    out['boundary_counts_before_inherited_aliases']=external_without_aliases('forward')
    out['inverse_boundary_counts_before_inherited_aliases']=external_without_aliases('inverse')
    out['retained_segment_digests']={direction:[digest(x) for x in (base['forward_segments'][1:] if direction=='forward' else base['inverse_segments'][:10])] for direction in ('forward','inverse')}
    out['deleted_occurrences']=[dict(direction='forward',index=0,label=base['forward_segments'][0]['label'],kind='QUERY_OLD_H',operations=56,sha256=digest(base['forward_segments'][0])),dict(direction='inverse',index=10,label=base['inverse_segments'][10]['label'],kind='QUERY_OLD_H',operations=56,sha256=digest(base['inverse_segments'][10]))]
    out['owned']['native_c0']='Existing owned c0 borrowed only in strict correction, CLEAR before copy/read and zero on return; native body/scalar lifetimes remain disjoint.'
    out['expected_forward']='A=(D*x-R*y,D*k-R*h); E=J*R*(y,h), with qcurrent=barepositiveC1axis0'
    out['expected_main_inverse']='undo_K_from_CURRENT_E; qinv120=positiveQ120+centralX120; unchangedactual5411 inverse with old-h episode removed'
    out['supplementary_H1_per_direction']=120
    paid=deepcopy(base['inherited_paid_profile']);paid['1']+=120;out['declared_complete_paid_profile_per_direction']=paid
    out['component_comparison']=dict(reference='Exact original balancedT followed by same full currentQ120',old_complete_H1=2321,new_complete_H1=2313,delta_H1=-8,helpers_unchanged=392,owned_peak_unchanged=9,current_mode_queries_retained=8,thin112_reuse_claimed=False)
    out['base_optional_consumer_CONDITION_ONLY']=out.pop('optional_consumer_CONDITION_ONLY')
    out['base_scope']=base['scope']
    out['scope']='Exact deferred-K/current-source-Q component only, under retained native/source/phase premises; original peer fusedT retained unchanged as dependency. No global caller, target admission, thin-query reuse or funded kappa.'
    out['inverse_scope']='MAIN functional inverse only under actual5411 native ABI;392 helpers are positive jobs in each direction, not helper inverse composition.'
    out['raw_IT_applicability']='Not emitted: main functional inverse is not helper inverse composition, a full literal raw-IT, dual supplier or global caller admission.'
    out['complete_caller']=False;out['gain_claimed']=False;out['new_kappa']=None
    out['credit']=base['credit']+'; root deferred-K identity and source audit; new occurrence-specific overlay/strict-readonly completion by Chris R/Clear1nsight with substantial OpenAI Codex assistance. Original peer emitter/native body retained unchanged.'
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    manifest,data=inputs(a.manifest);result=emit(manifest,data)
    raw=(json.dumps(result,indent=2)+'\n').encode()
    with a.output.open('xb') as f:f.write(raw)
    print(json.dumps(dict(status=result['status'],output_sha256=sha256(raw).hexdigest(),output_bytes=len(raw),base_packet_sha256=PINS['base_packet'],forward_counts=result['forward_counts'],inverse_counts=result['inverse_counts'],semantic_verification_executed=False,pricing_or_native_engine_executed=False),sort_keys=True))
