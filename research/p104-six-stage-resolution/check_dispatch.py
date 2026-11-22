#!/usr/bin/env python3
"""Exercise profile forwarding and the actual positive stop branch at feasible sizes."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys

SOURCE = (Path(sys.argv[1]).resolve() if len(sys.argv) > 1
          else Path(__file__).resolve().parent.parent / 'last-tick')
sys.path.insert(0, str(SOURCE))
from upstream import install

install()
from band_product import Product
from band_positive import Positive
from calibration import LAST_TICK


def main():
    calls = []
    supplied = object()

    def inspect_h_pack(machine, tape, start, end, bit, rank_log, make_supplier):
        calls.append(('h_pack', rank_log, make_supplier() is supplied))

    # This exercises the real Product.h binding; its large body is deliberately mocked.
    product = object.__new__(Product)
    product.profile = LAST_TICK
    with patch('band_product.h_pack', side_effect=inspect_h_pack), \
         patch('band_product.production_supplier', return_value=supplied) as supplier:
        product.h(None, 0, 1, 0)
        supplier.assert_called_once_with(1_600_000, 10**21)
    assert calls == [('h_pack', 1_600_000, True)]

    class ContinueActive(Exception):
        pass

    class Probe(Positive):
        @property
        def owners(self):
            # Stop before any fake fields enter the physical supplier.
            raise ContinueActive

    columns = SimpleNamespace(window=1, offset=0)

    def run(den, h):
        visited = []
        probe = Probe(None, None, 2, denominator=den)
        with patch('band_positive.one_axis', side_effect=lambda field, axis: visited.append(axis)):
            try:
                probe._run(None, 10, 3, columns, h)
            except ContinueActive:
                return 'active_before_supplier', visited
            return 'stopped', visited

    assert run(3, 27) == ('stopped', [10, 11, 12])
    assert run(3, 26) == ('active_before_supplier', [12])
    assert run(10**21, 2**4096) == ('active_before_supplier', [12])
    print('PASS_PROFILE_FACTORY_FORWARDING', 1_600_000, 10**21)
    print('PASS_ACTUAL_POSITIVE_STOP_BRANCH', 'D=3 equality and below',
          'D=10^21 active finite control; supplier mocked')


if __name__ == '__main__':
    main()
