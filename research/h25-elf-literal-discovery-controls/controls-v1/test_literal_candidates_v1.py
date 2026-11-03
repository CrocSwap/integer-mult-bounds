"""SOURCE ONLY: new synthetic data controls. Never call helper.main or target.

Actual execution requires a separate parent grant. Required CLI pins bind the
reviewed NEW v2 helper. Old v1 remains preserved as rejected provenance.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import types

HISTORICAL_V1_SHA = 'c9044f4926cbcc880eb17b579b2cd6e323f1657bf6b6463138fc0b4310fe4b04'
V2_SHA = '56b44235f55685d61e5c8b8099d825b4ec5a53987910f506dffad309c12ffb53'
V2_BYTES = 11809
BUILDER_SHA = '979f719820707490920bf39f3c398129ed6e49b2df898e76a1f7292cc8d8d47d'
BUILDER_BYTES = 3022


class ControlFailure(RuntimeError):
    pass


def need(value, reason):
    if not value:
        raise ControlFailure(reason)


def pinned(raw, size, digest):
    need(type(raw) is bytes and len(raw) == size, 'source size pin')
    need(hashlib.sha256(raw).hexdigest() == digest, 'source digest pin')


def load_checked(path, size, digest, tag):
    raw = path.read_bytes()
    pinned(raw, size, digest)  # BEFORE any compilation/import of NEW source.
    module = types.ModuleType('new_c05_synthetic_' + tag + '_' + digest[:16])
    module.__file__ = str(path)
    # Use the checked bytes; do not re-read a path after the pin check.
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    need(module.__name__ != '__main__', 'main guard identity')
    return module


def unqualified(row):
    for key in ('relocation_effects_audited', 'instruction_boundaries_validated',
                'source_role_qualified', 'D_applicability_qualified',
                'certificate_feasible', 'full_C05', 'full_V03'):
        need(row.get(key) is False, 'promotion of ' + key)
    for ref in row['references']:
        need(ref['instruction_boundary_validated'] is False, 'candidate boundary promoted')


def has(row, kind, offset, pc, target):
    return any(r['kind'] == kind and r['file_offset'] == offset and
               r['link_pc_or_slot'] == pc and r['candidate_target'] == target
               for r in row['references'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--helper', required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args(argv)
    own = Path(__file__).resolve().parent
    expected = own.parent / 'repair-v2/passive_image_candidates_v2.py'
    need(Path(args.helper).is_absolute() and Path(args.helper).resolve() == expected.resolve(),
         'only the reviewed NEW helper path allowed')
    need(args.sha256 == V2_SHA, 'unreviewed helper hash/old v1 not executable here')
    fixture = load_checked(own / 'literal_fixtures_v1.py', BUILDER_BYTES, BUILDER_SHA, 'fixtures')
    helper = load_checked(expected, V2_BYTES, V2_SHA, 'locator')
    data = fixture.fixtures()
    need(len(data) == 20 and all(type(x) is bytes for x in data.values()), 'fixture set differs')
    passed, failed = [], []
    def case(name, action):
        try:
            action(); passed.append(name)
        except Exception as exc:
            failed.append({'case': name, 'error': type(exc).__name__ + ': ' + str(exc)[:400]})
    def inspect(name, offset=640):
        row = helper.inspect(data[name], literal_offset=offset)
        unqualified(row)
        return row
    def expect_stop(name, body=None, offset=640):
        try:
            helper.inspect(data[name] if body is None else body, literal_offset=offset)
        except helper.Stop:
            return
        raise ControlFailure('required mapping/format STOP absent: ' + name)
    def mapping_and_lea():
        r = inspect('S01')
        need(r['literal_link_address'] == 0x400180 and r['ELF_type'] == 2, 'manual map')
        need(has(r, 'CANDIDATE_REXW_LEA_RIP_DISP32', 512, 0x400100, 0x400180), 'manual LEA')
    case('S01_literal_mapping_and_LEA_candidate', mapping_and_lea)
    case('S02_absolute_imm64', lambda: need(has(inspect('S02'), 'CANDIDATE_REXW_MOV_IMM64',
                                             512, 0x400100, 0x400180), 'MOV imm64'))
    case('S03_zeroextended_imm32', lambda: need(has(inspect('S03'), 'CANDIDATE_MOV_R32_IMM32_ZEROEXT',
                                                 512, 0x400100, 0x400180), 'MOV imm32'))
    def interior_boundary():
        r = inspect('S04')
        need(has(r, 'CANDIDATE_REXW_LEA_RIP_DISP32', 514, 0x400102, 0x400180), 'interior raw candidate')
        need(r['instruction_boundaries_validated'] is False, 'false interior instruction accepted')
    case('S04_interior_pattern_stays_unvalidated', interior_boundary)
    case('S05_no_discovery_not_unused_proof', lambda: need(inspect('S05')['references'] == [], 'dead literal'))
    case('S06_overwrite_not_semantically_qualified', lambda: need(
         inspect('S06')['certificate_feasible'] is False, 'overwrite semantic inference'))
    for name in ('S07', 'S08', 'S09', 'C01', 'C02', 'TRUNC_PHDR', 'SHORT_HEADER',
                 'SEGMENT_WRAP', 'WRONG_ENDIAN', 'WRONG_MACHINE'):
        case(name + '_required_STOP', lambda name=name: expect_stop(name))
    def ninth_reference():
        r = inspect('S10')
        need(r['status'] == 'STOP_CANDIDATE_CAP' and r['candidate_overflow'] is True,
             'candidate cap not STOP')
        need(len(r['references']) == 8, 'retained candidate bound')
    case('S10_ninth_reference_cap', ninth_reference)
    def symbolic_bias():
        r = inspect('S14')
        need(r['ELF_type'] == 3 and r['load_bias'] == 'symbolic beta' and
             r['literal_link_address'] == 0x400180, 'ET_DYN bias incorrectly concrete')
    case('S14_symbolic_load_bias', symbolic_bias)
    case('X01_signextended_imm32', lambda: need(has(inspect('X01'),
         'CANDIDATE_REXW_MOV_IMM32_SIGNEXT', 512, 0x400100, 0x400180), 'signext immediate'))
    def slot_reference():
        r = inspect('X02_SLOT', 768)
        need(r['literal_link_address'] == 0x500080, 'second segment literal')
        need(has(r, 'RAW_LE64_LITERAL_ADDRESS', 704, 0x500040, 0x500080), 'literal slot')
        need(has(r, 'CANDIDATE_REXW_MOV_FROM_RIP_SLOT', 512, 0x400100, 0x500040), 'RIP slot')
    case('X02_pointer_slot_and_RIP_reference', slot_reference)
    case('literal_expected_span_shift_STOP', lambda: expect_stop('S01', offset=641))
    def pin_negative(size, digest):
        try:
            pinned(b'abc', size, digest)
        except ControlFailure:
            return
        raise ControlFailure('wrong source pin accepted')
    case('loader_wrong_size_before_compile', lambda: pin_negative(2, hashlib.sha256(b'abc').hexdigest()))
    case('loader_wrong_hash_before_compile', lambda: pin_negative(3, '0' * 64))
    result = {'schema': 'new-literal-candidate-synthetic-controls-result-v1',
              'status': 'PASS_DISCOVERY_CONTROLS_ONLY' if not failed else 'FAIL',
              'python_optimize': sys.flags.optimize, 'case_count': len(passed) + len(failed),
              'passed_count': len(passed), 'failed_count': len(failed),
              'passed': passed, 'failures': failed, 'helper_sha256': V2_SHA,
              'old_v1_preserved_failed_source': HISTORICAL_V1_SHA,
              'semantic_falsifiers_not_implemented': ['S11 role/reachability',
                  'S12 relocation effects', 'S13 private-call/alias effects'],
              'main_or_actual_driver_called': False, 'full_C05': False, 'full_V03': False,
              'certificate_feasibility_established': False, 'original_credit': 0,
              'costs': 'OPEN_NOT_ZERO'}
    print(json.dumps(result, sort_keys=True))
    return 0 if not failed else 1


if __name__ == '__main__':
    try:
        exit_code = main()
    except Exception as exc:
        print(json.dumps({'status': 'PREFLIGHT_REFUSAL', 'case_count': 0,
              'passed_count': 0, 'failed_count': 0, 'preflight_failure_count': 1,
              'error': type(exc).__name__ + ': ' + str(exc)[:400],
              'main_or_actual_driver_called': False, 'full_C05': False, 'full_V03': False}))
        exit_code = 2
    raise SystemExit(exit_code)
