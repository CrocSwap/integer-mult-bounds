#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One immutable p16 h1804 B=6 five-cell screen, hard wall and atomic checkpoints."""
from argparse import ArgumentParser
from datetime import datetime,timezone
from decimal import Decimal,localcontext
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json,os,signal,subprocess,sys,time

P=16
B=F(6)
DIRECTIONS=[('a',F(3,4),F(5,6)),('b',F(5,6),F(11,12)),
            ('c',F(11,12),F(23,24)),('d',F(23,24),F(1))]
PINS={
 'round321/benchmark/producer/BIT-451.json':'538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749',
 'round336/independent/receipt.json':'69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818',
 'round339/independent/receipt.json':'41a80ef6b08339dd146791d5a22a7472de8a8ab651b35f25a0282a4ee751295e',
 'round341/independent/receipt-with-minimum.json':'42aede07a16e538f97e43341a605e7a432fc0e600504cb1a381e1476abaa30fd',
 'round342/independent/receipt.json':'f91280ef454af5d74559788e7f63fd442d8778937c52575160be2718354defcd',
 'round342/independent/outer-verified.json':'148a6315592977093c90de293ca3a904da5cf8dd2fa7840d3a23538d1a87857b',
 'round344/primary/receipt.json':'0c76967a2ff454986969c82a0683baaabb6622cb2ea91d4864702571af0ccb8c',
 'round344/independent/receipt.json':'1fd90f20d38e5368a98deef7efe4bce880f95b6da8078d4aa37e78921173f1ac',
 'round344/independent/outer-verified.json':'0741754b7644e6d61ab4f36f3471e564aa6ec052a3a4245a2d19402aed1983ad',
 'round342/screen.py':'10cbcc0fe5c7f44c9a2852a13e6acdf87b52471d52b9685c579c05fc63aab2ea',
 'round343/screen.py':'bcb2134b4570246029b35d1eb585f04fdf2318b686910dac1c45fb3ee674554d',
}


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


class Fail(Exception):
    pass


def need(flag,what):
    if not flag:
        raise Fail(what)


def upper_power_2(e):
    if not e:
        return F(1)
    with localcontext() as ctx:
        ctx.prec=80
        a=e*F(Decimal(2).ln().next_plus())
        d=(Decimal(a.numerator)/Decimal(a.denominator)).next_plus()
        return F(d.exp().next_plus())


def compute(root,data,mark):
    inputs=[]
    for path,pin in PINS.items():
        raw=(root/path).read_bytes()
        if path == 'round344/primary/receipt.json':
            # Replay clocks vary. Pin every scientific field of the original
            # power-17 receipt (file SHA-256 94cddffb4dee71ab62572745d801d8c9b2757fa71e1be46ddd64927593683799).
            previous = json.loads(raw)
            del previous['events'], previous['supervisor']
            raw = json.dumps(previous,sort_keys=True,separators=(',',':')).encode()

        if sha256(raw).hexdigest()!=pin: raise ValueError('SHA-256 '+path)
        if path.endswith('.py'):
            env={'__name__':'pinned_arithmetic'}
            exec(compile(raw,path,'exec'),env)
            inputs.append(env)
        else:
            inputs.append(json.loads(raw))
    bit,grid,mom,source,p18,signed18,previous_primary,old,signed,math,end=inputs
    math['P']=P
    lower,up,down=end['power_lower'],math['up'],math['down']
    need(end['log_ends'](1)==(0,0) and old['uniform_J']==668 and old['p']==17 and
         signed['new_component_sha256']==PINS['round344/independent/receipt.json'] and
         F(old['candidate_grid_claim'])==F(signed['signed']['claim'])==F('0.00387992804551') and
         previous_primary['decision']=='ADVANCE_ONE_COMPLETE_REPLAY' and
         signed18['new_component_sha256']==PINS['round342/independent/receipt.json'] and p18['p']==18,'complete predecessor')
    price=math['price'](bit,old)
    data['price']=price
    eta=F(bit['uniform']['eta'][0]);delta=F(bit['separation']['trial'])
    mu=list(map(F,mom['moments'][:P+1]))
    limit=(F(749,1150))**P
    data['leading']={'ratio':str(limit),'capacity':str(B*eta)}
    need(len(mu)==17 and mu[0]==1 and mu[1]==F(749,1000),'moment prefix')
    need(price['passed'] and limit<B*eta,'full price or terminal')
    mark('price; normalized base; true cover; seven stages; old ceiling; terminal')
    def power_up(a,b,e):
        if a==b or e==0: return F(1)
        with localcontext() as ctx:
            ctx.prec=80
            z=e*(end['log_ends'](a)[1]-end['log_ends'](b)[0])
            d=(Decimal(z.numerator)/Decimal(z.denominator)).next_plus()
            return up(F(d.exp().next_plus()))
    t=1-delta
    paid={int(r):n for r,n in bit['native']['paid'].items()}
    targets={int(r):n for r,n in bit['native']['targets'].items()}
    N0=sum(paid.values()); need(N0==107460 and F(7,5)<5<7<11,'cutoff inventory and ordering')
    S5=sum(n*lower(r,1,t) for r,n in paid.items() if r<=5)
    small_fraction=up((N0*power_up(7,5,t)/S5)**451)
    first=lower(16,5,451*delta)
    middle=down(lower(16,7,451*delta)*(1+(1-small_fraction)*(lower(7,5,451*delta)-1)))
    last=F(old['band_gain'])
    data['nonroot']={'raw_labels':N0,'S5_lower':str(S5),'low_share_upper':str(small_fraction),
                     'pointwise_lower':str(first),'middle_lower':str(middle),'old_high_lower':str(last)}
    need(0<=small_fraction<1 and min(first,middle,last)>B,'three fixed nonroot guards')
    b=F(source['source_lower']['root']);lowroot=down(b*lower(16,1,451*delta/4))
    data['low_root_lower']=str(lowroot)
    need(lowroot>B,'low x root guard')
    mark('three nonroot regimes and low root')
    endpoints=bit['separation']['three_engine_intervals']['source_1']
    alpha=F(endpoints['alpha'][0]);w1=F(bit['separation']['target_tilt']);w2=F(17,100)
    need(w1==F(17,50) and 0<alpha,'original source alpha, lambda')
    target_t_lo=sum(n*lower(r,1,t) for r,n in targets.items())
    target_shift_hi=sum(n*power_up(r,1,t-w2) for r,n in targets.items())
    lams=[F(endpoints['lambda'][1]),up(power_up(16,1,w2)*target_shift_hi/target_t_lo)]
    need(all(0<l<alpha for l in lams),'both independently valid decreasing root shares')
    S=up(alpha**(-451));decays=[up((l/alpha)**451) for l in lams]
    need(max(decays)<1,'rounded root factors')
    data['chernoff']={'alpha_lower':str(alpha),'T_t_lower':str(target_t_lo),'T_shifted_upper':str(target_shift_hi),
                       'w':['17/50','17/100'],'lambda_upper':list(map(str,lams)),'decay_upper':list(map(str,decays))}
    cs=list(math['heights'](mu))
    caps={}; estimates={}; data['cells']={}
    for name,l,u in DIRECTIONS:
        floor=min(B,down(b*lower(16,1,451*delta*(1-u))))
        shares=[]
        for w,decay in zip((w1,w2),decays):
            values=[up(S*upper_power_2(4*451*u*w))]
            for _ in range(32): values.append(up(values[-1]*decay))
            shares.append(values)
        estimates[name]=list(zip(*shares))
        caps[name]=[eta*(B-(B-floor)*min(F(1),r1,r2)) for r1,r2 in estimates[name]]
        data['cells'][name]={'l':str(l),'u':str(u),'root_lower':str(floor),
                             'shares_u0':list(map(str,estimates[name][0])),
                             'shares_u32':list(map(str,estimates[name][32])),'tail_capacity':str(caps[name][-1])}
    data['explicit']={name:{} for name,_,_ in DIRECTIONS};data['newton']={}
    def point(name,l,g):
        saved=data['explicit'][name]
        if str(g) in saved: return
        ratio=cs[g]/(F(319,100)+F(23,20)*(g+l))**P
        capacity=caps[name][g]
        saved[str(g)]={'ratio':str(ratio),'capacity':str(capacity),'root_share_uppers':list(map(str,estimates[name][g])),'passes':ratio<capacity}
        if ratio>=capacity: raise Fail(f'{name} explicit G={g}')
    def coeff(name,offset,l,capacity):
        rs=math['newton'](cs,offset,l)
        need(rs[-1]==limit,'fixed leading coefficient')
        rows=data['newton'][name]={}
        for j,r in enumerate(rs):
            rows[str(j)]={'ratio':str(r),'capacity':str(capacity),'passes':r<capacity}
            if r>=capacity: raise Fail(f'{name} Newton j={j}')
    for name,l,u in [DIRECTIONS[-1],*DIRECTIONS[:-1]]: point(name,l,16)
    for name,l,u in DIRECTIONS:
        for g in (0,31): point(name,l,g)
    mark('12 cached endpoint and G16 decisions')
    coeff('low',0,0,B*eta)
    mark('17 low-x coefficients')
    for name,l,u in DIRECTIONS:
        for g in range(32): point(name,l,g)
        mark(name+' all 32 explicit heights')
        coeff(name,32,l,caps[name][-1])
        mark(name+' all 17 tail coefficients')
    need(sum(map(len,data['explicit'].values()))==128 and sum(map(len,data['newton'].values()))==85,'coverage')


def worker(root,path):
    begin=time.monotonic()
    data={'case':{'p':16,'h':1804,'q':'749/1000','B':'6','x_cuts':['3/4','5/6','11/12','23/24'],'G_cut':32},
          'pins':PINS,'decision':'RUNNING','events':[]}
    def mark(label):
        data['events'].append({'utc':utc(),'elapsed':time.monotonic()-begin,'stage':label})
        tmp=path.with_suffix('.writing')
        tmp.write_text(json.dumps(data)+'\n');tmp.replace(path)
    mark('single discovery start')
    try:
        compute(root,data,mark)
        data['decision']='ADVANCE_ONE_COMPLETE_REPLAY'
    except Fail as e:
        data.update(decision='RETIRE_FROZEN_CERTIFICATE',reason=str(e))
    except Exception as e:
        data.update(decision='INPUT_OR_ARITHMETIC_ERROR',reason=repr(e))
    mark('discovery close')
    print(data['decision'],data.get('reason',''))


def main():
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--campaign-root',required=True,type=Path)
    cli.add_argument('--out',required=True,type=Path)
    cli.add_argument('--child',action='store_true')
    a=cli.parse_args()
    if a.child:
        worker(a.campaign_root,a.out)
        return
    if a.out.exists():
        raise SystemExit('Choose a fresh path; this receipt is sealed.')
    with TemporaryDirectory() as scratch:
        snapshot=Path(scratch)/'progress.json'
        begin=time.monotonic();started=utc()
        proc=subprocess.Popen([sys.executable,'-IB',str(Path(__file__).resolve()),'--campaign-root',str(a.campaign_root),
                               '--out',str(snapshot),'--child'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              text=True,start_new_session=True)
        killed=False
        try:
            stdout,_=proc.communicate(timeout=max(0,45-(time.monotonic()-begin)))
        except subprocess.TimeoutExpired:
            killed=True
            try: os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            stdout,_=proc.communicate()
        wall=time.monotonic()-begin;verify=utc()
        d=json.loads(snapshot.read_bytes()) if snapshot.is_file() else {'events':[]}
        if killed or wall>45: d['decision']='CAPPED_UNRESOLVED'
        elif proc.returncode!=0 or d.get('decision')=='RUNNING': d['decision']='CHILD_ERROR_UNRESOLVED'
        n=sum(map(len,d.get('newton',{}).values()));e=sum(map(len,d.get('explicit',{}).values()))
        d['coverage']={'direct_checked':e,'direct_unvisited':128-e,'coefficients_checked':n,'coefficients_unvisited':85-n}
        if d.get('decision')=='ADVANCE_ONE_COMPLETE_REPLAY' and (n,e)!=(85,128):
            d['decision']='INCOMPLETE_COVERAGE'
        d['supervisor']={'started_utc':started,'reserve_started_utc':verify,'deadline_seconds':45,'reserve_seconds':15,
                         'child_wall':wall,'killed':killed,'exit':proc.returncode,'child_output':stdout[-2048:]}
        d['supervisor'].update(receipt_utc=utc(),total_wall=time.monotonic()-begin)
        if d['supervisor']['total_wall']>60: d['decision']='CAPPED_UNRESOLVED'
        a.out.write_text(json.dumps(d,indent=2)+'\n')
        print(d['decision'],d.get('reason',''),d['coverage'],round(wall,4))


if __name__=='__main__':
    main()
