"""Exact cache construction, geometric bound and source application.

Standard library only. Apache-2.0; substantial OpenAI Codex assistance.
"""
from decimal import Decimal as D,localcontext
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import geometry as G
import primitive as P
import center


def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row.get('usage')!='input':
            continue
        G.need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Changed source '+row['path'])
    plan=json.loads((HERE/'PLAN.json').read_text())
    G.need(sha256((HERE/'geometry.py').read_bytes()).hexdigest()==plan['geometry_sha256'],'Unchanged prospective geometry')
    return plan


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


def geometry_checks():
    ls=G.lagrangians(2);G.need(len(ls)==15,'All two-qubit Lagrangians including noncanonical phase charts')
    checks=0
    for a,b,c in product(ls,repeat=3):
        for parents in ([None,0,0],[None,0,1]):
            G.tree_bound([a,b,c],parents);checks+=1
    spaces=G.subspaces(3)
    G.need(len(spaces)==16,'All canonical three-axis frames')
    terminals=[G.span([]),G.span([1,2]),G.span([1,4])]
    choices=[]
    for f in spaces:
        ranks=sorted(G.distance(t,f) for t in terminals)
        choices.append({'meeting_basis':G.basis(f),'edge_grades':ranks})
    with localcontext() as ctx:
        ctx.prec=60
        for s in [D(1)-D('.00302015'),D('.5')]:
            power=lambda r:D(0) if not r else (D(r).ln()*s).exp()
            scores=[sum(power(r) for r in x['edge_grades']) for x in choices]
            G.need(abs(min(scores)-min(D(3),2*power(2)))<D('1e-55'),'Exact-profile three-terminal minimum')
        transition=(D(3)/2).ln()/D(2).ln()
    tree=[G.canonical_chart(G.span(b),3) for b in [[],[1],[1,2],[1,4]]]
    sharp=G.tree_bound(tree,[None,0,1,1])
    G.need(sharp['edge_rank_mass']==sharp['intersection_floor']==3,'Branching example attains intersection bound')
    return {'all_two_qubit_lagrangians':len(ls),'arbitrary_chart_path_and_tree_checks':checks,
            'canonical_three_axis_meetings':choices,'cache_tree_mass':sharp,
            'transition_s':str(transition),'scope':'General proof is written; these finite checks corroborate its ranks and transcription.'}


def price_checks(plan):
    m=load(ROOT/'research/higher-moment-strictification/verify.py','cache_exact_moments')
    def margin(targets,paid,c):
        a=m.moment(targets,1-c);b=m.moment(paid,1-c)
        return a[0]-b[1],a[1]-b[0]
    gains={}
    for c in ['.00302015','.004','.005','.01']:
        gain=margin({2:2},{1:3},Q(c));debt=margin({2:2},{1:4},Q(c))
        G.need(gain[0]>0 and debt[1]<0,'Positive reuse gain; one extra H1 destroys it')
        gains[c]={'saving':[str(v) for v in gain],'after_one_extra_H1':[str(v) for v in debt]}
    G.need(margin({2:2},{1:3},Q('.5'))[1]<0,'At exponent one-half separate copies beat the three-H1 tree')
    with localcontext() as ctx:
        ctx.prec=55
        predicted=D(plan['predicted_gain_at_selected_exponent'])
        lo,hi=margin({2:2},{1:3},Q('.00302015'))
        to_dec=lambda q:D(q.numerator)/q.denominator
        G.need(to_dec(lo)-D('1e-52')<predicted<to_dec(hi)+D('1e-52'),'Frozen preconstruction gain agrees with exact bounds')
    return {'baseline_paid':{'2':2},'cache_paid':{'1':3},'productive_owner_delta':0,
            'outward_moment_gains':gains,'repair_budget':'Strictly less than one extra H1 per module at every tested positive saving.',
            'selected_installation':False,'new_kappa':None}


def run():
    plan=authenticate()
    ce=load(ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','cache_pinned_clifford')
    primitive=P.run(ce,G.subspaces(3));print('PASS_EXACT_CACHE_PRIMITIVE',flush=True)
    geo=geometry_checks();print('PASS_GENERAL_CHART_TREE_CONTROLS',flush=True)
    source=center.run(ROOT);print('PASS_ALL_16_SELECTED_CENTER_BLOCKS',flush=True)
    return {'status':'PASS_GAUSSIAN_CACHE_REUSE_AND_SHARP_CENTER_BOUND_NO_NEW_KAPPA',
            'plan_sha256':sha256((HERE/'PLAN.json').read_bytes()).hexdigest(),
            'primitive':primitive,'geometry':geo,'price':price_checks(plan),'selected_centers':source,
            'claims':'Constructive all-width block identity under retained Gaussian/owned-erasure contracts; written sharp bound for typed-copy trees with fixed canonical contact caps. Finite exact corroboration, no formal kernel or full supplier admission.'}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    # JSON object keys are strings. Compare the serialized schema so an exact
    # integer rank key from the frozen geometry helper is not a false mismatch.
    result=json.loads(json.dumps(run()))
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:G.need(result==json.loads((HERE/'RESULT.json').read_text()),'Every saved mathematical field reproduced')
    print(json.dumps({'status':result['status'],'new_kappa':None,'module_gain':json.loads((HERE/'PLAN.json').read_text())['predicted_gain_at_selected_exponent']},sort_keys=True))
