"""Derive fresh scoped proof sources; keep predecessor files immutable.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OLD=ROOT/'research/kappa-round3-warp-lean-20261022'

def sub(text,old,new,n=1):
    assert text.count(old)==n,(old,text.count(old),n)
    return text.replace(old,new)

def save(name,text):
    (HERE/name).write_text(text,encoding='utf-8',newline='\n')

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def main():
    data=json.loads((HERE/'ARITHMETIC.json').read_text())
    assert data['kappa']=='15108879/5000000000'
    assert data['strictification']['tested']=='302177581/100000000000'
    assert data['compiler']['H']==38569300000000000
    sources={}
    def source(name):
        path=OLD/name;sources[path.relative_to(ROOT).as_posix()]=sha256(path.read_bytes()).hexdigest()
        return path.read_text(encoding='utf-8')
    text=source('numerical_generate.py')
    text=sub(text,'Q(302177, 100000000)','Q(302177581, 100000000000)')
    text=sub(text,"ROOT/'research/kappa-round3-warp-20261022/ARITHMETIC.json'","HERE/'ARITHMETIC.json'")
    text=sub(text,'Q(1,10**9)','Q(1,10**11)')
    text=sub(text,'1 / 1000000000 : ℝ','1 / 100000000000 : ℝ')
    text=sub(text,"HERE/'NumericalMoments.lean'","HERE/'TightenedNumerical.lean'")
    save('numerical_generate.py',text)
    text=source('generate_arithmetic.py')
    for old,new in [
        ("ROOT/'research/kappa-round3-warp-20261022/ARITHMETIC.json'","HERE/'ARITHMETIC.json'"),
        ('kappa = 9443/3125000','kappa = 15108879/5000000000'),
        ('(37769/12500000 : ℚ) < kappa','(9443/3125000 : ℚ) < kappa'),
        ('(1/700000000 : ℚ)','(1/700000000000 : ℚ)'),
        ('1024*(1/1000000000)','1024*(1/100000000000)'),
        ('700000000*44836 = (31385200000000:ℕ)','700000000000*55099 = (38569300000000000:ℕ)'),
        ('((700000000:ℕ)*44836+1)^1000 < 2^44836','((700000000000:ℕ)*55099+1)^1000 < 2^55099'),
        ('((700000000:ℕ)*44835+1)^1000 < 2^44835','((700000000000:ℕ)*55098+1)^1000 < 2^55098'),
        ("HERE/'ArithmeticCertificate.lean'","HERE/'TightenedArithmetic.lean'"),
    ]:text=sub(text,old,new)
    save('generate_arithmetic.py',text)
    text=source('CompilerCapacity.lean')
    text=sub(text,'302177 / 100000000','302177581 / 100000000000')
    save('TightenedCapacity.lean',text)
    text=source('KappaWarpVerification.lean')
    for old,new in [
        ('9443 / 3125000','15108879 / 5000000000'),
        ('37769 / 12500000','9443 / 3125000'),
        ('302177 / 100000000','302177581 / 100000000000'),
        ('99697823 / 100000000','99697822419 / 100000000000'),
        ('119697823 / 100000000','119697822419 / 100000000000'),
        ('1 / 1000000000 : ℝ','1 / 100000000000 : ℝ'),
        ('700000000 : ℕ','700000000000 : ℕ'),
        ('44836','55099'),
    ]:
        assert old in text,old
        text=text.replace(old,new)
    text=text.replace('import ArithmeticCertificate','import TightenedArithmetic')
    text=text.replace('import CompilerCapacity','import TightenedCapacity')
    text=text.replace('import NumericalMoments','import TightenedNumerical')
    text=text.replace('KappaWarpVerification','KappaTightenedVerification')
    save('TightenedVerification.lean',text)
    for name in ['numerical_generate.py','generate_arithmetic.py']:
        with contextlib.redirect_stdout(io.StringIO()) as out:load(HERE/name,'tightened_'+name[:-3]).main()
        save(name[:-3]+'-output.json' if name.startswith('numerical') else 'arithmetic-generation.log',out.getvalue())
        print(out.getvalue().encode('ascii','backslashreplace').decode(),flush=True)
    save('PROOF-SOURCES.json',json.dumps(dict(status='GENERATED_WITNESSES_PENDING_LEAN',predecessor_sha256=sources,
        prepared_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.lean')},
        preparation_script_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
