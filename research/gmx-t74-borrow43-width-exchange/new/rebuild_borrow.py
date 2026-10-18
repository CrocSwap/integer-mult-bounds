"""rebuild_borrow.py: rebuild the k=43 BORROW-WORDs from borrow/inputs (canonical words, block certificate, #2226-style witnesses),
check they equal the shipped borrow/words byte-for-content, run the extended auditor (borrow/audit_local.py) and its negative controls.
usage: python -B rebuild_borrow.py [--no-controls]   (exit 0 only if everything passes)"""
import sys,json,gzip,subprocess,hashlib,tempfile
from pathlib import Path
D=Path(__file__).resolve().parent/'borrow';sys.path.insert(0,str(D))
import build_word,word_patch
CASES=[('gauge44','base','eeb6a236'),('extra','extra','cd417b90')]
def content(p):return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()
def refit_apply(word0,patch):
    """frame refit: replace exactly the listed gate frames (gates unchanged) and the local profile."""
    import copy
    w=copy.deepcopy(word0)
    for sec,i,fr in patch['frames']:
        assert w[sec][i][:-1]==word0[sec][i][:-1];w[sec][i][-1]=fr
    w['report']['local_profile']=patch['local_profile']
    return w
def run_audit(word,base,rec):
    cmd=[sys.executable,'-B',str(D/'audit_local.py'),'--word',str(word),'--output',str(rec)]+(['--base',str(base)] if base else [])
    return subprocess.run(cmd,capture_output=True,text=True)
def kernel_check(prev,w,patch):
    """The kernel edit(s) (helper-donor pivot kernels, PR1625 shape): the shipped B section differs from the previous word's by exactly the declared gate-level edit
    (frames ignored): reads of the pivots inserted/deleted, nothing else; every inserted and deleted gate is a read of a declared pivot with coefficient +-1."""
    qs=set(patch['pivots']);ed=word_patch.kernel_gate_edit(prev['B'],w['B'])
    ok=ed==patch['declared_gate_edit'] and all(g[0]=='add' and g[2] in qs and abs(g[3])==1 and g[4]==1 for _,_,g in ed)
    ok&=sum(e[0]=='delete' for e in ed)==len(qs) and sum(e[0]=='insert' for e in ed)==4*len(qs)
    for k in w:
        if k not in('A','B','restore','warps','report','cleanup'):ok&=w[k]==prev[k]
    for k in('A','restore'):   # frame-only changes outside B
        ok&=len(w[k])==len(prev[k]) and all(x[:-1]==y[:-1] for x,y in zip(w[k],prev[k]))
    return ok
def kernel_controls(w,patch,tmp):
    """every perturbation of the kernel edit must be rejected by the independent audit"""
    import copy
    res={};qs=set(patch['pivots'])
    pos=[j for kind,j,g in patch['declared_gate_edit'] if kind=='insert']
    def audit_bad(name,m):
        bp=Path(tmp)/(name+'.json.gz');bp.write_bytes(gzip.compress(json.dumps(m,separators=(',',':')).encode()))
        r=run_audit(bp,None,Path(tmp)/(name+'.out.json'));res[name]=r.returncode!=0;return r.returncode!=0
    ok=True
    m=copy.deepcopy(w);m['B'][pos[0]][3]=-m['B'][pos[0]][3];m['cleanup']=word_patch.derive_cleanup(m,word_patch.restored_of(w));ok&=audit_bad('kernel_sign_flipped',m)
    m=copy.deepcopy(w);del m['B'][pos[1]];ok&=audit_bad('kernel_read_dropped',m)
    m=copy.deepcopy(w);m['B'][pos[2]][3]*=2;ok&=audit_bad('kernel_coefficient_doubled',m)
    m=copy.deepcopy(w);m['B'][pos[3]][1]=m['B'][pos[3]][1]+1;ok&=audit_bad('kernel_read_moved_to_neighbour_register',m)
    return ok,res
ok=True;out={}
for canon,wt,h in CASES:
    tmp=Path(tempfile.mkdtemp())/'w.json.gz'
    build_word.main(str(D/'inputs'/f'{canon}.canonical.json.gz'),str(D/'inputs/blocks.json'),str(D/'inputs'/f'witness_43_{wt}.json'),str(tmp),h)
    shipped=D/'words'/f'BORROW-WORD-43{"base" if wt=="base" else "extra"}.json.gz'
    base=str(D/'inputs'/f'{canon}.canonical.json.gz')
    word0=json.loads(gzip.decompress(tmp.read_bytes()))
    chain=[word0];steps=[]
    rf=D/'inputs'/f'refit_43{wt}.json';kf=D/'inputs'/f'kernel_43{wt}.json'
    if rf.exists():chain.append(refit_apply(chain[-1],json.loads(rf.read_text())));steps.append('refit')
    kpatch=json.loads(kf.read_text());chain.append(word_patch.apply_kernel(chain[-1],kpatch));steps.append('kernel')
    final=json.loads(gzip.decompress(shipped.read_bytes()))
    same=final==chain[-1];kok=kernel_check(chain[-2],final,kpatch)
    # audits: the pinned pre-refit/pre-kernel word against the canonical base; every later state independently (forward + dual free-algebra replay; refit and kernel change frames inside the pinned sections)
    tag=lambda n:D/'receipts'/f'AUDIT-43{wt}{n}.json'
    pw=Path(tempfile.mkdtemp());ps=[]
    for j,w_ in enumerate(chain[:-1]):
        f_=pw/f'w{j}.json.gz';f_.write_bytes(gzip.compress(json.dumps(w_,separators=(',',':')).encode()))
        r=run_audit(f_,base if j==0 else None,tag('-pinned' if j==0 else '-prekernel'));ps.append(r.returncode)
    r=run_audit(shipped,None,tag(''))
    ok&=same and kok and all(x==0 for x in ps) and r.returncode==0
    res=dict(rebuild_plus_patches_equals_shipped=same,patches=steps,kernel_edit_exact=kok,prior_state_audit_rc=ps,audit_rc=r.returncode)
    if '--no-controls' not in sys.argv:
        c=subprocess.run([sys.executable,'-B',str(D/'borrow_controls.py'),str(tmp),base,str(D/'receipts'/f'CONTROLS-43{wt}.json')],capture_output=True,text=True)
        ok&=c.returncode==0;res['controls_rc']=c.returncode
        kc_ok,kc=kernel_controls(final,kpatch,tempfile.mkdtemp());ok&=kc_ok;res['kernel_controls_rejected']=kc
        (D/'receipts'/f'CONTROLS-KERNEL-43{wt}.json').write_text(json.dumps(kc,indent=2)+'\n')
        if rf.exists():
            rp=json.loads(rf.read_text());bad=copy_=json.loads(json.dumps(chain[1]));sec,i_,fr=rp['frames'][-1];bad[sec][i_][-1]=[1]
            bp=pw/'bad.json.gz';bp.write_bytes(gzip.compress(json.dumps(bad,separators=(',',':')).encode()));br=run_audit(bp,None,pw/'bad.out.json');res['refit_tamper_rejected']=br.returncode!=0;ok&=br.returncode!=0
    out[canon]=res;print(canon,res,flush=True)
print('PASS_REBUILD_BORROW' if ok else 'FAIL_REBUILD_BORROW');sys.exit(0 if ok else 1)
