"""Relocation, source drift and actual receipt corruption controls."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    original=json.loads((HERE/'RESULT.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='z4-error-') as temp:
        root=Path(temp)
        package=root/'research/z4-persistent-error-envelope'
        package.mkdir(parents=True)
        for name in ['verify.py','SOURCES.json','RESULT.json']:
            shutil.copy2(HERE/name,package/name)
        sources=json.loads((HERE/'SOURCES.json').read_text())
        for row in sources['files']:
            if row['usage']=='input':
                target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/row['path'],target)
        def run(expected):
            proc=subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py')],capture_output=True,text=True,timeout=30)
            if (proc.returncode==0)!=expected:raise ValueError(proc.stdout+proc.stderr)
        run(True)
        variants=[]
        obj=copy.deepcopy(original);obj['words']['joint']['fractional_guard_bits']-=1;variants.append(obj)
        obj=copy.deepcopy(original);peak=obj['words']['joint']['weighted_all_cuts'];peak['coefficients']=peak['coefficients'].rsplit(';',1)[0];variants.append(obj)
        obj=copy.deepcopy(original);obj['words'].pop('joint_inverse');variants.append(obj)
        for obj in variants:
            (package/'RESULT.json').write_text(json.dumps(obj),encoding='utf-8');run(False)
        (package/'RESULT.json').write_text(json.dumps(original),encoding='utf-8')
        emitter=root/'research/z4-persistent-pair-seed57/inputs/PR1391-verify.py'
        emitter.write_bytes(emitter.read_bytes()+b'\n# altered source\n');run(False)
    print('PASS_Z4_ERROR_PACKAGE relocated=1 corruptions_rejected=4')


if __name__=='__main__':main()
