"""Replay exact source bindings, finite proof certificate and mandatory typed receipt."""
from pathlib import Path
import json
from core import canonical, require, result
PACKAGE=Path(__file__).resolve().parent
if __name__=='__main__':
    actual=result(PACKAGE)
    expected=json.loads((PACKAGE/'RESULT.json').read_text())
    require(canonical(actual)==canonical(expected),'complete typed RESULT mismatch')
    print('PASS_PROJECTION_RECURSION_FINITE_INFIMUM')
