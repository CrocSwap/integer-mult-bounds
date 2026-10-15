"""rebuild_borrow.py: rebuild the k=43 BORROW-WORDs from borrow/inputs (canonical words, block certificate, #2226-style witnesses),
check they equal the shipped borrow/words byte-for-content, run the extended auditor (borrow/audit_local.py) and its negative controls.
usage: python -B rebuild_borrow.py [--no-controls]   (exit 0 only if everything passes)"""
import sys,json,gzip,subprocess,hashlib,tempfile
from pathlib import Path
D=Path(__file__).resolve().parent/'borrow';sys.path.insert(0,str(D))
import build_word
CASES=[('gauge44','base','eeb6a236'),('extra','extra','cd417b90')]
def content(p):return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()
ok=True;out={}
for canon,wt,h in CASES:
    tmp=Path(tempfile.mkdtemp())/'w.json.gz'
    build_word.main(str(D/'inputs'/f'{canon}.canonical.json.gz'),str(D/'inputs/blocks.json'),str(D/'inputs'/f'witness_43_{wt}.json'),str(tmp),h)
    shipped=D/'words'/f'BORROW-WORD-43{"base" if wt=="base" else "extra"}.json.gz'
    same=content(tmp)==content(shipped);ok&=same
    base=str(D/'inputs'/f'{canon}.canonical.json.gz');rec=D/'receipts'/f'AUDIT-43{wt}.json'
    r=subprocess.run([sys.executable,'-B',str(D/'audit_local.py'),'--word',str(shipped),'--base',base,'--output',str(rec)],capture_output=True,text=True)
    ok&=r.returncode==0
    res=dict(rebuild_equals_shipped=same,audit_rc=r.returncode)
    if '--no-controls' not in sys.argv:
        c=subprocess.run([sys.executable,'-B',str(D/'borrow_controls.py'),str(shipped),base,str(D/'receipts'/f'CONTROLS-43{wt}.json')],capture_output=True,text=True)
        ok&=c.returncode==0;res['controls_rc']=c.returncode
    out[canon]=res;print(canon,res,flush=True)
print('PASS_REBUILD_BORROW' if ok else 'FAIL_REBUILD_BORROW');sys.exit(0 if ok else 1)
