"""Reject altered native widths, placements, ledgers and dual multipliers."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('owner_optimum', P/'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    V.require(not args.out.exists() and not args.out.resolve().is_relative_to(P), 'new external output file')
    V.verify_files()
    original = V.inputs()
    V.validate_inputs(*original)
    V.dual()
    rejected = []

    def trial(name, function, reason):
        try:
            function()
        except ValueError as error:
            V.require(reason in str(error), 'wrong rejection: '+name+' '+str(error))
            rejected.append(dict(name=name, reason=reason))
        else:
            raise ValueError('accepted mutation: '+name)

    data = list(original)
    word = copy.deepcopy(data[3])
    word['final'][224] = word['start'][224]
    data[3] = word
    trial('erase-helper-width', lambda: V.validate_inputs(*data), 'native width inventory')
    data = list(original)
    owners = copy.deepcopy(data[2])
    owners[1] = copy.deepcopy(owners[0])
    data[2] = owners
    trial('duplicate-owner', lambda: V.validate_inputs(*data), 'unique complete helper and bin call')
    data = list(original)
    owners = copy.deepcopy(data[2])
    owners[0]['time'] = 72
    data[2] = owners
    trial('out-of-window-call', lambda: V.validate_inputs(*data), 'owner time and port')
    data = list(original)
    program = copy.deepcopy(data[4])
    next(e for e in program['forward'] if e[0] in ('climb', 'center'))[-1] += 1
    data[4] = program
    trial('tamper-native-rank', lambda: V.validate_inputs(*data), 'both native paid profiles')
    prices = dict(V.WIDTH_PRICES, **{})
    prices[9] += 1
    trial('raise-width9-price', lambda: V.dual(prices), 'full-bin price')
    bonuses = dict(V.CAPACITY_PRICES)
    bonuses[48] += 1
    trial('raise-capacity48-price', lambda: V.dual(capacity_prices=bonuses), 'full-bin price')
    trial('zero-saving', lambda: V.moments(V.Q(0)), 'concavity domain')
    trial('unit-saving', lambda: V.moments(V.Q(1)), 'concavity domain')
    args.out.write_text(json.dumps(dict(status='PASS_OPTIMALITY_CONTROLS', positive=2,
                                       rejected=rejected), indent=2)+'\n')
    print('PASS_OPTIMALITY_CONTROLS', len(rejected))


if __name__ == '__main__':
    main()
