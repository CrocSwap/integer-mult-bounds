#!/usr/bin/env python3
"""Check the 32-port unit reader with independent integer realification."""
import argparse
from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
CAMPAIGN=HERE.parents[2]
ENGINE=HERE.parent/'sign-metric-review-20261020/check_review.py'
ENGINE_PIN='2dc96dc39b42c85885859c3b7c09700bda447ffe223f3d9aa03b5ffd1df68867'
FREEZE='root/SIGN-METRIC-UNIT-FREEZE-20261020.json'
FREEZE_PIN='0deadea1883d80a603a2819200697e60d518a580ed1d7bb04ffe60e6991bb82c'
PAYLOAD='root/sign-metric-unit-normal-20261020/RESPONSE.json'
PAYLOAD_PIN='1fe13e786e70ef7408fb5fbd121d08fb40d8ce0e117fe096aaee9f4243140d6a'
if sha256(ENGINE.read_bytes()).hexdigest()!=ENGINE_PIN:
    raise ValueError('Independent integer engine pin')
spec=importlib.util.spec_from_file_location('unit_reader_integer_review',ENGINE)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
need=r.need


def restrict_columns(a,ports,total):
    columns=list(ports)+[total+p for p in ports]
    return [{j:row[p] for j,p in enumerate(columns) if p in row} for row in a]


def divide(a,d):
    need(all(c%d==0 for row in a for c in row.values()),'Exact integer division')
    return [{j:c//d for j,c in row.items()} for row in a]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=HERE/'run-normal')
    args=parser.parse_args()
    raw=(CAMPAIGN/FREEZE).read_bytes()
    need(sha256(raw).hexdigest()==FREEZE_PIN,'Root unit reader freeze')
    freeze=json.loads(raw)
    for name,pin in freeze['files'].items():
        need(sha256((CAMPAIGN/'root'/name).read_bytes()).hexdigest()==pin,'Root frozen file '+name)
    raw=(CAMPAIGN/PAYLOAD).read_bytes()
    need(sha256(raw).hexdigest()==PAYLOAD_PIN,'Root unit reader payload')
    packet=json.loads(raw)
    prior=r.load('lanes/controller-followthrough-20261017/row-involution-20261020/run-normal/ROW-INVOLUTION.json')
    pairs=r.load('lanes/independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json')
    old=r.load('root/sign-metric-normal-20261020/RESPONSE.json')
    extra={5,4,35,12,29,32,26,31}
    full=set(old['selected'])|extra
    centre=prior['pivots']
    need(len(full)==32 and packet['full_ports']==sorted(full),'Actual32 FULL ports')
    need(packet['centre_ports']==centre and len(centre)==16,'Actual16 centre ports')
    h=r.eye(112);large=set()
    for pair in pairs['pair_codes']:
        p,q=pair['ports'];large.update((p,q))
        need((p in full)==(q in full) and (p in centre)==(q in centre),'Both physical pair closures')
        for i,row in zip((p,q),pair['matrix']):
            h[i]={j:int(c) for j,c in zip((p,q),row) if c}
    ht=r.transpose(h,112)
    hi2=[{j:(1 if i in large else 2)*v for j,v in row.items()} for i,row in enumerate(ht)]
    need(r.times(h,hi2)==r.times(hi2,h)==r.eye(112,2),'Pair inverse')
    H=r.realify(r.real_rows(h),112);R=r.realify(r.real_rows(hi2),112)
    D=r.realify(r.real_rows([{i:-1 if i in full else 1} for i in range(112)]),112)
    need(D==r.realify(packet['metric'],112) and r.times(D,H)==r.times(H,D),'Actual sign metric')
    w=[{} for _ in range(112)]
    for k,block in enumerate(prior['blocks']):
        need(len(set(block['ports'])&full)==2,'Two FULL ports per block')
        for p,d in zip(block['ports'],block['signs']):
            w[p][k]=[d,d if len(block['ports'])==8 and p in full else '0']
    W=r.realify(w,16)
    Vmode=r.scale(r.times(r.transpose(W,32),D),-1)
    need(r.times(Vmode,W)==r.eye(32,-2),'Sixteen rank-one reflection contractions')
    S=r.plus(r.eye(224),r.times(W,Vmode))
    A2=r.times(r.times(R,S),H)
    U2=r.times(R,W);V=r.times(Vmode,H)
    need(A2==r.realify(packet['response'],112,2),'Independent actual112 response')
    need(U2==r.realify(packet['correction_U'],16,2) and V==r.realify(packet['correction_V'],112),
         'Independent actual correction factors')
    need(r.times(V,U2)==r.eye(32,-4),'Exact correction rank16')
    need(r.times(A2,A2)==r.eye(224,4),'Actual involution')
    need(r.transpose(A2,224)==r.times(r.times(D,A2),D),'Actual sign-metric adjoint')
    diagonal={i:A2[i].get(i,0)//2 for i in range(112) if A2[i].get(i,0)}
    need(set(diagonal)==full and Counter(diagonal.values())=={2:16,3:16},'Actual32 diagonal exceptions')
    need(sum(diagonal.values())==80,'Trace80')
    M=restrict_columns(V,centre,112)
    need(M==r.realify(packet['centre_minor'],16),'Actual centre minor')
    Mi2=r.realify(packet['centre_minor_inverse'],16,2)
    need(r.times(M,Mi2)==r.times(Mi2,M)==r.eye(32,2),'Both exact Gaussian dyadic minor inverses')
    L2=r.times(Mi2,V)
    need(L2==r.realify(packet['centre_reader'],112,2),'Actual normalized reader')
    need(restrict_columns(L2,centre,112)==r.eye(32,2),'Reader centre block identity')
    need(r.times(L2,A2)==r.scale(L2,-2),'Actual centre action LA=-L')
    C2=r.eye(224,2)
    for k,p in enumerate(centre):
        C2[p]=L2[k];C2[112+p]=L2[16+k]
    Ci2=r.plus(r.eye(224,4),r.scale(C2,-1))
    need(C2==r.realify(packet['row_code'],112,2) and Ci2==r.realify(packet['row_code_inverse'],112,2),
         'Unit row code and its exact inverse')
    need(r.times(C2,Ci2)==r.times(Ci2,C2)==r.eye(224,4),'Both code inverse orders')
    N2=r.plus(C2,r.eye(224,-2))
    need(r.times(N2,N2)==[{} for _ in range(224)],'Square-zero code difference')
    CA2=divide(r.times(C2,A2),2)
    CAinv2=divide(r.times(A2,Ci2),2)
    need(r.times(CA2,CAinv2)==r.times(CAinv2,CA2)==r.eye(224,4),'Actual coded inverse')
    need(r.transpose(CA2,224)!=r.times(r.times(D,CAinv2),D),'The response metric does not pass through C')
    need(r.times(r.times(r.transpose(C2,224),D),C2)!=r.scale(D,4),'C does not preserve the sign metric')
    # An alternative uses the unchanged24-exception response with the same32 read ports.
    alt_centres=centre[:8]+[next(p for p in b['ports'] if p in extra) for b in prior['blocks'][8:]]
    oldV=r.realify(old['correction_V'],112)
    altM=restrict_columns(oldV,alt_centres,112)
    altMi2=[{j:c*(2 if i%16>=8 else 1) for j,c in row.items()} for i,row in enumerate(r.transpose(altM,32))]
    need(r.times(altM,altMi2)==r.times(altMi2,altM)==r.eye(32,2),'Unchanged24 response with32 read-port unit minor')
    altL2=r.times(altMi2,oldV)
    need(restrict_columns(altL2,alt_centres,112)==r.eye(32,2),'Alternative normalized centre coordinates')
    receipt={'status':'PASS_INDEPENDENT_SIGN_METRIC_UNIT_CAPTURE_REVIEW',
             'root_freeze_sha256':FREEZE_PIN,'payload_sha256':PAYLOAD_PIN,'independent_engine_sha256':ENGINE_PIN,
             'data_ports':112,'full_ports':32,'centre_ports':16,'correction_rank':16,
             'diagonal_values':diagonal,'trace':80,'determinant':1,
             'both_minor_inverse_orders':True,'both_row_code_inverse_orders':True,'centre_action_LA_equals_minus_L':True,
             'row_code_metric_inheritance_rejected':True,
             'alternative_unchanged24_response':{'full_read_ports':sorted(full),'unit_centre_pivots':alt_centres,
                 'both_minor_inverse_orders':True,'scope':'Algebra only; different centre slots and actual access need a separate word.'},
             'blockwise32_minimality_scope':'Independent rank-one sign-metric blocks; all diagonal exceptions and arbitrary normalized reader pivots must be in FULL selected fields.',
             'native_word_or_invoice_reviewed':False,
             'producer_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'CHECKS.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='diagonal_values'},sort_keys=True))


if __name__=='__main__':
    main()
