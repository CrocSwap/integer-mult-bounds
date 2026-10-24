"""Bounded exact-invoice screen of the public helper621 two-chart patch."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import gzip,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/warp-interface-20261022'))
from warp_merge import F,synthesize


def main():
    d=json.loads(gzip.decompress((HERE/'ACTUAL-WORD.json.gz').read_bytes()));c=d['canonical'];a=140
    F.need(set(c['frames'][a])=={30,429},'Pinned two-chart source basis')
    c['start'][621]=a;programs={}
    for direction,p in d['programs'].items():
        raw=[deepcopy(e) for e in p if e[0]!='climb']
        i=next(i for i,e in enumerate(raw) if e[0]=='scalar' and any(r==['L',621] for r in e[1][1:3]))
        F.need(raw[i][2]==115,'Frozen new first helper621 contact')
        raw[i][2]=a;programs[direction]=synthesize(c,raw)
    P=Counter(e[5] for e in programs['forward'] if e[0]=='climb');P.update(e[4] for e in programs['forward'] if e[0]=='center')
    H=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]) for r in range(224,632))
    t=1-.00302177585;oldP={1:2201,2:412,3:510,4:127,5:40,8:8};oldH={4:28,7:7,8:47,9:326}
    gain=sum(v*k**t for k,v in oldP.items())-sum(v*k**t for k,v in P.items())+sum(v*k**t for k,v in H.items())-sum(v*k**t for k,v in oldH.items())
    result={'status':'DISCOVERY_NEGATIVE_INVOICE_SCREEN','source_proposal':'Pierre-Loic Doulcet PR4626 c665f908fc991aa558ea8a8cd33e9ad26f97a22d',
            'scope':'Only replace helper621 entrance and first scalar contact by span{30,429} in the frozen joint-map witness; not a universal obstruction.',
            'paid':dict(P),'helpers':dict(H),'tested_saving_float':1-t,'moment_improvement_float':gain,'native_replay_run':False}
    (HERE/'COMBINE621-SCREEN.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
