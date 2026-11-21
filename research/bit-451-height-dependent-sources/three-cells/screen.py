#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One immutable p17 h1804 B=4 three-cell screen, hard wall and atomic checkpoints."""
from argparse import ArgumentParser
from datetime import datetime,timezone
from decimal import Decimal,localcontext
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json,os,signal,subprocess,sys,time

P=17
B=F(4)
DIRECTIONS=[('middle',F(5,6),F(11,12)),('upper',F(11,12),F(1))]
PINS={
 'round321/benchmark/producer/BIT-451.json':'538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749',
 'round336/independent/receipt.json':'69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818',
 'round339/independent/receipt.json':'41a80ef6b08339dd146791d5a22a7472de8a8ab651b35f25a0282a4ee751295e',
 'round341/independent/receipt-with-minimum.json':'42aede07a16e538f97e43341a605e7a432fc0e600504cb1a381e1476abaa30fd',
 'round342/independent/receipt.json':'f91280ef454af5d74559788e7f63fd442d8778937c52575160be2718354defcd',
 'round342/independent/outer-verified.json':'148a6315592977093c90de293ca3a904da5cf8dd2fa7840d3a23538d1a87857b',
 'round343/primary.json':'846c6441860cf5e91cf958a7f4a77e7bdf5befa8c519b82a157142f34535c4e9',
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
        if sha256(raw).hexdigest()!=pin: raise ValueError('SHA-256 '+path)
        if path.endswith('.py'):
            env={'__name__':'pinned_arithmetic'}
            exec(compile(raw,path,'exec'),env)
            inputs.append(env)
        else:
            inputs.append(json.loads(raw))
    bit,grid,mom,source,old,signed,control,math,end=inputs
    math['P']=P
    lower,up,down=end['power_lower'],math['up'],math['down']
    need(end['log_ends'](1)==(0,0) and old['uniform_J']==708 and old['p']==18 and
         signed['new_component_sha256']==PINS['round342/independent/receipt.json'] and
         F(old['candidate_grid_claim'])==F(signed['signed']['claim'])==F('0.00387992804547') and
         control['decision']=='PRIMARY_AND_INDEPENDENT_SIGNED_REPLAY_MATCH','complete predecessor')
    price=math['price'](bit,old)
    data['price']=price
    eta=F(bit['uniform']['eta'][0]);delta=F(bit['separation']['trial'])
    mu=list(map(F,mom['moments'][:P+1]))
    limit=(F(749,1150))**P
    data['leading']={'ratio':str(limit),'capacity':str(B*eta)}
    need(len(mu)==18 and mu[0]==1 and mu[1]==F(749,1000),'moment prefix')
    need(price['passed'] and limit<B*eta,'full price or terminal')
    mark('price; normalized base; true cover; seven stages; old ceiling; terminal')
    d=min(F(grid['mean_lower'])-F(3,5),F(4,5)-F(grid['mean_upper']))
    need(d>0 and 11**3>=4**5 and 11**4<=7**5,'unchanged band geometry')
    f=(1-F(grid['tensor_variance_upper'])/d**2)/(1+F(mom['epsilon_upper']))
    small=lower(16,7,451*delta);admit=down(1+f*(lower(4,1,451*delta)-1))
    data['nonroot']={'distance':str(d),'complete_fraction_lower':str(f),'partial_lower':str(small),'band_lower':str(admit)}
    need(f>0 and small>B and admit>B,'nonroot lower multiplier')
    b=F(source['source_lower']['root']);lowroot=down(b*lower(16,1,451*delta/6))
    data['low_root_lower']=str(lowroot)
    need(lowroot>B,'low x root guard')
    mark('both nonroot groups and low-x root')
    endpoint=bit['separation']['three_engine_intervals']['source_1']
    alpha,lam=F(endpoint['alpha'][0]),F(endpoint['lambda'][1])
    w=F(bit['separation']['target_tilt'])
    need(w==F(17,50) and 0<lam<alpha,'raw Chernoff normalization')
    S=up(alpha**(-451));decay=up((lam/alpha)**451)
    need(0<decay<1,'geometric tail')
    cs=list(math['heights'](mu))
    caps={};data['cells']={};data['decay_upper']=str(decay)
    for name,l,u in DIRECTIONS:
        floor=min(B,down(b*lower(16,1,451*delta*(1-u))))
        pref=up(S*upper_power_2(4*451*u*w))
        shares=[pref]
        for _ in range(32): shares.append(up(shares[-1]*decay))
        caps[name]=[eta*(B-(B-floor)*min(F(1),x)) for x in shares]
        data['cells'][name]={'l':str(l),'u':str(u),'root_lower':str(floor),'share_u0':str(pref),
                             'share_u32':str(shares[-1]),'tail_capacity':str(caps[name][-1])}
    data['explicit']={name:{} for name,_,_ in DIRECTIONS};data['newton']={}
    def point(name,l,g):
        saved=data['explicit'][name]
        if str(g) in saved: return
        ratio=cs[g]/(F(319,100)+F(23,20)*(g+l))**P
        capacity=caps[name][g]
        saved[str(g)]={'ratio':str(ratio),'capacity':str(capacity),'passes':ratio<capacity}
        if ratio>=capacity: raise Fail(f'{name} explicit G={g}')
    def coeff(name,offset,l,capacity):
        rs=math['newton'](cs,offset,l)
        need(rs[-1]==limit,'fixed leading coefficient')
        rows=data['newton'][name]={}
        for j,r in enumerate(rs):
            rows[str(j)]={'ratio':str(r),'capacity':str(capacity),'passes':r<capacity}
            if r>=capacity: raise Fail(f'{name} Newton j={j}')
    for name,l,u in DIRECTIONS:
        for g in (0,31): point(name,l,g)
    mark('four cached endpoint heights')
    coeff('low',0,0,B*eta)
    mark('18 low-x coefficients')
    for name,l,u in DIRECTIONS:
        for g in range(32): point(name,l,g)
        mark(name+' all 32 explicit heights')
        coeff(name,32,l,caps[name][-1])
        mark(name+' all 18 tail coefficients')
    need(sum(map(len,data['explicit'].values()))==64 and sum(map(len,data['newton'].values()))==54,'coverage')


def worker(root,path):
    begin=time.monotonic()
    data={'case':{'p':17,'h':1804,'q':'749/1000','B':'4','x_cuts':['5/6','11/12'],'G_cut':32},
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
        d['coverage']={'direct_checked':e,'direct_unvisited':64-e,'coefficients_checked':n,'coefficients_unvisited':54-n}
        if d.get('decision')=='ADVANCE_ONE_COMPLETE_REPLAY' and (n,e)!=(54,64):
            d['decision']='INCOMPLETE_COVERAGE'
        d['supervisor']={'started_utc':started,'reserve_started_utc':verify,'deadline_seconds':45,'reserve_seconds':15,
                         'child_wall':wall,'killed':killed,'exit':proc.returncode,'child_output':stdout[-2048:]}
        d['supervisor'].update(receipt_utc=utc(),total_wall=time.monotonic()-begin)
        if d['supervisor']['total_wall']>60: d['decision']='CAPPED_UNRESOLVED'
        a.out.write_text(json.dumps(d,indent=2)+'\n')
        print(d['decision'],d.get('reason',''),d['coverage'],round(wall,4))


if __name__=='__main__':
    main()
