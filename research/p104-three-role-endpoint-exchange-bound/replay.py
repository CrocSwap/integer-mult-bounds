"""Reproduce the exact P104 role-1454 three-role endpoint-exchange exclusion."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1,sha256
from json import dumps,loads
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory

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


def verify_inputs():
    pins=decode(source('LOCAL-PINS.json'))
    for name,expected in pins.items():
        if digest(source(name))!=expected:
            raise ValueError('changed package dependency '+name)
    p=decode(source('PROVENANCE.json'))
    for name,entry in p['files'].items():
        raw=source(name)
        assert digest(raw)==entry['sha256']==pins[name]
        assert sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==entry['git_blob']
    out={}
    for name,entry in p['derived_inputs'].items():
        raw=decompress(source(name))
        assert digest(raw)==decode(source(entry['receipt']))[entry['key']]
        out[Path(name).stem]=raw
    a=decode(source('inputs/ADMITTED.json'))
    assert a['head']=='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert a['kappa']=='0.00364665195644'
    return out


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
    inherited=verify_inputs()
    expected=decode(source('receipts/SHA256.json'))
    outputs={}
    def record(name,script,*args):
        raw=call(script,*args).stdout
        assert digest(raw)==expected[name],('changed deterministic receipt',name)
        outputs[name]=raw
        return decode(raw)

    r148,r150=root/'r148',root/'r150'
    for stage in (r148,r150):
        write(stage/'inputs/7334-WORD.json.gz',source('inputs/7334-WORD.json.gz'))
    for key,name in (('R143-PRICE.json','PRICE.json'),('R143-GEOMETRY.json','GEOMETRY.json'),
                     ('R96-PRICE.json','R96-PRICE.json')):
        write(r148/'inputs'/name,inherited[key])
    for name in ('7334-READBACK.json','reverse_span.py'):
        write(r148/'inputs'/name,source('inputs/'+name))
    write(r148/'lead/impulse.py',source('engines/third_impulse.py'))
    write(r148/'lead/basis.py',source('engines/third_basis.py'))
    write(r150/'lead/close.py',source('engines/close.py'))

    price=record('R148-PRICE.json',r148/'lead/impulse.py','--price-only')
    write(r148/'lead/PRICE.json',outputs['R148-PRICE.json'])
    screen=record('R148-IMPULSE.json',r148/'lead/impulse.py')
    write(r148/'lead/IMPULSE.json',outputs['R148-IMPULSE.json'])
    prefix=record('R148-PREFIX.json',r148/'lead/basis.py','prefix')
    for name in ('PRICE','IMPULSE','PREFIX'):
        write(r150/'inputs'/f'{name}.json',outputs[f'R148-{name}.json'])
    keys=record('R150-KEYS.json',r150/'lead/close.py','--freeze')
    write(r150/'lead/KEYS.json',outputs['R150-KEYS.json'])
    close=record('R150-RESULT.json',r150/'lead/close.py')

    reverse=r150/'independent/three_role.py'
    reverse_out=r150/'independent/RESULT.json'
    write(reverse,source('engines/three_role.py'))
    write(r150/'inputs/word.json.gz',source('inputs/7334-WORD.json.gz'))
    write(r150/'inputs/bank_trace.py',source('inputs/bank_trace.py'))
    write(r150/'lead/GEOMETRY.json',inherited['R143-GEOMETRY.json'])
    for name in ('IMPULSE','PREFIX'):
        write(r150/'third'/f'{name}.json',outputs[f'R148-{name}.json'])
    for name in ('KEYS','RESULT'):
        write(r150/'followup'/f'{name}.json',outputs[f'R150-{name}.json'])
    call(reverse,'--root',str(r150),'--output',str(reverse_out))
    data=reverse_out.read_bytes()
    assert digest(data)==expected['INDEPENDENT.json']
    outputs['INDEPENDENT.json']=data
    independent=decode(data)

    assert price['paid_delta']=={} and price['productive_delta']=={'5':-17,'6':17,'8':17,'9':-17}
    assert screen['counts']=={'no coframe':3961,'prefix pending':16494}
    assert len(screen['unresolved'])==15
    assert prefix['counts']=={'exact_rank_exclusion':8} and len(prefix['unvisited'])==7
    assert all(r['proof']['separating_covector']=={'1251':'1','1481':'4'} for r in prefix['rows'])
    assert len(close['rows'])==len(keys['ranges'])==7 and close['raw_cuts']==478
    assert close['progress']['events']==76466 and not close['unresolved']
    assert all(r['status']=='prefix excluded' and r['first_nonzero'] is None for r in close['rows'])
    assert len(independent['rows'])==15 and not independent['unresolved']
    assert set(outputs)==set(expected)

    def rejected(path,script,*args):
        raw=path.read_bytes()
        path.write_bytes(raw+b' ')
        check=call(script,*args,expect_success=False)
        assert check.returncode==1 and b'changed' in check.stderr
        path.write_bytes(raw)

    rejected(r148/'lead/IMPULSE.json',r148/'lead/basis.py','prefix')
    rejected(r150/'inputs/PREFIX.json',r150/'lead/close.py')
    rejected(r150/'followup/KEYS.json',reverse,'--root',str(r150),'--output',str(reverse_out))
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            write(out/name,raw)
    print('PASS_P104_THREE_ROLE_ENDPOINT_EXCHANGE_BOUND segments=15 eligible_cuts=16494 unresolved=0')


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=='__main__':
    main()
