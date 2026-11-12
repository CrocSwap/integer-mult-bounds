"""Replay both exact Type A QUERY source exclusions and the complete price."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from shutil import copyfile
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
CALLER='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
CALLER_BLOB='9451ceaf6e8e037894680b549f3ef41c21b260d7'
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'


def require(condition,message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result=dict(pairs)
    require(len(result)==len(pairs),'Duplicate input path or JSON key')
    return result


def read(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def replay(out):
    for rel,expected in read((HERE/'LOCAL-PINS.json').read_bytes()).items():
        path=HERE/rel
        require(path.resolve().is_relative_to(HERE) and digest(path.read_bytes())==expected,
                f'Changed input {rel}')
    wanted=read((HERE/'receipts/SHA256.json').read_bytes())
    source=decompress((HERE/'inputs/7113-CALLER.json.gz').read_bytes())
    require(digest(source)==CALLER and sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest()==CALLER_BLOB,
            'Changed exact caller')
    out.mkdir(parents=True,exist_ok=False)
    with TemporaryDirectory(prefix='query-cache-') as tmp:
        work=Path(tmp); price=work/'price'; independent=work/'independent'
        (price/'inputs').mkdir(parents=True); (independent/'inputs').mkdir(parents=True)
        for name in ('QUERY-CENSUS.json','7334-READBACK.json','7334-ADMITTED.json','pricing.py'):
            copyfile(HERE/'inputs'/name,price/'inputs'/name)
        copyfile(HERE/'engines/quote.py',price/'quote.py')
        copyfile(HERE/'engines/independent.py',independent/'independent.py')
        (price/'inputs/7113-CALLER.json').write_bytes(source)
        (independent/'inputs/CALLER.json').write_bytes(source)

        def stage(name,script,*args):
            result=run([executable,'-I','-B',str(script),*map(str,args)],cwd=work,
                       check=True,capture_output=True,timeout=20)
            require(digest(result.stdout)==wanted[name],f'Changed receipt {name}')
            (out/name).write_bytes(result.stdout)
            return result.stdout

        quote=stage('PRICE.json',price/'quote.py')
        (price/'PRICE.json').write_bytes(quote); (independent/'inputs/PRICE.json').write_bytes(quote)
        primary=read(stage('LEAD.json',HERE/'engines/lead.py',work))
        second=read(stage('INDEPENDENT.json',independent/'independent.py','--support'))
        stage('CONTROLS.json',independent/'independent.py','--controls-only')
        stock=read(quote)
        require(primary['head']==second['head']==stock['head']==HEAD and
                primary['caller_sha256']==second['caller_sha256']==CALLER,'Changed comparator')
        require(primary['price_sha256']==second['price_sha256']==digest(quote),'Support price mismatch')
        require(primary['q']==-1 and second['endpoint_checks']==4 and
                {p['q'] for p in second['probes']}=={-1,1},'Lost signed controls')
        require(not any((primary['survivors'],primary['unvisited'],second['symbolic_only'],second['unvisited'])),
                'A support gate is incomplete')
        require(len(primary['decisions'])==len(second['decisions'])==6,'Wrong exact pair count')

        def minor(rows,pair,coordinates):
            first,later=(rows[str(clock)] for clock in pair)
            i,j=map(str,coordinates)
            return Q(first.get(i,'0'))*Q(later.get(j,'0'))-Q(first.get(j,'0'))*Q(later.get(i,'0'))

        for a,b,key in zip(primary['decisions'],second['decisions'],stock['eligible_pairs_before_support'],strict=True):
            require(a['key']==b['pair']==key,'Changed ordered pair')
            require(a['status']=='source rows not proportional' and b['status']=='exact_nonproportional_source',
                    'Unexpected support disposition')
            for receipt,rows,field in ((a,primary['source_rows'],'cross_product'),(b,second['sources'],'determinant')):
                witness=receipt['witness']
                exact=minor(rows[receipt['probe']],key,witness['coordinates'])
                require(exact and exact==Q(witness[field]),'Incorrect rational minor')
        require(stock['whole_optimistic_stock_upper']=='288' and
                stock['by_number_of_reused_queries']['1']['exact_credit']=='96','Changed stock upper')
        (independent/'inputs/CALLER.json').write_bytes(source+b'\n')
        negative=run([executable,'-I','-B',str(independent/'independent.py'),'--support'],cwd=work,
                     capture_output=True,timeout=20)
        require(negative.returncode and b'Changed input CALLER.json' in negative.stderr and not negative.stdout,
                'Changed caller was accepted')
    require({p.name for p in out.iterdir()}==set(wanted),'Changed receipt set')
    print('PASS_TYPE_A_QUERY_CACHE_PAIR_BOUND pairs=6 excluded=6 unresolved=0 kappa_change=0')


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.out:
        replay(a.out.resolve())
    else:
        with TemporaryDirectory(prefix='query-cache-receipts-') as tmp:
            replay(Path(tmp)/'out')


if __name__=='__main__':
    main()
