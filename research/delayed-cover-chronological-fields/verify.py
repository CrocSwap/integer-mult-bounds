"""Read-only, source-authenticated deterministic scientific replay."""
from pathlib import Path
from hashlib import sha256,sha1
import argparse
import json
import shutil
import sys
import tempfile

HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok: raise ValueError(message)


def authenticate(base=HERE):
    manifest=json.loads((base/'CUSTODY.json').read_text())
    names=[]
    for row in manifest['files']:
        path=base/row['copy'];names.append(row['copy'])
        need(path.is_file() and not path.is_symlink(),'regular retained source')
        need(path.resolve().is_relative_to(base.resolve()),'local retained-source path')
        raw=path.read_bytes()
        need(len(raw)==row['bytes'] and sha256(raw).hexdigest()==row['sha256'],
             'retained source byte identity: '+row['copy'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
             'retained Git blob identity: '+row['copy'])
    actual={str(f.relative_to(base)) for directory in ('sources','numerical','vendor6719')
            for f in (base/directory).rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    need(actual==set(names) and len(names)==len(set(names)),'complete retained source inventory')
    return {'files':len(names),'bytes':sum(r['bytes'] for r in manifest['files'])}


def typed_equal(a,b):
    if type(a) is not type(b): return False
    if isinstance(a,dict): return a.keys()==b.keys() and all(typed_equal(a[k],b[k]) for k in a)
    if isinstance(a,list): return len(a)==len(b) and all(typed_equal(x,y) for x,y in zip(a,b))
    return a==b


def integrity_controls():
    with tempfile.TemporaryDirectory(prefix='field-source-control-') as name:
        base=Path(name)
        shutil.copy2(HERE/'CUSTODY.json',base/'CUSTODY.json')
        for directory in ('sources','numerical','vendor6719'):
            shutil.copytree(HERE/directory,base/directory,ignore=shutil.ignore_patterns('__pycache__'))
        changed=base/'numerical/controller.py'
        changed.chmod(changed.stat().st_mode | 0o200)  # Only this disposable copy.
        changed.write_bytes(changed.read_bytes()+b'\n# drift\n')
        try: authenticate(base)
        except ValueError as error: need('retained source byte identity' in str(error),'source control hits identity gate')
        else: raise ValueError('source drift accepted')
    need(not typed_equal({'complete':True},{'complete':1}),'boolean/integer receipt distinction')
    return ['retained-source-byte-drift','typed-receipt-drift']


def replay():
    source=authenticate()
    # A fresh cache namespace prevents even an existing matching .pyc from
    # replacing a source-authenticated import; -B alone only prevents writes.
    with tempfile.TemporaryDirectory(prefix='field-replay-bytecode-') as cache:
        sys.pycache_prefix=cache
        sys.path.insert(0,str(HERE))
        from check import fixture
        from bill import resources
        import join_check
        import controls
        import numerical_check
        cases=[
            dict(dimension=1,codes=(3,),width=1,fibre=1),
            dict(dimension=1,codes=(0,1),width=2,fibre=3,repeats=2),
            dict(dimension=1,codes=(0,1,2),width=3,fibre=2),
            dict(q=5,dimension=1,codes=(0,3,1),width=2,fibre=2,repeats=2,origins=[17*i for i in range(13)]),
            dict(dimension=2,codes=(0,1),width=2,fibre=1),
            dict(dimension=1,codes=(0,1,2),width=1,fibre=5,repeats=2),
            dict(dimension=64,codes=(0,1),width=1,fibre=1),
        ]
        physical=[]
        for params in cases:
            receipt,_,machine,_=fixture(**params)
            bill=resources(receipt['q'],receipt['N'],receipt['Q'],len(receipt['codes']),
                           receipt['w'],receipt['fibre'],receipt['repeats'])
            need(receipt['visited']==bill['all_visited_exact'],'exact complete visited count')
            need(sum(map(len,machine.visits[4:]))==bill['owned_visited_exact'],'exact owned backing count')
            need(receipt['steps']<=bill['transition_upper_bound'],'written transition majorant')
            physical.append({'execution':receipt,'bill':bill})
        joined=[join_check.fixture(width=1,depth=0,slabs=2,body=3),
                join_check.fixture(width=2,depth=1),join_check.fixture(width=2,depth=2),
                join_check.fixture(width=1,depth=3,slabs=2,body=2)]
        numeric=numerical_check.witness()
        negative=controls.run()
    return {'schema_version':1,'source':source,'physical':physical,'joined':joined,
            'numerical':numeric,'literal_controls':negative,'integrity_controls':integrity_controls(),
            'scope':'all-size raw-field producer and source-order composition; inherited numeric arithmetic; no new kappa'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--emit',action='store_true')
    parser.add_argument('--write-result',type=Path);parser.add_argument('--authenticate-only',action='store_true')
    args=parser.parse_args()
    if args.authenticate_only:
        print(json.dumps(authenticate(),sort_keys=True));return
    result=replay();raw=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    if args.write_result:
        with args.write_result.open('x') as out: json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
    else:
        need(typed_equal(result,json.loads((HERE/'RESULT.json').read_text())),'complete typed deterministic receipt')
    if args.emit: print(json.dumps(result,sort_keys=True,indent=2))
    print('PASS_DELAYED_COVER_CHRONOLOGICAL_FIELDS physical_cases=7 joined_cases=4 numerical_weights=1,7 '
          'literal_controls=9 integrity_controls=2 sha256='+sha256(raw).hexdigest()+' no_new_kappa')


if __name__=='__main__': main()
