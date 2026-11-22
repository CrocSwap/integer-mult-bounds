#!/usr/bin/env python3
"""The unmodified e264 binary trial cannot fund the .461 candidate."""
from pathlib import Path
from fractions import Fraction as Q
import sys
import traceback

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
sys.path.insert(1,str(ROOT))
from upstream import install
install()
from installations import Profile,BINARY_C
from activation import resource_receipt
from check_complete import profile_row

assert BINARY_C == Q(4484997569314581,2**60)
p=Profile(tuple(2*10**12*16**j for j in range(7)),36000,
          Q(39,10000),Q('.003890115286594461'),10**21)
assert BINARY_C < p.kappa < p.ordinary
resource_receipt(p)
try:
    profile_row(p)
except AssertionError as error:
    frames=traceback.extract_tb(error.__traceback__)
    last=frames[-1]
    assert last.filename.endswith('/check_complete.py')
    assert last.line=='assert prev < b < limit'
    print('PASS_UNMODIFIED_SOURCE_REJECTS_461_AT_PRICE_GUARD',last.lineno)
else:
    raise AssertionError('The unmodified binary trial unexpectedly funded .461')
