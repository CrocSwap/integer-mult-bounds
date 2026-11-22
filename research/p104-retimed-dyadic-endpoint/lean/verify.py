#!/usr/bin/env python3
"""Replay the Lean 4 core endpoint, axiom audit, olean import and corruptions."""
import argparse, hashlib, os, pathlib, re, subprocess, tempfile, time

HERE=pathlib.Path(__file__).resolve().parent
EXPECTED='2d2ff39d4fdf9d4fb4e60e842ff2ceb62e197e1339d01c924610f20e25ae0f44'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('lean',help='path to a Lean 4 binary, e.g. /path/to/bin/lean')
    args=p.parse_args()
    lean=str(pathlib.Path(args.lean).resolve())
    data=(HERE/'Endpoint.lean').read_bytes()
    assert hashlib.sha256(data).hexdigest()==EXPECTED
    source=data.decode('utf-8')
    assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',source)
    names=re.findall(r'^#print axioms (\w+)\s*$',source,re.M)
    assert len(names)==31 and len(names)==len(set(names))
    version=subprocess.check_output([lean,'--version'],text=True).strip()
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='kernel-replay-') as folder:
        work=pathlib.Path(folder)
        (work/'Endpoint.lean').write_bytes(data)
        run=subprocess.run([lean,'--trust=0','-o','Endpoint.olean','Endpoint.lean'],
                           cwd=work,text=True,capture_output=True)
        assert run.returncode==0,(run.returncode,run.stdout,run.stderr)
        lines=run.stdout.splitlines()
        assert len(lines)==len(names),(len(lines),len(names))
        assert all("'Endpoint461."+name+"' does not depend on any axioms" in lines
                   for name in names)
        assert 'sorryAx' not in run.stdout+run.stderr
        (work/'Consumer.lean').write_text((HERE/'Consumer.lean').read_text())
        env=os.environ.copy();env['LEAN_PATH']=str(work)
        consumer=subprocess.run([lean,'--trust=0','Consumer.lean'],cwd=work,env=env,
                                text=True,capture_output=True)
        assert consumer.returncode==0,(consumer.stdout,consumer.stderr)
        assert len(consumer.stdout.splitlines())==7
        assert all('does not depend on any axioms' in line for line in consumer.stdout.splitlines())
        checker=pathlib.Path(lean).with_name('leanchecker')
        separate='not available in this toolchain'
        if checker.exists():
            env['PATH']=str(checker.parent)+os.pathsep+env.get('PATH','')
            replay=subprocess.run([str(checker),'-v','Endpoint'],cwd=work,env=env,
                                  text=True,capture_output=True)
            assert replay.returncode==0 and 'replaying Endpoint' in replay.stdout+replay.stderr
            separate='passed'
        changes=[('DamagedC','def C : Nat := 287039844436133239',
                  'def C : Nat := 287039844436133238'),
                 ('NextTick','def K  : Nat := 3890115286594461000',
                  'def K  : Nat := 3890115286594462000')]
        for name,before,after in changes:
            assert source.count(before)==1
            (work/f'{name}.lean').write_text(source.replace(before,after))
            bad=subprocess.run([lean,'--trust=0',f'{name}.lean'],cwd=work,text=True,capture_output=True)
            assert bad.returncode!=0 and re.search(
                r"error:\s*tactic\s+['`]decide['`]\s+proved that the proposition",
                bad.stdout,re.I)
    print('LEAN_VERSION',version)
    print('SOURCE_SHA256',EXPECTED)
    print('TRUST_ZERO_AXIOM_FREE_DECLARATIONS',len(names))
    print('TRUST_ZERO_OLEAN_IMPORT_AXIOM_FREE',7)
    print('SEPARATE_LEANCHECKER',separate)
    print('CORRUPTION_REJECTIONS','damaged_c','next_kappa_tick')
    print('OBSERVED_ELAPSED_SECONDS',round(time.monotonic()-start,3))
    print('PASS_ENDPOINT461_LEAN_CORE')

if __name__=='__main__':main()
