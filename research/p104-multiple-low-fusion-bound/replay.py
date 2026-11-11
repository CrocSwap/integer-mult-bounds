"""Replay the exact #7334 multiple-low compensated-fusion exclusion."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha1,sha256
from json import loads
from pathlib import Path,PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError('duplicate JSON key')
    return result


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate(root):
    pins = decode((HERE/'LOCAL-PINS.json').read_bytes())
    for name, expected in pins.items():
        rel = PurePosixPath(name)
        assert rel.as_posix() == name and not rel.is_absolute() and '..' not in rel.parts
        if digest((HERE/name).read_bytes()) != expected:
            raise ValueError('changed dependency: ' + name)
    provenance = decode((HERE/'PROVENANCE.json').read_bytes())['files']
    for name, ref in provenance.items():
        assert name in pins and not ref['uncompress']
        raw = (HERE/name).read_bytes()
        assert digest(raw) == ref['sha256']
        assert sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest() == ref['git_blob']

    prior = decode((HERE/'inputs/PR7338-SHA256.json').read_bytes())
    assert pins['inputs/RANK-STOCK.json'] == prior['RANK-STOCK.json']
    inputs = root/'inputs'
    inputs.mkdir()
    for local, public in (('R68','GEOMETRY-68.json'),('R69','GEOMETRY-69.json'),('R70','RELAXED.json')):
        raw = decompress((HERE/f'inputs/{local}.json.gz').read_bytes())
        assert digest(raw) == prior[public], public
        (inputs/f'{local}.json').write_bytes(raw)
    for name in ('ADMITTED.json','RANK-STOCK.json','WORD.json.gz','pricing.py'):
        shutil.copyfile(HERE/'inputs'/name,inputs/name)
    admit = decode((inputs/'ADMITTED.json').read_bytes())
    assert admit['head'] == HEAD and admit['exit'] == 0
    assert admit['inputs']['WORD.json.gz'] == pins['inputs/WORD.json.gz']
    assert admit['caller'] == '07a76c5e2738882c0cb322278e56f6cae3c9885d'
    return inputs


def command(script,*args,check=True):
    argv = [sys.executable,'-I','-B',str(HERE/'engines'/script),*map(str,args)]
    return subprocess.run(argv,capture_output=True,check=check,timeout=15)


def replay(root,output):
    inputs = authenticate(root)
    expected = decode((HERE/'receipts/SHA256.json').read_bytes())
    generated = {}

    def record(name,raw,path=None):
        assert digest(raw) == expected[name], ('changed receipt',name)
        generated[name] = raw
        if path is not None:
            path.write_bytes(raw)
        return decode(raw)

    g68,g69,g70 = (inputs/f'R{i}.json' for i in (68,69,70))
    stock = inputs/'RANK-STOCK.json'
    quote_args = ('--r68-geometry',g68,'--r69-geometry',g69,'--r70-support',g70,
                  '--rank-stock',stock,'--tariff',inputs/'pricing.py')
    (root/'frontier').mkdir()
    bank_path = root/'frontier/BANKS.json'
    price = record('BANKS.json',command('bank_bound.py',*quote_args).stdout,bank_path)
    assert price['head'] == HEAD and price['geometry_pairs'] == 3422 and price['geometry_survivors'] == 456
    assert price['multi_low_banks'] == 8 and price['distinct_paid_calls'] == 16
    assert price['one_edit_cap'] == 1 and price['rank_types'] == {'1+1':6,'1+2':2}
    assert price['bank_shapes'] == {'2+1':2,'3+1':2,'4+1':4}
    assert 0 < Fraction(price['one_edit_comparator_gross_upper']) < 1
    assert 0 < Fraction(price['all_eight_comparator_gross_upper']) < 1
    assert Fraction(price['target']) == Fraction('0.0040075385047236')
    assert Fraction(price['target_old_margin'][1]) < Fraction(price['target_all_eight_margin'][1]) < 0
    assert Fraction(price['target_all_eight_gross_credit'][0]) > 0

    (root/'lead').mkdir()
    for name in ('local.py','rank.py'):
        shutil.copyfile(HERE/'engines'/name,root/'lead'/name)
    lead = record('LEAD.json',command('multi_low.py',root).stdout)
    verify_args = ('--banks',bank_path,'--g68',g68,'--g69',g69,
                   '--admission',inputs/'ADMITTED.json','--word',inputs/'WORD.json.gz')
    independent = record('INDEPENDENT.json',command('check_multilow.py',*verify_args).stdout)
    assert lead['head'] == independent['head'] == HEAD
    assert independent['status'] == 'EXHAUSTED' and independent['tested'] == 8
    assert not (lead['survivors'] or independent['survivors'] or lead['unvisited'] or independent['unvisited'])
    assert len(lead['controls']) == 2 and len(independent['controls']) == 4
    label = {'readout_excluded':'high readout exterior rank obstruction',
             'forward_span_excluded':'full low exterior rank obstruction'}
    counts = Counter()
    for bank,first,second in zip(price['rows'],lead['decisions'],independent['outcomes'],strict=True):
        assert bank['key'] == first['key'] == second['key']
        assert bank['h'] == first['h'] == second['h'] and bank['high'] == [second['readout_peer']]
        assert bank['low'] == first['low'] and bank['rank_type'] == first['rank_type'] == second['rank_type']
        assert first['status'] == label[second['status']]
        assert 0 < Fraction(first['complete_margin'][0])
        counts[second['status']] += 1
        if second['status'] == 'readout_excluded':
            assert Fraction(second['certificate']['determinant']) != 0
        else:
            assert second['h'] == 1182
            assert (second['exterior_donor_rank'],second['exterior_augmented_rank']) == (2,3)
            assert first['residue'] and all(Fraction(value) for value in first['residue'].values())
    assert counts == {'readout_excluded':7,'forward_span_excluded':1}

    g68.write_bytes(g68.read_bytes()+b'\n')
    changed = command('check_multilow.py',*verify_args,check=False)
    assert changed.returncode == 1 and b'changed input g68' in changed.stderr and not changed.stdout
    g68.write_bytes(decompress((HERE/'inputs/R68.json.gz').read_bytes()))
    stock.write_bytes(stock.read_bytes()+b'\n')
    changed = command('bank_bound.py',*quote_args,check=False)
    assert changed.returncode == 1 and b'stale rank_stock' in changed.stderr and not changed.stdout

    assert generated.keys() == expected.keys()
    if output is not None:
        output.mkdir()
        for name,raw in generated.items():
            (output/name).write_bytes(raw)
    print('PASS_P104_MULTIPLE_LOW_FUSION_BOUND banks=8 readout_excluded=7 low_excluded=1 '
          'unresolved=0 saving_upper=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__ and sys.version_info[:2] == (3,12), 'CPython 3.12 and assertions required'
    p = ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path)
    args = p.parse_args()
    with TemporaryDirectory(prefix='p104-multiple-low-fusion-') as temp:
        replay(Path(temp),args.out)
