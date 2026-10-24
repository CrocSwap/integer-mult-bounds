"""Finite source-expression, exact inverse, and directed enclosure controls.

JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
The universal theorem is the written PROOF, not inferred from this certificate.
"""
import ast,hashlib,importlib.util,json,math,time
from fractions import Fraction as Q
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,message):
    if not ok:raise ValueError(message)
def inverse(a):
    n=len(a);w=[list(row)+[Q(i==j) for j in range(n)] for i,row in enumerate(a)]
    for k in range(n):
        pivot=next(i for i in range(k,n) if w[i][k]);w[k],w[pivot]=w[pivot],w[k]
        scale=w[k][k];w[k]=[v/scale for v in w[k]]
        for i in range(n):
            if i!=k:
                scale=w[i][k];w[i]=[x-scale*y for x,y in zip(w[i],w[k])]
    return [row[n:] for row in w]
def product(a,b):return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*b)] for row in a]
def toeplitz_checks():
    cases=entries=0
    for q in (Q(1,2),Q(2,3),Q(3,4)):
        for n in (1,2,4,8):
            p=[Q(1)]
            for r in range(1,n):p.append(p[-1]*(1-q**(2*r)))
            g=[[q**((i-j)**2) for j in range(n)] for i in range(n)]
            direct=inverse(g)
            def choose(k,i):return p[k]/(p[i]*p[k-i])
            lower=[[(-q)**(i-j)*choose(i,j) if i>=j else Q(0) for j in range(n)] for i in range(n)]
            rebuilt=product([[lower[k][i]/p[k] for k in range(n)] for i in range(n)],lower)
            need(rebuilt==direct,'independent elimination versus finite q-LDU inverse')
            if n==2:
                omitted=product([list(v) for v in zip(*lower)],lower)
                need(omitted!=direct,'omitted inverse pivot discriminator')
            for i in range(n):
                for j in range(n):
                    need(abs(direct[i][j])<=q**abs(i-j)/p[-1]**3,'retained Toeplitz entry theorem');entries+=1
            cases+=1
    return dict(exact_inverse_cases=cases,entry_checks=entries)
class Coordinates(ast.NodeTransformer):
    def visit_Subscript(self,node):
        # Original k[None,:] is the column i; k[:,None] is the row j.
        need(isinstance(node.value,ast.Name) and node.value.id=='k','source coordinate expression')
        slots=node.slice.elts
        column=isinstance(slots[0],ast.Constant) and slots[0].value is None
        return ast.copy_location(ast.Name(id='i' if column else 'j',ctx=ast.Load()),node)
def source_expression():
    path=ROOT/'research/forward-fine-theta-conditioning/verify.py'
    tree=ast.parse(path.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='block')
    selected=[]
    for node in fn.body:
        if isinstance(node,ast.Assign):
            names={n.id for n in ast.walk(node.targets[0]) if isinstance(n,ast.Name)}
            if names&{'rho','lam','b0','c'}:selected.append(node)
            if 'arg' in names:expression=Coordinates().visit(node.value)
    setup=compile(ast.fix_missing_locations(ast.Module(body=selected,type_ignores=[])),'retained-block-setup','exec')
    expr=compile(ast.fix_missing_locations(ast.Expression(expression)),'retained-block-exponent','eval')
    return setup,expr

def geometry_checks():
    setup,expr=source_expression();theta=Q(1,400);rho=1+theta;c=Q(1,2)/rho
    env=dict(alpha=3,theta=theta,beta_start=-Q(1,2),math=SimpleNamespace(pi=Q(1)))
    exec(setup,env);need(env['c']==c and env['lam']==1/rho,'actual original first fixture parameters')
    pairs={(i,j) for i in range(400) for j in (0,1,199,398,399)}|{(i,i) for i in range(400)}
    for i,j in pairs:
        env.update(i=Q(i),j=Q(j));actual=eval(expr,env)
        dc=-Q(1,9)*(theta/rho*i*i-2*c*i)
        dr=Q(1,9)*(theta/rho**2*j*j-2*c/rho*j-c*c)
        need(-actual==dc+dr-Q(1,9)/rho*(i-j)**2,'unchanged source exponent versus exact gauges')
        d=i-j;bi=theta*i-rho*c;bj=theta*j-rho*c
        exponent=-dc-dr-Q(1,9)/rho*abs(d)
        coupled=Q(1,9)*bj*bj/rho**2+Q(1,9)/rho*(d*(bi+bj)-abs(d))
        need(exponent==coupled,'inverse gauge direction and coupled identity')
    for i in range(400):
        for j in range(400):
            d=i-j
            need(d*(i+j-400)-400*abs(d)<=-d*d,'full actual cell endpoint inequality')
    # Both closed endpoints, both signs, translated origins, and failure outside.
    for theta,n in ((Q(1,4),5),(Q(1,10),11),(Q(1,400),401)):
        for origin in (-17,0,29):
            betas=[-Q(1,2)+theta*k for k in range(n)]
            for i in (0,n//2,n-1):
                for j in (0,n//2,n-1):
                    d=i-j;need(d*(betas[i]+betas[j])-abs(d)<=-theta*d*d,'closed endpoints both index orders')
                    shifted_c=(theta*origin+Q(1,2))/(1+theta)
                    need(theta*(origin+i)-(1+theta)*shifted_c==betas[i],'origin shift')
    # Removing the phase-domain premise really breaks the weighted inequality.
    theta=Q(1,4);bi=Q(3,4);bj=bi-theta
    need((bi+bj)-1> -theta,'outside-phase rejection discriminator')
    # Concrete opposite-gauge mutant at a fixed admissible nonzero coordinate.
    theta=Q(1,4);rho=1+theta;c=Q(1,2)/rho;i,j=1,0;d=i-j
    dc=-Q(1,9)*(theta/rho*i*i-2*c*i)
    dr=Q(1,9)*(theta/rho**2*j*j-2*c/rho*j-c*c)
    correct=-dc-dr-Q(1,9)/rho*abs(d)
    need(dc-dr-Q(1,9)/rho*abs(d)!=correct,'wrong inverse gauge discriminator')
    need(inverse([[Q(1,3)]])[0][0]>Q(1),'N1 zero-centre inverse violates omitted alpha normalization')
    return dict(controls=['outside-phase','inverse-gauge-sign','origin-translation','alpha-normalization','both-closed-endpoints'],first_fixture=dict(alpha=3,theta='1/400',N=400,beta_start='-1/2'),source_exponent_pairs=len(pairs),full_phase_pairs=160000)

def intervals():
    spec=importlib.util.spec_from_file_location('retained_intervals',ROOT/'research/shifted-gaussian-conditioning/intervals.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def actual_interval_fixture():
    m=intervals();I=m.I;pi=m.pi_interval();theta=Q(1,400);rho=1+theta;b0=pi/9;gamma=b0/rho
    q=(-gamma).exp();step=q.square();powers=[I(1)];p=[I(1)]
    for k in range(1,400):powers.append(powers[-1]*step);p.append(p[-1]*(1-powers[-1]))
    invp=1/p[-1].power(3);pref=3*(b0/(4*rho*rho)).exp()*invp
    gaussian_sum=1+(pi/(gamma*theta)).sqrt();new=pref*gaussian_sum
    elementary_pref=3*(b0/(4*rho*rho)+pi.square()/(4*gamma)).exp()
    need(pref.hi<elementary_pref.lo,'finite product versus elementary product envelope')
    # A lower bound for the old displayed ceiling, since P_finite >= P_infinity.
    old=3*(3*b0/(4*rho*rho)).exp()/p[-1].power(4)/(1-(-b0/rho*theta).exp()).square()
    need(new.hi<old.lo,'strict improvement over old displayed theta^-2 ceiling')
    maximum=I(0);count=0
    for i in (0,1,20,199,398,399):
        for j in (0,1,20,199,398,399):
            d=i-j;bi=theta*i-Q(1,2);bj=theta*j-Q(1,2)
            weighted=sum((powers[k-max(i,j)]*p[k]/(p[i]*p[j]*p[k-i]*p[k-j]) for k in range(max(i,j),400)),I(0))
            need(weighted.hi<invp.lo,'actual finite inverse q-LDU weighted sum')
            exponent=b0*(bj*bj/rho**2)+gamma*(d*(bi+bj)-abs(d))
            entry=3*exponent.exp()*weighted
            envelope=pref*(-gamma*theta*d*d).exp()
            need(entry.hi<envelope.lo,'actual unrounded inverse entry enclosure')
            maximum=I(max(maximum.lo,entry.lo),max(maximum.hi,entry.hi));count+=1
    return dict(actual_inverse_entries=count,maximum_selected_entry=maximum.record(),new_norm_upper=new.record(),old_ceiling_lower=old.record(),finite_prefactor=pref.record(),interval_arithmetic=m.arithmetic_controls())

def main():
    start=time.monotonic()
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source SHA256: '+row['path'])
    result=dict(geometry=geometry_checks(),exact=toeplitz_checks(),interval=actual_interval_fixture(),claim='finite support for written explicit inverse bound; no sharp leading constant or physical theorem',seconds=round(time.monotonic()-start,6))
    print(json.dumps(result,sort_keys=True));print('PASS_BROAD_PHASE_CELL_INVERSE_BOUND')
if __name__=='__main__':main()
