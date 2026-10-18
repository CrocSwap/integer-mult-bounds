"""Behavioral evidence, regeneration, relocation and rejection checks."""
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

H = Path(__file__).resolve().parent
ROOT = H.parents[1]


def need(value, label):
    if not value:
        raise ValueError(label)


def call(script, args=(), ok=True, fragment='PASS_P104_OWNED_COLLECTOR_DUAL'):
    result = subprocess.run([sys.executable,'-I','-O','-B',str(script),*map(str,args)],
                            capture_output=True,text=True,cwd=script.parent,timeout=180)
    output = result.stdout + result.stderr
    need((result.returncode == 0) == ok and fragment in output, 'subprocess behavior '+output[-2500:])


def main():
    with tempfile.TemporaryDirectory(prefix='p104-collector-') as temporary:
        root = Path(temporary)
        package = root/'export/research'/H.name
        shutil.copytree(H,package)
        for name in json.loads((H/'VERIFY.json').read_text())['inputs']:
            target = root/'export'/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,target)
        regenerated = root/'regenerated.json'
        call(H/'build.py',['--out',regenerated],fragment='')
        need(json.loads(regenerated.read_text()) == json.loads((H/'DUAL.json').read_text()), 'complete regeneration')
        call(H/'build.py',['--out',regenerated],False,'FileExistsError')
        clean_regenerated = root/'clean-regenerated.json'
        call(H/'build.py',['--clean','--out',clean_regenerated],fragment='')
        need(json.loads(clean_regenerated.read_text()) == json.loads((H/'CLEAN-DUAL.json').read_text()), 'complete clean regeneration')
        files = list((root/'export').rglob('*'))
        original = {p:stat.S_IMODE(p.stat().st_mode) for p in files if p.is_file()}
        try:
            for path, mode in original.items():
                path.chmod(mode & ~stat.S_IWRITE)
            before = {str(p.relative_to(root)):p.read_bytes() for p in original}
            call(package/'verify.py')
            need(before == {str(p.relative_to(root)):p.read_bytes() for p in original}, 'read-only export unchanged')
            need(not any(p.name=='__pycache__' for p in (root/'export').rglob('*')), 'no bytecode in export')
        finally:
            for path, mode in original.items():
                path.chmod(mode)
        receipt = package/'RESULT.json'
        data = receipt.read_bytes()
        mutant = json.loads(data)
        mutant['boundary_inputs'] = 358.0
        receipt.write_text(json.dumps(mutant))
        call(package/'verify.py',ok=False,fragment='committed receipt mismatch')
        receipt.write_bytes(data)
        evidence = package/'DUAL.json'
        raw = evidence.read_bytes()
        evidence.unlink()
        call(package/'verify.py',ok=False,fragment='FileNotFoundError')
        need(not evidence.exists(), 'missing evidence not regenerated')
        evidence.write_bytes(raw)
        mutant = json.loads(raw)
        mutant['program'][0][2]='1'
        evidence.write_text(json.dumps(mutant))
        call(package/'verify.py',ok=False,fragment='input sign pass')
        evidence.write_bytes(raw)
        predecessor = package/'inputs/CIRCUIT.json'
        clean_evidence=package/'CLEAN-DUAL.json'
        raw_clean=clean_evidence.read_bytes()
        mutant=json.loads(raw_clean)
        i=next(i for i,e in enumerate(mutant['program']) if e[0]=='erase')
        mutant['program'][i-1][3]='0'
        clean_evidence.write_text(json.dumps(mutant))
        call(package/'verify.py',ok=False,fragment='complete clean-return word binding')
        clean_evidence.write_bytes(raw_clean)
        old = predecessor.read_bytes()
        predecessor.write_bytes(old+b'\n')
        call(package/'verify.py',ok=False,fragment='predecessor SHA256')
        predecessor.write_bytes(old)
        source = root/'export/research/p104-native-channel/inputs/P104-FIXTURE.json'
        old = source.read_bytes()
        source.write_bytes(old+b'\n')
        call(package/'verify.py',ok=False,fragment='input SHA256')
        source.write_bytes(old)
        executable = root/'export/research/p104-native-channel/vendor/native_verify.py'
        old = executable.read_bytes()
        executable.write_bytes(old+b'\nraise ValueError("UNAUTHENTICATED_EXECUTION")\n')
        call(package/'verify.py',ok=False,fragment='input SHA256')
        executable.write_bytes(old)
        output = root/'already-exists.json'
        output.write_text('retained')
        call(package/'verify.py',['--out',output],False,'FileExistsError')
        need(output.read_text()=='retained', 'output not overwritten')
    print('PASS_P104_COLLECTOR_BEHAVIOR regeneration readonly_export missing_evidence source_drift typed_receipt exclusive_output')


if __name__ == '__main__':
    main()
