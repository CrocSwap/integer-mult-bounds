"""Run the pinned predecessor qualifier with the independently admitted binary cap."""
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
from fractions import Fraction
from pathlib import Path

QUALIFY_SHA='fdf559fbe15f52c2b31f2947712a46aa6b4c93f211ea9a0b1f05b07d69664227'
INDEPENDENT_SHA='5865e19155488b80ccb1faa1ba74c2ffbc5ac22e8f22f10c5f4496ae49fc1229'
BIT_WORD='d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d'
OLD="bit_cap = Fraction(binary['ordinary_admitted'])"
NEW="bit_cap = Fraction('0.0038799074072')"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package',type=Path,required=True)
    args, rest=p.parse_known_args()
    package=args.package.resolve()
    source=package/'continuation/qualify.py'
    raw=source.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==QUALIFY_SHA
    independent=(package/'binary/INDEPENDENT.json').read_bytes()
    assert hashlib.sha256(independent).hexdigest()==INDEPENDENT_SHA
    receipt=json.loads(independent)
    assert receipt['word_sha256']==BIT_WORD and Fraction(receipt['ordinary_admitted'])==Fraction('0.0038799074072')
    producer=json.loads((package/'binary/FINITE.json').read_bytes())
    assert producer['word_sha256']==BIT_WORD and Fraction(receipt['ordinary_admitted'])<=Fraction(producer['ordinary_admitted'])
    code=raw.decode(); assert code.count(OLD)==1
    with tempfile.TemporaryDirectory(prefix='p104-capped-') as tmp:
        dest=Path(tmp)
        shutil.copyfile(package/'continuation/compiler.py',dest/'compiler.py')
        (dest/'qualify.py').write_text(code.replace(OLD,NEW))
        subprocess.run([sys.executable,'-IB',str(dest/'qualify.py'),'--package',str(package),*rest],check=True)

if __name__=='__main__': main()
