"""tamper controls (each mutant gets its inverse-reverse cleanup re-derived, and a rejection by a stale-cleanup/operator-id reason counts as a FAILURE) for the frame-refit alias 653<-563: every mutation must be rejected by audit_local.
usage: alias1_controls.py WORD PATCH OUT"""
import sys,json,gzip,copy,tempfile,io,contextlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import audit_local as al,word_patch as WP
w0=json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()));patch=json.loads(Path(sys.argv[2]).read_text());tmp=tempfile.mkdtemp();res={};good=True
def run(w):
    p=Path(tmp)/'m.json.gz';p.write_bytes(gzip.compress(json.dumps(w,separators=(',',':')).encode()))
    with contextlib.redirect_stdout(io.StringIO()):return al.run(p,Path(tmp)/'m.out.json',None,None)
def rederive(m):
    m2=copy.deepcopy(m);A=m2['A'];npre=m2['prelude_events'];m2['A']=A[npre:];m2['cleanup']=WP.derive_cleanup(m2,WP.restored_of(w0));m2['A']=A;return m2
VACUOUS=('explicit cleanup differs','warp operator id')   # reasons that only reflect a stale explicit cleanup, not the mutated mathematics
def expect(name,m):
    global good
    m=rederive(m)   # every mutant carries the cleanup re-derived from its own forward word, so it is rejected for a real reason
    try:run(m);res[name]=dict(rejected=False);good=False;print('NOT REJECTED',name)
    except RuntimeError as e:
        r=str(e);real=not r.startswith(VACUOUS);res[name]=dict(rejected=True,reason=r[:160],real_reason=real);good&=real;print('rejected' if real else 'VACUOUS',name,'|',r[:90])
print('unmutated',run(w0)['status'])
for a in patch['aliases']:
    h,L=a['h'],a['L'];op=next(i for i,r in enumerate(w0['warps']) if r[1]==L and r[0]==a['pos'])
    reads=[i for i,g in enumerate(w0['B']) if i>=a['pos'] and g[0]=='add' and g[2]==L]
    writes=[i for i,g in enumerate(w0['B']) if i>=a['pos'] and g[0]=='add' and g[1]==L]
    m=copy.deepcopy(w0);m['B'][reads[0]][3]*=-1;expect(f'{h}<-{L} borrowed read sign flipped',m)
    m=copy.deepcopy(w0);m['B'][reads[0]][3]*=2;expect(f'{h}<-{L} borrowed read doubled',m)
    if writes:m=copy.deepcopy(w0);m['B'][writes[0]][3]*=-1;expect(f'{h}<-{L} borrowed write sign flipped',m)
    m=copy.deepcopy(w0);del m['warps'][op]
    for e_ in m['A'][:m['prelude_events']]:
        if e_[0]=='warp' and abs(e_[2])>op+1:e_[2]-=1 if e_[2]>0 else -1
    expect(f'{h}<-{L} warp dropped',m)
    m=copy.deepcopy(w0);m['warps'][op][2][0]^=m['warps'][op][2][1];expect(f'{h}<-{L} G wrong',m)
    m=copy.deepcopy(w0);m['warps'][op][0]=a['pos']-400;expect(f'{h}<-{L} warp before lender retirement',m)
    m=copy.deepcopy(w0);m['start_extra'][str(h)]=a['E'];expect(f'{h} kept with an entrance frame',m)
Path(sys.argv[3]).write_text(json.dumps(dict(all_rejected=good,controls=res),indent=1)+'\n');print('ALL CONTROLS REJECTED' if good else 'CONTROL FAILURE');sys.exit(0 if good else 1)
