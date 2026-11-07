#!/usr/bin/env python3
"""All-count aligned-arm ceiling; @CubeJerry/OpenAI, Apache-2.0."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import argparse
import json
import price_ceiling as p


def direct(total, arms, thin=None):
    p.need(type(arms) is int and arms>=3, 'at least three aligned arms')
    p.need(type(total) is int and total>=arms, 'positive arm sizes')
    if thin is None:thin=2+(arms+1)//2
    z=Counter({a:total*c for a,c in p.NATIVE.items()})
    z[8*total+1]+=208;z[8*total]-=104;z[1]-=104*thin
    q,r=divmod(total,arms)
    for g,mult in ((q,arms-r),(q+1,r)):
        for j in range(1,g+1):z[8*j+1]+=104*mult
        for j in range(1,g):z[8*j]-=104*mult
    return dict(z)


def binary(total, arms):
    p.need(arms>=3 and total>=arms, 'aligned-arm domain')
    z=p.moment({a:total*c for a,c in p.NATIVE.items()})
    outer=p.add(p.scale(p.power(8*total+1),2),p.scale(p.power(8*total),-1))
    charge=2+(arms+1)//2
    outer=p.add(outer,(-charge*p.SCALE,-charge*p.SCALE))
    cap=p.add(p.scale(p.delta(2),2),(-p.SCALE,-p.SCALE))
    q,r=divmod(total,arms)
    for g,mult in ((q,arms-r),(q+1,r)):
        side=p.power(8*g+1)
        for j in range(1,g):
            d=p.delta(j)
            side=p.add(side,(max(d[0],cap[0]),max(d[1],cap[1])))
        outer=p.add(outer,p.scale(side,mult))
    return p.add(z,p.scale(outer,104))


def three_certificate(optimum=33):
    before=p.moment(p.difference(direct(optimum,3),direct(optimum-1,3)))
    after=p.moment(p.difference(direct(optimum+1,3),direct(optimum,3)))
    maximum=p.moment(direct(optimum,3))
    gap=p.add(p.add(p.delta(11),p.scale(p.delta(2),-2)),(p.SCALE,p.SCALE))
    p.need(before[0]>0 and after[1]<0, 'three-arm adjacent signs')
    p.need(maximum[1]<0 and gap[0]>0, 'three-arm negative binary envelope')
    p.need(Fraction(25,24)**2<2, 'three-arm concavity ratio')
    return {'before':before,'after':after,'maximum':maximum,'binary_gap':gap}


def run():
    p.authenticate((p.HERE/'retained/CHAIN-RESULT.json').read_bytes())
    a9=Counter({8*j+1:1 for j in range(1,10)})
    for j in range(1,9):a9[8*j]-=1
    slope={81:1,72:-1}
    z={a:2*a9[a]-18*slope.get(a,0) for a in set(a9)|set(slope)}
    z[1]=z.get(1,0)-1
    intercept=p.moment(z)
    p.need(intercept[1]<0, 'negative all-arm supporting-line intercept')
    four=p.certificate();three=three_certificate()
    cases=0
    for arms in range(3,25):
        for total in range(arms,97):
            p.need(binary(total,arms)[1]<0, 'finite all-arm binary corroboration')
            cases+=1
    def undercharged():
        p.need(p.moment(direct(38,6,thin=4))[1]<0, 'missing growing thin charge')
    controls=[p.reject(lambda:three_certificate(32),'false three-arm maximum32'),
              p.reject(lambda:three_certificate(34),'false three-arm maximum34'),
              p.reject(lambda:direct(38,2),'two-arm scope extension'),
              p.reject(undercharged,'constant four-query charge at six arms')]
    p.need(p.moment(direct(38,6,thin=4))[0]>0, 'undercharged model is favorable')
    return {'status':'PASS_ALL_ALIGNED_ARMS_PRICE','saving':'1/310',
            'all_arm_counts':'>=3 with one common complete coupling idle',
            'twice_support_intercept':p.display(intercept),
            'three_arm_certificate':{k:p.display(v) for k,v in three.items()},
            'four_or_more_maximum_bound':p.display(four['maximum']),
            'finite_corroboration':{'arms':[3,24],'total_range':'arms..96',
                                    'cases':cases,'seed':None,'stop_rule':'exhaust stated pairs'},
            'negative_controls':controls,'new_kappa':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run();path=Path(__file__).with_name('ALL-ARMS-PRICE-RESULT.json')
    if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:p.need(json.loads(path.read_text())==result,'deterministic all-arm receipt')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
