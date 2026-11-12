"""Reproduce the two exact P104 owned reconstruction exclusions."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1,sha256
from json import dumps,loads
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import sys

ROOT=Path(__file__).resolve().parent


def unique(items):
    out=dict(items)
    if len(out)!=len(items):
        raise ValueError('duplicate JSON key')
    return out


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def source(name):
    path=Path(name)
    if path.is_absolute() or '..' in path.parts or path.as_posix()!=name:
        raise ValueError('invalid package-relative path '+name)
    return (ROOT/path).read_bytes()


def load_inputs():
    pins=decode(source('LOCAL-PINS.json'))
    for name,expected in pins.items():
        if digest(source(name))!=expected:
            raise ValueError('changed package dependency '+name)
    p=decode(source('PROVENANCE.json'))
    for name,entry in p['files'].items():
        raw=source(name)
        assert digest(raw)==entry['sha256']==pins[name]
        assert sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==entry['git_blob']
    old=decompress(source('inputs/R92-PRICE.json.gz'))
    assert digest(old)==decode(source('inputs/PR7362-SHA256.json'))['R92-PRICE.json']
    a=decode(source('inputs/ADMITTED.json'))
    assert a['head']=='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert a['kappa']=='0.00364665195644'
    return old


def call(script,*args,expect_success=True):
    p=run([sys.executable,'-I','-B',str(script),*args],capture_output=True,timeout=40)
    if expect_success and p.returncode:
        sys.stderr.write(p.stderr.decode(errors='replace'))
        p.check_returncode()
    return p


def write(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)


def replay(root,out):
    old=load_inputs()
    expected=decode(source('receipts/SHA256.json'))
    outputs={}
    def record(name,script,*args):
        raw=call(script,*args).stdout
        assert digest(raw)==expected[name],('changed deterministic receipt',name)
        outputs[name]=raw
        return decode(raw)

    r137,r138=root/'r137',root/'r138'
    both=('7334-WORD.json.gz','aggregate.py','donor_span.py','pricing.py')
    for d in (r137,r138):
        for name in both:
            write(d/'inputs'/name,source('inputs/'+name))
        write(d/'inputs/R92-PRICE.json',old)
    for name in ('R137-PLAN.md','R80-OWNED.json'):
        write(r137/'inputs'/name,source('inputs/'+name))
    write(r137/'lead/first_use.py',source('engines/first_use.py'))
    write(r137/'verify_impulses.py',source('engines/verify_impulses.py'))
    write(r138/'lead/write_prefix.py',source('engines/write_prefix.py'))
    write(r138/'verify_prefix.py',source('engines/verify_prefix.py'))
    write(r138/'inputs/grouped_impulses.py',source('engines/verify_impulses.py'))

    p1=record('R137-PRICE.json',r137/'lead/first_use.py','--price-only')
    m1=record('R137-LEAD.json',r137/'lead/first_use.py')
    for d in (r137,r138):
        write(d/'inputs/R137-PRICE.json',outputs['R137-PRICE.json'])
    write(r137/'inputs/R137-LEAD-RESULT.json',outputs['R137-LEAD.json'])
    write(r138/'inputs/R137-RESULT.json',outputs['R137-LEAD.json'])
    i1=record('R137-INDEPENDENT.json',r137/'verify_impulses.py')

    p2=record('R138-PRICE.json',r138/'lead/write_prefix.py','--price-only')
    m2=record('R138-LEAD.json',r138/'lead/write_prefix.py')
    write(r138/'inputs/R138-PRICE.json',outputs['R138-PRICE.json'])
    write(r138/'inputs/R138-LEAD-RESULT.json',outputs['R138-LEAD.json'])
    i2=record('R138-INDEPENDENT.json',r138/'verify_prefix.py',
        '--price-sha',expected['R138-PRICE.json'],'--lead-sha',expected['R138-LEAD.json'])

    assert p1['stock']==i1['paid_owned_ranks']=={'1':20,'2':9,'3':2,'4':13,'5':2,'6':1}
    assert p2['rank_counts']=={'1':3,'2':1,'3':1,'4':4,'5':1,'6':1}
    assert m1['counts']=={'outside donor span':47} and m2['counts']=={'outside donor span':11}
    assert not (m1['unvisited'] or m2['unvisited'] or i1['unresolved'] or i2['unresolved'])
    assert i1['progress']['events_visited']==i2['progress']['events_visited']==76466
    assert i1['bank_role_checks']==442 and sum(r['live_donor_checks'] for r in i2['cases'])==115
    assert i1['grouped_impulses']==24 and i2['grouped_impulses']==9
    assert len(i1['cases'])==47 and len(i2['cases'])==11
    assert set(outputs)==set(expected)

    def rejected(path,script,*args):
        raw=path.read_bytes()
        path.write_bytes(raw+b' ')
        check=call(script,*args,expect_success=False)
        assert check.returncode==1 and b'changed dependency' in check.stderr
        path.write_bytes(raw)

    rejected(r137/'inputs/R137-LEAD-RESULT.json',r137/'verify_impulses.py')
    rejected(r138/'inputs/R137-RESULT.json',r138/'verify_prefix.py','--controls-only')
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            write(out/name,raw)
    print('PASS_P104_OWNED_FIRST_USE_PREFIX_BOUND immediate=47 delayed=11 unresolved=0')


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=='__main__':
    main()
