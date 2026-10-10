"""Source-bound PR211/V7 fallback candidate overlay; original V5 files remain immutable.

Reconstruct the complete changed graph, physical word and rational frames from
the pinned PR200 files, PR211's 6,191-frame witness and frozen440 butterflies.
No search is performed here. All graph and physical changes are explicit.
"""
from pathlib import Path
from collections import defaultdict
import base64,copy,gzip,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
assert __debug__
HERE=Path(__file__).resolve().parent
P=None
FRAME_FILE=HERE/'opframe-bases.json.gz.b64'
OVERLAY_FILE=HERE/'butterfly-overlay.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(obj):return (json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def candidate(bit_root):
    global P
    from common import check_source
    bit_root=Path(bit_root).resolve();check_source(bit_root,'bit')
    P=bit_root/'research/paired-cube-diagonal-bit-168'
    def pin_name(p):
        return ('source/'+p.relative_to(bit_root).as_posix()) if p.is_relative_to(bit_root) else ('package/'+p.name)
    assert sha(OVERLAY_FILE.read_bytes())=='ca66a9c3d8f3a29dc805dc89306f0b23b8e934cbbbf3a9334e7391fbbc1086ee','frozen butterfly overlay'
    overlay=json.loads(OVERLAY_FILE.read_bytes())
    assert overlay['source_head']=='cd14825023b75af4f5919a30e5e6d548b6ade5bc'
    source_raw=gzip.decompress(base64.b64decode(FRAME_FILE.read_bytes()))
    assert len(source_raw)==4977602
    assert sha(source_raw)=='56b2ed0f6b867e8cafdc32ac70419cfda36d02838844572098b3fc77f8026e58'
    assert hashlib.sha1(b'blob '+str(len(source_raw)).encode()+b'\0'+source_raw).hexdigest()=='8433d7724cbed83401fa42beee8653c62657ec0d'
    module=load('pr207_scheduling_source_word',P/'bit/word.py')
    word=module.Candidate()
    source_word=copy.deepcopy(word.w)
    original_graph=copy.deepcopy(word.g)
    # Register the source-pinned leader refinements before butterfly changes.
    leader=json.loads(source_raw);assert len(leader)==len({i for i,B in leader})==6191
    for i,B in leader:word.opframe[i]=word.register(B)
    used=set();changed_nodes=set();changed_operations=set()
    for plan in overlay['plans']:
        i,j,k=plan['operations'];a,b,c,d=plan['roles']
        assert not used.intersection(plan['roles']);used.update(plan['roles'])
        assert word.ops[i][:2]==[a,d] and word.ops[j][:2]==[b,c]
        assert word.ops[k][:2]==[a,b]
        word.ops[i][1]=c;word.ops[j][1]=d;changed_operations.update((i,j))
        for op,n,args,B in zip((i,j),plan['pair_nodes'],plan['new_pair_source_args'],plan['new_pair_frames']):
            assert word.ops[op][2]==n and len(args)==2 and all(s<word.v for s in args)
            word.g['args'][n]=args
            f=word.register(B);word.opframe[op]=f
            word.w['node_frame'][str(n)]=f
            assert word.C.nondeg(f),'new abstract pair frame nondegenerate'
            changed_nodes.add(n)
    assert len(overlay['plans'])==440 and len(changed_operations)==len(changed_nodes)==880
    assert len(changed_operations & {i for i,B in leader})==3,'Exactly three PR211 pair frames are superseded by proved butterfly pair frames'
    word.w['op_frame']=word.opframe[:]
    word.nf={int(n):f for n,f in word.w['node_frame'].items()}
    word.changed_frames=[i for i,(x,y) in enumerate(zip(word.original_opframe,word.opframe)) if x!=y]
    word.role_ops=defaultdict(list)
    for i in word.phase1+word.rest:
        for s in word.ops[i][:2]:word.role_ops[s].append(i)
    assert all(xs==sorted(xs) for xs in word.role_ops.values())
    pos={i:p for p,i in enumerate(word.rest)}
    word.first={s:pos.get(xs[0],-1) for s,xs in word.role_ops.items()}
    word.last={s:pos.get(xs[-1],-1) for s,xs in word.role_ops.items()}
    word.endframe={s:word.opframe[xs[-1]] for s,xs in word.role_ops.items()}
    for recipient,donor in word.pairs:assert word.last[donor]<word.readtime[recipient]
    for key in ('gauges','pairs','rootroles','root_frame','source_frame','sources','reads','phase1'):
        assert word.w[key]==source_word[key],('preserved word interface',key)
    assert word.g['roots']==original_graph['roots']
    assert len(word.ops)==len(source_word['ops'])==41288
    # Exact emitted artifacts, represented in canonical bytes. The complete
    # serialized program is reconstructible solely from frozen files above.
    frames=copy.deepcopy(word.C.fr)
    for f,B in word.C.B.items():
        if str(f) not in frames['frames']:
            frames['frames'][str(f)]={'b':[list(r) for r in B],'dim':len(B)}
    emitted={'graph_p12.json':canonical(word.g),'word_p12.json':canonical(word.w),'frames_p12.json':canonical(frames)}
    pin_paths=[FRAME_FILE,OVERLAY_FILE,P/'bit/word.py',P/'bit/base_word.py',P/'bit/terminal.py',P/'bit/prime_witnesses.py',Path(word.module.__file__)]
    meta=dict(source_head='c63e50a5dde96fe1459d6b29e55e47f42f104347',butterfly_origin_head=overlay['source_head'],overridden_pair_operation_intersections=sorted(changed_operations & {i for i,B in leader}),base_head=overlay['base_head'],leader_frame_changes=6191,butterflies=440,changed_graph_nodes=880,changed_gate_controls=880,source_pins={pin_name(p):sha(p.read_bytes()) for p in pin_paths},emitted_sha256={name:sha(b) for name,b in emitted.items()},emitted_bytes={name:len(b) for name,b in emitted.items()},full_serialization_canonical=True,physical_operation_count=len(word.ops),immutable_overlay_sha256=sha(OVERLAY_FILE.read_bytes()))
    return word,emitted,meta
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--bit-root',type=Path,required=True);args=parser.parse_args()
    word,emitted,meta=candidate(args.bit_root)
    word.exact_frames();row=word.row()
    print(json.dumps(dict(status='PASS_COMBINED_CANDIDATE_GEOMETRY_LEDGER',metadata=meta,row=row),sort_keys=True))
