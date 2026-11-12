"""Replay both exact one-field typed MOVE exclusion bounds."""
from fractions import Fraction as Q
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE / 'closure'
INPUTS = ROOT / 'round212/lead/inputs'
COMPARATOR = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
CLOCKS = [32944,32945]


def check_pins():
    pins = {}
    for line in (PACKAGE/'PINS.txt').read_text().splitlines():
        digest, rel = line.split()
        assert rel not in pins and sha256((PACKAGE/rel).read_bytes()).hexdigest() == digest, rel
        pins[rel] = digest
    assert set(pins) == {p.relative_to(PACKAGE).as_posix() for p in ROOT.rglob('*') if p.is_file()}
    caller_manifest = loads((INPUTS/'7113-SHA256.json').read_bytes())
    for name in ('clifford_exact.py', 'native_verify.py'):
        bound = caller_manifest[f'replay/supplier7112/short-caller/admission-source/frozen/{name}']
        assert bound == pins[f'closure/round212/lead/inputs/{name}']


def checked(script, result, *args):
    proc = run([executable, '-I', '-B', str(ROOT/script), *map(str,args)],
               check=True, capture_output=True, timeout=35)
    assert not proc.stderr and proc.stdout == (ROOT/result).read_bytes(), script
    return loads(proc.stdout)


def check_identity(lead, independent):
    assert lead['rank'] == independent['paid_rank'] == 5
    assert lead['projective_order'] == independent['projective_order'] == 4
    assert lead['squared_pauli'] == [7,[128,0,0],[128,0,2]]
    assert independent['square_offdiagonal_witness'] == [504,0,0,-1,0]
    assert independent['signed_one_slice_columns_verified'] == 512
    assert independent['dropped_C_gate_rejected']
    counts = independent['initial_residue_counts']
    assert counts == [6,6,10,10] and Q(max(counts),sum(counts)) == Q(5,16)
    assert Q(independent['required_two_lane_ambient_fraction_all_f_ge_1']) == 2*(1-Q(5,16)) == Q(11,8)
    lo, hi = map(Q,lead['quote'])
    assert Q('67.66946959214') < lo < hi < Q('67.66946959215')


def check_monomial(lead, independent):
    assert lead['width'] == independent['f'] == 4
    assert lead['one_slice_columns'] == independent['columns'] == 512
    assert lead['one_slice_support'] * independent['columns'] == independent['nonzero_one_slice_entries']
    n = independent['ambient_dimension']
    assert n == 1 << 36
    entry_cap = Q(lead['target_entry_upper'])
    assert entry_cap == Q(independent['target_entry_cap']) == Q(1,1024)
    assert Q(independent['one_slice_max_squared_magnitude'])**2 == entry_cap
    assert Q(independent['relative_trace_upper']) == 2*n*entry_cap
    assert Q(independent['relative_fixed_dimension_upper']) == n*(1+entry_cap)
    rank_lower = Q(independent['target_displacement_lower'])
    assert rank_lower == n*Q(lead['target_pair_rank_lower_per_ambient']) == n*Q(1023,1024)
    core_upper = Q(independent['core_displacement_upper'])
    assert core_upper == n*Q(lead['core_rank_upper_per_ambient']) == n*Q(7,8)
    for row in independent['core_cases']:
        fractions = list(map(Q, lead['core_residue_fractions'][str(row['rank'])]))
        assert Q(row['fixed_fraction']) == fractions[0]
        assert min(fractions) >= Q(1,8) and sum(fractions) == 1
    assert Q(independent['strict_dimension_gap']) == rank_lower-core_upper == n*Q(127,1024)


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3,12)
    check_pins()
    lead212 = checked('round212/lead/typed_volume.py','round212/lead/RESULT.json')
    ind212 = checked('round212/independent/replay.py','round212/independent/RESULT.json',INPUTS)
    lead213 = checked('round213/lead/monomial.py','round213/lead/RESULT.json')
    ind213 = checked('round213/independent/replay.py','round213/independent/RESULT.json',ROOT/'round212/independent/replay.py',INPUTS)
    assert all(receipt['clocks'] == CLOCKS for receipt in (lead212,ind212,lead213,ind213))
    for independent in (ind212,ind213):
        assert (independent['head'],independent['caller']) == (COMPARATOR,CALLER)
        assert independent['roles'] == [625,624] and (independent['source'],independent['target']) == (3,117)
    check_identity(lead212,ind212)
    check_monomial(lead213,ind213)
    print('PASS_TYPED_MOVE_VOLUME: identity 11N/8, monomial 1023N/1024, normalized core at most 7N/8')


if __name__ == '__main__':
    main()
