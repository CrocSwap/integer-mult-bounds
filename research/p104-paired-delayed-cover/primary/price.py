#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One 768-factor delayed-cover loss, fixed peer word, carrier and prefix."""
from argparse import ArgumentParser
from datetime import datetime,timezone
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import gzip,io,json,os,signal,subprocess,sys,tarfile,time

PKG={
 'APPLICATION.json':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f',
 'APPLICATION-SOURCES.tar.gz':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968',
 'BINARY-CANDIDATE.json.gz':'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326',
 'verify_application.py':'f774304804e705ac576459cca725b348f09e67e6020fe6165df9b7d39c605c54',
 'SOURCES.json':'4dd42ee240925ae1bc1ffa3b885b33eb66ab4d323695d106c00ce7519dffd9bb',
}
ARCH={
 'recipient/binary/finite.py':'c780cea060f4a9efef064b239636162a7e8e84e40369abc1a1c4679dfbeb3041',
 'parent/binary/independent/price.py':'d720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b',
 'parent/qualify_complex.py':'236988674f4efe96134de83a224f9c5f4508f6049237415bc24a18669cf5ad67',
 'recipient/continuation/qualify.py':'fdf559fbe15f52c2b31f2947712a46aa6b4c93f211ea9a0b1f05b07d69664227',
 'source/certificates/frontier7000/CLAIM.json':'3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2',
 'source/research/paired-query-only-bit/EFREE-CALLER.json.gz':'757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b',
 'source/research/paired-query-only-bit/retained/inputs/credited_trim.py':'fcff17fdd3108be68761fbde0fcbfe218be166cf518c99f7163e60d53ab785d9',
}
BRIDGE='9731b93026717f5fa15851e3633cbb4bdc76eba2bffb9d6b4a3b69f7dd502443'
HEAD='fb9b6a7b0d27da1cf98430893a3016bf811e2aa4'


def utc(): return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


def require(flag,msg):
    if not flag: raise ValueError(msg)


def dec(x,n):
    unit=10**n;u=x*unit;require(u.denominator==1,'decimal grid')
    return f'{u.numerator//unit}.{u.numerator%unit:0{n}d}'


def stages(covered,seed):
    rho=F(1,250);v=seed;out=[]
    for _ in range(4):
        bound=(1-rho)*covered+rho*v
        nxt=F((bound*10**15).__floor__()-1,10**15)
        require(v<nxt<bound<rho<1-bound,'all stage terms and interior rounding')
        out.append({'previous':str(v),'endpoint':str(bound),'admitted':dec(nxt,15),
                    'charged_minimum_slack':str(min(rho-nxt,bound-nxt,1-rho-nxt))})
        v=nxt
    return v,out


def grid(bit,rational_low):
    scale=10**14
    k=min((rational_low*scale).__floor__(),(bit*scale).__floor__())-8
    claim,test=F(k,scale),F(k+7,scale)
    require(0<claim<test<bit and test<rational_low,'old signed grid')
    return claim,test


def science(args,data,mark):
    checked={}
    for name,pin in PKG.items():
        raw=(args.peer_package/name).read_bytes()
        require(sha256(raw).hexdigest()==pin,name)
        checked[name]=raw
    require(sha256(args.bridge.read_bytes()).hexdigest()==BRIDGE,'whole-cover theorem')
    app=json.loads(checked['APPLICATION.json'])
    word=json.loads(gzip.decompress(checked['BINARY-CANDIDATE.json.gz']))
    canonical=sha256(json.dumps(word,separators=(',',':'),sort_keys=True).encode()).hexdigest()
    require(canonical==app['binary_word'] and word['public']==630 and app['binary_native']['calls']==36
            and app['rational_calls']==48 and app['source_count']==134,'real peer circuits')
    with tarfile.open(fileobj=io.BytesIO(checked['APPLICATION-SOURCES.tar.gz']),mode='r:gz') as t:
        names=t.getnames()
        require(len(set(names))==len(names)==134,'source names')
        for key,pin in ARCH.items():
            raw=t.extractfile(key).read()
            require(sha256(raw).hexdigest()==pin,key)
            if key.endswith('/CLAIM.json'): seed=F(json.loads(raw)['admitted_BIT_saving'])
    require(seed==F('0.00385248'),'original paid seed')
    H=app['binary_H'];require(H==299610000000000,'same carrier')
    low,high=map(F,app['binary_raw']);rational_low=F(app['rational_raw'][0])
    trial=low-F(1,10**11);uniform=F(1,10**10)
    require(0<low<high<rational_low and H*uniform==29961,'directed endpoints and existing uniform charge')
    old_cap,old_stages=stages(trial-2*uniform,seed)
    old,old_test=grid(old_cap,rational_low)
    require(old_cap==F(app['binary_ordinary']) and old==F(app['claim'])==F('0.00389011507650'),'baseline price replay')
    data['comparator']={'head':HEAD,'word':canonical,'trial':str(trial),'uniform_loss':str(uniform),
                        'H':H,'seed':str(seed),'old_cover_loss':str(uniform),'stages':old_stages,
                        'cap':dec(old_cap,15),'claim':dec(old,14),'tested':dec(old_test,14)}
    mark('authenticated literal 768 supplier, both callers and source; exact old cap and grid')
    loss=F(1,H*2**38)
    surcharge=F(64,2**45)
    relaxation=H*loss*F(1,2)
    require(0<loss<uniform and surcharge==F(1,2**39)==relaxation,'directed cover guard')
    # 1+actual surcharge < 1+surcharge; 2^(H*d)>1+(H*d)/2.
    covered=trial-uniform-loss
    cap,invoice=stages(covered,seed)
    claim,tested=grid(cap,rational_low)
    tick=F(1,10**14)
    old_ceiling=high-2*uniform-7*tick
    require(0<old<old_ceiling<claim<tested<cap<covered<low<rational_low,'strict old complete ceiling')
    data['candidate']={'case':'same-prime-2^-38','cover_loss':str(loss),'uniform_loss':str(uniform),
                       'surcharge_strict_upper':str(surcharge),'N_to_d_strictly_above':str(1+relaxation),
                       'covered':str(covered),'stages':invoice,'cap':dec(cap,15),'tested':dec(tested,14),
                       'claim':dec(claim,14),'old_ceiling':str(old_ceiling),'separation':str(claim-old_ceiling),
                       'absolute_gain':str(claim-old),'relative_percent':str(100*(claim-old)/old)}
    mark('whole-cover contraction, four stages, ordinary and candidate signed-grid price')
    data['decision']='ADVANCE_ONE_COMPLETE_SIGNED_REPLAY'


def worker(args):
    out={'decision':'RUNNING','pins':{'peer':PKG,'peer_archive':ARCH,'bridge':BRIDGE},'events':[]}
    begin=time.monotonic()
    def mark(s):
        out['events'].append({'utc':utc(),'elapsed':time.monotonic()-begin,'stage':s})
        tmp=args.out.with_suffix('.partial');tmp.write_text(json.dumps(out)+'\n');tmp.replace(args.out)
    mark('one case started')
    try: science(args,out,mark)
    except Exception as e: out.update(decision='UNRESOLVED_OR_REJECTED',error=repr(e))
    mark('one case closed')


def main():
    cli=ArgumentParser(description=__doc__)
    for k in ('peer-package','bridge','out'): cli.add_argument('--'+k,type=Path,required=True)
    cli.add_argument('--child',action='store_true');a=cli.parse_args()
    if a.child:
        worker(a);return
    require(not a.out.exists(),'use a fresh output destination')
    with TemporaryDirectory() as tmp:
        snapshot=Path(tmp)/'work.json'
        begin=time.monotonic();start=utc()
        cp=subprocess.Popen([sys.executable,'-IB',str(Path(__file__).resolve()),'--peer-package',str(a.peer_package),
                             '--bridge',str(a.bridge),'--out',str(snapshot),'--child'],start_new_session=True,
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        killed=False
        try: stdout,_=cp.communicate(timeout=max(0,30-(time.monotonic()-begin)))
        except subprocess.TimeoutExpired:
            killed=True
            try: os.killpg(cp.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            stdout,_=cp.communicate()
        wall=time.monotonic()-begin
        d=json.loads(snapshot.read_bytes()) if snapshot.exists() else {'events':[]}
        if killed or wall>30: d['decision']='CAPPED_UNRESOLVED'
        elif cp.returncode!=0 or d.get('decision')=='RUNNING': d['decision']='CHILD_ERROR'
        d['supervisor']={'launch':start,'verification':utc(),'child_exit':cp.returncode,'killed':killed,
                         'child_wall':wall,'discovery_cap':30,'reserve_seconds':10,'output':stdout[-500:]}
        if 'candidate' in d: require(F(d['candidate']['claim'])-F(d['comparator']['claim'])==F(d['candidate']['absolute_gain']),'receipt comparison')
        d['supervisor'].update(sealed=utc(),total_wall=time.monotonic()-begin)
        if d['supervisor']['total_wall']>40: d['decision']='CAPPED_UNRESOLVED'
        a.out.write_text(json.dumps(d,indent=2)+'\n')
        print(d['decision'],d.get('error',''),d.get('candidate',{}).get('cap',''))


if __name__=='__main__':
    main()
