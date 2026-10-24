#!/usr/bin/env python3
"""Quick host-only audit of frozen actual evidence; no numerical cohort imports.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import hashlib,io,json,shutil,subprocess,sys,tarfile,tempfile
P=Path(__file__).resolve().parent

def need(x,m):
    if not x: raise ValueError(m)
def digest(data):return hashlib.sha256(data).hexdigest()
def validate_bytes(data,expected):need(digest(data)==expected,'authenticated bytes differ')
def source_members():
    pins=json.loads((P/'PACKAGE-PINS.json').read_text())
    data=(P/'inputs/pr5095-consumed-source.tar.gz').read_bytes()
    validate_bytes(data,pins['source_archive_sha256'])
    manifest=json.loads((P/'inputs/SOURCE-COHORT.json').read_text())
    validate_bytes((P/'inputs/SOURCE-COHORT.json').read_bytes(),pins['source_manifest_sha256'])
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz')as archive:
        members=archive.getmembers()
        need(len(members)==len(manifest)==83,'exact83-file source inventory')
        need(len({m.name for m in members})==83,'no duplicate archive members')
        out={}
        for member in members:
            need(member.isfile() and member.name in manifest,'regular declared source member')
            need(not member.name.startswith('/') and '..'not in Path(member.name).parts,'canonical source path')
            payload=archive.extractfile(member).read();validate_bytes(payload,manifest[member.name]);out[member.name]=payload
    return out

def main():
    pins=json.loads((P/'PACKAGE-PINS.json').read_text())
    frozen=json.loads((P/'EVIDENCE-SHA256.json').read_text())
    validate_bytes((P/'EVIDENCE-SHA256.json').read_bytes(),pins['evidence_manifest_sha256'])
    for name,h in frozen.items():validate_bytes((P/name).read_bytes(),h)
    sources=source_members()
    # A source-integrity negative control must reject a changed byte.
    sample=next(iter(sources.values()));bad=bytes([sample[0]^1])+sample[1:]
    try:validate_bytes(bad,digest(sample))
    except ValueError:pass
    else:raise ValueError('source drift control did not reject')
    a=P/'evidence/real-packed-outer-consumer-20261023'
    r=json.loads((a/'FULL-PACKED-ATTEMPT2-RESULT.json').read_text())
    h=r['actual_Tensor_observations'][0]['raw_bits']
    def decode(bits):
        values=[]
        for k in range(70):
            word=bits[k*50:(k+1)*50];v=sum(b<<i for i,b in enumerate(word));values.append(v-(1<<50)if word[-1]else v)
        return list(zip(values[::2],values[1::2]))
    H=decode(h);tz=lambda n,s:(-1 if n<0 else 1)*(abs(n)>>s)
    def product(J,shift):return [(tz(2*a*b+2*c*d,shift),tz(-a*a+b*b+c*c-d*d,shift))for(a,b),(c,d)in zip(H,J)]
    J=[H[((-i)%5)*7+((-j)%7)]for i in range(5)for j in range(7)]
    expected=decode(r['arrays']['actual_pointwise_bits'])
    need(product(J,50)==expected,'captured nonlinear product')
    need(product(H,50)!=expected,'wrong frequency-negation control discriminates')
    need(product(J,48)!=expected,'raw-sum wrong-shift control discriminates')
    corrupt=h.copy();corrupt[0]^=1
    need(digest(bytes(corrupt))!=r['actual_Tensor_observations'][0]['return_sha256'],'captured-return drift control discriminates')
    # Run the unchanged independent checker over a temporary byte-identical
    # layout. The retained checker imports only stdlib and host integers.
    with tempfile.TemporaryDirectory(prefix='packed-staged-evidence-')as directory:
        layout=Path(directory)
        shutil.copytree(P/'evidence',layout/'evidence')
        author=layout/'evidence/real-packed-outer-consumer-20261023'
        for name,data in sources.items():
            target=author/'staged-source'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        checker=layout/'evidence/packed-caller-independent-gate-20261023/check_postrun.py'
        command=[sys.executable,'-I','-B','-W','error']
        if sys.flags.optimize:command+=['-O']
        completed=subprocess.run(command+[str(checker)],capture_output=True,text=True,timeout=30)
        need(completed.returncode==0,'unchanged independent host checker: '+completed.stdout+completed.stderr)
        print(completed.stdout.strip())
    print('PASS_QUICK_FROZEN_EVIDENCE_AND_SOURCE_INTEGRITY; no Tensor/CRT/owner execution; controls=source-drift,return-drift,wrong-J,wrong-shift')
if __name__=='__main__':main()
