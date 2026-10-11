"""Bind fresh evidence; project named transport, clock and display-only fields.

Prepared with OpenAI Codex assistance. Apache-2.0; native notices apply.
"""
from pathlib import Path
from hashlib import sha256
import copy
import gzip
import json
import math


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode() + b'\n'


def semantic(value):
    return sha256(canonical(value)).hexdigest()


def full_word_science(payload):
    """Omit only native discovery display floats, after raw receipt binding.

    These two fields are produced after construction by floating-point
    bisection. They are not consumed by any native admission or price check.
    Exact rational prices, the complete word and every other report field
    remain bound by the resulting canonical hash.
    """
    value = json.loads(payload)
    report = value['report']
    for key in ('complex_coarse_float', 'gain_percent_float'):
        display = report.pop(key)
        assert type(display) is float and math.isfinite(display)
    return value


def complex_science(fresh, primitive_receipt):
    fresh = Path(fresh)
    native = fresh / 'split-centres'
    result = read(fresh / 'RESULT.json')
    assert result['status'] == 'PASS_CONDITIONAL_SPLIT_CENTRE_ASSEMBLY'
    assert result['phase_mode'] == 'full replay'
    assert result['manifest_sha256'] == '3129eb4321f706542470f8443f66a6b4351a12a9ceec85e7f76aa19db1e1e32f'
    assert result['verification_steps'] == [
        'hamming_packets', 'complex_construct', 'complex_audit', 'complex_emit',
        'complex_phases', 'bit_construct', 'bit_export', 'bit_global', 'bit_audit',
        'bit_price', 'complex_integrate', 'complex_replay', 'combined']
    audit = read(native / 'SCALAR-FRAME-AUDIT.json')
    phases = read(native / 'CLIFFORD-REVIEW.json')
    integration = read(native / 'INTEGRATION.json')
    independent = read(native / 'INDEPENDENT-REPLAY.json')
    primitive = read(primitive_receipt)
    word = gzip.decompress((native / 'CANONICAL-WORD.json.gz').read_bytes())
    full_word = gzip.decompress((native / 'FULL-WORD.json.gz').read_bytes())
    template = gzip.decompress((native / 'GLOBAL-TEMPLATE.json.gz').read_bytes())
    word_hash = sha256(word).hexdigest()
    template_hash = sha256(template).hexdigest()
    assert integration['canonical_word_sha256'] == audit['canonical_word_sha256'] == phases['canonical_word_sha256'] == digest(native / 'CANONICAL-WORD.json.gz')
    assert audit['full_word_sha256'] == digest(native / 'FULL-WORD.json.gz')
    full_hash = semantic(full_word_science(full_word))
    assert integration['scalar_audit_sha256'] == digest(native / 'SCALAR-FRAME-AUDIT.json')
    assert integration['exact_phase_receipt_sha256'] == digest(native / 'CLIFFORD-REVIEW.json')
    assert integration['global_template_sha256'] == independent['template_sha256'] == template_hash
    assert phases['recipe_sha256'] == digest(native / 'CLIFFORD-RECIPES.json')
    assert json.loads(template)['exact_local_clifford_recipe_sha256'] == phases['recipe_sha256']
    assert independent['status'] == 'PASS_INDEPENDENT_NEW_STRUCTURAL_IR_REPLAY'
    assert independent['all_eight_global_scalar_columns'] and independent['bank_owners_and_padding_exact']
    assert set(independent['mutation_controls_rejected']) == {
        'wrong_scale', 'missing_center', 'wrong_common_frame', 'wrong_child_rank',
        'missing_padding', 'aliased_owner', 'missing_cover_phase'}
    assert phases['all_child_equalities_include_global_phase'] and phases['directed_edges'] == 2918
    assert phases['frames'] == audit['frames'] == 956 and phases['endpoint_adapters'] == 240
    assert audit['live_columns_each_orientation'] == 800 and audit['arbitrary_helper_columns'] == 560
    assert audit['all_live_source_and_helper_rows_restored'] and audit['all_target_rows_correct']
    assert audit['transported_ports_exactly_match_fixed_routes']
    assert integration['global_profile'] == independent['paid_profile']
    assert (integration['m'], integration['R'], integration['live'], integration['physical']) == (73, 560, 12720, 13298)
    assert integration['rank_mass'] == 73 * 12720 - 2496
    assert primitive['status'] == 'PASS_INDEPENDENT_LITERAL_PRIMITIVES_ALL800_COLUMNS_AND_ACTUAL_PAYMENT'
    assert primitive['canonical_word_sha256'] == digest(native / 'CANONICAL-WORD.json.gz')
    assert primitive['global_template_sha256'] == digest(native / 'GLOBAL-TEMPLATE.json.gz')
    assert primitive['canonical_word_uncompressed_sha256'] == word_hash
    assert primitive['global_template_uncompressed_sha256'] == template_hash
    for orientation in ('forward', 'backward'):
        p = primitive['orientations'][orientation]
        assert p['columns'] == 800 and p['all_live_endpoints_exact'] and p['private_work_zero']
        assert p['omitted_actual_first_halve_rejected']
        assert p['real_component_primitives'] == integration['local_program_checks'][orientation]['real_component_primitive_bound']
    # Native receipts and raw compressed inputs are fully bound above. Replace
    # only transport hashes, elapsed times and the two unused display floats
    # named in full_word_science in this portable projection.
    audit = copy.deepcopy(audit)
    phases = copy.deepcopy(phases)
    integration = copy.deepcopy(integration)
    primitive = copy.deepcopy(primitive)
    assert isinstance(audit.pop('seconds'), (int, float))
    assert isinstance(phases.pop('seconds'), (int, float))
    audit['canonical_word_sha256'] = phases['canonical_word_sha256'] = integration['canonical_word_sha256'] = word_hash
    audit['full_word_sha256'] = full_hash
    integration['scalar_audit_sha256'] = semantic(audit)
    integration['exact_phase_receipt_sha256'] = semantic(phases)
    primitive['canonical_word_sha256'] = word_hash
    primitive['global_template_sha256'] = template_hash
    assert result['complex_template_sha256'] == template_hash
    projected_result = result
    return dict(native_result=projected_result, scalar_frames=audit,
                exact_phases=phases, integration=integration,
                independent_template=independent, actual_primitives=primitive,
                canonical_word_uncompressed_sha256=word_hash,
                full_word_scientific_sha256=full_hash,
                global_template_uncompressed_sha256=template_hash,
                projection='All mathematical and interface fields retained. Raw native inputs and receipts are checked first; compressed transport hashes and elapsed seconds are projected or rebound. Only report.complex_coarse_float and report.gain_percent_float, unused native discovery displays, are omitted from the canonical full-word hash.')
