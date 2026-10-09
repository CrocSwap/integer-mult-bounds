#!/usr/bin/env python3
"""Replay all finite bit161 evidence in a disposable, portable directory."""
from pathlib import Path
from hashlib import sha256
import gzip,json,shutil,subprocess,sys,tempfile,time

HERE=Path(__file__).resolve().parent
def read(path):return json.loads(path.read_text())
def run(script,*args,reject=False):
    started=time.monotonic()
    p=subprocess.run([sys.executable,str(script),*map(str,args)],capture_output=True,text=True,timeout=900)
    if reject:assert p.returncode!=0,'Corruption accepted: '+script.name
    elif p.returncode:raise RuntimeError(script.name+' failed:\n'+p.stdout[-6000:]+'\n'+p.stderr[-6000:])
    print(('REJECT'if reject else'PASS'),script.name,f'({time.monotonic()-started:.1f}s)',flush=True)

def main():
    assert not sys.flags.optimize,'Run without -O; inherited assertions are required'
    manifest=read(HERE/'MANIFEST.json')
    for name,digest in manifest['sha256'].items():assert sha256((HERE/name).read_bytes()).hexdigest()==digest,name
    print('PASS',len(manifest['sha256']),'frozen source/input/output hashes',flush=True)
    with tempfile.TemporaryDirectory(prefix='bit161-')as temporary:
        work=Path(temporary)/'package';shutil.copytree(HERE,work,ignore=shutil.ignore_patterns('__pycache__'))
        p=work/'inputs/research'
        run(p/'round8-network-final-geometry.py','--output',work/'fresh-geometry.json')
        old=read(p/'pr-review-network-geometry.json');new=read(work/'fresh-geometry.json')
        for key in old:
            if key!='elapsed':assert old[key]==new[key],('geometry',key)
        candidate=p/'round8-foundations-minimal-v-word.json.gz'
        run(p/'round8-network-physical-ledger.py','--candidate',candidate,'--output',work/'literal-replay')
        old=read(p/'round8-network-minimal-v-ledger/result.json');new=read(work/'literal-replay/result.json')
        for key in old:
            if key!='elapsed':assert old[key]==new[key],('ledger',key)
        assert gzip.decompress((p/'round8-network-minimal-v-ledger/forward-events.i32.gz').read_bytes())==gzip.decompress((work/'literal-replay/forward-events.i32.gz').read_bytes())
        old=read(p/'round8-network-opposite-profile.json')
        run(p/'round8-network-opposite-profile.py')
        assert read(p/'round8-network-opposite-profile.json')==old
        run(p/'round8-network-pr104-check.py')
        run(work/'partition161.py');assert read(work/'groups161.json')==read(HERE/'groups161.json')
        receipt=read(work/'partition161-receipt.json');old=read(HERE/'partition161-receipt.json')
        for key in old:
            if key!='seconds':assert receipt[key]==old[key],('partition receipt',key)
        run(work/'profile161.py');assert read(work/'profile161.json')==read(HERE/'profile161.json')
        run(work/'certify161.py');assert read(work/'certificate.json')==read(HERE/'certificate.json')
        # Coverage-preserving swap deliberately violates pairwise H-orthogonality.
        groups=read(work/'groups161.json');a=set(groups[0][0]);found=False
        for j in range(1,len(groups)):
            for k,t in enumerate(groups[j]):
                if len(a&set(t))!=1:
                    groups[0][1],groups[j][k]=groups[j][k],groups[0][1];found=True;break
            if found:break
        assert found
        (work/'groups161.json').write_text(json.dumps(groups)+'\n')
        run(work/'profile161.py',reject=True)
        # Missing a true output scatter must fail complete formal-column replay.
        word=json.loads(gzip.decompress(candidate.read_bytes()))
        index=next(i for i,e in enumerate(word['events'])if e[0]=='out');del word['events'][index]
        bad=work/'bad-word.json.gz';bad.write_bytes(gzip.compress(json.dumps(word).encode(),mtime=0))
        run(p/'round8-network-physical-ledger.py','--candidate',bad,'--output',work/'bad-ledger',reject=True)
        profile=read(HERE/'profile161.json');rows={int(t):n for t,n in profile['child_multiplicities'].items()};rows[1]-=1
        assert sum(t*n for t,n in rows.items())!=profile['m']*profile['W']-profile['deficit']
        print('REJECT omitted paid child; next-grid enclosure already checked',flush=True)
    print('PASS exact coarse bit saving 129310447/10^12; ordinary stopped wrapper and final assembly are separate.')

if __name__=='__main__':main()
