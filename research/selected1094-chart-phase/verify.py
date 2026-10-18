#!/usr/bin/env python3
"""Source-bound residual chart/phase audit; no new supplier or kappa.

Gareth Davidson, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from algebra import (canonical, census, closed_kernel, convolution, defect, digest,
                     linear, orthonormal, projector, rank, rebased, require)

ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
OWNERS = 'research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz'
PREFIX = 'candidate/strict/'
MEMBERS = {
    'template': PREFIX + 'global/hosted/GLOBAL-TEMPLATE.json.gz',
    'sigmas': PREFIX + 'global/hosted/ACTUAL-SIGMAS.json.gz',
    'hosted': PREFIX + 'global/hosted/HOSTED.json',
    'phases': PREFIX + 'global/base/work/complex-nine-native/DATA-PHASES.json',
    'word': PREFIX + 'global/base/providers/gauge44/CANONICAL-WORD.json.gz',
    'parent': PREFIX + 'global/base/split-centres/GLOBAL-TEMPLATE.json.gz',
    'checks': PREFIX + 'global/base/providers/gauge44/LOCAL-CHECKS.json',
    'replay': PREFIX + 'REPLAY.json',
}


def pairs(items):
    out = {}
    for key, value in items:
        require(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def load_bytes(data, compressed=False):
    if compressed:
        data = gzip.decompress(data)
    def invalid(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def read(path):
    return load_bytes(path.read_bytes(), path.suffix == '.gz')


def inputs(root):
    manifest = read(HERE / 'SOURCES.json')
    pins = {}
    for item in manifest['files']:
        if item['usage'] != 'input':
            continue
        p = root / item['path']
        require(p.resolve().is_relative_to(root.resolve()), 'source path escape')
        data = p.read_bytes()
        require(hashlib.sha256(data).hexdigest() == item['sha256'], 'source pin: ' + item['path'])
        pins[item['path']] = item['sha256']
    objects, member_pins = {}, {}
    with tarfile.open(root / ARCHIVE, 'r:gz') as archive:
        names = [m.name for m in archive.getmembers()]
        require(len(names) == len(set(names)), 'duplicate archive member')
        for key, name in MEMBERS.items():
            member = archive.getmember(name)
            require(member.isfile(), 'nonregular archive input')
            data = archive.extractfile(member).read()
            objects[key] = load_bytes(data, name.endswith('.gz'))
            member_pins[name] = hashlib.sha256(data).hexdigest()
    objects['owners'] = read(root / OWNERS)
    require(objects['replay'] == read(root / 'research/community-frontier1094-audit/REPLAY.json'), 'selected replay binding')
    source = read(root / 'research/complex-t16-rare-pattern-exchanges/SOURCE.json')
    for name in ('audit_allcold.py', 'emit_allcold.py'):
        require(source['files']['code/' + name] == pins['research/gauge44-slots-t16/code/' + name], 'selected controller code binding')
    h = objects['hosted']
    require(digest(objects['template']) == h['template_sha256'], 'decoded hosted template binding')
    for key, suffix in (('word', 'providers/gauge44/CANONICAL-WORD.json.gz'),
                        ('phases', 'work/complex-nine-native/DATA-PHASES.json'),
                        ('checks', 'providers/gauge44/LOCAL-CHECKS.json')):
        require(member_pins[MEMBERS[key]] == h['source_artifacts'][suffix], 'hosted source binding')
    return objects, dict(files=pins, archive_members=member_pins)


def port_basis(q):
    # Orthogonal transvection taking the first missing coordinate to q,
    # followed by the source's declared coordinate order.
    missing = next(j for j in range(9) if not ((q >> j) & 1))
    v = q ^ (1 << missing)
    order = list(range(73))
    order[0], order[missing] = order[missing], order[0]
    return tuple((1 << j) ^ (v if (v >> j) & 1 else 0) for j in order)


def chart_contract(columns, expected_axes, ambient=73):
    require(len(columns) == ambient, 'complete chart')
    orthonormal(columns, ambient)
    width = len(expected_axes)
    require(tuple(columns[:width]) == tuple(expected_axes), 'ordered active-axis binding')


def reject(name, call):
    try:
        call()
    except (ValueError, KeyError, IndexError):
        return name
    raise ValueError('control unexpectedly accepted: ' + name)


def audit_selected(data):
    word, hosted, template, phases = (data[k] for k in ('word', 'hosted', 'template', 'phases'))
    require((word['v'], word['h'], word['R'], phases['m']) == (112, 9, 480, 73), 'selected dimensions')
    require(data['owners'] == template['hosting']['pooled_slots'], 'literal role binding')
    require(len(data['owners']) == hosted['hosted_residuals'] == data['replay']['roles'] == 69120, 'selected roles')
    bases = [port_basis(q) for q in word['ports']]
    for p, b in enumerate(bases):
        orthonormal(b, 73)
        require(phases['recipes'][p]['q'] == word['ports'][p], 'physical port identity')
    widths = []
    for h in range(word['R']):
        start = word['frames'][word['start'][224 + h]]
        final = word['frames'][word['final'][224 + h]]
        require(rank(start + final) == rank(final), 'nested helper frames')
        widths.append(rank(final) - rank(start))
    require(set(widths) == {4, 5, 7, 8, 9}, 'selected widths')
    charts = data['sigmas']
    require(len(charts) == hosted['unique_actual_73column_sigmas'] == data['replay']['actual_73_axis_charts'] == 10002, 'selected charts')
    for name, columns in charts.items():
        require(hashlib.sha256(json.dumps(columns, separators=(',', ':')).encode()).hexdigest() == name, 'chart content hash')
        require(len(columns) == 73, 'chart dimension')
        orthonormal(columns, 73)
    calls = {(c['stage'], c['replica']): c for c in template['calls']}
    require(len(calls) == 144, 'selected complete calls')
    used, signatures, route_cache, role_keys = set(), {}, {}, set()
    stream = hashlib.sha256()
    count_by_width = Counter()
    first_role = None
    for role in data['owners']:
        stage, rep, helper, family = (role[k] for k in ('stage', 'replica', 'helper', 'family'))
        key = (stage, rep, helper)
        require(key not in role_keys, 'duplicate role')
        role_keys.add(key)
        call = calls[stage, rep]
        actual_family, route = call['owners'][224 + helper]
        require(actual_family == family and role['time'] == call['time'], 'call route binding')
        port, child, offset, width = (role[k] for k in ('port', 'child', 'offset', 'width'))
        require(width == widths[helper] and 0 <= port < 112 and family % 112 == port, 'role width/port')
        require(role['copy'] == role['owner_replica'] * 112 + port, 'owner copy')
        pending = phases['recipes'][port]['idle_children'][child]['orthogonal_axes']
        require(type(offset) is int and offset >= 0 and offset + width <= len(pending), 'pending slice bounds')
        active = tuple(pending[offset:offset + width])
        route_key = (port, child, offset, width)
        if route_key not in route_cache:
            b = bases[port]
            positions = [b.index(q) for q in active]
            spectators = [j for j in range(73) if j not in positions][:9 - width]
            expected_route = [3, child, offset] if width == 9 else [4, child, offset, width, spectators]
            order = positions + spectators + [j for j in range(73) if j not in positions and j not in spectators]
            columns = tuple(b[j] for j in order)
            name = hashlib.sha256(json.dumps(columns, separators=(',', ':')).encode()).hexdigest()
            require(name in charts and tuple(charts[name]) == columns, 'missing literal emitted chart')
            require(columns[:width] == active, 'pending active columns')
            route_cache[route_key] = (name, expected_route)
        name, expected_route = route_cache[route_key]
        require(route == expected_route, 'literal residual/spectator route')
        used.add(name)
        signatures[name, width] = active
        stream.update(json.dumps([stage, rep, helper, family, name], separators=(',', ':')).encode() + b'\n')
        count_by_width[width] += 1
        if width == 4 and first_role is None:
            first_role = dict(role=role, chart=name)
    require(role_keys == {(s, r, h) for s in range(9) for r in range(16) for h in range(480)}, 'complete role domain')
    require(used == set(charts), 'unreferenced emitted chart')
    require(stream.hexdigest() == hosted['sigma_stream_sha256'], 'complete chart stream')

    kernel_stream = hashlib.sha256()
    coefficient_checks = mutated_checks = 0
    for (name, width), active in sorted(signatures.items()):
        # Literal physical convolution, subset formula, and chart transport.
        for sign in (-1, 1):
            physical = convolution(active, sign)
            direct = closed_kernel(active, sign)
            coordinate = convolution(tuple(1 << i for i in range(width)), sign)
            transported = {linear(charts[name], z): value for z, value in coordinate.items()}
            require(physical == direct == transported, 'exact normalized residual kernel')
            coefficient_checks += len(physical)
            kernel_stream.update(canonical([name, width, sign, sorted(physical.items())]) + b'\n')
        change = tuple((15 ^ (1 << i)) if i < 4 else (1 << i) for i in range(width))
        alternative = rebased(active, change)
        require(defect(change) == 15, 'four-axis defect')
        bad, good = closed_kernel(alternative), closed_kernel(active)
        require(bad[0] == good[0] and bad[active[0]] == tuple(-a for a in good[active[0]]), 'same-projector phase witness')
        mutated_checks += 1

    role, name = first_role['role'], first_role['chart']
    original = tuple(charts[name])
    change = tuple((15 ^ (1 << i)) if i < 4 else (1 << i) for i in range(73))
    mutant = rebased(original, change)
    orthonormal(mutant, 73)
    require(projector(original[:4], 73) == projector(mutant[:4], 73), 'same active projector')
    require(original[4:] == mutant[4:], 'unchanged spectator completion')
    good, bad = convolution(original[:4]), convolution(mutant[:4])
    require(good == closed_kernel(original[:4]) and bad == closed_kernel(mutant[:4]), 'literal four-axis witness')
    require(set(good) == set(bad) and all(a*a+b*b == 16 for a,b in good.values()), 'same nonzero support/magnitudes')
    require(good[0] == bad[0] and good[original[0]] != bad[original[0]], 'not a global phase')
    controls = [reject('same-projector orthogonal phase mutant', lambda: chart_contract(mutant, original[:4]))]
    repeated = list(original); repeated[-1] = repeated[0]
    controls.append(reject('repeated spectator axis', lambda: chart_contract(repeated, original[:4])))
    swapped = list(original); swapped[0], swapped[4] = swapped[4], swapped[0]
    controls.append(reject('active/spectator swap', lambda: chart_contract(swapped, original[:4])))
    controls.append(reject('missing chart column', lambda: chart_contract(original[:-1], original[:4])))
    controls.append(reject('out-of-range axis', lambda: chart_contract(original[:-1] + (1 << 73,), original[:4])))
    controls.append(reject('dependent kernel', lambda: closed_kernel((1, 1))))
    positive = tuple(63 ^ (1 << i) for i in range(6))
    require(defect(positive) == 0 and convolution(positive) == convolution(tuple(1 << i for i in range(6))), 'positive nonpermutation rebase')
    require(convolution(tuple(reversed(original[:4]))) == good, 'positive axis permutation')
    sample = dict(first_role)
    sample.update(original_active=original[:4], mutated_active=mutant[:4],
                  displacement=original[0], same_projector=True, same_spectators=True,
                  expected_amplitude=[str(Fraction(a,16)) for a in good[original[0]]],
                  mutated_amplitude=[str(Fraction(a,16)) for a in bad[original[0]]],
                  zero_displacement_amplitude=[str(Fraction(a,16)) for a in good[0]],
                  spectator_fiber_inputs=[0, original[4]],
                  affected_displacements=sum(good[x] != bad[x] for x in good), total_displacements=len(good))
    return dict(roles=len(role_keys), calls=len(calls), full_charts=len(charts),
                chart_gram_entries=len(charts)*73*73, width_inventory=dict(sorted(Counter(widths).items())),
                roles_by_width=dict(sorted(count_by_width.items())), active_chart_signatures=len(signatures),
                kernel_coefficients_both_signs=coefficient_checks, kernel_stream_sha256=kernel_stream.hexdigest(),
                chart_stream_sha256=stream.hexdigest(), same_projector_mutated_signatures=mutated_checks,
                witness=sample, controls=controls,
                positive_controls=['axis permutation', 'six-axis nonpermutation Z4-preserving rebase'])


def run(root):
    data, pins = inputs(root)
    return dict(status='PASS_SELECTED1094_CHART_PHASE', sources=pins,
                selected=audit_selected(data), orthogonal_census=census(),
                scope='Exact source-bound residual chart and phase audit, conditional on normalized local endpoints; no current production defect, new supplier, runtime or kappa claim.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', type=Path, default=HERE.parents[1])
    ap.add_argument('--receipt', type=Path)
    ap.add_argument('--write-expected', action='store_true')
    args = ap.parse_args()
    if args.receipt:
        require(not args.receipt.exists(), 'receipt already exists')
    expected = HERE / 'EXPECTED.json'
    if args.write_expected:
        require(not expected.exists(), 'expected receipt already exists')
    result = load_bytes(canonical(run(args.source_root.resolve())))
    if args.write_expected:
        with expected.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
    else:
        require(result == read(expected), 'complete receipt mismatch')
    if args.receipt:
        with args.receipt.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
    print(result['status'], 'roles=' + str(result['selected']['roles']),
          'charts=' + str(result['selected']['full_charts']), 'no_new_kappa')
    print('receipt_sha256', digest(result))


if __name__ == '__main__':
    main()
