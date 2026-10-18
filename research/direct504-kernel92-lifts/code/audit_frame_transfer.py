"""Independent PR534 monotone-lift check plus composition-specific controls.
The selected kernel prefix and inverse cleanup remain fixed. Prepared by Codex.
"""
from pathlib import Path
import copy,gzip,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];source,new,out=map(Path,sys.argv[1:4]);out.mkdir(exist_ok=False)
read=lambda p:json.loads(gzip.decompress(p.read_bytes()));old=read(source);word=read(new);assert old['cleanup']==word['cleanup'],'cleanup changed'
checker=ROOT/'vendor/pr534/check_frame_lifts.py'
def check(path,report):return subprocess.run([sys.executable,'-B',str(checker),str(source),str(path),str(report)],capture_output=True,text=True)
r=check(new,out/'FRAME-LIFTS.json');assert r.returncode==0,r.stderr
receipt=json.loads((out/'FRAME-LIFTS.json').read_text());assert receipt['lifted_total']==662
mutants=[]
for kind in ('scalar-change','entrance-change','below-constructor','nonmonotone'):
    w=copy.deepcopy(word)
    if kind=='scalar-change':next(e for e in w['B']if e[0]=='add')[3]+=1
    elif kind=='entrance-change':w['start_extra'].pop(next(iter(w['start_extra'])))
    elif kind=='below-constructor':
        i=next(i for i,e in enumerate(old['B'])if e[-1]);w['B'][i][-1]=[]
    else:
        e=next(e for e in w['B']if 112<=e[1]<224);e[-1]=[1<<i for i in range(9)]
    p=out/(kind+'.json.gz');p.write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));result=check(p,out/(kind+'-unexpected.json'));assert result.returncode!=0,kind
    (out/(kind+'.log')).write_text(result.stdout+result.stderr);mutants.append(kind)
(out/'CONTROLS.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_FRAME_TRANSFER_AND_CONTROLS',mutations_rejected=mutants,unchanged_cleanup=True,frame_lifts=662),indent=2)+'\n');print('PASS_FRAME_TRANSFER',len(mutants),'controls',flush=True)
