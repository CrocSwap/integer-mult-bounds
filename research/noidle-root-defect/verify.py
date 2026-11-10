#!/usr/bin/env python3
"""Exact finite controls for the no-idle defect theorem; see PROOF.md.
Jerry Chen / @CubeJerry, substantial OpenAI GPT-6 Astra Pro assistance. Apache-2.0.
"""
import argparse
import ast
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
F, PORTS = 18, 104
EXPECTED = {1:-2220,2:-446,3:-485,4:-1,5:-135,6:-4,7:1,8:39,9:359}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rejected(operation, message):
    try:
        operation()
    except ValueError:
        return
    raise ValueError('Negative control accepted: ' + message)


def authenticate(raw, pin):
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'Retained SHA256')
    framed = b'blob ' + str(len(raw)).encode() + b'\0' + raw
    need(hashlib.sha1(framed).hexdigest() == pin['git_blob'], 'Retained Git blob')


def source_profile():
    pins = json.loads((ROOT/'retained/SOURCE-PINS.json').read_text())['sources']
    need(len(pins) == 1, 'One exact external source')
    pin = pins[0]
    need(pin['head_commit'] == '51f54e3c31f2f3a3e056a483b3ed66ae916ad06a', 'Frozen #6833 head')
    raw = (ROOT/pin['retained_path']).read_bytes()
    authenticate(raw, pin)
    rejected(lambda: authenticate(raw+b'\n', pin), 'source-byte mutation')
    values = {}
    for node in ast.parse(raw).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('HELPERS','LOCAL_PAID'):
                    need(target.id not in values, 'No repeated census assignment')
                    values[target.id] = ast.literal_eval(node.value)
    need(set(values) == {'HELPERS','LOCAL_PAID'}, 'Both native censuses')
    need(all(type(k) is int and type(v) is int and k>0 and v>0
             for row in values.values() for k,v in row.items()), 'Positive integral census')
    helper, paid = values['HELPERS'], values['LOCAL_PAID']
    d = {r:helper.get(r,0)-paid.get(r,0) for r in sorted(set(helper)|set(paid))}
    need(d == EXPECTED, 'Recounted signed native profile')
    need(sum(r*c for r,c in d.items()) == -1720, 'Native rank mass')
    return d, pin


# log(u)=2*atanh((u-1)/(u+1)); range reduction keeps 0<=z<=1/3.
# The omitted positive tail after m terms is bounded by replacing every
# denominator by 2*m+1 and summing the resulting geometric series.
def log_unit(u):
    need(Q(1)<=u<=Q(2), 'Logarithm range reduction')
    z = (u-1)/(u+1)
    total, power, m = Q(0), z, 48
    for j in range(m):
        total += power/(2*j+1)
        power *= z*z
    lo = 2*total
    return lo, lo+2*power/((2*m+1)*(1-z*z))


@lru_cache(maxsize=None)
def log_bounds(r):
    need(type(r) is int and r>=1, 'Positive integer logarithm')
    k = r.bit_length()-1
    a,b = log_unit(Q(2))
    c,d = log_unit(Q(r,2**k))
    return k*a+c,k*b+d


def exp_polynomial(a, degree):
    need(Q(0)<=a<=Q(1), 'Alternating exponential range')
    total = term = Q(1)
    for j in range(1,degree+1):
        term *= -a/j
        total += term
    return total


@lru_cache(maxsize=None)
def power_bounds(r,kappa):
    need(Q(0)<=kappa<=Q(1), 'Exponent domain')
    if r==1 or kappa==0:
        return Q(r),Q(r)
    lo,hi = log_bounds(r)
    # exp(-a) decreases: odd-degree Taylor at the upper a is a lower bound;
    # even-degree Taylor at the lower a is an upper bound, by alternating terms.
    lower = r*exp_polynomial(kappa*hi,11)
    upper = r*exp_polynomial(kappa*lo,12)
    need(0<lower<=upper<=r, 'Positive ordered power enclosure')
    return lower,upper


def interval_sum(coefficients,kappa):
    lo=hi=Q(0)
    for r,c in sorted(coefficients.items()):
        a,b = power_bounds(r,kappa)
        lo += c*(a if c>=0 else b)
        hi += c*(b if c>=0 else a)
    return lo,hi


def enclosure(bounds, places=14):
    scale = 10**places
    low = bounds[0].numerator*scale//bounds[0].denominator
    high = -((-bounds[1].numerator*scale)//bounds[1].denominator)
    def text(value):
        sign = '-' if value<0 else ''
        value=abs(value)
        return sign+str(value//scale)+'.'+str(value%scale).zfill(places)
    return [text(low),text(high)]


def envelope(native,defect):
    c = {r:F*v for r,v in native.items()}
    extra = {25:6,9:18,1:-9} if defect==3 else {9:36,1:-22}
    for r,v in extra.items():
        c[r]=c.get(r,0)+PORTS*v
    return c


def prices(native):
    brackets = {3:('0.0033288660495','0.0033288660497'),
                4:('0.0029312090589','0.0029312090593')}
    out={}
    for defect in (3,4):
        c=envelope(native,defect)
        lower,upper=brackets[defect]
        left,right=interval_sum(c,Q(lower)),interval_sum(c,Q(upper))
        need(left[0]>0 and right[1]<0, 'Strict crossing bracket')
        headline=interval_sum(c,Q('.00337180'))
        test=interval_sum(c,Q('.0033718004755'))
        need(headline[1]<0 and test[1]<0, 'Cannot reach pending benchmark')
        fence=(Q('-7.086'),Q('-7.085')) if defect==3 else (Q('-67.047'),Q('-67.046'))
        need(fence[0]<test[0]<=test[1]<fence[1], 'Displayed negative interval')
        need(sum(r*v for r,v in c.items())==(552 if defect==3 else 448), 'Exact t=1 endpoint')
        need(sum(c.values())<0, 'Exact t=0 endpoint')
        out[str(defect)]={'crossing_bracket':[lower,upper],
                         'lower_margin':enclosure(left),'upper_margin':enclosure(right),
                         'pending_headline_margin':enclosure(headline),
                         'pending_raw_upper_margin':enclosure(test)}
    bound=Q(2220*8,81)-Q(2,7)-Q(39,8)
    need(bound==Q(323717,1512) and bound>0, 'Normalized derivative bound')
    need(F>2*2*(2+1), 'Defects one and two exclude eighteen full calls')
    rejected(lambda:power_bounds(9,Q(-1,100)), 'negative kappa')
    need(power_bounds(25,Q(0))==(Q(25),Q(25)), 'Integer-power endpoint')
    p9=power_bounds(9,Q('.00337180'))
    for d in range(2,37):
        pd=power_bounds(1+8*d,Q('.00337180'))
        need(pd[1]-1<d*(p9[0]-1), 'Finite integer-degree concavity control')
    return out,str(bound)


def eye(n):
    return [[Q(i==j) for j in range(n)] for i in range(n)]


def multiply(a,b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))),Q(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def rank(matrix):
    if not matrix:
        return 0
    a=[[Q(x) for x in row] for row in matrix]
    rows,cols,pivot=len(a),len(a[0]),0
    for col in range(cols):
        row=next((r for r in range(pivot,rows) if a[r][col]),None)
        if row is None:
            continue
        a[pivot],a[row]=a[row],a[pivot]
        divisor=a[pivot][col]
        a[pivot]=[x/divisor for x in a[pivot]]
        for r in range(pivot+1,rows):
            if a[r][col]:
                factor=a[r][col]
                a[r]=[x-factor*y for x,y in zip(a[r],a[pivot])]
        pivot+=1
        if pivot==rows:
            break
    return pivot


def inverse(a):
    n=len(a)
    work=[[Q(x) for x in row]+identity for row,identity in zip(a,eye(n))]
    for col in range(n):
        row=next((r for r in range(col,n) if work[r][col]),None)
        need(row is not None,'Invertible matrix')
        work[col],work[row]=work[row],work[col]
        divisor=work[col][col]
        work[col]=[x/divisor for x in work[col]]
        for r in range(n):
            if r!=col and work[r][col]:
                factor=work[r][col]
                work[r]=[x-factor*y for x,y in zip(work[r],work[col])]
    return [row[n:] for row in work]


def query_matrix(x,y):
    n=len(x)
    need(len(y)==n and any(x) and any(y),'Nonzero rank-one query')
    need(sum((a*b for a,b in zip(x,y)),Q(0))==0,'Square-zero query')
    return [[Q(i==j)-2*x[i]*y[j] for j in range(n)] for i in range(n)]


def check_root(queries,full):
    n,total=len(queries[0][0]),len(queries)
    endpoint=eye(n)
    for x,y in queries:
        endpoint=multiply(query_matrix(x,y),endpoint)
    need(endpoint==[[-x for x in row] for row in eye(n)],'Complete root endpoint')
    xmat=[[queries[j][0][i] for j in range(total)] for i in range(n)]
    ymat=[list(y) for _,y in queries]
    gram=multiply(ymat,xmat)
    a=[[Q(i==j)+(2*gram[i][j] if i>j else 0) for j in range(total)] for i in range(total)]
    b=[[a[i][j]-gram[i][j] for j in range(total)] for i in range(total)]
    need(multiply(multiply(xmat,inverse(a)),ymat)==eye(n),'Independent displacement identity')
    defect=total-n
    need(rank(b)==defect,'Complete A-G rank defect')
    supports=[]
    for index in full:
        x,y=queries[index]
        support={i for i in range(n) if x[i] or y[i]}
        need(len(support)==2,'Full support is a coordinate pair')
        supports.append(tuple(sorted(support)))
    active=set(v for edge in supports for v in edge)
    bfull=[[b[i][j] for j in full] for i in full]
    need(len(full)<=len(active)+rank(bfull)<=len(active)+defect,
         'Full occurrences versus active coordinates and defect')
    need(len(full)<=2*defect*(defect+1),'Universal full-call bound on root fixture')
    return {'n':n,'N':total,'F':len(full),'defect':defect,
            'distinct_supports':len(set(supports)),'active_coordinates':len(active)}


def direct_sum_root(blocks):
    # In two dimensions these three I-2xy factors multiply to -I.
    template=[((1,0),(0,-1)),((0,1),(1,0)),((-1,1),(1,1))]
    out=[]
    for block in range(blocks):
        for x,y in template:
            xx=[Q(0)]*(2*blocks);yy=xx[:]
            xx[2*block:2*block+2]=map(Q,x)
            yy[2*block:2*block+2]=map(Q,y)
            out.append((xx,yy))
    return out


def roots():
    fixtures=[]
    for blocks in (1,2,3,4,6):
        word=direct_sum_root(blocks)
        fixtures.append(check_root(word,list(range(len(word)))))
        # Insert arbitrary dense thin queries R,-R: their product is identity
        # because R^2=0. Neither is constrained to a full coordinate pair.
        x=[Q(1)]*(2*blocks)
        y=[Q((-1)**i) for i in range(2*blocks)]
        word[1:1]=[(x,y),([-a for a in x],y)]
        full=[0]+list(range(3,len(word)))
        fixtures.append(check_root(word,full))
    word=direct_sum_root(2)
    x,y=word[0]
    damaged=[([-a for a in x],y)]+word[1:]
    rejected(lambda:check_root(damaged,list(range(6))),'wrong root coefficient')
    rejected(lambda:query_matrix([Q(0),Q(0)],[Q(1),Q(0)]),'zero query')
    rejected(lambda:query_matrix([Q(1)],[Q(1)]),'one-coordinate nonzero nilpotent')
    need(fixtures[2]['F']==6 and fixtures[2]['distinct_supports']==2,
         'Parallel occurrences retain native-call multiplicity')
    return fixtures


def star_controls():
    alphabet=((0,1),(1,0),(1,1),(1,-1),(2,3))
    checked=zero_cases=0
    for size in range(1,6):
        for pairs in product(alphabet,repeat=size):
            b=[[Q(i==j)+((i>j)-(i<j))*pairs[i][1]*pairs[j][0]
                for j in range(size)] for i in range(size)]
            zeros=sum(a*c==0 for a,c in pairs)
            need(rank(b)>=zeros+(size-zeros+1)//2,'Star rank with zero-product pivots')
            checked+=1
            zero_cases+=bool(zeros)
    # The factor two in the isolated star rank estimate cannot be replaced by
    # one without another premise. This does not assert a complete root exists.
    signs=(-1,1,-1,1)
    b=[[Q(i==j)+((i>j)-(i<j))*signs[i] for j in range(4)] for i in range(4)]
    need(rank(b)==2,'Rank-two four-leaf principal-star fixture')
    rejected(lambda:need(rank(b)>=4,'False star rank >= degree'),'false degree strengthening')
    return {'alphabet':[list(pair) for pair in alphabet], 'maximum_size':5,
            'matrices_checked':checked,'matrices_with_zero_products':zero_cases,
            'four_leaf_rank':rank(b)}


def graph_parameters(adjacency):
    @lru_cache(maxsize=None)
    def matching(mask):
        if not mask:
            return 0
        bit=mask&-mask
        vertex=bit.bit_length()-1
        rest=mask^bit
        best=matching(rest)
        partners=adjacency[vertex]&rest
        while partners:
            partner=partners&-partners
            partners^=partner
            best=max(best,1+matching(rest^partner))
        return best
    v=sum(bool(row) for row in adjacency)
    delta=max((row.bit_count() for row in adjacency),default=0)
    nu=matching((1<<len(adjacency))-1)
    return v,nu,delta


def graph_controls():
    counts={}
    for n in range(1,7):
        edges=[(i,j) for i in range(n) for j in range(i+1,n)]
        for mask in range(1<<len(edges)):
            adjacency=[0]*n
            for k,(i,j) in enumerate(edges):
                if mask>>k&1:
                    adjacency[i]|=1<<j
                    adjacency[j]|=1<<i
            v,nu,delta=graph_parameters(tuple(adjacency))
            need(v<=nu*(delta+1),'Maximum-matching graph inequality')
        counts[str(n)]=1<<len(edges)
    # The central edge is a maximal matching of P4, but not a maximum one.
    # With that size-one matching, the claimed inequality would incorrectly say 4<=3.
    path=(2,5,10,4)
    v,nu,delta=graph_parameters(path)
    need((v,nu,delta)==(4,2,2),'P4 independent matching control')
    rejected(lambda:need(v<=1*(delta+1),'Wrong maximal matching'),'maximal versus maximum')
    return {'all_labelled_simple_graphs_by_order':counts,'total':sum(counts.values()),
            'maximal_matching_counterexample':'P4 central edge'}


def invoice(native,degrees,defect,thin=None):
    need(sum(degrees)==36 and all(type(d) is int and d>=0 for d in degrees),
         'All thirty-six full-call incidences, with multiplicity')
    q=len(degrees)+defect-F
    need(q>=0,'Nonnegative thin-query count')
    if thin is not None:
        need(thin==q,'Thin count equals N-F=n+defect-F')
    coefficients={r:F*c for r,c in native.items()}
    for d in degrees:
        r=1+8*d
        coefficients[r]=coefficients.get(r,0)+PORTS
    coefficients[1]-=PORTS*q
    return {r:c for r,c in coefficients.items() if c}


def invoice_controls(native):
    d3=[3]*6+[1]*18
    d4=[1]*36
    need(invoice(native,d3,3)==envelope(native,3),'E3 relaxed degree census')
    need(invoice(native,d4,4)==envelope(native,4),'E4 relaxed degree census')
    # Actual direct sum: six independent two-dimensional roots, three full
    # calls on each pair. Added degree-zero fields cancel with paid thin terms.
    actual=[3]*12
    need(invoice(native,actual,6)==invoice(native,actual+[0]*4,6),
         'Inactive productive fields retain their cancelling query charge')
    rejected(lambda:invoice(native,d3,3,thin=8),'omitted thin query')
    rejected(lambda:invoice(native,[1]*12,6),'parallel calls collapsed to distinct supports')
    paid=invoice(native,d3,3)
    unpaid=dict(paid);unpaid[1]+=104
    need(interval_sum(paid,Q('.00337180'))[1]<0<interval_sum(unpaid,Q('.00337180'))[0],
         'Omitting one thin charge creates a false favorable envelope')
    return {'relaxed_degree_censuses':{'defect3':d3,'defect4':d4},
            'actual_direct_sum_degrees':actual,'inactive_cancellation':4,
            'omitted_thin_charge_rejected':True,'parallel_collapse_rejected':True}


def run():
    native,pin=source_profile()
    price,bound=prices(native)
    return {'schema_version':1,'result':'PASS_NOIDLE_ROOT_DEFECT',
            'claim':'F <= 2*delta*(delta+1), coordinate rank-two no-idle class only',
            'no_new_kappa':True,'native_source':pin,
            'native_signed_profile':{str(r):c for r,c in native.items()},
            'envelopes':price,'normalized_derivative_lower_bound':bound,
            'root_fixtures':roots(),'star_controls':star_controls(),
            'graph_controls':graph_controls(),'invoice_controls':invoice_controls(native),
            'negative_controls':['source-byte corruption','negative kappa',
                'wrong root coefficient','zero query','one-coordinate nilpotent',
                'false rank>=star-degree','maximal instead of maximum matching',
                'omitted thin query','parallel-occurrence collapse'],
            'universal_proof':'PROOF.md; finite controls do not establish universal coverage'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Regenerate deterministic RESULT.json')
    args=parser.parse_args()
    result=run()
    path=ROOT/'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(path.is_file(),'RESULT.json exists; use --write only for author regeneration')
        need(result==json.loads(path.read_text()),'Exact deterministic result replay')
    print(result['result'])
    print('No new kappa; F=18 requires defect>=3; both complete envelopes lose to 0.00337180.')
    print('Exact controls: '+str(result['graph_controls']['total'])+' graphs, '+
          str(result['star_controls']['matrices_checked'])+' star blocks, '+
          str(len(result['root_fixtures']))+' roots, 9 rejection controls.')


if __name__=='__main__':
    main()
