"""Reproduce the exact retimed chart-207 productive split exclusion."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
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
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    pins = decode((HERE/'LOCAL-PINS.json').read_bytes())
    for name, expected in pins.items():
        rel = PurePosixPath(name)
        assert rel.as_posix() == name and not rel.is_absolute() and '..' not in rel.parts
        if digest((HERE/name).read_bytes()) != expected:
            raise ValueError('changed dependency: ' + name)
    provenance = decode((HERE/'PROVENANCE.json').read_bytes())['files']
    for name, record in provenance.items():
        assert name in pins and not record['uncompress']
        raw = (HERE/name).read_bytes()
        assert digest(raw) == record['sha256']
        assert sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest() == record['git_blob']
    manifest = decode((HERE/'price/inputs/PR7338-SHA256.json').read_bytes())
    assert pins['price/inputs/RANK-STOCK.json'] == manifest['RANK-STOCK.json']


def command(script, *args, timeout=35, check=True):
    argv = [sys.executable, '-I', '-B', str(HERE/script), *map(str,args)]
    return subprocess.run(argv, capture_output=True, check=check, timeout=timeout)


def replay(scratch, output):
    authenticate()
    expected = decode((HERE/'receipts/SHA256.json').read_bytes())
    generated = {}

    def record(name, raw, path=None):
        assert digest(raw) == expected[name], ('changed receipt', name)
        generated[name] = raw
        if path is not None:
            path.write_bytes(raw)
        return decode(raw)

    (scratch/'price').mkdir()
    (scratch/'lead').mkdir()
    (scratch/'independent').mkdir()
    (scratch/'support').mkdir()
    shutil.copytree(HERE/'inputs',scratch/'inputs')
    price_path = scratch/'price/PRICE.json'
    price = record('PRICE.json',command('price/quote.py').stdout,price_path)
    assert price['head'] == HEAD and not price['paid_delta']
    assert price['productive_delta'] == {'1':17,'8':17,'9':-17}
    assert (sum(price['paid'].values()),sum(price['old_targets'].values()),
            sum(price['new_targets'].values()),price['signed_rank_surplus']) == (110519,22461,22478,1424)
    assert 0 < Fraction(price['new_margin'][0])
    assert Fraction(price['margin_with_one_added_raw_rank_one_upper']) < 0

    geom_path = scratch/'lead/OCCUPANCY.json'
    geometry = record('OCCUPANCY.json',command('engines/occupancy.py',scratch,timeout=20).stdout,geom_path)
    assert geometry['head'] == HEAD and len(geometry['endpoint_cohort']) == 615
    assert geometry['affected_candidates'] == [205,532,969,1081,1250,1453]
    assert geometry['new']['complete'] and geometry['old']['complete']
    assert len(geometry['new']['rows']) == 41
    first_keys, last_keys = geometry['representative_keys'], geometry['unvisited_keys']
    assert (len(first_keys),len(last_keys)) == (128,18)
    assert len(set(map(tuple,first_keys+last_keys))) == 146

    word = scratch/'inputs/7334-WORD.json.gz'
    reverse_path = scratch/'independent/RESULT.json'
    record('REVERSE.json',command('engines/reverse_207.py','--inputs',scratch/'inputs','--price',
                                  price_path,'--price-sha',expected['PRICE.json'],timeout=20).stdout,reverse_path)
    geometry_compare = record('GEOMETRY-COMPARE.json',command('engines/compare_geometry.py',
                                                              geom_path,reverse_path,word).stdout,scratch/'independent/COMPARE.json')
    assert geometry_compare['matched_raw_new_cuts'] == 41
    assert geometry_compare['raw_pivot_pairs'] == 166
    assert geometry_compare['lead_representative_pairs'] == 146
    assert len(geometry_compare['equivalent_extra_pairs']) == 5
    assert geometry_compare['no_distinct_chart_207_event_omitted']

    admit = HERE/'price/inputs/ADMITTED.json'
    first_path = scratch/'support/RESULT.json'
    first = record('FIRST-SUPPORT.json',command('engines/paired_support.py','--word',word,'--price',price_path,
                  '--price-sha',expected['PRICE.json'],'--geometry',geom_path,'--geometry-sha',
                  expected['OCCUPANCY.json'],'--admission',admit).stdout,first_path)
    lead_first = record('FIRST-RANK.json',command('engines/paired_rank.py',scratch,'first').stdout,
                        scratch/'lead/PAIRED.json')
    assert first['unresolved'] == last_keys and not first['support_only']
    assert not lead_first['unvisited']

    cont = scratch/'continuation'
    (cont/'inputs').mkdir(parents=True)
    (cont/'support').mkdir()
    (cont/'lead').mkdir()
    shutil.copyfile(HERE/'engines/continuation.py',cont/'continuation.py')
    for path,name in (
        (HERE/'engines/paired_support.py','paired_support.py'),(first_path,'R72-SUPPORT.json'),
        (geom_path,'R72-OCCUPANCY.json'),(word,'7334-WORD.json.gz'),
        (price_path,'PRICE.json'),(admit,'ADMITTED.json'),
    ):
        shutil.copyfile(path,cont/'inputs'/name)
    selected = record('SELECTION.json',command(cont/'continuation.py','--derive-only').stdout,
                      cont/'support/SELECTION.json')
    assert selected['representative_keys'] == last_keys and not selected['unvisited_keys']
    last = record('REMAINING-SUPPORT.json',command(cont/'continuation.py','--support','--selection-sha',
                                                   expected['SELECTION.json']).stdout,cont/'support/RESULT.json')
    lead_last = record('REMAINING-RANK.json',command('engines/paired_rank.py',scratch,'remaining').stdout,
                       cont/'lead/PAIRED.json')
    assert not (last['unresolved'] or last['support_only'] or lead_last['unvisited'])
    assert last['fresh_replayed'] == 16 and last['same_bank_reused'] == 2

    counts = Counter()
    for actual,rank,keys in ((first,lead_first,first_keys),(last,lead_last,last_keys)):
        assert [row['key'] for row in actual['decisions']] == keys
        per_cut = Counter((row['key'][0],row['status'].replace('_',' ')) for row in actual['decisions'])
        assert per_cut == {(row['cut'],row['status']):row['cases'] for row in rank['rows']}
        counts.update(row['status'] for row in actual['decisions'])
    assert counts == {'no_nonzero_pure_prefix':3,'no_nonzero_pure_suffix':57,'no_unit_pairing':86}

    reconciliation = record('RECONCILED.json',command('engines/reconcile.py',scratch,cont).stdout)
    summary = reconciliation['summary']
    assert summary['raw_keys'] == 166 and summary['canonical_keys'] == 146
    assert summary['unresolved'] == summary['advanced'] == 0
    assert summary['exclusions'] == counts
    assert len(reconciliation['reverse_post_block_aliases']) == 5

    stale = command('engines/reverse_207.py','--inputs',scratch/'inputs','--price',price_path,
                    '--price-sha','0'*64,timeout=10,check=False)
    assert stale.returncode == 1 and not stale.stdout
    mutated = scratch/'mutated'
    shutil.copytree(HERE/'price',mutated)
    stock = mutated/'inputs/RANK-STOCK.json'
    stock.write_bytes(stock.read_bytes()+b'\n')
    changed = command(mutated/'quote.py',timeout=10,check=False)
    assert changed.returncode == 1 and b'changed pinned input: RANK-STOCK.json' in changed.stderr
    assert not changed.stdout

    assert generated.keys() == expected.keys()
    if output is not None:
        output.mkdir()
        for name, raw in generated.items():
            (output/name).write_bytes(raw)
    print('PASS_P104_RETIMED_CHART207_SPLIT_BOUND raw=166 representatives=146 '
          'no_prefix=3 no_suffix=57 no_pairing=86 unresolved=0 saving_upper=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__ and sys.version_info[:2] == (3,12), 'CPython 3.12 and assertions required'
    p = ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path)
    args = p.parse_args()
    with TemporaryDirectory(prefix='p104-retimed-chart207-') as temp:
        replay(Path(temp),args.out)
