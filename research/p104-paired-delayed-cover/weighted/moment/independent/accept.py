"""Validate the changed 40th-moment service against both full signed application outputs."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys

def need(condition, reason):
    if not condition:
        raise ValueError(reason)

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def run(a):
    need(digest(a.prior_checker)=='1e6518e266b01d5124eaa71fee4344a28ea07d6655a50376d7779699e2218073','independent 48-call checker')
    lib=runpy.run_path(str(a.prior_checker))
    read=lib['read']
    oldsha='65473eba091d40551586a3e078bb6c4155813ba64e7207e0698765a2e738da0d'
    oldaccept=read(a.prior_accept,'32d40619c37fdcf91f63930e3ebdf1ec0e19210f91e4f1a74617fcc1b3ada10c')
    old,oldbit,oldphys,oldapp=lib['run_files'](a.prior_run,oldsha)
    need(oldaccept['outcome']=='PASS_COMPLETE_INDEPENDENT_WEIGHTED_ACCEPTANCE' and
         oldaccept['outputs']==old['output_sha256'] and oldaccept['replay_sha256']==oldsha,'fully accepted prior')
    pr=read(a.primary,'8c09bcccce796c9b01efed5d9363af8fe6b8719f588eb6de5148933411a8850d')
    ind=read(a.independent,'5c9d36bad5d7fca162d135e9d8658ab408a6d89edd262be167747cc164c12229')
    peer=read(a.peer/'APPLICATION.json','587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f')
    s,bit,physical,app=lib['run_files'](a.run,a.replay_sha)
    need(s['prior_receipt_sha256']==oldsha and s['peer_head']==old['peer_head'] and
         s['primary_sha256']==digest(a.primary) and s['independent_sha256']==digest(a.independent),'two independently frozen suppliers')
    need(pr['case']['p']==ind['p']==40 and pr['case']['v']==ind['v']==768 and
         pr['case']['h']==ind['h']==1024 and pr['case']['H']==ind['H']==299610000000000,'same case')
    H=ind['H'];h=ind['h'];p=ind['p'];v=ind['v'];L=ind['uniform_numerator'];lam=F(7,10)
    need(L==pr['L']==1524 and bit['peer_finite']==oldbit['peer_finite'] and
         bit['prior_binary_sha256']==old['output_sha256']['BINARY.json'],'same source, stock and original costs')
    need(ind['decision']=='ADVANCE_ONE_SIGNED_REPLAY' and pr['result']=='PASS_FULL_PRICED_MOMENT_SIGNED_REQUIRED','two prices pass')
    terms=list(map(F,pr['stirling_terms_0_through_40']))
    scaled=sum(terms)*(F(3,2*v)**p)
    need(len(terms)==41 and terms[0]==0 and all(x>0 for x in terms[1:]) and ind['direct_terms']==769 and
         scaled==F(pr['raw_moment_upper'])==F(ind['raw_moment']),'exact equality of 769 probability terms and 41 Stirling contributions')
    for raw,extra,total in ((scaled,pr['positive_split_uplift_upper'],pr['complete_moment_upper']),
                            (scaled,ind['full_split_upper'],ind['completed_moment'])):
        need(raw+F(extra)==F(total)<lam**p,'separately charged moment guard')
    need(F(ind['law']['completed_mean_upper'])<=F(67,100) and F(pr['raw_mean_upper'])<=F(67,100) and
         max(map(int,peer['binary_native']['paid_all']))==56 and 56**2<15**3 and
         F(ind['binomial_probability'])==F(pr['case']['q_letter'])==F(67,150),'actual letter support and law')
    eta=F(bit['peer_finite']['uniform']['eta']['lower'])
    ends=[((F(7,20)+lam)/F(21,10))**p,(lam/F(51,50))**p]
    need(ends==list(map(F,[ind['root_ratio'],ind['infinite_height_ratio']]))==list(map(F,[pr['endpoint_zero'],pr['endpoint_infinity']])) and max(ends)<eta,'entire source/complement bound')
    need(h**p*2**(L-1)<=(H+h)**p<h**p*2**L and L*(H+h)>2*H*p,'first strict carrier and continuous tail')
    d=F(1,H*2**38)
    need(F(bit['delayed_cover_debit'])==F(oldbit['delayed_cover_debit'])==d and F(bit['uniform_loss'])==F(L,H) and
         F(oldbit['uniform_loss'])==F(4876,H),'unmodified complete cover with separately repriced uniform service')
    C=F(bit['peer_finite']['tested_saving'])
    covered=C-F(L,H)-d;previous=F('0.00385248');rows=[]
    need(covered==F(bit['covered'])==F(ind['covered'])==F(pr['covered']),'full covered service')
    for ob,ib,pb in zip(bit['candidate_stages'],ind['stages'],pr['stages'],strict=True):
        end=(249*covered+previous)/250
        nxt=F(int(end*10**15)-1,10**15);slack=min(end-nxt,F(1,250)-nxt,F(249,250)-nxt)
        need(nxt==F(ob['claim'])==F(ib['cap'])==F(pb['admitted']) and F(ob['previous'])==previous and
             F(ib['bound'])==F(pb['endpoint'])==end and F(ob['envelope'][0])<=end<=F(ob['envelope'][1]) and
             F(ib['slack'])==F(pb['charged_minimum_slack'])==slack>0 and previous<nxt,'entire strict service')
        rows.append([str(previous),str(end),str(nxt),str(slack)]);previous=nxt
    cap=previous;tick=F(1,10**14)
    claim=(min(F(peer['rational_raw'][0]),cap)//tick-8)*tick;tested=claim+7*tick
    need(len(rows)==4 and cap==F(app['binary_ordinary'])==F(bit['admitted'])==F(pr['cap'])==F(ind['cap']) and
         claim==F(app['claim'])==F(pr['claim'])==F(ind['claim']) and tested==F(s['tested'])<cap,'independent full grid')
    invoice=lib['physical_invoice'](a.peer,physical,oldphys,app,oldapp)
    outer=lib['signed_gate'](a.peer,peer,invoice,oldapp,app,physical)
    delta=claim-F(old['claim']);peer_delta=claim-F(peer['claim'])
    old_ceiling=F(peer['binary_raw'][1])-F(4876,H);sep=claim-old_ceiling
    need(sep==F(pr['separation'])==F(ind['separation'])>0 and delta==F(s['difference'])>0 and app['premises']==oldapp['premises'],'strict signed gain')
    return dict(outcome='PASS_COMPLETE_INDEPENDENT_40TH_MOMENT_ACCEPTANCE',peer_head=s['peer_head'],prior_replay_sha256=oldsha,
                replay_sha256=a.replay_sha,outputs=s['output_sha256'],invoice=invoice,caller=physical['caller'],native_calls=[36,48],
                cap=app['binary_ordinary'],claim=app['claim'],tested=s['tested'],gain_vs_previous=str(delta),percent_vs_previous=str(100*delta/F(old['claim'])),
                gain_vs_peer=str(peer_delta),percent_vs_peer=str(100*peer_delta/F(peer['claim'])),previous_ceiling_separation=str(sep),ordinary_stages=rows,
                moment_term_counts=[41,769],outer=outer,premises=app['premises'],known_good=['8027','R351 full accepted'],
                rejections=['one lower terminal','added rational paid rank one','supplied cap equals tested rate'])
def main():
    cli=ArgumentParser()
    for name in ('prior-checker','prior-run','prior-accept','primary','independent','peer','run','out'):
        cli.add_argument('--'+name,type=Path,required=True)
    cli.add_argument('--replay-sha',required=True)
    a=cli.parse_args();need(sys.implementation.name=='cpython' and sys.version_info[:2]==(3,12) and __debug__,'CPython 3.12')
    result=run(a)
    with a.out.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    print(result['outcome'],result['claim'],result['gain_vs_previous'])
if __name__=='__main__':
    main()
