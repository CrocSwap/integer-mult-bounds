"""Local transition oracle using the frozen PR62 literal profiler formulas.

The input is a candidate-transition list, not an executable word. This tool
exports exact integer child profiles, which are discovery costs only. Changed
words still require independent whole-word replay and full profile verification.
"""
from pathlib import Path
import argparse,hashlib,json,math,struct,subprocess
HERE=Path(__file__).resolve().parent
FROZEN=HERE.parents[1]/'matrix-synthesis/bridge/pr62'
ZIG=HERE.parents[1]/'matrix-synthesis/toolchain/zig-x86_64-windows-0.14.1/zig.exe'

def main():
    p=argparse.ArgumentParser();p.add_argument('--h',type=int,choices=(23,25),required=True)
    p.add_argument('--strategy',default='profile_collect');p.add_argument('--incremental',action='store_true');p.add_argument('--basis',choices=('native','shift1'),default='native');a=p.parse_args()
    source=FROZEN/'scripts/experiments/binary_frame_profiles.cpp'
    text=source.read_text();assert hashlib.sha256(source.read_bytes()).hexdigest()=='8e2e391d3ee57cbb1372c68e4aa031e1b861321536eabd642ada54e12e678669'
    original='for(auto&[key,count]:transitions){if(!count)continue;'
    emit='''std::ofstream pairout(std::string(argv[1])+".pair-profiles.jsonl");
auto emit=[&](U a,U b,const std::vector<int64_t>&prior,int64_t count){
 pairout<<"{\\"a\\":"<<a<<",\\"b\\":"<<b<<",\\"rank\\":"<<(frames[b].rank-frames[a].rank)<<",\\"blocks\\":[";
 for(U t=0;t<=h;t++){if(t)pairout<<",";assert((blocks[t]-prior[t])%count==0);pairout<<(blocks[t]-prior[t])/count;}
 pairout<<"]}\\n";
};
for(auto&[key,count]:transitions){if(!count)continue;auto prior=blocks;'''
    assert original in text;text=text.replace(original,emit)
    small='if(rr<=2){blocks[1]+=count*rr;continue;}if(aa==0&&bb==1){blocks[h]+=count;continue;}'
    assert small in text;text=text.replace(small,'if(rr<=2){blocks[1]+=count*rr;emit(aa,bb,prior,count);continue;}if(aa==0&&bb==1){blocks[h]+=count;emit(aa,bb,prior,count);continue;}')
    finish='}matrices++;matrix_cache[aa].clear();matrix_cache[bb].clear();'
    assert text.count(finish)==1;text=text.replace(finish,finish+'emit(aa,bb,prior,count);')
    cpp=HERE/'pair_profile_oracle.cpp';exe=HERE/'pair-profile-oracle.exe'
    if not cpp.exists() or cpp.read_text()!=text or not exe.exists():
        cpp.write_text(text)
        subprocess.run([str(ZIG),'c++','-std=c++17','-O2',str(cpp),'-I',str(FROZEN/'scripts/partial_swap'),'-o',str(exe)],check=True)
    d=json.loads((HERE/a.strategy/f'h{a.h}'/'candidate-frames.json').read_text())
    suffix=''if a.basis=='native'else '-'+a.basis
    point_permutation=list(range(a.h))if a.basis=='native'else[(i+1)%a.h for i in range(a.h)]
    def mask(m):return sum(1<<point_permutation[i]for i in range(a.h)if m>>i&1)
    frames=[(0,0,0),(0,0,a.h)]+[(mask(c),mask(u),1 if c==u else u.bit_count()-c.bit_count())for c,u in d['frames']]
    proposed=set(map(tuple,d['pairs']))
    previous=HERE/f'pair-profiles-h{a.h}{suffix}.jsonl'
    oldrows={}
    if previous.exists():
        for line in previous.read_text().splitlines():
            row=json.loads(line);key=(row['a'],row['b']);proposed.add(key);oldrows[key]=row
    pairs=[]
    for x,y in sorted(proposed):
        if x==y or frames[x][2]==frames[y][2]:continue
        if a.incremental and (x,y)in oldrows:continue
        assert frames[x][2]<frames[y][2]
        if x!=0 and y!=1:
            c,u,_=frames[x];cc,uu,_=frames[y]
            assert not cc&~c and not u&~uu
        pairs.append((x,y))
    mass=sum(frames[y][2]-frames[x][2]for x,y in pairs)
    path=HERE/f'candidate-pairs-h{a.h}{suffix}.bin'
    with path.open('wb')as out:
        out.write(struct.pack('<6I2Q',a.h,math.comb(a.h,3),mass//a.h,len(frames),len(pairs),0,mass,mass%a.h))
        for c,u,r in frames:out.write(struct.pack('<2QI',c,u,r))
        for x,y in pairs:out.write(struct.pack('<2Iq',x,y,1))
    subprocess.run([str(exe),str(path)],check=True)
    generated=Path(str(path)+'.pair-profiles.jsonl')
    freshrows=[json.loads(line)for line in generated.read_text().splitlines()]
    assert len(freshrows)==len(pairs)
    if a.incremental:
        for row in freshrows:oldrows[row['a'],row['b']]=row
        raw=(''.join(json.dumps(oldrows[key],separators=(',',':'))+'\n'for key in sorted(oldrows))).encode()
    else:raw=generated.read_bytes()
    target=HERE/f'pair-profiles-h{a.h}{suffix}.jsonl';target.write_bytes(raw)
    immutable=HERE/f'pair-profiles-h{a.h}{suffix}-{hashlib.sha256(target.read_bytes()).hexdigest()}.jsonl'
    if immutable.exists():assert immutable.read_bytes()==target.read_bytes()
    else:immutable.write_bytes(target.read_bytes())
    rows=[json.loads(line)for line in target.read_text().splitlines()]
    assert all(sum(t*n for t,n in enumerate(row['blocks']))==row['rank']for row in rows)
    receipt=dict(axis=a.h,basis=a.basis,point_permutation=point_permutation,profiled_pairs=len(rows),freshly_profiled_pairs=len(freshrows),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),oracle_cpp_sha256=hashlib.sha256(cpp.read_bytes()).hexdigest(),
        exact_profile_dump_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),exact_profile_dump=str(immutable.name),header_sha256=hashlib.sha256((FROZEN/'scripts/partial_swap/binary_io.hpp').read_bytes()).hexdigest(),frozen_commit='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',scope='per-transition profile oracle for discovery; not whole-word validation')
    (HERE/f'pair-oracle-h{a.h}{suffix}.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
