"""Reprice the funded first-read edit on the exact 17-copy invoice."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from json import dumps
from pathlib import Path
from runpy import run_path

SOURCE = 'inputs/r58/PRICE.json'
SOURCE_PIN = '8d70669e720faabc932366dafbc1bd1fdaef6f088c4eb02b0ea3707ba309ab53'


def quote(root):
    frozen = (root/SOURCE).read_bytes()
    assert sha256(frozen).hexdigest() == SOURCE_PIN
    engine = run_path(str(root/'entrance_price.py'))
    same = engine['quote'](root)
    assert (dumps(same,sort_keys=True,indent=2)+'\n').encode() == frozen
    assert all(Fraction(row['credit'][1]) < 1 for row in same['rank_prices'].values())
    return {**same,'scope':'fund the first read using one already-paid partner ascent',
            'source_price_sha256':SOURCE_PIN,'new_paid_calls_per_copy':-1,
            'paid_positions_after':110519,'productive_positions_after':22461,
            'one_edit_cap':1}


if __name__ == '__main__':
    p = ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path)
    a = p.parse_args()
    print(dumps(quote(a.root),sort_keys=True,indent=2))
