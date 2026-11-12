"""Reproduce the exact unit-body fixed-frame support and simultaneous rank bound."""
from fractions import Fraction as Q
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
SOURCE_BLOBS = {
    'inputs/CALLER.json': '9451ceaf6e8e037894680b549f3ef41c21b260d7',
    'inputs/TARGET.json': '70886f4087fff3b13cc0478a2cbd451645b080a0',
    'inputs/R209-REVERSE.json': 'f821598c073c4a217f3e83075951ea87085d0935',
    'inputs/7439-PROOF.md': '9ad59b120363e4ab0a49db4eb3d6fc82fa1b4752',
    'inputs/dependency.py': '7cb80295fe235037719d4a189f0e6448ec1426c2',
    'inputs/forward.py': '7842fd300e9aa30ea65a8526c92f761b7ea876b0',
}
ENGINES = [('host_support.py','R224-FORWARD'), ('reverse_host.py','R224-REVERSE'),
           ('host_pairs.py','R225-FORWARD'), ('pair_rank.py','R225-REVERSE')]


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def digest(name, data, pins):
    assert sha256(data).hexdigest() == pins[name], name
    return data


def same_results(a, b, c, d):
    assert a['target_rank'] == b['rank'] == c['target_rank'] == d['target_rank'] == 19
    assert a['blocked'] == c['blocked'] == d['blocked_local'] == 0 and not b['missing_hosts']
    for row, alt in zip(a['hosts'], b['records'], strict=True):
        assert [row['stage'],row['clock'],row['physical_roles'],row['selected_factor']] == [alt['host'],alt['clock'],alt['axes'],alt['selected_index']]
        assert [row['image_intersection_dim'],row['covector_intersection_dim']] == [alt['image_intersection'],alt['covector_intersection']] == [1,2]
    for row, alt, im, co in zip(c['hosts'], d['records'], c['gathered_image_lines'], c['gathered_covector_choices'], strict=True):
        assert [row['stage'],row['clock'],row['physical_roles'],row['selected_factor']] == [alt['host'],alt['clock'],alt['axes'],alt['selected_index']]
        assert row['local_image'] == alt['local_image'] == ['1','1','0','0']
        assert row['allowed_local_covectors'] == [alt['local_covector']] == [['-1','1','0','0']]
        assert im == alt['gathered_image'] and co == alt['gathered_covector']
    assert len(d['records']) == 16
    assert c['proposed_image_rank'] == d['gathered_image_rank'] == d['max_reused_hosts'] == 1
    assert c['proposed_covector_rank'] == d['gathered_covector_rank'] == 16
    assert d['min_missing_hosts'] == 15
    p = Q(d['single_host_credit_upper'])
    assert p == Q(c['best_gross_upper'])
    assert p - 15*(96-p) == Q(d['raw_upper']) < Q('-634.654061')
    assert b['mutated_axis_control_rejected'] and d['mate_mutation_rejected']


def rejected(fn):
    try:
        fn()
    except AssertionError:
        return
    raise AssertionError('mutated control passed')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    pins = loads((ROOT/'PINS.json').read_bytes(), object_pairs_hook=unique)
    members = {p.relative_to(ROOT).as_posix() for sub in ('inputs','receipts') for p in (ROOT/sub).iterdir() if p.is_file()}
    assert set(pins) == members | {'PROVENANCE.json', *(p for p,_ in ENGINES)}
    sources = {}
    for name in sorted(pins):
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        sources[name] = digest(name,(ROOT/path).read_bytes(),pins)
    for name, blob in SOURCE_BLOBS.items():
        raw = sources[name]
        assert sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest() == blob
    result = []
    for engine, receipt in ENGINES:
        actual = loads(run([executable,'-I','-B',str(ROOT/engine)],check=True,capture_output=True,timeout=31).stdout,
                       object_pairs_hook=unique)
        assert actual == loads(sources[f'receipts/{receipt}.json'],object_pairs_hook=unique)
        result.append(actual)
    same_results(*result)
    assert result[-1]['single_host_credit_upper'].encode() in sources['inputs/7439-PROOF.md']
    rejected(lambda: same_results(*result[:3],dict(result[3],gathered_image_rank=2)))
    name = 'inputs/TARGET.json'
    rejected(lambda: digest(name,sources[name][:-1],pins))
    print('PASS_FIXED_FRAME_HOST_REUSE: 16 local pairs, simultaneous image rank 1, gross upper below -634.654061 raw')


if __name__ == '__main__':
    main()
