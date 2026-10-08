"""Shared paths and serialization for the balanced split witness."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
import importlib.util
import json
from pathlib import Path
from fractions import Fraction

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SELECTED = HERE/'selected'
EXP = ROOT/'scripts/experiments'
sys.path.insert(0, str(EXP))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def json_value(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    return value


def write_json(path, value):
    Path(path).write_text(json.dumps(json_value(value), indent=2, sort_keys=True)+'\n')


def config(h):
    if type(h) is not int or h not in (23, 25):
        raise ValueError('Only h=23 and h=25 are certified')
    return dict(order='cover-core' if h == 23 else 'reverse-node',
                horizon='next-use', live_order='insertion' if h == 23 else 'cost', weight='entropy',
                live=True, completion='future', retired_order='rank' if h == 23 else 'cost',
                oracle_permutation=None if h == 23 else permutation(h), enlarge=0)


def permutation(h):
    if h == 23:
        order = [1, 3, 2, *range(4, 20), 21, 20, 22, 0]
        return [order.index(i) for i in range(h)]
    if h == 25:
        return [(i+1) % h for i in range(h)]
    raise ValueError('Unsupported coordinate permutation')
