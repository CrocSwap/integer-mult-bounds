"""Relocated optimized execution and source/typed-receipt fail-closed controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def run(argv,success,marker):
    output=subprocess.run(argv,capture_output=True,text=True,timeout=180)
    if (output.returncode==0)!=success or marker not in output.stdout+output.stderr:
        raise ValueError(repr((argv,output.returncode,output.stdout,output.stderr)))


def main():
    with tempfile.TemporaryDirectory(prefix='selected-child-') as temporary:
        root=Path(temporary)
        package=root/'research/selected-child-stream-return'
        package.parent.mkdir(parents=True)
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']=='input':
                dest=root/row['path']
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],dest)
        command=[sys.executable,'-I','-O','-B',str(package/'verify.py')]
        run(command,True,'PASS_SELECTED_CHILD_STREAM_RETURN')
        receipt=package/'RESULT.json'
        value=json.loads(receipt.read_text())
        value['exact_inverse']=1  # bool/int equality is not accepted as a typed receipt.
        receipt.write_text(json.dumps(value))
        run(command,False,'receipt mismatch')
        receipt.write_bytes((HERE/'RESULT.json').read_bytes())
        source=package/'vendor/arithmetic.py'
        source.write_bytes(source.read_bytes()+b'\n')
        run(command,False,'source hash vendor/arithmetic.py')
    print('PASS_SELECTED_CHILD_RETURN_CLI relocated_optimized=1 rejected=2')


if __name__=='__main__':
    main()
