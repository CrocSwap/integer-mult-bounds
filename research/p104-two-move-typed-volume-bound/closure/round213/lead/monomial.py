"""Exact typed MOVE rank capacities for any unitary monomial erasure."""
from fractions import Fraction as F
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from math import comb
from pathlib import Path
from runpy import run_path
from signal import alarm

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'round212/lead/inputs/WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'round212/lead/inputs/native_verify.py':'3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38',
}


def main():
    assert __debug__
    alarm(30)
    for name,digest in PINS.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest
    paths = ROOT/'round212/lead/inputs'
    word = loads(decompress((paths/'WORD.json.gz').read_bytes()))
    assert word['program'][32944:32946] == [['MOVE',625,3,117,False],['MOVE',624,3,117,False]]
    assert not word['frames'][3] and word['frames'][117] == [8,17,34,68,391]
    v = run_path(str(paths/'native_verify.py'))
    target = v['frame'](word['frames'][117],9)
    for j in range(512):
        col, log_den = v['state'](target,j)
        assert len(col) == 32
        assert all(32*(a*a+b*b) == 2**(2*log_den) for a,b in col.values())
    width = 4
    max_entry = F(1,2**(5*width//2))
    pair_rank_lower = 1-max_entry
    ranks = {}
    for r in range(1,7):
        n = width*r
        residue_fractions = [F(sum(comb(n,j) for j in range(i,n+1,4)),2**n) for i in range(4)]
        ranks[r] = list(map(str,residue_fractions))
        assert min(residue_fractions) >= F(1,8)
    child_rank_upper = F(7,8)
    assert pair_rank_lower == F(1023,1024) > child_rank_upper
    alarm(0)
    print(dumps({'pins':PINS,'clocks':[32944,32945],'width':width,'one_slice_columns':512,
                 'one_slice_support':32,'target_entry_upper':str(max_entry),'target_pair_rank_lower_per_ambient':str(pair_rank_lower),
                 'core_rank_upper_per_ambient':str(child_rank_upper),'core_residue_fractions':ranks,
                 'case_cap':1,'seconds_cap':30},sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
