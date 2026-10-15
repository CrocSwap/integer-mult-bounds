"""Tamper controls of the native borrow chain.  Every tampered BORROW-WORD / emitted artifact must be REJECTED by the chain.
usage: bw_tamper.py BORROW-WORD.json.gz NATIVE_LOCAL_DIR WORK_DIR [--files]   (--files also reruns the heavier file-level stages)"""
import copy,gzip,json,os,shutil,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
word_path=Path(sys.argv[1]).resolve();local=Path(sys.argv[2]).resolve();work=Path(sys.argv[3]).resolve();work.mkdir(parents=True,exist_ok=True)
flags=(0x00000040|0x08000000) if os.name=='nt' and os.environ.get('BW_IDLE','1')=='1' else 0
def run(script,*args):
    p=subprocess.run([sys.executable,'-B',str(HERE/script),*map(str,args)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=HERE,creationflags=flags)
    return p.returncode,p.stdout.decode(errors='replace')
W=json.loads(gzip.decompress(word_path.read_bytes()))
results=[];t0=time.monotonic()
def word_tamper(name,fn,expect):
    w=copy.deepcopy(W);fn(w);p=work/(name+'.json.gz');p.write_bytes(gzip.compress(json.dumps(w).encode()))
    out=work/('out-'+name)
    if out.exists():shutil.rmtree(out)
    rc,log=run('bw_transport.py',p,out)
    ok=rc!=0 and expect in log
    results.append(dict(name=name,rejected=rc!=0,expected_reason=expect,reason_matches=expect in log,last_line=log.strip().splitlines()[-1][:200] if log.strip() else ''))
    assert ok,(name,rc,log[-600:])
def sw(g,i,j):g[i],g[j]=g[j],g[i]
first_cleanup_warp=lambda w:next(i for i,e in enumerate(w['cleanup']) if e[0]=='warp')
word_tamper('wrong_G_not_carrying_frame',lambda w:w['warps'][0].__setitem__(2,[w['warps'][0][2][0]^w['warps'][0][2][1]]+w['warps'][0][2][1:]),'G does not map the from frame onto the to frame')
word_tamper('non_invertible_G',lambda w:w['warps'][0][2].__setitem__(1,w['warps'][0][2][0]),'non-invertible G')
word_tamper('missing_inverse_warp_in_cleanup',lambda w:w['cleanup'].pop(first_cleanup_warp(w)),'arbitrary-input endpoint')
word_tamper('missing_forward_warp',lambda w:w['warps'].pop(0),'')
word_tamper('frame_mismatch_from_basis',lambda w:w['warps'][0].__setitem__(3,next(x[3] for x in w['warps'] if sorted(x[3])!=sorted(w['warps'][0][3]) and len(x[3])==len(w['warps'][0][3]))),'')
word_tamper('inverse_warp_sign_flipped',lambda w:w['cleanup'].__setitem__(first_cleanup_warp(w),['warp',w['cleanup'][first_cleanup_warp(w)][1],abs(w['cleanup'][first_cleanup_warp(w)][2]),w['cleanup'][first_cleanup_warp(w)][3]]),'arbitrary-input endpoint')
word_tamper('inverse_warp_wrong_operator',lambda w:w['cleanup'].__setitem__(first_cleanup_warp(w),['warp',w['cleanup'][first_cleanup_warp(w)][1],-(abs(w['cleanup'][first_cleanup_warp(w)][2])%len(w['warps'])+1),w['cleanup'][first_cleanup_warp(w)][3]]),'arbitrary-input endpoint')
word_tamper('inverse_warp_on_wrong_register',lambda w:w['cleanup'].__setitem__(first_cleanup_warp(w),['warp',(w['cleanup'][first_cleanup_warp(w)][1]+1)%(w['report']['v']*2),w['cleanup'][first_cleanup_warp(w)][2],w['cleanup'][first_cleanup_warp(w)][3]]),'arbitrary-input endpoint')
word_tamper('warp_moved_after_its_first_use',lambda w:w['warps'][0].__setitem__(0,w['warps'][0][0]+5),'')
if W['initial_corrections']:
    word_tamper('initial_correction_sign_flipped',lambda w:w['initial_corrections'][0].__setitem__('coefficient',str(-__import__('fractions').Fraction(w['initial_corrections'][0]['coefficient']))),'arbitrary-input endpoint')
    word_tamper('initial_correction_dropped',lambda w:w['initial_corrections'].pop(0),'arbitrary-input endpoint')
    word_tamper('initial_correction_wrong_operator',lambda w:w['initial_corrections'][0].__setitem__('operator_word',[w['initial_corrections'][0]['operator_word'][0]%len(w['warps'])+1]),'arbitrary-input endpoint')
word_tamper('zero_buffer_gate_dropped',lambda w:w['cleanup'].pop(next(i for i,e in enumerate(w['cleanup']) if e[0]=='add' and e[1]>=2*w['report']['v']+w['report']['R'])),'arbitrary-input endpoint')
if '--files' in sys.argv:
    def file_tamper(name,script,files,mutate,expect_fail=True):
        d=work/('files-'+name)
        if d.exists():shutil.rmtree(d)
        shutil.copytree(local,d);mutate(d)
        rc,log=run(script,d,*[]) if script!='bw_adapters.py' else run(script,d/'CANONICAL-WORD.json.gz',d/'RESIDUAL-ADAPTERS.json',d/'WRAPPER-CHECKS.json')
        results.append(dict(name=name,rejected=rc!=0,last_line=log.strip().splitlines()[-1][:200] if log.strip() else ''));assert rc!=0,(name,log[-400:])
    def edit_json(path,fn,gz=False):
        d=json.loads(gzip.decompress(path.read_bytes()) if gz else path.read_text());fn(d)
        path.write_bytes(gzip.compress(json.dumps(d,sort_keys=True,separators=(',',':')).encode(),mtime=0) if gz else json.dumps(d,sort_keys=True,separators=(',',':')).encode())
    def recipe_phase(d):edit_json(d/'CLIFFORD-RECIPES.json',lambda r:next(x for x in r['warps'] if x['sign']>0 and x['old']!=x['new'])['left'].__setitem__('phase',(next(x for x in r['warps'] if x['sign']>0 and x['old']!=x['new'])['left']['phase']+1)%4))
    def recipe_drop_inverse(d):edit_json(d/'CLIFFORD-RECIPES.json',lambda r:r['warps'].pop(next(i for i,x in enumerate(r['warps']) if x['sign']<0)))
    def recipe_swap_G(d):edit_json(d/'CLIFFORD-RECIPES.json',lambda r:next(x for x in r['warps'] if x['sign']>0).__setitem__('G_columns',next(x for x in r['warps'] if x['sign']>0)['G_columns'][::-1]))
    def prog_drop_warp(d):edit_json(d/'LOCAL-PROGRAMS.json.gz',lambda p:p['forward'].pop(next(i for i,e in enumerate(p['forward']) if e[0]=='warp' and e[2]<0 and i>len(p['forward'])//2)),gz=True)
    def prog_wrong_G(d):edit_json(d/'CANONICAL-WORD.json.gz',lambda c:c['warps'][0].__setitem__('G_columns',c['warps'][0]['G_columns'][::-1]),gz=True)
    file_tamper('recipe_phase_tampered','bw_check_recipes.py',None,recipe_phase)
    file_tamper('recipe_inverse_missing','bw_check_recipes.py',None,recipe_drop_inverse)
    file_tamper('recipe_G_tampered','bw_check_recipes.py',None,recipe_swap_G)
    file_tamper('program_missing_inverse_warp','bw_audit_local.py',None,prog_drop_warp)
    file_tamper('word_G_reversed','bw_audit_local.py',None,prog_wrong_G)
(work/'TAMPER-RESULTS.json').write_text(json.dumps(dict(status='PASS_ALL_TAMPERS_REJECTED',tampers=results,seconds=time.monotonic()-t0),indent=1)+'\n')
print('PASS all',len(results),'tampers rejected in',round(time.monotonic()-t0,1),'s')
