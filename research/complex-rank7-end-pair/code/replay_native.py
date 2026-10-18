"""Run unchanged native checks on an explicit raw complex supplier word."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_sha(path):
    return hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def need(value, message):
    if not value:
        raise ValueError(message)


def cold_control_census(word):
    meta = word['refactored_cleanup']
    registers = lambda gate: gate[1:3] if gate[0] == 'add' else gate[1:2]
    entering = list(map(int, meta.get('entering_low_frame_ended_helpers', [])))
    premix = word['A'][:meta['premix_gates']]
    cold = list(map(int, meta['cold_low_frame_ended_helpers']))
    hyperplanes = [helper for helper in cold if len(word['helper_final'][str(helper)]) == 8]
    absorptions = meta.get('forward_absorption_A_indices', [])
    ended = set(map(int, word['helper_final']))
    tail = [(index, word['cleanup'][index], frame) for index, frame in word['early_cleanup']]
    accumulators = set()
    for position, (_, gate, frame) in enumerate(tail):
        if (gate[0] == 'add' and gate[1] not in ended and gate[2] not in ended and len(frame) < 8
                and any(later[0] == 'add' and later[2] == gate[1] and later[1] in hyperplanes
                        for _, later, _ in tail[position + 1:])):
            accumulators.add(gate[1])
    return {'common': 14, 'entering_ends': 3 * len(entering),
            'entering_premix': 3 * sum(any(helper in registers(gate) for gate in premix) for helper in entering),
            'premix_target_writes': 5 if meta.get('premix_target_writes', 0) else 0,
            'forward_absorptions': 7 if absorptions else 0,
            'shared_anchor_and_release': 5 if hyperplanes and absorptions else 0,
            'dimension_eight_ends': 3 * len(hyperplanes), 'factored_accumulators': 2 * len(accumulators)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('ancestor-package', 'dependency', 'raw', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--expected-local-pins', type=Path)
    ap.add_argument('--finalize-completed', action='store_true',
                    help='Validate existing successful stage logs and finalize their receipt without rerunning checks')
    args = ap.parse_args()
    need(__debug__, 'Assertions must remain enabled')
    ancestor, dep, raw, out = [getattr(args, name).resolve()
                               for name in ('ancestor_package', 'dependency', 'raw', 'out')]
    need(out.is_dir() if args.finalize_completed else not out.exists(), 'Use the required output directory state')
    need(not any(out.is_relative_to(p) for p in (ancestor, dep)), 'Output must be outside source packages')
    completed_stages = read(out / 'STAGES.json') if args.finalize_completed else []
    if not args.finalize_completed:
        out.mkdir(parents=True)
    else:
        need(not (out / 'RESULT.json').exists() and not (out / 'RECEIPT.json').exists(),
             'Only incomplete receipt finalization may be resumed')
    root = ancestor / 'vendor/main'
    source = root / 'research/complex-k492-owner-repair/vendor/multicold'
    pr635 = ancestor / 'vendor/pr635/research/complex-571-cold14-st2'
    base = source / 'vendor/pr558'
    parent = base / 'vendor/pr552'
    routing = parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(source), GAIN_PR564_SOURCE=str(source))
    for key in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD',
                'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'PR635_CODE', 'SW4_PIN'):
        env.pop(key, None)
    stages = []
    inputs = {'raw_word_content': payload_sha(raw), 'raw_word_file': sha(raw),
              'ancestor_manifest': sha(ancestor / 'MANIFEST.json'),
              'dependency_manifest': sha(dep / 'MANIFEST.json')}
    started = time.monotonic()

    def run(name, script, *arguments, portable=True, extra_env=None):
        print('RUN', name, flush=True)
        cmd = [sys.executable, '-B'] + ([str(source / 'code/run_portable.py')] if portable else [])
        cmd += [str(script), *map(str, arguments)]
        log = out / (name + '.log')
        if args.finalize_completed:
            need(len(stages) < len(completed_stages), 'Missing completed checker stage')
            record = completed_stages[len(stages)]
            need(record['name'] == name and record['command'] == cmd and record['exit_code'] == 0
                 and record['script_sha256'] == sha(script) and record['log_sha256'] == sha(log),
                 'Completed checker stage binding: ' + name)
            stages.append(record)
            print('VERIFIED_COMPLETED', name, flush=True)
            return
        before = time.monotonic()
        with log.open('w') as stream:
            result = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT,
                                    env=dict(env, **(extra_env or {})))
        stages.append({'name': name, 'command': cmd, 'script_sha256': sha(script),
                       'exit_code': result.returncode, 'seconds': time.monotonic() - before,
                       'log_sha256': sha(log)})
        dump(out / 'STAGES.json', stages)
        if result.returncode:
            raise RuntimeError(name + ' failed:\n' + log.read_text()[-8000:])
        print('PASS', name, flush=True)

    run('ancestor-manifest', ancestor / 'verify_manifest.py', portable=False)
    run('dependency-manifest', dep / 'verify_manifest.py', portable=False)
    local = out / 'local'
    run('independent-raw-audit', dep / 'independent/audit_local.py', '--word', raw,
        '--main', root, '--output', out / 'INDEPENDENT-AUDIT.json', portable=False)
    run('native', pr635 / 'code/hpe_audit_and_transport.py', '--raw', raw,
        '--routing', routing, '--out', local)
    run('ledgers', pr635 / 'code/hpe_emit_local.py', local)
    run('local-replay', pr635 / 'code/hpe_audit_local.py', local)
    run('wrappers', pr635 / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz',
        local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    run('cold-end-controls', dep / 'construction/layers_p6n/layer_end_controls.py', raw,
        routing, out / 'controls', extra_env={'PR635_CODE': str(pr635 / 'code')})
    run('phases', base / 'code/phases_full.py', local,
        parent / 'complex-global/vendor531/vendor/clifford')
    need(not args.finalize_completed or len(stages) == len(completed_stages), 'Complete stage census')
    audit = read(out / 'INDEPENDENT-AUDIT.json')
    need(audit['status'] == 'PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES'
         and audit['checked_columns'] == 728 and audit['content_sha256'] == inputs['raw_word_content'],
         'Independent raw audit failed or bound to another input')
    native = read(local / 'INDEPENDENT-LOCAL-REPLAY.json')
    need(native['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
         and len(native['negative_controls_rejected']) == 25, 'Incomplete native controls')
    for orientation in ('forward', 'backward'):
        need(native['local'][orientation]['all_exact_columns'] == 728
             and native['local'][orientation]['private_work_erased'], 'Native column restoration')
        need(native['paid_profiles'][orientation] == audit['local_profile'], 'Native paid profile mismatch')
    wrapper = read(local / 'WRAPPER-CHECKS.json')
    need(wrapper['status'] == 'PASS_RESIDUAL_WRAPPERS_ARE_EXACT', 'Residual wrapper failure')
    control = read(out / 'controls/COLD-END-CONTROLS.json')
    cold_census = cold_control_census(read(raw))
    need(control['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS'
         and len(control['rejected']) == len(set(control['rejected'])) == sum(cold_census.values()),
         'Incomplete cold-end controls')
    phase = read(local / 'CLIFFORD-REVIEW.json')
    need(phase['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES'
         and phase['all_child_equalities_include_global_phase'] is True, 'Incomplete phase equality')
    need(phase['canonical_word_sha256'] == sha(local / 'CANONICAL-WORD.json.gz')
         and phase['recipe_sha256'] == sha(local / 'CLIFFORD-RECIPES.json'), 'Stale phase binding')
    checks = read(local / 'LOCAL-CHECKS.json')
    pins = {'canonical_sha256': payload_sha(local / 'CANONICAL-WORD.json.gz'),
            'program_sha256': {o: checks[o]['sha256'] for o in ('forward', 'backward')},
            'clifford_recipes_sha256': sha(local / 'CLIFFORD-RECIPES.json')}
    if args.expected_local_pins:
        expected = read(args.expected_local_pins)
        need(all(expected[k] == value for k, value in pins.items()), 'Nominated native pins differ')
        inputs['expected_local_pins'] = sha(args.expected_local_pins)
    need(payload_sha(raw) == inputs['raw_word_content'] and sha(raw) == inputs['raw_word_file'],
         'Raw input changed during native replay')
    result = {'status': 'PASS_COMPLETE_NATIVE_REPLAY_UNCHANGED_CHECKERS', 'input_sha256': inputs,
              'profile': audit['local_profile'], 'phase_edges': phase['directed_edges'],
              'pins': pins, 'seconds': sum(stage['seconds'] for stage in stages), 'stages': stages,
              'cold_control_census': cold_census, 'cold_controls_rejected': len(control['rejected']),
              'finalized_from_completed_stages': args.finalize_completed,
              'scope': 'Fresh raw/native forward and dual columns, scalar/frame/cones, wrappers, 25 native controls, every applicable cold-end control, and every exact phase edge. Global admission and construction ancestry remain separate.'}
    dump(out / 'RESULT.json', result)
    artifacts = [p for p in out.rglob('*') if p.is_file() and p.name != 'RECEIPT.json']
    dump(out / 'RECEIPT.json', {'status': result['status'],
         'artifacts': {p.relative_to(out).as_posix(): sha(p) for p in artifacts}})
    print(result['status'], json.dumps(result['profile']), flush=True)


if __name__ == '__main__':
    main()
