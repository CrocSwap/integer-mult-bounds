"""Source-bound QQ16 child defect contract; ywz65 + OpenAI Codex, Apache-2.0."""
import argparse,json,sys
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import engine,sources,controls
need=sources.need
def typed(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def experiment():
    old=sources.load(); retained,word=old.calculate()
    need(typed(retained)==typed(json.loads((HERE/'vendor/pr2540/RESULT.json').read_text())),'retained receipt')
    need(typed(word)==typed(json.loads((HERE/'vendor/pr2540/WORD.json').read_text())),'retained literal word')
    R,records,_=old.N.load_sources()
    result,peaks,final=engine.forward(old,word,records)
    expected,_=old.logical_reference()
    for name,want in expected.items():
        got={(v[2:],g):c for (v,g),c in final[name].items() if v.startswith('i:')}
        need(got==want,'independent ideal endpoint '+name)
    reverse_checks=0
    for kind,peak in result['peaks'].items():
        row=engine.reverse(word,records,peak['event'],peak['field'])
        need(row==peaks[kind],'independent reverse peak '+kind);reverse_checks+=len(row)
    # Every final borrowed/output field is independently checked by reverse traversal.
    for name in sorted(final):
        if name.startswith(('Z','W','X','Y')):
            row=engine.reverse(word,records,len(word)-1,name)
            need(row==final[name],'independent reverse endpoint '+name);reverse_checks+=len(row)
    P=Q(result['peaks']['P']['value']);K=Q(result['peaks']['K']['value'])
    guard=0
    while Q(1<<guard)<2*P*K:guard+=1
    need(K/Q(1<<guard)<=Q(1,2),'feedback denominator')
    need(2*P*K<=1<<guard,'all-b error allowance')
    result.update({'schema_version':1,'retained_controls':len(retained['controls']),'unchanged_invoice':retained['invoice'],
        'reverse_coefficients_checked':reverse_checks,'state_relative_guard_bits':guard,
        'scope':'Completed ADD/native/cover-map defects; exact owned CLEAR; capture defects retained; inherited B1 and current-entry errors excluded. Maximum per-owner payload Hilbert norm. No physical child admission or new kappa.'})
    result['literal_checks']=controls.run(old,word,records,result,peaks,final)
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--authenticate-only',action='store_true');a=p.parse_args()
    if a.authenticate_only:sources.authenticate();print('PASS_QQ16_DEFECT_SOURCE_PINS');return
    result=experiment();path=HERE/'RESULT.json'
    if a.write:
        with path.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(typed(result)==typed(json.loads(path.read_text())),'typed complete receipt')
    print('PASS_QQ16_CHILD_DEFECT',json.dumps({k:result[k] for k in ['fault_sites','peaks','state_relative_guard_bits','reverse_coefficients_checked']}))
if __name__=='__main__':main()
