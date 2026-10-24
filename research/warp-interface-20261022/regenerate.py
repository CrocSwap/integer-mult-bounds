"""Rebuild the frozen actual word from source plus PATCH, without a solver."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import argparse,gzip,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from warp_merge import J,F,synthesize


def main(output=None):
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:F.need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Pinned source '+row['path'])
    patch=json.loads((HERE/'PATCH.json').read_text());base,old,*_=J.construct()
    F.need(len(base['frames'])==patch['base_frame_count'],'Exact source frame prefix')
    c=deepcopy(base);c['frames']+=patch['additional_frames'];programs={}
    for d,p in old.items():
        raw=[deepcopy(e) for e in p if e[0]!='climb']
        for i,a,b in patch['scalar_frame_changes']:
            F.need(raw[i][0]=='scalar' and raw[i][2]==a,'Guarded scalar contact edit');raw[i][2]=b
        for i,op,a,b,x,y in patch['warp_frame_changes']:
            F.need(raw[i][0]=='warp' and raw[i][2:]==[op,a,b],'Guarded warp frame edit');raw[i][3:5]=[x,y]
        programs[d]=synthesize(c,raw)
    bindings={w['op']:w for w in patch['actual_operator_bindings']}
    for w in c['warps']:
        b=bindings[w['op']]
        F.need({k:v for k,v in w.items() if k not in ('G_columns','from_frame','to_frame')}=={k:v for k,v in b.items() if k not in ('G_columns','from_frame','to_frame')},'Same logical native operator and occurrence')
    c['warps']=patch['actual_operator_bindings']
    canonical={k:c[k] for k in ['frames','start','final','ports','h','v','warps']}
    prof=Counter(e[5] for e in programs['forward'] if e[0]=='climb');prof.update(e[4] for e in programs['forward'] if e[0]=='center');canonical['local_profile']=dict(prof)
    canonical['warp_edges']=sorted({(1 if e[2]>0 else -1,abs(e[2]),e[3],e[4]) for e in programs['forward'] if e[0]=='warp'})
    payload={'canonical':canonical,'programs':programs,'discovery_word_sha256':patch['discovery_word_sha256'],'scope':patch['scope']}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode();expected=json.loads((HERE/'ACTUAL-WORD-FREEZE.json').read_text())
    F.need(sha256(raw).hexdigest()==expected['canonical_payload_sha256'],'Every regenerated proof-relevant byte equals frozen canonical payload')
    if output:Path(output).write_bytes(gzip.compress(raw,mtime=0))
    print('PASS_SOLVER_FREE_EXACT_REGENERATION',sha256(raw).hexdigest())


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output');args=ap.parse_args();main(args.output)
