"""Reproduce the complete compensated-fusion geometry and exact support screens."""

from argparse import ArgumentParser
from hashlib import sha256
from io import BytesIO
from json import dumps, loads
from pathlib import Path
from subprocess import run
from sys import executable
from tarfile import TarInfo, open as tar_open
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ADMISSION = 'c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13'
G68 = 'ce9604444161b3532d02eb788cb3a24fbbdaf4c1354d596ac08a2c9edeb72c76'
G69 = 'a2dd10737f5bfbd3818e6766df3890e445fd46f661af9521f5d724b7c56c1d45'
SELECTION = 'bc14204ea6245da881a117492b77e3ee576022e5b9bda96c077a2b32a9b280a0'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(items):
    result = dict(items)
    require(len(result) == len(items), 'Duplicate manifest path')
    return result


def read(path):
    return loads(path.read_bytes(), object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def replay(out):
    manifest = read(HERE/'LOCAL-PINS.json')
    for rel, expected in manifest.items():
        path = HERE/rel
        require(path.resolve().is_relative_to(HERE) and digest(path.read_bytes()) == expected,
                f'Changed input {rel}')
    expected = read(HERE/'receipts/SHA256.json')
    out.mkdir(parents=True, exist_ok=False)
    def stage(name, path, *args, cwd=HERE, timeout=35):
        result = run([executable,'-I','-B',str(HERE/path),*map(str,args)],cwd=cwd,
                     capture_output=True,check=True,timeout=timeout)
        require(digest(result.stdout) == expected[name], f'Changed receipt {name}')
        target = out/name
        target.write_bytes(result.stdout)
        return target

    stage('READBACK.json','price/verify_price.py',cwd=HERE/'price')
    price = stage('RANK-STOCK.json','price/rank_stock.py',cwd=HERE/'price')
    admission,word = (HERE/'inputs'/n for n in ('ADMITTED.json','7334-WORD.json.gz'))
    parent = HERE/'inputs/7314-WORD.json.gz'
    stage('RETIME-KNOWN.json','engines/retime.py','--known-control','--word',parent)
    stage('RETIME-SYNTHETIC.json','engines/retime.py','--synthetic-control')
    with TemporaryDirectory(prefix='fusion-readout-control-') as tmp:
        archive = Path(tmp)/'known.tar'
        data = parent.read_bytes()
        member = TarInfo('research/p104-funded-863-return/WORD.json.gz')
        member.size = len(data)
        with tar_open(archive,'w') as tar:
            tar.addfile(member,BytesIO(data))
        stage('GEOMETRY-CONTROL.json','engines/geometry.py','--control-archive',archive)
        mutant = Path(tmp)/'mutant.gz'
        mutant.write_bytes(word.read_bytes()+b'\n')
        reject = run([executable,'-I','-B',str(HERE/'engines/geometry.py'),'--word',str(mutant),
                      '--price',str(price),'--admission',str(admission),'--admission-sha',ADMISSION],
                     cwd=HERE,capture_output=True,timeout=10)
        require(reject.returncode and b'wrong candidate word' in reject.stderr,'Changed word was accepted')
    g68 = stage('GEOMETRY-68.json','engines/geometry.py','--word',word,'--price',price,
                '--admission',admission,'--admission-sha',ADMISSION)
    g69 = stage('GEOMETRY-69.json','engines/continue_geometry.py','--selection',g68,
                '--selection-sha',SELECTION,'--word',word,'--price',price,'--admission',admission,timeout=40)
    for label,geo,geo_sha,case_count,cap in ((68,g68,G68,4,128),(69,g69,G69,1193,1193)):
        scope = 'first' if label == 68 else 'remaining'
        lead = stage(f'STRICT-{label}.json',f'engines/paired_{scope}.py',price,geo,geo_sha,word)
        independent = stage(f'STRICT-INDEPENDENT-{label}.json',f'engines/paired_check_{scope}.py',
                            '--word',word,'--geometry',geo,'--geometry-sha',geo_sha,'--admission',admission,
                            '--admission-sha',ADMISSION,'--cap',cap,timeout=40)
        x,y = read(lead),read(independent)
        require(len(x['outcomes']) == y['cases_visited'] == case_count and not x['unresolved']
                and not y['unvisited_cases'] and not x['survivors'] and not y['support_only'], 'Strict screen incomplete')
        require([row['key'] for row in x['outcomes']] == [row['key'] for row in y['decisions']], 'Strict key mismatch')
        if label == 69:
            stage('STRICT-COMPARE-69.json','engines/compare_strict.py',lead,independent,geo)
    r70 = stage('RELAXED.json','engines/relaxed.py',price,g68,g69,word)
    r70i = stage('RELAXED-INDEPENDENT.json','engines/relaxed_check.py','--word',word,
                 '--geometry',g68,'--geometry-sha',G68,'--geometry',g69,'--geometry-sha',G69,
                 '--admission',admission,'--admission-sha',ADMISSION,'--cap',1197,timeout=40)
    stage('RELAXED-COMPARE.json','engines/compare_relaxed.py',r70,r70i)
    r71 = stage('BANK.json','engines/readout_bank.py',price,g68,g69,r70,word)
    r71i = stage('BANK-INDEPENDENT.json','engines/check_readout.py','--word',word,'--price',price,
                 '--admission',admission,'--g68',g68,'--g69',g69,'--r70-lead',r70,
                 '--r70-independent',r70i,'--r71-lead',r71)
    first,last = read(g68),read(g69)
    require(len(first['visited']) == 64 and len(last['visited']) == 3358 and not last['unvisited'], 'Geometry did not exhaust')
    require(len(first['survivors'])+len(last['survivors'])==456, 'Wrong geometry survivor count')
    relaxed = read(r70)
    require(relaxed['dispositions']=={'dirty return readout failed':377,'nonlocal forward leakage':820}
            and not relaxed['unresolved'] and not relaxed['survivors'], 'Relaxed gate incomplete')
    b, bi = read(r71),read(r71i)
    require(b['counts']=={'exterior readout rank obstruction':43} and bi['tested']==43
            and not b['unvisited'] and not bi['unvisited'] and not b['survivors'], 'Full-bank gate incomplete')
    require(set(expected) == {p.name for p in out.iterdir()}, 'Receipt inventory mismatch')
    print('PASS_COMPENSATED_FUSION_READOUT_BOUND geometry=3422 geometric_survivors=456 strict=1197 relaxed=1197 full_bank=43 kappa_change=0')


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.out is not None:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix='compensated-fusion-') as tmp:
            replay(Path(tmp)/'receipts')


if __name__ == '__main__':
    main()
