"""One complete C correctness replay; never a hosted performance-factor claim."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types
ROOT=Path(__file__).resolve().parent
pins=json.loads((ROOT/'CODE-SOURCES.json').read_text())['files']
for name in ('verify_full.py','archive_support.py','replay.py'):
    if sha256((ROOT/name).read_bytes()).hexdigest()!=pins[name]:raise ValueError('full correctness wrapper pin: '+name)
S=types.ModuleType('_gf2_verify_full_support');S.__file__=str(ROOT/'archive_support.py')
exec(compile((ROOT/'archive_support.py').read_bytes(),S.__file__,'exec'),S.__dict__)


def main():
    import shutil
    import tempfile
    S.need(len(sys.argv)==1 and sys.flags.optimize==0,'one full correctness run with original assertions')
    S.authenticate();temporary=Path(tempfile.mkdtemp(prefix='gf2-full-correctness-'))
    replay=S.source_module('_gf2_verify_full_replay',ROOT/'replay.py')
    try:
        result=replay.run('C',temporary/'run',timeout=150)
        S.need(result['scientific']['science']==json.loads((ROOT/'anchor.json').read_text())['science'],'full exact anchor equality')
        S.authenticate()
        # Only fresh private clone directories become writable, after all checks.
        # Read-only input/package paths are never changed.
        for directory in temporary.rglob('*'):
            if directory.is_dir() and not directory.is_symlink():directory.chmod(0o755)
        shutil.rmtree(temporary)
    except BaseException as error:
        error.add_note('Full correctness evidence retained at '+str(temporary))
        raise
    print(json.dumps(dict(status='PASS_GF2_FULL_C_CORRECTNESS',hosted_performance_factor_claim=False,fixed_benchmark_sample=False,inner_timeout_seconds=150)))


if __name__=='__main__':main()
