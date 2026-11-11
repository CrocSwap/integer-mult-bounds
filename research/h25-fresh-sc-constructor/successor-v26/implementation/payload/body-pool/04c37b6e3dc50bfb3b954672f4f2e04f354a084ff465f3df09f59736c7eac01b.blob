"""Fresh unchanged finite controls in normal or optimized interpreter mode."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types
ROOT=Path(__file__).resolve().parent
pins=json.loads((ROOT/'CODE-SOURCES.json').read_text())['files']
for name in ('verify.py','archive_support.py'):
    if sha256((ROOT/name).read_bytes()).hexdigest()!=pins[name]:raise ValueError('finite wrapper source pin: '+name)
S=types.ModuleType('_gf2_finite_support');S.__file__=str(ROOT/'archive_support.py')
exec(compile((ROOT/'archive_support.py').read_bytes(),S.__file__,'exec'),S.__dict__)


def main():
    import os
    import runpy
    import shutil
    import tempfile
    S.need(len(sys.argv)==1,'no alternate finite workload')
    S.authenticate();temporary=Path(tempfile.mkdtemp(prefix='gf2-full-finite-'))
    old_argv=sys.argv[:];old_path=sys.path[:];old_cache=sys.pycache_prefix;old_dont=sys.dont_write_bytecode
    prior_tmp=os.environ.get('TMPDIR')
    try:
        sys.pycache_prefix=str(temporary/'bytecode');sys.dont_write_bytecode=True
        os.environ['TMPDIR']=str(temporary)
        sys.path.insert(0,str(ROOT/'engine'))
        driver=ROOT/'engine/compare_side_verifier.py'
        sys.argv=[str(driver),'--mode','finite','--output',str(temporary/'evidence')]
        runpy.run_path(str(driver),run_name='__main__')
        receipt=json.loads((temporary/'evidence/receipt.json').read_text())
        S.need(receipt['status']=='FINITE_PASS' and receipt['mode']=='finite' and receipt['environment']['optimization']==sys.flags.optimize,'complete unchanged finite suite in requested interpreter mode')
        S.authenticate()
    except BaseException as error:
        error.add_note('Failed finite build/control evidence retained at '+str(temporary))
        raise
    else:shutil.rmtree(temporary)
    finally:
        sys.argv=old_argv;sys.path[:]=old_path;sys.pycache_prefix=old_cache;sys.dont_write_bytecode=old_dont
        if prior_tmp is None:os.environ.pop('TMPDIR',None)
        else:os.environ['TMPDIR']=prior_tmp
    print(json.dumps(dict(status='PASS_GF2_FULL_FINITE_CONTROLS',optimization=sys.flags.optimize,complete_cli_not_run=True)))


if __name__=='__main__':main()
