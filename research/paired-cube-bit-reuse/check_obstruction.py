#!/usr/bin/env python3
"""Exact obstruction to compensated reuse into the selected bit gauges.

Every selected gauge excludes every source incidence line. Every eligible
donor endpoint contains a source incidence line. Therefore the complete
donor/recipient compatibility graph is empty, before lifetime restrictions.
This is a finite certificate, not a claim about alternative gauge compilers.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def source_obstructions(checker, frames):
    """Record an explicit nonzero integer annihilator pairing for every line."""
    witnesses = []
    for frame in sorted(set(frames)):
        for source, vector in enumerate(checker.chi):
            obstruction = next(((i, checker_dot(row, vector))
                                for i, row in enumerate(checker.A[frame])
                                if checker_dot(row, vector)), None)
            need(obstruction is not None, 'selected gauge contains a source line')
            witnesses.append((frame, source, *obstruction))
    return witnesses


def checker_dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def donor_witness(checker, role, frame, node):
    support = checker.sup[node]
    need(support > 0, 'eligible donor has nonempty conservative source support')
    source = (support & -support).bit_length()-1
    need(checker.in_frame(checker.chi[source], frame),
         'donor endpoint contains its nonempty source-support witness')
    return role, frame, node, source


def rejected(action, name):
    try:
        action()
    except ValueError:
        return {'mutation': name, 'result': 'REJECTED'}
    raise ValueError('mutation accepted: '+name)


def certificate(source, plan=None, source_commit=None):
    source = source.resolve()
    base = source/'research/paired-cube-bit'
    checker_path = base/'check_paired_cube_bit.py'
    spec = importlib.util.spec_from_file_location('bit_reuse_input_checker', checker_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checker = module.Checker(base/'out', 12)
    checker.frames()
    checker.decoder()
    checker.geometry()
    checker.chains()
    word, h = checker.w, checker.h
    operations = word['ops']
    opframes = [checker.nf[node] for _, _, node in operations]
    changed = []
    if plan is not None:
        plan = plan.resolve()
        document = json.loads(plan.read_text())
        need(document['p'] == 12, 'frame plan parameter')
        seen = set()
        for operation, rows in document['frames']:
            need(type(operation) is int and 0 <= operation < len(operations)
                 and operation not in seen, 'one valid plan entry per operation')
            need(all(len(row) == h and all(type(x) is int for x in row)
                     for row in rows), 'integer frame plan rows')
            seen.add(operation)
            basis, _ = module.reduce_rows(rows, h)
            frame = max(checker.B)+1
            annihilator, _ = module.kernel(basis, h)
            checker.B[frame], checker.A[frame] = basis, annihilator
            checker.dimf[frame] = len(basis)
            need(checker.nondeg(frame), 'planned frame nondegenerate over Q')
            node = operations[operation][2]
            bits = checker.sup[node]
            while bits:
                low = bits & -bits
                need(checker.in_frame(checker.chi[low.bit_length()-1], frame),
                     'planned frame contains complete conservative source support')
                bits -= low
            opframes[operation] = frame
            changed.append(operation)

    gauges = word['gauges']
    gauge_frames = [g['frame'] for g in gauges]
    line_witnesses = source_obstructions(checker, gauge_frames)
    root_roles = set(word['rootroles'])
    starts = {role: word['source_frame'][int(leaf)]
              for leaf, role in word['sources'].items()}
    starts.update({g['role']: g['frame'] for g in gauges})
    current = dict(starts)
    endpoints = {}
    for operation, (a, b, node) in enumerate(operations):
        frame = opframes[operation]
        for role in (a, b):
            need(role not in current or checker.sub(current[role], frame),
                 'actual operation frame chain nested')
            current[role] = frame
            endpoints[role] = (frame, node)
    for j, role in enumerate(word['rootroles']):
        need(checker.sub(current[role], word['root_frame'][j]),
             'actual endpoint contained in its root frame')
    eligible = set(range(checker.prof['R']))-root_roles
    need(eligible <= endpoints.keys(), 'every non-root donor has an endpoint')
    donor_witnesses = [donor_witness(checker, role, *endpoints[role])
                       for role in sorted(eligible)]
    controls = [rejected(lambda: source_obstructions(checker, [word['full_frame']]),
                         'replace_selected_gauge_by_full_space')]
    zero = max(checker.B)+1
    checker.B[zero] = []
    checker.A[zero] = [tuple(int(i == j) for i in range(h)) for j in range(h)]
    checker.dimf[zero] = 0
    role = min(eligible)
    controls.append(rejected(lambda: donor_witness(checker, role, zero, endpoints[role][1]),
                             'erase_donor_source_support'))
    inputs = [checker_path]+[base/'out'/f'{name}_p12.json'
                             for name in ('graph', 'word', 'frames', 'kchron', 'profile')]
    if plan is not None:
        inputs.append(plan)
    pins = {str(path.relative_to(source)).replace('\\', '/'): sha256(path.read_bytes()).hexdigest()
            for path in inputs}
    head = subprocess.check_output(['git', '-C', str(source), 'rev-parse',
                                    (source_commit or 'HEAD')+'^{commit}'],
                                   text=True).strip()
    committed = {}
    for relative in pins:
        obj = subprocess.check_output(['git', '-C', str(source), 'rev-parse',
                                       head+':'+relative], text=True).strip()
        working = subprocess.check_output(['git', '-C', str(source), 'hash-object',
                                           '--path='+relative, relative], text=True).strip()
        need(obj == working, 'source input matches recorded commit: '+relative)
        committed[relative] = obj
    return {
        'status': 'PASS exact empty compatibility graph',
        'source_commit': head,
        'input_sha256': pins,
        'committed_input_objects': committed,
        'source_inputs_match_recorded_commit': True,
        'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'p': 12, 'h': h, 'source_ports': checker.v,
        'logical_auxiliary_roles': checker.prof['R'],
        'selected_gauge_roles': len(gauges),
        'unique_selected_gauge_frames': len(set(gauge_frames)),
        'selected_gauge_dimensions': dict(sorted(Counter(g['dim'] for g in gauges).items())),
        'source_line_obstruction_checks': len(line_witnesses),
        'source_lines_contained_in_selected_gauges': 0,
        'integer_annihilator_witnesses_sha256': digest(line_witnesses),
        'eligible_non_root_donor_roles': len(eligible),
        'donor_endpoint_source_witness_checks': len(donor_witnesses),
        'donor_endpoint_witnesses_sha256': digest(donor_witnesses),
        'candidate_role_pairs_excluded_by_geometry': len(eligible)*len(gauges),
        'compatible_geometry_edges': 0,
        'legal_geometry_and_chronology_edges': 0,
        'modified_operation_frames_checked': len(changed),
        'controls': controls,
        'argument': 'For every selected gauge and every source incidence vector, an explicit '
                    'nonzero integer annihilator pairing excludes that line. Every eligible '
                    'donor endpoint contains an explicitly checked source incidence line. '
                    'Consequently no donor endpoint is contained in any selected gauge. '
                    'This proves the entire compatibility graph empty before read deadlines.',
        'scope': 'Fixed selected gauge spaces and the checked conservative-support donor '
                 'model. The obstruction persists under any donor frame changes retaining '
                 'a nonempty source incidence line, including valid frame ascents and descents, '
                 'and under gauge shrinkage. It does not exclude different gauge spaces, '
                 'different target read chains, or a different compiler. This certifies no '
                 'moment improvement and no general optimality or all-size theorem.'}


def main():
    need(not sys.flags.optimize, 'refusing -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[2],
                        help='repository source checkout (default: this repository)')
    parser.add_argument('--source164', type=Path, help='reproduce PR164, including its selected frame plan')
    parser.add_argument('--plan', type=Path, help='optional operation-frame plan inside source checkout')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--commit', help='recorded input commit; --check uses the saved certificate commit')
    parser.add_argument('--check', action='store_true', help='recompute and compare an existing certificate')
    args = parser.parse_args()
    if args.source164 is not None:
        need(args.plan is None, '--source164 selects its own frame plan')
        args.source = args.source164
        args.plan = args.source/'research/paired-cube-bit-descent/descent.json'
    if args.out is None:
        args.out = Path(__file__).with_name('pr164-obstruction.json' if args.source164 else
                                          'pr168-obstruction.json')
    if args.check and args.commit is None:
        args.commit = json.loads(args.out.read_text())['source_commit']
    result = certificate(args.source, args.plan, args.commit)
    serialized = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.check:
        need(args.out.read_text() == serialized, 'certificate reproduces byte for byte')
    else:
        args.out.write_text(serialized, encoding='utf-8', newline='\n')
    print(json.dumps({key: result[key] for key in
                      ('status', 'source_commit', 'source_line_obstruction_checks',
                       'candidate_role_pairs_excluded_by_geometry', 'compatible_geometry_edges')},
                     sort_keys=True))


if __name__ == '__main__':
    main()
