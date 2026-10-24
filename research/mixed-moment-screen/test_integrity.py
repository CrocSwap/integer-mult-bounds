"""Exercise the real public verifier in a source-only temporary export."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent

def run(root):
    return subprocess.run([sys.executable,'-I','-O','-B',str(root/'verify.py')],
                          cwd=root,capture_output=True,text=True)

def main():
    with tempfile.TemporaryDirectory(prefix='mixed-screen-integrity-') as name:
        root=Path(name).resolve()
        for source in HERE.iterdir():
            if source.is_file(): shutil.copyfile(source,root/source.name)
        good=run(root)
        if good.returncode or 'PASS_SCOPED_MIXED_MOMENT_PROBE' not in good.stdout:
            raise ValueError('source-only optimized replay failed: '+good.stderr)
        for name,message in [('INPUT.json','frozen PR4470 source receipt hash'),
                             ('upstream_moment.py','frozen upstream moment engine hash'),
                             ('RESULT.json','complete deterministic receipt equality')]:
            path=root/name
            saved=path.read_bytes()
            if name=='RESULT.json':
                data=json.loads(saved)
                data['cases'][0]['full_positive_exp']['decision']='reject'
                path.write_text(json.dumps(data),encoding='utf-8')
            else:
                path.write_bytes(saved+b'\n')
            try:
                bad=run(root)
                if bad.returncode==0 or message not in bad.stderr:
                    raise ValueError('mutation did not reject: '+name)
            finally:
                path.write_bytes(saved)
    print('PASS_SOURCE_ONLY_OPTIMIZED_REPLAY_AND_THREE_INTEGRITY_CONTROLS')

if __name__=='__main__': main()
