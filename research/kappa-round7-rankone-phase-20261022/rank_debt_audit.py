"""Independent actual-path audit and exact pinned PR4696 verifier replay."""
from pathlib import Path
from hashlib import sha1,sha256
from collections import Counter
import gzip,json,subprocess,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
import full_form_gate as F

def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def need(ok,message):
    if not ok:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def pivots(columns):
    out={}
    for x in columns:
        while x:
            p=x.bit_length()-1
            if p not in out:out[p]=x;break
            x^=out[p]
    return out
def contains(basis,x):
    while x:
        p=x.bit_length()-1
        if p not in basis:return False
        x^=basis[p]
    return True
def apply(columns,x):
    out=0
    while x:
        bit=x&-x;out^=columns[bit.bit_length()-1];x^=bit
    return out
def inverse(columns):
    # Independent Gauss-Jordan inverse, rather than the upstream 512-value map.
    rows=[sum(((columns[j]>>i)&1)<<j for j in range(9))|(1<<(9+i)) for i in range(9)]
    for i in range(9):
        hit=next((j for j in range(i,9) if rows[j]>>i&1),None)
        need(hit is not None,'Invertible nine-bit warp')
        rows[i],rows[hit]=rows[hit],rows[i]
        for j in range(9):
            if j!=i and rows[j]>>i&1:rows[j]^=rows[i]
    need([r&511 for r in rows]==[1<<i for i in range(9)],'Gauss-Jordan identity')
    out=[sum(((rows[i]>>(9+j))&1)<<i for i in range(9)) for j in range(9)]
    need(all(apply(out,apply(columns,1<<i))==1<<i for i in range(9)),'Inverse orientation')
    return out

def actual_paths(payload,direction):
    c=payload['canonical'];word=payload['programs'][direction];frames=c['frames'];bases=list(map(pivots,frames))
    need(all(len(b)==len(f) for b,f in zip(bases,frames)),'Independent actual frames')
    maps={w['op']:w['G_columns'] for w in c['warps']}
    maps.update({-op:inverse(cols) for op,cols in list(maps.items())})
    current={('L',r):f for r,f in enumerate(c['start'])};current['C',0]=None
    images=[list(frames[f]) for f in c['start']];widths=[[] for _ in range(632)]
    blocks=[[] for _ in range(632)];census=Counter();paid=Counter();adapter_roles=[]
    owners={};contacts=0
    def close(r):
        if r>=224:
            need(len(blocks[r])<=1,'Actual no-marker helper block has at most one paid call')
            census[len(blocks[r])]+=1
        blocks[r]=[]
    for i,e in enumerate(word):
        kind=e[0]
        if kind=='climb':
            _,_,r,a,b,d=e;role=('L',r)
            need(current[role]==a and len(frames[b])-len(frames[a])==d>0,'Actual increasing paid edge')
            need(all(contains(bases[b],x) for x in frames[a]),'Nested paid transport')
            need(all(contains(bases[a],x) for x in images[r]),'Transported entrance remains inside current chart')
            widths[r].append(d);blocks[r].append(d);current[role]=b;paid[d]+=1;owners[i]=role
        elif kind=='warp':
            _,role,op,a,b=e;role=tuple(role);r=role[1]
            need(role[0]=='L' and current[role]==a,'Actual warp owner/input')
            image=[apply(maps[op],x) for x in frames[a]]
            need(len(frames[a])==len(frames[b]) and len(pivots(image))==len(frames[b]) and
                all(contains(bases[b],x) for x in image),'Complete warp image')
            images[r]=[apply(maps[op],x) for x in images[r]];current[role]=b;owners[i]=role
        elif kind=='center':
            _,r,a,b,d=e;role=('C',r)
            need(current[role]==a and sorted([len(frames[a]),len(frames[b])])==[0,8] and d==8,'Actual owned center zero/eight dual pair')
            current[role]=b;paid[d]+=1;owners[i]=role
        elif kind=='scalar':
            gate,frame=e[1:];op=gate[0];dst=tuple(gate[1])
            if op=='clear':
                need(dst==('C',0),'Only owned zero clear');current[dst]=frame
            else:
                refs=gate[1:3] if op in ['add','copy'] else gate[1:2]
                need(op in ['add','copy','scale'] and all(current[tuple(r)]==frame for r in refs),'Actual common scalar chart')
                fields=[r for typ,r in refs if typ=='L'];need(len(set(fields))==len(fields),'Distinct scalar field owners')
                for r in fields:close(r)
                if op=='copy':need(dst==('C',0),'Owned-only overwrite')
                contacts+=1
        elif kind=='adapter':
            adapter_roles.append(e[2])  # Deliberately no block cut or frame change.
        else:need(kind=='phase','Known inert marker')
    need(paid==Counter({1:2201,2:412,3:510,4:127,5:40,8:8}),'Complete paid profile')
    ranks=Counter();maxima=Counter();path_mass=0;helper_owner_jobs=0
    for r in range(632):
        close(r);need(current['L',r]==c['final'][r],'Every final residence chart')
        h=len(frames[c['final'][r]])-len(frames[c['start'][r]])
        need(sum(widths[r])==h,'Every persistent path rank telescopes')
        if r>=224:
            need(h>0 and all(contains(bases[c['final'][r]],x) for x in frames[c['start'][r]]),'Positive nested helper endpoint')
            need(images[r]==frames[c['start'][r]],'Actual composed warp fixes helper entrance pointwise')
            need(all(d<=h for d in widths[r]),'Every helper step bounded by its endpoint rank')
            ranks[h]+=1;maxima[max(widths[r],default=0)]+=1;path_mass+=h;helper_owner_jobs+=len(widths[r])
    need(ranks==Counter({4:28,7:7,8:47,9:326}) and path_mass==3471,'All helper endpoint jobs')
    need(len(adapter_roles)==448 and all(r<224 for r in adapter_roles),'All inert adapter markers are on main owners')
    # Compare actual graph edges to independently reconstructed owner occurrences.
    wrapped=dict(payload);wrapped['programs']=dict(payload['programs'],forward=word)
    g=F.geometry(wrapped)
    need(g['components']==1067 and len(g['edges'])==len(owners),'Actual 1067 component graph')
    need({edge['event'] for edge in g['edges']}==set(owners),'Graph edges are actual owned occurrences')
    return dict(direction=direction,actual_components=g['components'],actual_edges=len(g['edges']),
        persistent_rank_telescopes=632,pointwise_fixed_helper_entrances=408,helper_rank_mass=path_mass,
        helper_jobs=helper_owner_jobs,helper_ranks=dict(ranks),helper_maximum_paid_step=dict(maxima),
        helper_blocks_without_adapter_cuts=dict(census),adapter_markers=448,helper_adapter_markers=0,
        scalar_contacts=contacts,paid=dict(paid),distinct_paid_owner_occurrences=len(owners),
        block_hypotheses_survive_no_inert_marker_freezes=True)

def main():
    began=time.monotonic();upstream=read(HERE/'UPSTREAM.json');folder=HERE/'upstream/phase-rank-debt'
    for row in upstream['files']:
        data=(HERE/row['copy']).read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'Upstream file hash')
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['blob'],'Upstream exact Git blob')
    before={str(p.relative_to(folder)):digest(p) for p in folder.rglob('*') if p.is_file()}
    proc=subprocess.run([sys.executable,'-I','-O','-B','verify.py'],cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
    (HERE/'RANK-DEBT-REPLAY.log').write_bytes(proc.stdout)
    need(proc.returncode==0 and b'PASS_PHASE_RANK_DEBT:' in proc.stdout,'Exact upstream isolated optimized replay')
    after={str(p.relative_to(folder)):digest(p) for p in folder.rglob('*') if p.is_file()}
    need(before==after,'Upstream replay leaves exact source and result bytes unchanged')
    raw=(HERE/'sources/native-word.json.gz').read_bytes();need(raw==(folder/'inputs/round3-native.json.gz').read_bytes(),'Same actual native bytes')
    payload=json.loads(gzip.decompress(raw));results=[actual_paths(payload,d) for d in ['forward','backward']]
    original=read(folder/'RESULT.json')
    for row in results:
        prior=original['orientations'][row['direction']]
        need(row['helper_blocks_without_adapter_cuts']=={int(k):v for k,v in prior['helper_contact_blocks_by_original_paid_calls'].items()},'Same helper blocks without inert-marker cuts')
    report=dict(status='PASS_INDEPENDENT_ACTUAL_GRAPH_PHASE_RANK_DEBT_AUDIT',script_sha256=digest(__file__),
        graph_gate_script_sha256=digest(HERE/'full_form_gate.py'),sources_sha256=digest(HERE/'SOURCES.json'),
        upstream_pins_sha256=digest(HERE/'UPSTREAM.json'),upstream_replay_stdout_sha256=digest(HERE/'RANK-DEBT-REPLAY.log'),
        upstream_commit=upstream['commit'],upstream_verifier_exit_code=proc.returncode,upstream_sources_unchanged=True,
        orientations=results,seconds=time.monotonic()-began,
        conclusion='Owner-wise rank-debt hypotheses hold on the actual graph without inert-marker cuts; planned fixed-subspace multi-edge phase mincuts are covered, so no duplicate511 search is run.',
        scope='Independent source/path/block hypothesis audit plus exact upstream verifier replay. Rank-form grammar and analytic rank-debt proof are read premises, not Lean formalizations. Shared-owner jobs, cross-contact fusion, changed graph/subspaces/maps/main contract and new controllers remain outside.')
    (HERE/'RANK-DEBT-AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(report['status']);print(proc.stdout.decode().strip())
    print('NO_ADAPTER_HELPER_BLOCKS',results[0]['helper_blocks_without_adapter_cuts'])
if __name__=='__main__':main()
