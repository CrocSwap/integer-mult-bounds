"""Reprice the complete new invoice with three rational implementations."""
from copy import deepcopy
import json
from linear import HERE,load,need,read
from pricing import caller_invoice,root_invoice
from outer import verify_price
import independent_moments as third

def main():
    word=read(HERE/'WORD.json.gz');caller=read(HERE/'retained/data/caller.json')
    result=read(HERE/'RESULT.json');claim=result['claim']
    a=read(HERE/'retained/data/root_A.json');b=read(HERE/'retained/data/root_B.json')
    rc=load(HERE/'retained/6917/root_check.py','composition_root_A')
    need(rc.run(a)==[],'All exact type-A root identities')
    path=HERE/'retained/6917/root_check_hosted.py'
    source=path.read_text().replace("R=json.load(open(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'data','root.json')))",'R=_R').replace('sys.exit(1 if bad else 0)','')
    def hosted(root):
        ns={'_R':root,'__file__':str(path),'print':lambda *a,**k:None}
        exec(compile(source,str(path),'exec'),ns)
        return ns['bad']
    need(hosted(b)==[],'All exact type-B root identities')
    from fractions import Fraction as Q
    for root,fn in [(a,rc.run),(b,hosted)]:
        bad=deepcopy(root);bad['X'][5][3]=str(Q(bad['X'][5][3])+1)
        need(fn(bad)!=[],'Wrong root coefficient rejected')
    t,p=caller_invoice(word,caller)
    rt,rp=root_invoice(word,[(read(HERE/'retained/data/root_A.json'),96),(read(HERE/'retained/data/root_B.json'),8)])
    need(+t==+rt and +p==+rp,'Complete independent root/caller accounting')
    actual=verify_price(t,p,claim)
    need(actual==result['outer'],'Fresh outer ledger and compiler constants')
    other=third.check(word,caller,claim)
    need(json.loads(json.dumps(other))==read(HERE/'MOMENTS.json'),'Third rational interval implementation')
    bad=dict(claim,kappa=claim['raw_upper'])
    try:third.check(word,caller,bad)
    except ValueError:pass
    else:raise ValueError('An overstated saving passed')
    need(actual['strict_checks']==54 and actual['functional_checks']==4,'All outer predicates checked')
    cap=load(HERE/'retained/compiler/ambient_bounds.py','composition_ambient').verify()
    need(Q(claim['tested'])<=Q(cap['covered_saving_interval'][1]) and claim['logarithm_power']==cap['logarithm_power'],'Separate ambient-cap range certificate applies')
    print(json.dumps(actual,sort_keys=True));print('PASS_COMPLETE_COMPOSITION_PRICE')

if __name__=='__main__':main()
