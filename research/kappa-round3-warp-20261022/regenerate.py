"""Rebuild the exact frozen word from predecessor plus guarded patch, no solver."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/warp-interface-20261022'))
from warp_merge import F,synthesize


def main(output=None):
    patch=json.loads((HERE/'PATCH.json').read_text(encoding='utf-8'))
    raw=(ROOT/patch['base_path']).read_bytes();F.need(sha256(raw).hexdigest()==patch['base_sha256'],'Frozen complete predecessor source')
    old=json.loads(gzip.decompress(raw));c=deepcopy(old['canonical']);programs={}
    F.need(len(c['frames'])==patch['base_frame_count'],'Complete inherited frame prefix')
    c['frames']+=patch['additional_frames']
    for field,changes in patch['boundary_changes'].items():
        for r,a,b in changes:F.need(c[field][r]==a and 224<=r<632,'Guarded strictly helper boundary edit');c[field][r]=b
    for d,word in old['programs'].items():
        p=[deepcopy(e) for e in word if e[0]!='climb']
        for i,a,b in patch['scalar_frame_changes']:
            F.need(p[i][0]=='scalar' and p[i][2]==a,'Guarded scalar contact edit');p[i][2]=b
        for i,op,a,b,x,y in patch['warp_frame_changes']:
            F.need(p[i][0]=='warp' and p[i][2:]==[op,a,b],'Guarded warp contact edit');p[i][3:5]=[x,y]
        programs[d]=synthesize(c,p)
    c['warps']=patch['actual_operator_bindings']
    c['local_profile']=dict(Counter(e[5] for e in programs['forward'] if e[0]=='climb')+Counter(e[4] for e in programs['forward'] if e[0]=='center'))
    c['warp_edges']=sorted({(1 if e[2]>0 else -1,abs(e[2]),e[3],e[4]) for e in programs['forward'] if e[0]=='warp'})
    result={'canonical':c,'programs':programs,'discovery_word_sha256':patch['discovery_word_sha256'],'scope':patch['scope']}
    payload=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    frozen=json.loads((HERE/'ACTUAL-WORD-FREEZE.json').read_text(encoding='utf-8'))
    F.need(sha256(payload).hexdigest()==frozen['canonical_payload_sha256'],'Every complete canonical byte equals the frozen witness')
    if output:Path(output).write_bytes(gzip.compress(payload,mtime=0))
    print('PASS_SOLVER_FREE_REGENERATION',sha256(payload).hexdigest())
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output');args=ap.parse_args();main(args.output)
