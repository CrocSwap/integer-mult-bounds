"""Author the exact constructive patch from the frozen candidate word."""
from copy import deepcopy
import gzip,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from warp_merge import J,F


def main():
    payload=json.loads(gzip.decompress((HERE/'ACTUAL-WORD.json.gz').read_bytes()));c=payload['canonical'];base,programs,*_=J.construct()
    old=[e for e in programs['forward'] if e[0]!='climb'];new=[e for e in payload['programs']['forward'] if e[0]!='climb']
    F.need(len(old)==len(new),'No hidden opcode deletion/addition')
    scalar=[];warps=[]
    for i,(a,b) in enumerate(zip(old,new)):
        F.need(a[0]==b[0],'Same chronological opcode')
        if a[0]=='scalar':
            F.need(a[1]==b[1],'Same scalar operator')
            if a[2]!=b[2]:scalar.append([i,a[2],b[2]])
        elif a[0]=='warp':
            F.need(a[:3]==b[:3],'Same logical warp/register')
            if a[3:]!=b[3:]:warps.append([i,a[2],a[3],a[4],b[3],b[4]])
        else:F.need(a==b,'Same fixed center/marker/adapter')
    patch={'schema':'changed-native-G-scalar-graph/1','base_commit':'f626db5c3a3d781d8f7695038776c621651f75e1',
           'base_frame_count':len(base['frames']),'additional_frames':c['frames'][len(base['frames']):],
           'scalar_frame_changes':scalar,'warp_frame_changes':warps,'actual_operator_bindings':c['warps'],
           'discovery_word_sha256':payload['discovery_word_sha256'],'scope':payload['scope']}
    (HERE/'PATCH.json').write_text(json.dumps(patch,indent=2,sort_keys=True)+'\n')
    print('EXACT_CONSTRUCTIVE_PATCH',len(scalar),'scalar contacts',len(warps),'warp frame pairs')


if __name__=='__main__':main()
