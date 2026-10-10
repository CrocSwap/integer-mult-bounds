#!/usr/bin/env python3
"""Read-only exact arithmetic replay. Full physical supplier checks are separate.
Requires two immutable upstream checkouts; no downloads or source edits.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import lcm
import argparse,hashlib,json,subprocess,sys
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)

def checkout(path,pin):
    path=path.resolve()
    def git(*args):
        p=subprocess.run(['git','-C',str(path),*args],capture_output=True,text=True)
        need(p.returncode==0,'Git failed: '+p.stderr);return p.stdout.strip()
    need(git('rev-parse','HEAD')==pin,'Incorrect pinned checkout: '+str(path))
    need(not git('status','--porcelain','--untracked-files=no'),'Tracked source changes in '+str(path))
    return path

def main():
    need(not sys.flags.optimize,'Assertions must be enabled; do not use -O')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pr161',type=Path,required=True)
    ap.add_argument('--pr163',type=Path,required=True)
    args=ap.parse_args()
    expected=json.loads((HERE/'expected.json').read_text())
    r161=checkout(args.pr161,expected['public161_pin'])
    r163=checkout(args.pr163,expected['public163_pin'])
    sys.path.insert(0,str(r161/'scripts'))
    import paired_cube_network as p
    from audit_community_candidate import moment
    ar=r163/'research/paired-cube-balanced-161/arithmetic'
    sys.path.insert(0,str(ar))
    import certificate as c
    from interval_moment import saving_grid
    n=json.loads((r161/'certificates/paired-cube-network.json').read_text())
    raw=json.loads((r161/'research/paired-cube-bit/out/profile_p12.json').read_text())
    inherited={int(k):int(v) for k,v in raw['child_histogram'].items()}
    original=n['bit']['counts']
    need(inherited=={int(k):int(v) for k,v in original['child_multiplicities'].items()},'Bit sources disagree')
    need((raw['m'],raw['h'],raw['v'],raw['R'],raw['selected_roles'])==(72,24,1760,23368,5720),'Wrong immutable word')
    need(raw['selected_rank_histogram']=={'20':5720},'Wrong selected ranks')
    need(sum(k*v for k,v in inherited.items())==1934000,'Inherited rank mass')
    packed=dict(inherited);need(packed.pop(60)==5720,'Exterior child inventory')
    W=2*1760+3*(Q(5720,18)+Q(17648,3))
    rank=sum(k*v for k,v in packed.items())
    need((W,rank,72*W-rank,max(packed))==(Q(66364,3),1590800,1936,22),'Packed ledger')
    # Actual disjoint coordinate blocks, not nullity divisibility alone.
    need(all(sum(j//4==i for j in range(72))==4 for i in range(18)),'Selected blocks')
    need(all(sum(j//24==i for j in range(72))==24 for i in range(3)),'Undeferred blocks')
    profile=dict(original,W_per_vertex=W,rank_per_vertex=rank,deficit_per_vertex=1936,
                 child_multiplicities={r:Q(v) for r,v in packed.items()},edge_count=sum(packed.values()),maxchild=22)
    coarse=Q(302618322217,500000000000000)
    atom=Q(302446903,500000000000)
    old=Q(384599,10**10)
    effective=(1-atom)*coarse+atom*old
    need(0<effective<atom<1-effective,'Paid atom toll')
    need(p.BAD==Q(1,10**16) and p.OLD==old,'Retained constants changed')
    def bit_ok(a):
        try:
            ideal=p.exact_moment(profile,a)
            fallback=p.BAD*Q(32*72**2*profile['edge_count'],W*72)*p.exp_upper(a*p.log_upper(Q(72)))
            return ideal['moment_upper']+fallback<1 and rank+p.BAD*32*72**2*profile['edge_count']<72*W
        except ValueError:return False
    need(bit_ok(coarse),'Paid bit moment does not contract')
    need(not bit_ok(coarse+Q(1,10**15)),'Adjacent coarse grid control accepted')
    # Independent 80-term log / 12-term exponential enclosure implementation.
    scale=lcm(W.denominator,*(v.denominator for v in profile['child_multiplicities'].values()))
    _,bound=moment(72,int(scale*W),[(r,int(scale*v)) for r,v in profile['child_multiplicities'].items()],coarse)
    _,fallback=moment(72,int(scale*W),[(1,int(scale*32*72**2*profile['edge_count']))],coarse)
    need(bound+p.BAD*fallback<1,'Independent bit moment failed')
    upstream=json.loads((r163/'research/paired-cube-balanced-161/certificate.json').read_text())
    row=upstream['complex']['profile']
    complexprofile=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,
        total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
    complexmoment=saving_grid(complexprofile,10**18)
    need(complexmoment['accepted']['saving']==c.AC,'Complex moment changed')
    c.normalized_body_check()
    result=c.price(row,c.AC,coarse,c.BETA,c.ETA,c.WEAKENING,'balanced',atom)
    need(c.js(result)==expected['combo'],'Exact certificate differs')
    need(result['kappa']==Q(118877394946471,200000000000000000),'Wrong final kappa')
    need(result['a']<effective and len(result['assembly']['constraints'])==47 and len(result['assembly']['margins'])==7,'Supported assembly')
    try:
        c.assembly(result['finite_bridge'],row,result['a'],result['kappa']+Q(1,10**18),beta=c.BETA,h=c.ETA,a_complex=c.AC)
    except (ValueError,AssertionError):pass
    else:raise ValueError('Adjacent final grid control accepted')
    checkout(r161,expected['public161_pin']);checkout(r163,expected['public163_pin'])
    print(json.dumps({'status':'PASS','kappa':str(result['kappa']),
        'decimal':'0.000594386974732355','strict_constraints':47,'margins':7,
        'bit_mass':rank,'bit_volume':str(W),'scope':'Exact conditional finite arithmetic plus ledger and coordinate partitions; full physical realization and all-size inherited contracts are separate.'},indent=2))
if __name__=='__main__':main()
