"""Exact ambient-cap majorants. @CubeJerry, OpenAI assistance, Apache-2.0."""
from fractions import Fraction as Q

def need(x,m):
    if not x:raise ValueError(m)

def log_integer(n):
    need(type(n) is int and n>=1,'positive log input')
    def series(x):
        z=(x-1)/(x+1);v=80
        lo=2*sum((z**(2*j+1)/(2*j+1) for j in range(v)),Q(0))
        return lo,lo+2*z**(2*v+1)/((2*v+1)*(1-z*z))
    k=n.bit_length()-1;a,b=series(Q(2));c,d=series(Q(n,2**k))
    return k*a+c,k*b+d

def log_one_minus(x):
    need(0<=x<1,'complement log input');v=80
    hi=-sum((x**j/j for j in range(1,v+1)),Q(0))
    return hi-x**(v+1)/((v+1)*(1-x)),hi

def bounds(saving,ambient=153,power=1920,theta_numerator=63,theta_denominator=64,log_power=2300):
    saving=Q(saving);a,b=log_integer(ambient);c,d=log_one_minus(saving)
    x,y=log_one_minus(1-Q(theta_numerator,theta_denominator))
    eta=(c-power*saving*b,d-power*saving*a);two=log_integer(2)
    return dict(log_complement_margin=(eta[0]-log_power*y,eta[1]-log_power*x),log_base_margin=(log_power*two[0]-power*saving*b,log_power*two[1]-power*saving*a),log_eta=eta,log_theta_power=(log_power*x,log_power*y))

def show(pair):
    scale=10**30;lo,hi=pair
    return [str(Q((lo*scale).__floor__(),scale)),str(Q(-((-hi*scale).__floor__()),scale))]

def verify():
    source=Q('0.00351406007');cap=Q('0.0036');new=bounds(cap)
    need(new['log_complement_margin'][0]>0 and new['log_base_margin'][0]>0,'2300 covers actual153 through saving.0036')
    old=bounds(source,log_power=2134)
    need(old['log_complement_margin'][1]<0,'2134 fails conservative153 cap')
    prior=bounds(source,ambient=145,log_power=2134)
    need(prior['log_complement_margin'][0]>0,'2134 succeeds stated145 cap')
    need(11**64<12**63,'separated exits')
    need(2*11**(1920*64)<=153**(1920*63),'shifted exit log')
    step,j=10**11,122933
    need((step*j+1)**2300<2**j and (step*(j-1)+1)**2300>=2**(j-1),'uniform grid and predecessor')
    return dict(ambient_cap=153,maximum_productive_rank=145,power=1920,cutoff_base=11,completion_base=12,theta_bar='63/64',covered_saving_interval=['0','0.0036'],logarithm_power=2300,cap_log_margins={k:show(v) for k,v in new.items()},source2134_actual153_log_margin=show(old['log_complement_margin']),source2134_stated145_log_margin=show(prior['log_complement_margin']),uniform_gap='1/100000000000',first_winning_grid_index=j,uniform_rank_log2=step*j,scope='Geometry and majorant only; raw moment, BIT, physical and outer predicates remain separate.')

if __name__=='__main__':
    import json
    print(json.dumps(verify(),indent=2,sort_keys=True));print('PASS_ACTUAL_AMBIENT_MAJORANT')
