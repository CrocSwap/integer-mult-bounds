"""Independent invoice reconstruction and acceptance of an existing full signed replay."""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import runpy
import tarfile
import tempfile

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def need(ok, why):
    if not ok:
        raise ValueError(why)

def obj(p):
    def strict(pairs):
        x=dict(pairs)
        need(len(x)==len(pairs),"duplicate JSON keys")
        return x
    return json.loads(p.read_bytes(),object_pairs_hook=strict)

def main():
    cli=argparse.ArgumentParser()
    for key in ('peer','run','independent','primary','out'):
        cli.add_argument('--'+key,type=Path,required=True)
    cli.add_argument('--adapter',type=Path,required=True)
    a=cli.parse_args()
    proof_files={'APPLICATION.json':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f',
                 'APPLICATION-SOURCES.tar.gz':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968',
                 'BANK-FACTORS-RECEIPT.json':'bdb3052152bdd15ae36c30c98877dcebf864fc2c58a7b1fa66f2d5affa149288',
                 'CALLER-CENSUS.json':'6a685bdc50aeba01a79fa437490190568513d62e0765844e7f3e8fa29a913e16'}
    for k,h in proof_files.items():
        need(sha(a.peer/k)==h,k)
    need(sha(a.independent)=='5c723ea9c6b085b6e0aa792f34cfa64daed551a9bf2f629efc54d219008596d2',"independent price")
    need(sha(a.primary)=='228b7c47572c9b1c7568db2f59248af454296a1e3ad094da585073bbd594f5cb',"primary price")
    need(sha(a.adapter)=='d6dd8f406e4e09377b2539a744ada909d3ab44baefdec17d0af450d6e867f051',"audited adapter version")
    independent=obj(a.independent);primary=obj(a.primary);base=obj(a.peer/'APPLICATION.json')
    result=obj(a.run/'REPLAY.json')
    seen={k:sha(a.run/k) for k in ('APPLICATION.json','PHYSICAL.json','BINARY.json')}
    need(seen==result['output_sha256'],"full replay closure")
    app=obj(a.run/'APPLICATION.json');physical=obj(a.run/'PHYSICAL.json');binary=obj(a.run/'BINARY.json')
    changes={k for k in app.keys()|base.keys() if app.get(k)!=base.get(k)}
    need(changes=={'binary_ordinary','claim'},"preserved physical and interface summary")
    need(result['peer_head']=='fb9b6a7b0d27da1cf98430893a3016bf811e2aa4' and len(app['premises'])==5,"peer/premises")
    old=binary['peer_finite'];h=old['uniform']['H']
    need(old['cover_prime_condition']=='odd q > 2^45*N^5 avoiding the frozen finite catalogue witnesses' and
         h==base['binary_H'] and old['uniform']['N']==f'2^{h}',"same carrier and prime rule")
    need(old['stock']['W']=='B*|GL_N(F_q)|*q^(N^2*(w-1))' and 'S_old' in old['stock']['reserve']
         and old['stock']['backend_levels']==4 and old['stock']['depth']=='2+ceil(log_N(n))',"stock and restoration invariant")
    need(F(binary['delayed_cover_debit'])==F(1,h*2**38) and F(old['uniform']['gap'])==F(1,10**10)
         and old['uniform']['preceding_integer_grid_fails'] and old['uniform']['logarithm_power']==623,"charged separate debits")
    need(old['finite_product_bound_bit_lengths']==base['binary_product'] and old['raw_crossing']==base['binary_raw'],"original finite compiler")
    cap=F(binary['admitted']);claim=F(app['claim']);tick=F(1,10**14);tested=claim+7*tick
    need(cap==F(app['binary_ordinary'])==F(independent['cap'])==F(primary['candidate']['cap']) and
         claim==F(independent['candidate'])==F(primary['candidate']['claim']),"independent paid and signed bind")
    previous=F('0.00385248')
    for s,row in zip(binary['candidate_stages'],independent['new_rows'],strict=True):
        q=F(249,250)*F(binary['covered'])+previous/250
        new=F((q*10**15)//1-1,10**15)
        need(new==F(s['claim'])==F(row['new']) and previous==F(s['previous']) and
             min(q-new,F(1,250)-new,F(249,250)-new)==F(row['margin'])>0,"fully charged strict ordinary stage")
        previous=new
    need(previous==cap,"terminal acceptance")
    caller=obj(a.peer/'CALLER-CENSUS.json');bank=obj(a.peer/'BANK-FACTORS-RECEIPT.json')
    p=physical['native'];c=physical['caller_census'];actual=physical['application']
    need(all(c[k]==caller[k] for k in caller) and c['calls']==48,"exact fixed caller")
    need(physical['caller']==physical['caller_proof']['readback']['event_stream_sha256']==
         '156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858',"signed caller/phase order")
    invoice={}
    for key,nkey,ckey in [('paid','paid_native_ranks','fixed_caller_paid'),('targets','positive_helper_ranks','fixed_root_targets')]:
        tally=Counter({k:v*c['calls'] for k,v in p[nkey].items()})
        tally.update(c[ckey]);invoice[key]=dict(tally)
        need(invoice[key]==actual['invoice'][key]==bank['paid' if key=='paid' else 'productive'],"three independent signed invoice sources")
    need(p['retired_and_guards_restored'] and p['all_public_inputs_preserved_until_final_installs']
         and p['same_owner_complete_fixture_outputs']==p['exact_all_public_rows']==p['exact_source_columns']==bank['public']==1291,
         "native restoration and public inputs")
    need(p['coefficient_products']==bank['forward_terms']==base['rational_grid']['all_basis_products'] and bank['adjoint_terms']==88780788 and
         p['minimum_product_grid']==int(bank['minimum_product_grid'])==base['rational_grid']['product_grid'],"basis, adjoint and grid")
    need(base['rational_word']==bank['new_word'] and base['rational_layout']==bank['layout'],"literal word/layout")
    need(actual['ordinary']['ordinary_elementary_record_upper']==base['ordinary']['ordinary_elementary_record_upper'] and
         physical['common_depth_guards']==base['ordinary']['common_depth_guards'],"ordinary work and tape depth")
    with tarfile.open(a.peer/'APPLICATION-SOURCES.tar.gz') as tar:
        data=tar.extractfile('source/research/p104-dual-supplier-lift/complex/supplier_gate.py').read()
    need(hashlib.sha256(data).hexdigest()=='3796b2e5a27f3caa142d16364154788e60d0099f1e24a8dcd028e4fbd35a84ca',"signed gate source")
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'gate.py';path.write_bytes(data)
        gate=runpy.run_path(str(path))['gate']
    gate.__globals__['BIT_PIN']=str(cap)
    weights={'T':invoice['targets'],'P':invoice['paid']}
    g=gate(weights,claim,tested,*base['rational_raw'],cap)
    need(g==actual['compiler'] and g['outer']==base['outer'] and F(g['BIT_margin'])==cap-tested,"independent signed gate/54+4")
    need(all(F(app['rational_raw'][i])==F(g['raw_bracket'][i]) for i in (0,1)),"retained raw endpoints")
    need(g['outer']['strict_count']==54 and g['outer']['functional_count']==4 and F(g['outer']['minimum_margin'])>0,"complete gate")
    def rejects(code):
        try:
            code()
        except (AssertionError,ValueError):
            return True
        return False
    damaged={'T':weights['T'],'P':dict(weights['P'])};damaged['P']['1']+=1
    need(rejects(lambda:gate(damaged,claim,tested,*base['rational_raw'],cap)),"unpaid rank control")
    need(rejects(lambda:gate(weights,claim,tested,*base['rational_raw'],tested)),"strict below-cap negative")
    need(claim>F(base['binary_raw'][1])-2*F(old['uniform']['gap']) and claim-F(base['claim'])==F(result['difference']),"strict historical separation")
    output=dict(outcome='PASS_COMPLETE_INDEPENDENT_SIGNED_ACCEPTANCE',peer_head=result['peer_head'],price_receipts={'primary':sha(a.primary),'independent':sha(a.independent)},
                replay_receipt_sha256=sha(a.run/'REPLAY.json'),output_sha256=seen,changed_peer_summary_fields=sorted(changes),
                cap=str(cap),claim=str(claim),tested=str(tested),gain=str(claim-F(base['claim'])),signed_checks=g['outer'],newly_checked_controls=['extra_rank_one','cap_equals_tested'],
                native_calls_binary=app['binary_native']['calls'],native_calls_rational=c['calls'],paid_rational=sum(weights['P'].values()),productive_rational=sum(weights['T'].values()),
                minimum_complete_stock_stage_margin=str(min(F(s['margin']) for s in independent['new_rows'])),caller_sha256=physical['caller'],premises=app['premises'])
    with a.out.open('x') as stream:
        json.dump(output,stream,sort_keys=True,indent=2);stream.write('\n')
    print(output['outcome'],app['claim'],output['gain'])
if __name__=='__main__':
    main()
