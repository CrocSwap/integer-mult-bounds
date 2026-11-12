"""Reproduce the exact fixed-paid P104 two-role endpoint-exchange exclusion."""
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

    r143,r146=root/'r143',root/'r146'
    for name,raw in inherited.items():
        write(r143/'scout/inputs'/name,raw)
    write(r143/'scout/inputs/pricing.py',source('inputs/pricing.py'))
    for stage in (r143,r146):
        write(stage/'inputs/7334-WORD.json.gz',source('inputs/7334-WORD.json.gz'))
    write(r143/'inputs/reverse_span.py',source('inputs/reverse_span.py'))
    write(r143/'scout/quote.py',source('engines/quote.py'))
    for name in ('geometry.py','support.py'):
        write(r143/'lead'/name,source('engines/'+name))
    write(r146/'lead/impulse.py',source('engines/impulse.py'))

    price=record('R143-PRICE.json',r143/'scout/quote.py')
    write(r143/'lead/PRICE.json',outputs['R143-PRICE.json'])
    g=record('R143-GEOMETRY.json',r143/'lead/geometry.py')
    write(r143/'lead/GEOMETRY.json',outputs['R143-GEOMETRY.json'])
    bare=record('R143-BARE.json',r143/'lead/support.py','bare')
    write(r143/'lead/BARE.json',outputs['R143-BARE.json'])
    basis=record('R143-BASIS.json',r143/'lead/support.py','basis','--bare-sha',expected['R143-BARE.json'])
    write(r143/'lead/BASIS.json',outputs['R143-BASIS.json'])

    for name in ('PRICE','GEOMETRY','BASIS'):
        write(r146/'inputs'/f'{name}.json',outputs[f'R143-{name}.json'])
    keys=record('R146-KEYS.json',r146/'lead/impulse.py','--freeze')
    write(r146/'lead/KEYS.json',outputs['R146-KEYS.json'])
    close=record('R146-RESULT.json',r146/'lead/impulse.py')

    reverse=r143/'independent/reverse.py'
    reverse_out=r143/'independent/RESULT.json'
    write(reverse,source('engines/independent_reverse.py'))
    for name in ('bank_trace.py','word.json.gz'):
        actual='7334-WORD.json.gz' if name=='word.json.gz' else name
        write(r143/'inputs'/name,source('inputs/'+actual))
    for name in ('KEYS','RESULT'):
        write(r143/'followup'/f'{name}.json',outputs[f'R146-{name}.json'])
    call(reverse,'--root',str(r143),'--output',str(reverse_out))
    data=reverse_out.read_bytes()
    assert digest(data)==expected['INDEPENDENT.json']
    outputs['INDEPENDENT.json']=data
    independent=decode(data)
    assert independent['scope']==20 and independent['raw_cuts']==20455 and independent['unresolved']==0
    assert len(independent['rows'])==20
    assert all(r['evaluations']==['0','0'] and r['required']=='2' for r in independent['rows'])
    assert [r['key'] for r in independent['rows']]==g['ranges']


    assert price['old_rank_pair']==[5,9] and price['new_rank_pair']==[6,8]
    assert price['potential_unordered_pairs']==615 and price['whole_compatible_pair_cap']==1
    assert len(g['exact_pairs'])==6 and len(g['ranges'])==20 and g['raw_cuts']==20455
    assert len(bare['rows'])==16 and len(basis['rows'])==8
    assert all(r['decision']=='prefix excluded' for r in bare['rows']+basis['rows'])
    assert all(r['prefix']['separating_covector']=={'1454':'1','1481':'-2'} for r in basis['rows'])
    assert len(close['rows'])==len(keys['ranges'])==12 and close['raw_cuts']==5080
    assert close['progress']['events']==76466 and not close['unresolved']
    assert all(r['status']=='prefix excluded' and r['first_nonzero'] is None for r in close['rows'])
    covered={tuple(r['key']) for r in basis['rows']}|{(*r[:3],r[-1]) for r in keys['ranges']}
    assert covered=={(*r[:3],r[-1]) for r in g['ranges']}

    def rejected(path,script,*args):
        raw=path.read_bytes()
        path.write_bytes(raw+b' ')
        check=call(script,*args,expect_success=False)
        assert check.returncode==1 and b'changed' in check.stderr
        path.write_bytes(raw)

    rejected(r143/'lead/GEOMETRY.json',r143/'lead/support.py','bare')
    rejected(r146/'inputs/BASIS.json',r146/'lead/impulse.py')
    rejected(r143/'followup/KEYS.json',reverse,'--root',str(r143),'--output',str(reverse_out))
    assert set(outputs)==set(expected)

    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            write(out/name,raw)
    print('PASS_P104_FIXED_PAID_ENDPOINT_EXCHANGE_BOUND partners=6 ranges=20 raw_cuts=20455 unresolved=0')


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=='__main__':
    main()
