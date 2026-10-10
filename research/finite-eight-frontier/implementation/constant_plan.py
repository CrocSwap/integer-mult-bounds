"""Exact symbolic sequential constants. No astronomical 2**L is materialized."""
from fractions import Fraction as Q
def need(ok,why):
    if not ok:raise ValueError(why)
def ceilq(q):return -((-q.numerator)//q.denominator)
def number(n):need(type(n) is int and n>=0,'constant exact nonnegative integer');return {'op':'integer','value':n}
def ref(name):return {'op':'reference','name':name}
def mul(a,b):return {'op':'multiply','arguments':[a,b]}
def add(a,b):return {'op':'add','arguments':[a,b]}
def cutoff_expression(delta,C):
    need(0<delta<=1,'sequential cutoff positive gap')
    return {'op':'maximum','arguments':[number(1),number(ceilq(36/delta**2)),{'op':'ceiling','argument':mul({'op':'rational','value':str(2/delta)},add(number(4),{'op':'ceil_log2','argument':C}))}]}
def expected_level(j,old,next_,delta,recipe,induction_factor):
    oldname='C_old_0' if j==0 else 'C_next_'+str(j-1)
    # Chosen before L: dominate every previous ordinary constant and every
    # fixed primitive/wrapper/row/stock recipe coefficient, all >=1.
    C=mul(number(recipe),mul(ref('P_'+str(j)),add(number(1),ref(oldname))))
    L=cutoff_expression(delta,ref('C_toll_'+str(j)))
    large=mul(number(induction_factor),ref('C_toll_'+str(j)))
    exponent={'op':'ceiling','argument':mul(ref('L_'+str(j)),{'op':'rational','value':str(next_-old)})}
    inflation={'op':'power_two','exponent':exponent}
    completed=add(ref('C_large_'+str(j)),mul(ref(oldname),inflation))
    return {'stage':j,'old_saving':str(old),'next_saving':str(next_),'gap':str(delta),'old_constant':oldname,'toll_name':'C_toll_'+str(j),'toll':C,'cutoff_name':'L_'+str(j),'cutoff':L,'large_name':'C_large_'+str(j),'large':large,'next_name':'C_next_'+str(j),'next':completed,'small_width_inflation_exponent':exponent}
def validate(plan,chain,gaps,recipe,induction_factor):
    need(type(plan) is dict and len(plan.get('levels',[]))==len(gaps) and len(chain)==len(gaps)+1 and 1<=len(gaps)<=10,'bounded sequential ordinary constant levels')
    need(type(recipe) is int and recipe>=1 and type(induction_factor) is int and induction_factor>=1 and plan.get('recipe_coefficient')==recipe and plan.get('induction_factor')==induction_factor,'sequential actual recipe/induction bindings')
    linear=Q(plan['linear_gap']);stopped=Q(plan['stopped_gap']);need(0<linear<=1 and 0<stopped<=1 and induction_factor==ceilq(1+1/linear+1/stopped),'sequential large-width contraction majorant')
    need(plan.get('variables')==[{'name':'C_old_0','domain':'integer >=1, inherited completed ordinary leaf constant'},*[{'name':'P_'+str(j),'domain':'integer >=1, already fixed primitive/row/wrapper/setup/padding constant'} for j in range(len(gaps))]],'quantified constant domains')
    available={'C_old_0'}|{'P_'+str(j) for j in range(len(gaps))}
    def references(expr):
        if type(expr) is dict:
            if expr.get('op')=='reference':return {expr['name']}
            out=set()
            for value in expr.values():out.update(references(value))
            return out
        if type(expr) is list:
            out=set()
            for value in expr:out.update(references(value))
            return out
        return set()
    for j,level in enumerate(plan['levels']):
        expected=expected_level(j,chain[j],chain[j+1],gaps[j],recipe,induction_factor)
        for name,expr in (('toll_name','toll'),('cutoff_name','cutoff'),('large_name','large'),('next_name','next')):
            need(references(level[expr])<=available,'noncircular sequential constant dependency');available.add(level[name])
        need(level==expected,'sequential ordinary small-width inflation formula')
        need(chain[j+1]>chain[j] and gaps[j]>0,'sequential positive saving/gap')
    return {'levels':len(gaps),'sequential_noncirculation':1,'small_width_factor':'2**ceil(L*(a_next-a_old)) >= 2**(L*(a_next-a_old))','large_width_induction':'C_large >= C_toll*(1+1/gap_linear+1/gap_stopped)','cutoff_proof':'L delta^2 >=36 and L delta >=2*(4+ceilLog2 C_toll); all e>=2**L lower toll <=1/16','small_width_proof':'w<2**L implies C_old*w**(a_next-a_old)<=C_old*2**ceil(L*(a_next-a_old))','scope':'exact quantified finite expression DAG; inherited fixed primitive constants not numerically evaluated'}
def build(chain,gaps,recipe,linear_gap,stopped_gap):
    need(len(chain)==len(gaps)+1 and 1<=len(gaps)<=10 and type(recipe) is int and recipe>=1 and 0<linear_gap<=1 and 0<stopped_gap<=1,'finite sequential constant inputs')
    factor=ceilq(1+1/linear_gap+1/stopped_gap)
    plan={'variables':[{'name':'C_old_0','domain':'integer >=1, inherited completed ordinary leaf constant'},*[{'name':'P_'+str(j),'domain':'integer >=1, already fixed primitive/row/wrapper/setup/padding constant'} for j in range(len(gaps))]],'induction_factor':factor,'linear_gap':str(linear_gap),'stopped_gap':str(stopped_gap),'recipe_coefficient':recipe,'levels':[expected_level(j,chain[j],chain[j+1],gaps[j],recipe,factor) for j in range(len(gaps))]}
    plan['proof']=validate(plan,chain,gaps,recipe,factor);return plan
