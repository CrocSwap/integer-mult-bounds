"""Replay the #7314 public helper entrance exclusion."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
ENGINES=HERE/'engines'


def unique(pairs):
    obj=dict(pairs)
    if len(obj)!=len(pairs):
        raise ValueError('duplicate JSON key')
    return obj


def load(raw):
    return json.loads(raw,object_pairs_hook=unique)


def authenticate(scratch):
    pins=load((HERE/'LOCAL-PINS.json').read_bytes())
    for name,digest in pins.items():
        rel=PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or rel.as_posix()!=name:
            raise ValueError(f'invalid dependency path {name}')
        assert sha256((HERE/name).read_bytes()).hexdigest()==digest, ('changed input',name)
    for source in ('inputs','admission'):
        shutil.copytree(HERE/source,scratch/source)
    provenance=load((HERE/'PROVENANCE.json').read_bytes())['files']
    assert len(provenance)==5
    for name,ref in provenance.items():
        assert name in pins
        raw=(HERE/name).read_bytes()
        if ref['uncompress']:
            raw=gzip.decompress(raw)
            (scratch/name).with_suffix('').write_bytes(raw)
        assert sha256(raw).hexdigest()==ref['sha256'], name
        assert sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==ref['git_blob'], name
    anchor=load((scratch/'admission/ANCHORED.json').read_bytes())
    for ref in anchor['evidence']:
        rel=PurePosixPath(ref['path'])
        assert len(rel.parts)==1 and not rel.is_absolute() and '..' not in rel.parts
        assert pins[f'admission/{rel.as_posix()}']==ref['sha256']


def run(engine,*args,seconds=20,check=True):
    argv=[sys.executable,'-I','-B',str(ENGINES/engine),*map(str,args)]
    return subprocess.run(argv,check=check,capture_output=True,timeout=seconds)


def check_price(price):
    p,t=(Counter({int(r):n for r,n in price[key].items()}) for key in ('paid','targets'))
    assert (sum(p.values()),sum(t.values()))==(110536,22461) and price['copies']==17

    def mass(hist):
        return sum(r*n for r,n in hist.items())

    assert mass(t)-mass(p)==1424
    for key,row in price['rank_prices'].items():
        rank=int(key)
        paid=p.copy()
        target=t.copy()
        paid[1]-=17
        target[rank]-=17
        target[rank-1]+=17
        assert min(paid.values())>=0 and min(target.values())>=0
        assert sum(paid.values())==110519 and sum(target.values())==22461
        assert (mass(p)-mass(paid),mass(t)-mass(target))==(17,17)
        assert mass(target)-mass(paid)==1424
        net=target.copy()
        net.subtract(paid)
        net.subtract(t)
        net.update(p)
        assert {str(r):n for r,n in net.items() if n}==row['signed_net_delta']
        assert 0<Fraction(row['margin'][0]) and Fraction(row['credit'][1])<1
        assert Fraction(price['old_margin'][1])+Fraction(row['credit'][1])-1<0


def replay(scratch,emit):
    authenticate(scratch)
    expected=load((HERE/'receipts/SHA256.json').read_bytes())
    generated={}

    def record(name,raw,path=None):
        assert sha256(raw).hexdigest()==expected[name], name
        generated[name]=raw
        if path is not None:
            path.write_bytes(raw)
        return load(raw)

    price=scratch/'PRICE.json'
    quoted=record('PRICE.json',run('price.py',scratch).stdout,price)
    check_price(quoted)
    price_sha=expected['PRICE.json']
    forward=record('CONTACT.json',run('contact.py',scratch,'--price-sha',price_sha).stdout,
                   scratch/'CONTACT.json')
    assert forward['events']==76461 and not forward['unvisited_roles'] and not forward['survivors']

    (scratch/'independent').mkdir()
    reverse=record('REVERSE.json',
                   run('reverse_entrance.py',scratch/'inputs','--price',price,'--price-sha',price_sha,
                       '--seconds',20).stdout,scratch/'independent/RESULT.json')
    assert reverse['complete'] and reverse['visited_helpers']==1101 and not reverse['survivors']
    compare=record('COMPARE.json',run('compare.py',scratch).stdout)
    assert compare['roles_compared']==1101 and compare['unresolved']==0 and compare['support_saving_upper']==0
    assert not compare['proper_first_moves_any_positive_rank']
    assert Counter(r['paid_rank'] for r in compare['all_nonexcluded_first_moves'])=={1:6,3:2,4:1,5:1}
    assert all(r['first_dest']==r['end'] and r['residual_rank']==0 for r in compare['all_nonexcluded_first_moves'])

    # Mutations run only against disposable copies.
    stale=run('reverse_entrance.py',scratch/'inputs','--price',price,'--price-sha','0'*64,
              '--seconds',10,check=False)
    assert stale.returncode==1 and b'changed price receipt' in stale.stderr and not stale.stdout
    caller=scratch/'inputs/7113/CALLER.json'
    caller.write_bytes(caller.read_bytes()+b'\n')
    changed=run('price.py',scratch,check=False)
    assert changed.returncode==1 and b'Changed input inputs/7113/CALLER.json' in changed.stderr
    assert not changed.stdout

    assert generated.keys()==expected.keys()
    if emit is not None:
        emit.mkdir()
        for name,raw in generated.items():
            (emit/name).write_bytes(raw)
    print('PASS_P104_HELPER_ENTRANCE_BOUND helpers=1101 first_moves=10 proper=0 '
          'admissible=0 unresolved=0 saving_upper=0 kappa_change=0')


if __name__=='__main__':
    assert __debug__, 'assertions are required'
    assert sys.version_info[:2]==(3,12), 'Python 3.12 required'
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    with TemporaryDirectory(prefix='p104-helper-entrance-') as tmp:
        replay(Path(tmp),args.out)
