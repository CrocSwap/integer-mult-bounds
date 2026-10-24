"""Independent tight tail/rank-compiler/bootstrap arithmetic successor.

Uses the separately implemented PR4760 census and positive-series engine.
No primary price/tail/interval module is imported or called.
"""
from pathlib import Path
# Apache-2.0. Internal independent OpenAI Codex check for ai-nanachi.
from fractions import Fraction as F
from decimal import Decimal,localcontext
from hashlib import sha256
import importlib.util,json,sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PKG=HERE.parent/'bit-compact-productive-controller'
PRIMARY=HERE/'RESULT.json'
TESTED=F('.00347545806');UNIFORM=F('.00347545805')
ETA=F(1,2**39);V=1024;U=F(1,5);RHO=F(1,100)
COVER_GAP=F(1,2**36)+F(1,10**20);C1=UNIFORM-COVER_GAP
PRIME=2**45;B0=F('.0034597');OLD_EXACT=F(17713901828029,5120000000000000)


def need(v,m):
    if not v:raise ValueError(m)


def ceil(x):return -((-x.numerator)//x.denominator)
def floor(x):return x.numerator//x.denominator


def decimal(x):
    with localcontext() as c:
        c.prec=60;return str(Decimal(x.numerator)/x.denominator)


def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x


def main():
    ipath=PKG/'independent_price.py'
    spec=importlib.util.spec_from_file_location('separate_PR4760_tight_census',ipath);I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
    T,P,local,helpers,baseline=I.census();X=I.X
    need(sum(T.values())==11400 and sum(P.values())==57339 and helpers=={4:4,8:432},'unchanged actual productive unit')
    t=1-TESTED;target=X.moment(T,t);paid=X.moment(P,t)
    alpha=X.div(paid,target)
    gamma=X.div(X.moment(P,t+U),X.mul(X.power(17,U),target))
    delta=X.div((F(sum(T.values())*18),)*2,X.mul(X.power(17,TESTED),target))
    need(alpha[1]<1-ETA,'tight strict raw alpha gap')
    need(gamma[1]<F(31,32) and delta[1]<F(19,20),'both completely charged tails')
    need(F(31,32)**128<F(1,16) and F(19,20)**128<F(1,16),'tail blocks imply2^-32decay atpower1024')
    surplus=1-1/(1+V*ETA)-F(4,2**32)
    need(surplus>0,'alpha Bernoulli bound plus both tails strictly contracts')
    h=F(1,64);z=1-UNIFORM;z0=(t+z)/2;g=z0-t
    overhead=(5+8*h)*V;debt=1+8*V*(1-z0)
    H0=ceil((g*overhead+debt)/(h*g));H1=floor(H0*(1-z0)/(z-z0))+1
    need(g>0 and H0>=8*V and H0*h*g>=g*overhead+debt,'new effective compiler induction')
    need(H1*(z-z0)>H0*(1-z0),'new uniform rank bound')
    need(17**64<18**63 and max(T)<256,'strict completed rank separation')
    need(F(PRIME)>256/COVER_GAP,'complete delayed-cover fallback prime budget')
    previous=B0;levels=[]
    for level in range(1,4):
        exact=(1-RHO)*C1+RHO*previous;admitted=F(floor(exact*10**10),10**10)
        if exact==admitted:admitted-=F(1,10**10)
        row=dict(level=level,backend_level=level-1,completed_backend_saving=previous,ordinary_exact=exact,ordinary_exact_decimal=decimal(exact),admitted=admitted,admitted_decimal=decimal(admitted),adapter_gap=RHO-exact,stock_gap=1-exact-RHO,ordinary_relaxation_gap=exact-admitted,improvement_gap=admitted-previous)
        need(all(row[k]>0 for k in('adapter_gap','stock_gap','ordinary_relaxation_gap','improvement_gap')),'all finite ordinary stage gaps')
        need((1-RHO)*(1-C1)+RHO*(1-previous)==1-exact,'actual ordinary body exponent')
        levels.append(row);previous=admitted
    need(previous==F(1737729,500000000),'independently derived final finegrid saving')
    # Only now read and compare the primary table, including every level's tail.
    primary=json.loads(PRIMARY.read_bytes())
    need(F(primary['C1'])==C1 and primary['new_H0']==H0 and primary['new_H1']==H1,'primary newrank constants agree')
    shared={'tested':TESTED,'uniform':UNIFORM,'cover_gap':COVER_GAP,'atom':RHO,'alpha_gap':ETA,'prime_coefficient':F(PRIME)}
    need(all(F(primary['params_shared'][k])==v for k,v in shared.items()),'all primary shared parameters')
    need(len(primary['levels'])==3,'three completed finite levels')
    for computed,root in zip(levels,primary['levels']):
        for k in('level','completed_backend_saving','ordinary_exact','admitted'):
            need(F(root[k])==computed[k],'independent stage agreement '+k)
        cert=root['certificate'];tail=cert['tail'];need(tail['compiler_H0']==H0 and tail['uniform_H1']==H1,'all levels use the newcompiler bounds')
        need(all(F(cert['params'][k])==v for k,v in shared.items()),'all per-level shared parameters')
        need(F(cert['params']['old_backend'])==computed['completed_backend_saving'] and F(cert['params']['admitted'])==computed['admitted'],'actual predecessor/admission at each level')
        need(F(cert['after_cover'])==C1 and F(cert['ordinary_exact'])==computed['ordinary_exact'] and F(cert['admitted'])==computed['admitted'],'nested certificate exact values')
        need(F(tail['tested_saving'])==TESTED and F(tail['uniform_saving'])==UNIFORM and tail['tensor_power']==V and tail['cutoff_base']==17 and tail['target_floor_base']==18 and F(tail['tail_exponent'])==U,'entire tail and cutoff parameters')
        need(F(tail['normalized_surplus_lower'])==surplus,'primary strict tail surplus')
        for name,bounds in [('alpha',alpha),('gamma',gamma),('delta',delta)]:
            display=tail[name]
            need(F(display['lower'])<=bounds[0]<=bounds[1]<=F(display['upper']),'independent series enclosure contained in primary '+name)
        margins=cert['margins']
        need(F(margins['adapter'])==computed['adapter_gap'] and F(margins['stock'])==computed['stock_gap'] and F(margins['ordinary_relaxation'])==computed['ordinary_relaxation_gap'],'all stage margins agree')
        need(F(margins['prime_allowance'])==F(PRIME)-256/COVER_GAP,'all per-stage full prime allowances')
    gain=previous/OLD_EXACT-1
    need(F(primary['relative_gain_over_previous_exact'])==gain,'comparison against actual previous exact')
    controls={}
    def reject(label,condition):
        need(not condition,'bad control unexpectedlypasses '+label);controls[label]='REJECT'
    reject('old_alpha_gap_2^-32',alpha[1]<1-F(1,2**32))
    reject('weaker_alpha_gap_2^-40_same_tailbudget',1-1/(1+V*F(1,2**40))-F(4,2**32)>0)
    reject('old_H0',377227157504*h*g>=g*overhead+debt)
    reject('old_H1',262206447682297857*(z-z0)>H0*(1-z0))
    reject('old_atom_00346',F('.00346')>levels[-1]['ordinary_exact'])
    reject('closed_covered_limit',levels[-1]['ordinary_exact']>C1)
    reject('unfunded_prime_2^36',F(2**36)>256/COVER_GAP)
    rawlo=F('.003475458064076428997514');rawhi=F('.003475458064076428997515')
    result=dict(status='PASS_INDEPENDENT_TIGHT_TAIL_NEW_COMPILER_AND_THREE_FINITE_LEVELS',targets=T,paid=P,local=local,helpers=helpers,tested=TESTED,uniform=UNIFORM,t=t,alpha_gap=ETA,alpha=alpha,gamma=gamma,delta=delta,tail_surplus=surplus,compiler_H0=H0,uniform_H1=H1,uniform_N_symbolic='2^'+str(H1),cover_gap=COVER_GAP,C1=C1,prime_coefficient=PRIME,prime_allowance_margin=F(PRIME)-256/COVER_GAP,levels=levels,admitted=previous,relative_gain_over_PR4760_exact=gain,percent_gain_over_PR4760_exact=decimal(100*gain),raw_crossing_minus_admitted=[rawlo-previous,rawhi-previous],negative_controls=controls,primary_price_imported=False,actual_backend_API_independently_verified=False,new_WORD=False,new_whole_kappa=False,sourcepins={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in(ipath,PKG/'exact_series.py',PKG/'SOURCES.json',PRIMARY)},scope='Same rawSOURCE unit; new tested/uniform exponents require NEW compiled rankN,q/ROW/height/tape/stock constants. Numeric finite stages only; actual completebackend API/algorithm freezing remains under same sourcebridge conditional framework. No infinite-limit or materialized uniformWORD claim.')
    encoded=encode(result);target=HERE/'INDEPENDENT.json'
    if '--write'in sys.argv:target.write_bytes((json.dumps(encoded,sort_keys=True,indent=2)+'\n').encode())
    else:need(encoded==json.loads(target.read_bytes()),'Deterministic independent certificate')
    print(json.dumps(dict(status=result['status'],H0=H0,H1=H1,tail_surplus=str(surplus),separators=[r['admitted_decimal'] for r in levels],percent_gain=result['percent_gain_over_PR4760_exact'],controls=len(controls))))


if __name__=='__main__':main()
