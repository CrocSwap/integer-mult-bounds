"""Construct common-pivot charges for all joint helper subspaces."""
from collections import Counter
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
BASE = HERE / 'retained/research/bit-single-relation-bank-obstruction'


def module(name):
    spec = importlib.util.spec_from_file_location(name, BASE / (name+'.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def terminal_flag(engine, bank, roles):
    mask, outside, rows = sum(1 << i for i in roles), {}, []
    for key, value in bank.items():
        tags = {key}
        while value & ~mask:
            pivot = (value & ~mask).bit_length()-1
            if pivot not in outside:
                outside[pivot] = value, tags
                break
            donor, indices = outside[pivot]
            value ^= donor
            tags ^= indices
        else:
            if value:
                rows.append(dict(key=key, signal=engine.coordinates(value), relation=sorted(tags)))
    return rows


def produce():
    engine = module('census')
    word, _ = engine.source()
    baseline = engine.read(BASE / 'CERTIFICATE.json.gz')
    result = []
    for reverse, orientation in enumerate(baseline['orientations']):
        _, _, banks, moves = engine.walk(word, bool(reverse))
        dimensions = {int(c): f['dim'] for c, f in word['frames'].items()}
        paid_rank = lambda key: abs(dimensions[moves[key][0]]-dimensions[moves[key][1]])
        for group in orientation['groups']:
            terminal = group['exit']
            if reverse:
                basis = terminal_flag(engine, banks[terminal], group['roles'])
                profiles = [[paid_rank(row['key'])] for row in basis]
            else:
                basis = [dict(signal=[i]) for i in group['roles']]
                profiles = [[group['terminal_rank_max']] for _ in basis]
            transform = engine.echelon((sum(1 << i for i in row['signal']), {j}) for j, row in enumerate(basis))
            spaces = []
            for space in group['spaces']:
                chart = space['chart']
                if chart == terminal:
                    continue
                keys = list(banks[chart])
                positions = {key: j for j, key in enumerate(keys)}
                image = engine.echelon((sum(1 << positions[k] for k in b['relation']), set()) for b in space['basis'])
                bank_pivots = sorted(keys[j] for j in image)
                rank_max = max(map(paid_rank, bank_pivots))
                coordinates = [sorted(engine.solve(sum(1 << i for i in b['signal']), transform)) for b in space['basis']]
                pivots = sorted(engine.echelon((sum(1 << i for i in value), set()) for value in coordinates))
                for pivot in pivots:
                    profiles[pivot].append(rank_max)
                spaces.append(dict(chart=chart, coordinates=coordinates, pivots=pivots,
                                   bank_pivots=bank_pivots, rank_max=rank_max))
            lost = group['lost_rank']
            loads = [sum(row) for row in profiles]
            if all(sum(row) < lost or row == [lost] for row in profiles):
                rule = 'coordinatewise'
            else:
                engine.need(reverse and group['entrance'] == 1 and terminal == 0 and lost == 8,
                            'only the declared transpose exception')
                engine.need(max(loads) == 8 and loads.count(8) == 1 and all(x <= 7 for x in loads if x != 8),
                            'joint bound 7k+1')
                engine.need(2**100 * 8**99 > 15**100, 'joint power inequality')
                rule = '7k+1 for k>=2; baseline certificate for k=1'
            result.append(dict(direction=orientation['direction'], entrance=group['entrance'], exit=terminal,
                               roles=group['roles'], lost_rank=lost, rule=rule, basis=basis,
                               spaces=spaces, profiles=profiles, load_histogram=dict(sorted(Counter(loads).items()))))
    return dict(status='PASS_JOINT_BIT_RELATION_OBSTRUCTION', groups=result,
                kappa_interval=['0', '1/100'], maximum_codimension=410)


if __name__ == '__main__':
    import json
    print(json.dumps(produce(), indent=2))
