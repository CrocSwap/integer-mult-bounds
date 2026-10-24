"""Concave-moment objective over the frozen actual mixed-gauge rank graph.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import mixed_gauge as M

HERE=Path(__file__).resolve().parent
KAPPA=Q('0.00302177581')
SCALE=10**18


def outward(lo,hi,digits=60):
    denominator=10**digits
    a=(lo.numerator*denominator)//lo.denominator
    b=-((-hi.numerator*denominator)//hi.denominator)
    return Q(a,denominator),Q(b,denominator)


def log_bounds(x,terms=48):
    x=Q(x);z=(x-1)/(x+1)
    low=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)),Q(0))
    tail=2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return outward(low,low+tail,70)


def rank_power(r):
    if r==0:return Q(0),Q(0)
    if r==1:return Q(1),Q(1)
    k=r.bit_length()-1
    la,lb=log_bounds(Q(r,1<<k));ta,tb=log_bounds(2)
    lo,hi=la+k*ta,lb+k*tb
    def minus_exp_bounds(z):
        M.R.need(0<=z<1,'Small positive moment perturbation')
        terms=[Q(1)];term=Q(1)
        for j in range(1,25):term=-term*z/j;terms.append(term)
        return sum(terms[:24]),sum(terms[:25])
    lower=minus_exp_bounds(KAPPA*hi)[0]
    upper=minus_exp_bounds(KAPPA*lo)[1]
    return outward(r*lower,r*upper)


def net_profile(terms,modes):
    result=Counter()
    for e in terms:result[e['costs'][modes[e['source']]][modes[e['target']]]]+= -1 if e['kind']=='helper' else 1
    return result


def gain_bounds(before,after,bounds):
    low=Q(0);high=Q(0)
    for rank in before.keys()|after.keys():
        c=before[rank]-after[rank]
        a,b=bounds[rank]
        low+=c*(a if c>=0 else b);high+=c*(b if c>=0 else a)
    return low,high


def main():
    graph=M.R.read(HERE/'MIXED-GAUGE.json.gz')
    ranks={r for data in graph['results'] for e in data['terms'] for row in e['costs'] for r in row}
    bounds={r:rank_power(r) for r in ranks}
    weights={r:int((a+b)*SCALE/2+Q(1,2)) for r,(a,b) in bounds.items()}
    error=max(max(abs(Q(weights[r],SCALE)-a),abs(Q(weights[r],SCALE)-b)) for r,(a,b) in bounds.items())
    rows=[]
    for data in graph['results']:
        terms=[{**e,'costs':[[weights[r] for r in row] for row in e['costs']]} for e in data['terms']]
        structure=M.signed_structure(terms,graph['components']);cases=[]
        for boundary,fixed in [('strict',graph['strict_fixed']),('helper_free_optimistic',graph['base_fixed'])]:
            row=dict(boundary=boundary)
            if structure['sign_frustrated_edges']==0:
                modes,energy=M.solve_mincut(terms,graph['components'],fixed,structure['colors'])
                before=net_profile(data['terms'],[0]*graph['components']);after=net_profile(data['terms'],modes)
                lower,upper=gain_bounds(before,after,bounds)
                row.update(solver='exact integer mincut on certified-close quantized moment',modes=modes,
                           quantized_energy=energy,quantized_gain=M.value(terms,[0]*graph['components'])-energy,
                           moment_gain_lower=str(lower),moment_gain_upper=str(upper),
                           changed_components=sum(modes),local_deficit=sum(k*v for k,v in after.items())-1792*data['ell'],
                           net_profile_delta={str(k):after[k]-before[k] for k in sorted(ranks) if after[k]!=before[k]},
                           genuine_positive_finite_moment=lower>0)
            else:row.update(solver='non-submodular optimization required',modes=None)
            cases.append(row)
        rows.append(dict(ell=data['ell'],interaction_structure={k:v for k,v in structure.items() if k!='colors'},cases=cases))
        print('PASS_WEIGHTED_GAUGE_SETUP',data['ell'],'frustrated',structure['sign_frustrated_edges'],
              [{k:v for k,v in row.items() if k not in ['modes','moment_gain_lower','moment_gain_upper']} for row in cases],flush=True)
    output=dict(status='PASS_CERTIFIED_MOMENT_WEIGHT_GRAPH',kappa=str(KAPPA),q=str(1-KAPPA),scale=SCALE,
                rank_power_bounds={str(r):list(map(str,ab)) for r,ab in bounds.items()},max_quantization_error=str(error),
                results=rows,graph_sha256=sha256((HERE/'MIXED-GAUGE.json.gz').read_bytes()).hexdigest(),
                script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),new_kappa=False,
                scope='Finite weighted rank screen only. Quantization is not an exact irrational optimization theorem; candidate gains are separately checked with rational intervals. Native absolute phases, helper and all-f admission remain open.')
    (HERE/'WEIGHTED-GAUGE.json.gz').write_bytes(gzip.compress(json.dumps(output,sort_keys=True,separators=(',',':')).encode(),mtime=0))


if __name__=='__main__':main()
