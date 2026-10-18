"""rebuild_borrow.py: rebuild the k=43 BORROW-WORDs from borrow/inputs (canonical words, block certificate, #2226-style witnesses),
check they equal the shipped borrow/words byte-for-content, run the extended auditor (borrow/audit_local.py) and its negative controls.
usage: python -B rebuild_borrow.py [--no-controls]   (exit 0 only if everything passes)"""
import sys,json,gzip,subprocess,hashlib,tempfile
from pathlib import Path
D=Path(__file__).resolve().parent/'borrow';sys.path.insert(0,str(D))
import build_word
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
ok=True;out={}
for canon,wt,h in CASES:
    tmp=Path(tempfile.mkdtemp())/'w.json.gz'
    build_word.main(str(D/'inputs'/f'{canon}.canonical.json.gz'),str(D/'inputs/blocks.json'),str(D/'inputs'/f'witness_43_{wt}.json'),str(tmp),h)
    shipped=D/'words'/f'BORROW-WORD-43{"base" if wt=="base" else "extra"}.json.gz'
    base=str(D/'inputs'/f'{canon}.canonical.json.gz');rec=D/'receipts'/f'AUDIT-43{wt}.json'
    patchf=D/'inputs'/f'refit_43{wt}.json'
    if patchf.exists():
        # frame refit: the pinned word (check_base against the canonical base) plus the exact frame patch must equal the shipped word;
        # the shipped word itself is audited independently (forward + dual free-algebra replay, no base pin because the refit changes frames inside the pinned A section)
        patch=json.loads(patchf.read_text());word0=json.loads(gzip.decompress(tmp.read_bytes()))
        refit=refit_apply(word0,patch)
        same=json.loads(gzip.decompress(shipped.read_bytes()))==refit
        pre=run_audit(tmp,base,D/'receipts'/f'AUDIT-43{wt}-prerefit.json');r=run_audit(shipped,None,rec)
        ok&=same and pre.returncode==0 and r.returncode==0
        res=dict(rebuild_plus_refit_equals_shipped=same,prerefit_pinned_audit_rc=pre.returncode,audit_rc=r.returncode,refit_frames=len(patch['frames']))
        if '--no-controls' not in sys.argv:
            c=subprocess.run([sys.executable,'-B',str(D/'borrow_controls.py'),str(tmp),base,str(D/'receipts'/f'CONTROLS-43{wt}.json')],capture_output=True,text=True)
            ok&=c.returncode==0;res['controls_rc']=c.returncode
            # refit control: a refit frame that does not contain the register's current frame must be rejected by the independent audit
            bad=json.loads(gzip.decompress(shipped.read_bytes()));sec,i,fr=patch['frames'][-1];bad[sec][i][-1]=[1];bp=Path(tempfile.mkdtemp())/'bad.json.gz';bp.write_bytes(gzip.compress(json.dumps(bad,separators=(',',':')).encode()))
            br=run_audit(bp,None,bp.parent/'bad.out.json');res['refit_tamper_rejected']=br.returncode!=0;ok&=br.returncode!=0
    else:
        same=content(tmp)==content(shipped);ok&=same
        r=run_audit(shipped,base,rec);ok&=r.returncode==0
        res=dict(rebuild_equals_shipped=same,audit_rc=r.returncode)
        if '--no-controls' not in sys.argv:
            c=subprocess.run([sys.executable,'-B',str(D/'borrow_controls.py'),str(shipped),base,str(D/'receipts'/f'CONTROLS-43{wt}.json')],capture_output=True,text=True)
            ok&=c.returncode==0;res['controls_rc']=c.returncode
    out[canon]=res;print(canon,res,flush=True)
print('PASS_REBUILD_BORROW' if ok else 'FAIL_REBUILD_BORROW');sys.exit(0 if ok else 1)
