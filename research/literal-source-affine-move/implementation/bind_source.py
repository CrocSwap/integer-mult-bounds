"""Authenticate actual MOVE24476 and certify its complete exact operator."""
from pathlib import Path
import atexit,copy,gzip,json,subprocess,sys,tempfile
from hashlib import sha256
HERE=Path(__file__).resolve().parent
_cache=tempfile.TemporaryDirectory(prefix='actual-affine-bind-');atexit.register(_cache.cleanup)
sys.dont_write_bytecode=True;sys.pycache_prefix=str(Path(_cache.name)/'absent')
import move as C


def need(ok,label):
    if not ok:raise ValueError(label)


def verify(repo=None,recompile=False):
    source=C.SOURCE;recipe=source['recipe']
    need(source['event_index']==24476 and source['event']==['MOVE',727,3,470,False],'actual event24476')
    need(source['frames']=={'3':[],'470':[75,137,265]},'complete source frames')
    need(recipe['rank']==3 and recipe['right']['offset']==5 and recipe['right']['phase']==2,'new actual target')
    if repo is not None:
        pin=C.manifest['event_archive'];raw=subprocess.check_output(['git','show',pin['commit']+':'+pin['path']],cwd=repo)
        need(len(raw)==pin['bytes'] and sha256(raw).hexdigest()==pin['sha256'],'whole selected archive')
        word=json.loads(gzip.decompress(raw))
        need(sha256(json.dumps(word,separators=(',',':'),sort_keys=True).encode()).hexdigest()==pin['canonical_sha256'],'canonical selected word')
        event=word['program'][24476]
        need(event==source['event'] and {str(i):word['frames'][i] for i in event[2:4]}==source['frames'],'current extraction')
    if recompile:
        if not __debug__:raise ValueError('canonical compiler rebind requires normal mode')
        compiler=C.load('actual_affine_canonical_compiler',HERE/'engines/reference/rank2/reference/source/clifford_exact.py')
        fresh,_=compiler.lower_child(compiler.canonical_frame(9,()).adjoint().then(compiler.canonical_frame(9,(75,137,265))))
        need(json.loads(json.dumps(fresh))==recipe,'canonical exact lowering')
    exact=C.load('actual_affine_independent',HERE/'engines/reference/rank2/reference/source/native_verify.py')
    target=exact.adjoint(exact.frame((),9))+exact.frame((75,137,265),9)
    exact.equal(exact.recipe(recipe),target,'actual source complete matrix and phase')
    counts={}
    for side in ('right','left'):
        rec=recipe[side];word=C.P.LINEAR.cnot_word(tuple(rec['matrix_rows']))
        for x in range(512):
            y=x
            for t,c in word:y^=((y>>c)&1)<<t
            wanted=sum(((row&x).bit_count()&1)<<i for i,row in enumerate(rec['matrix_rows']))
            need(y==wanted,'generated fixed binary matrix')
        mon=exact.monomial(rec)
        exact.equal((('phase',rec['phase']),)+mon[:-1],mon,'scalar phase moved before G/X')
        counts[side]={'CNOTs':len(word),'offset':rec['offset'],'phase':rec['phase']}
    controls=[]
    for label,key,change in (('wrong_phase','phase',lambda x:(x+1)%4),('wrong_offset','offset',lambda x:x^4)):
        wrong=copy.deepcopy(recipe);wrong['right'][key]=change(wrong['right'][key])
        try:exact.equal(exact.recipe(wrong),target,label)
        except ValueError:controls.append(label)
        else:raise ValueError('source mutant survived: '+label)
    try:exact.equal(exact.recipe(recipe),exact.adjoint(target),'inverse orientation')
    except ValueError:controls.append('inverse_orientation')
    else:raise ValueError('inverse source orientation survived')
    return {'marker':'PASS_ACTUAL_AFFINE_MOVE_SOURCE','event_index':24476,'owner':727,'private':False,
            'private_flag_is_not_inversion':True,'rank':3,'factors':counts,'matrix_columns':1024,
            'full_archive_reextracted':repo is not None,'canonical_recipe_recompiled':recompile,'controls':controls}


if __name__=='__main__':
    repo=sys.argv[sys.argv.index('--source-repo')+1] if '--source-repo' in sys.argv else None
    result=verify(repo,'--recompile' in sys.argv)
    if '--write' in sys.argv:(HERE/'SOURCE-BINDING.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
