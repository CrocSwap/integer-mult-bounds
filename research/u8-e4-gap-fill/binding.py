"""Bind checked source, both providers, roles, charts, invoice and arithmetic.

The payload checks follow PR942's final_binding.py, generalized to two providers.
Receipt consistency is not authentication or an all-size proof.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path
from support import P, ROOT, T37, dump, identity, load, read, require, sha, validate_sources


def payload_sha(path):
    return hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()


def check(work, baseline):
    require(__debug__, 'Inherited verifier checks require assertions')
    sources = validate_sources()
    sys.path.insert(0, str(T37))
    predecessor = load(T37 / 'final_binding.py', 'e4_t37_adapter_binding')
    adapters = predecessor.check_adaptations(work)
    require(read(work / 'ANCESTRY-942.json')['status'] == 'PASS_COMPLETE_PR942_COMPOSITION', 'Complete cold ancestry')
    require(read(work / 'ANCESTRY-942.json')['selected_binding'] == read(baseline / 'FINAL-BINDING.json'), 'Ancestry binding receipt')
    claim = read(P / 'CLAIM.json')
    construction = read(work / 'construction/CONSTRUCTION.json')
    require(construction['status'] == 'PASS_LITERAL_E4_AND_T37_OWNER_CONSTRUCTION', 'Literal construction')
    build = load(P / 'build.py', 'e4_readonly_reconstruction')
    word, roles = build.construct(read(baseline / 'native/barch/FULL-WORD.json.gz'), read(T37 / 'OWNERS.json.gz'))
    require(word == read(work / 'construction/WORD.json.gz'), 'Actual raw E4 word')
    require(roles == read(work / 'construction/OWNERS.json.gz'), 'Actual frozen roles')
    require(identity(word) == construction['word_identity'] and identity(roles) == construction['owners_identity'], 'Construction receipt identities')
    require(construction['source_word_sha256'] == sha(baseline / 'native/barch/FULL-WORD.json.gz'), 'Fresh U8 input bytes')
    require(read(work / 'native/local/FULL-WORD.json.gz') == word, 'Native raw source')
    checker = load(P / 'independent.py', 'e4_independent_binding')
    require((work / 'independent_mixed_adapter.py').read_text() == checker.adapted_text(), 'Independent checker source')
    independent = read(work / 'INDEPENDENT-OWNERS.json')
    require(independent['status'] == 'PASS_INDEPENDENT_MIXED_E4_T37_WINDOWS_CHARTS_PREFIX_ROW', 'Independent owner status')
    require(independent['checker_adaptation']['adapter_sha256'] == sha(work / 'independent_mixed_adapter.py'), 'Checker hash')
    for path, digest in independent['input_sha256'].items():
        require(sha(path) == digest, 'Independent owner input bytes: ' + path)
    require(len(independent['controls_rejected']) == 8 and len(independent['omitted_edits_rejected']) == 20, 'Owner mutation coverage')
    g = work / 'strict/global'
    hosted, base = g / 'hosted', g / 'base'
    summary = read(hosted / 'HOSTED.json')
    template = read(hosted / 'GLOBAL-TEMPLATE.json.gz')
    owner = read(g / 'audit/OWNERS-AND-PROFILE.json')
    controller = read(g / 'audit/ASYNC-AUDIT.json')
    invoice = read(g / 'audit/PREFIX-AND-INVOICE.json')
    assembly = read(work / 'strict/ASSEMBLY.json')
    price = read(work / 'INDEPENDENT-PRICE.json')
    plan = read(work / 'lift/PLAN.json')
    spec = read(work / 'runtime/data/SPEC.json')
    require(assembly['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY', 'Strict final admission')
    require(Q(assembly['kappa']) == Q(claim['kappa']) == Q(price['kappa']), 'Kappa agreement')
    require(Q(assembly['complex_lower']) == Q(claim['complex_lower']) == Q(price['root']['endpoint']), 'Complex endpoint agreement')
    require(Q(assembly['bit_lower']) == Q(claim['bit_lower']), 'Bit endpoint')
    require(assembly['complex_profile'] == owner['paid_profile'] == controller['complex_profile'] ==
            independent['profile'] == claim['profile'] == plan['profile'] == spec['expected']['global_profile'], 'Profile agreement')
    require(invoice['provider_counts'] == controller['provider_counts'] == assembly['provider_counts'] ==
            independent['provider_counts'] == claim['provider_counts'], 'Actual mixed dispatch counts')
    expected_dispatch = {(s, r): 'gauge44_e4' if (s, r) == (0, 0) else 'gauge44'
                         for s in range(9) for r in range(37)}
    require({(c['stage'], c['replica']): c['provider_id'] for c in template['calls']} == expected_dispatch, 'Emitted per-call dispatch')
    require({(s, r): p for s, r, p in spec['dispatch']} == expected_dispatch, 'Strict spec dispatch')
    require(template['hosting']['pooled_slots'] == roles, 'Serialized whole owners')
    require(template['hosting']['owner_map_sha256'] == sha(work / 'construction/OWNERS.json.gz'), 'Owner source bytes')
    require(template['async_schedule']['order'] == read(T37 / 'ORDER.json'), 'Unchanged invocation order')
    for key in ('live', 'physical', 'rank_mass', 'deficit'):
        require(owner[key] == independent[key] == claim[key], 'Physical count: ' + key)
    require(owner['hosted_residuals'] == independent['roles'] == 167832, 'Complete helper inventory')
    require(controller['complete_invocations'] == invoice['complete_invocation_sweeps'] == 333, 'Complete sweeps')
    require(invoice['global_prefix_bits'] == independent['prefix_bits'] == 779 <
            invoice['charged_prefix_bits'] == independent['charged_prefix_bits'] == price['charged_prefix_bits'] == 1024, 'Prefix reserve')
    require(invoice['finite']['physical_row_coefficient'] == independent['physical_row_coefficient'] == 17495 < 20161, 'Row reserve')
    require(len(invoice['strict_checks']) == 9 and all(invoice['strict_checks'].values()), 'All nine finite checks')
    require(price['owner_receipt_sha256'] == sha(work / 'INDEPENDENT-OWNERS.json'), 'Independent price inputs')
    require(price['bootstrap'] == assembly['bootstrap'], 'Independent full-payload bootstrap')
    for result in (price, assembly):
        require(len(result['outer']) == 47 and all(Q(v) > 0 for v in result['outer'].values()), 'Strict outer inequalities')
    template_hash = payload_sha(hosted / 'GLOBAL-TEMPLATE.json.gz')
    require(template_hash == summary['template_sha256'] == owner['template_sha256'] ==
            controller['complex_template_sha256'] == invoice['template_sha256'] == assembly['template_sha256'], 'Actual template bytes')
    require(invoice['owner_audit_sha256'] == sha(g / 'audit/OWNERS-AND-PROFILE.json'), 'Invoice owner input')
    require(invoice['controller_audit_sha256'] == sha(g / 'audit/ASYNC-AUDIT.json'), 'Invoice controller input')
    require(read(work / 'lift/GLOBAL-TEMPLATE.json.gz') == read(baseline / 'lift/GLOBAL-TEMPLATE.json.gz'), 'Unchanged checked bank envelope')
    require(invoice['parent_template_sha256'] == identity(read(work / 'lift/GLOBAL-TEMPLATE.json.gz')), 'Invoice parent geometry')
    require(plan['assignment_content_sha256'] == identity(roles) and
            plan['assignment_sha256'] == plan['replica_lift']['owners_file_sha256'] == spec['data']['owners_sha256'] == sha(work / 'construction/OWNERS.json.gz'), 'Plan/spec owner identity')
    require(spec['data']['plan_sha256'] == sha(work / 'lift/PLAN.json'), 'Spec plan bytes')
    binding = read(g / 'BINDING.json')
    require(binding['source_plan_sha256'] == sha(work / 'lift/PLAN.json') and
            binding['runtime_plan_sha256'] == sha(g / 'PLAN.json'), 'Runtime binding')
    files = ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json',
             'INDEPENDENT-LOCAL-REPLAY.json', 'RESIDUAL-ADAPTERS.json', 'CLIFFORD-RECIPES.json', 'CLIFFORD-REVIEW.json')
    expected_sources = {'work/complex-nine-native/DATA-PHASES.json'} | {
        'providers/' + pid + '/' + name for pid in expected_dispatch.values() for name in files}
    require(set(summary['source_artifacts']) == expected_sources and owner['source_artifacts'] == summary['source_artifacts'], 'Complete provider source inventory')
    require(set(binding['providers']) == {'gauge44', 'gauge44_e4'}, 'Both bound providers')
    for relative, digest in summary['source_artifacts'].items():
        require(sha(base / relative) == digest, 'Provider/phase bytes: ' + relative)
    for pid, native in [('gauge44', baseline / 'native/local'), ('gauge44_e4', work / 'native/local')]:
        for name in files:
            require(sha(base / 'providers' / pid / name) == sha(native / name) ==
                    binding['providers'][pid]['artifact_sha256'][name], 'Fresh native provider: ' + pid + '/' + name)
    # Independently derive every emitted sigma from physical pending axes.
    canonical = read(base / 'providers/gauge44/CANONICAL-WORD.json.gz')
    phases = read(base / 'work/complex-nine-native/DATA-PHASES.json')
    bases = []
    for port in canonical['ports']:
        zero = next(i for i in range(9) if not (port >> i & 1))
        correction = port ^ (1 << zero)
        axes = list(range(9))
        axes[0], axes[zero] = axes[zero], axes[0]
        bases.append([(1 << i) ^ (correction if correction >> i & 1 else 0) for i in axes] + [1 << i for i in range(9, 73)])
    sigmas, cache, stream = {}, {}, hashlib.sha256()
    for call in template['calls']:
        for helper, (family, route) in enumerate(call['owners'][224:]):
            port, child, offset = family % 112, route[1], route[2]
            width = 9 if route[0] == 3 else route[3]
            key = port, child, offset, width
            if key not in cache:
                frame = bases[port]
                pending = list(map(int, phases['recipes'][port]['idle_children'][child]['orthogonal_axes']))
                occupied = [frame.index(v) for v in pending[offset:offset+width]]
                spectators = [j for j in range(73) if j not in occupied][:9-width]
                wanted_route = [3, child, offset] if width == 9 else [4, child, offset, width, spectators]
                order = occupied + spectators + [j for j in range(73) if j not in occupied and j not in spectators]
                sigma = [frame[j] for j in order]
                digest = hashlib.sha256(json.dumps(sigma, separators=(',', ':')).encode()).hexdigest()
                cache[key], sigmas[digest] = (digest, wanted_route), sigma
            digest, wanted_route = cache[key]
            require(route == wanted_route, 'Actual spectator route')
            stream.update(json.dumps([call['stage'], call['replica'], helper, family, digest], separators=(',', ':')).encode() + b'\n')
    require(sigmas == read(hosted / 'ACTUAL-SIGMAS.json.gz'), 'Complete emitted sigma dictionary')
    require(len(sigmas) == independent['actual_73_axis_charts'] == owner['actual_73column_sigmas'], 'Independent chart count')
    require(stream.hexdigest() == summary['sigma_stream_sha256'] == controller['actual_sigma_stream_sha256'], 'Full role sigma stream')
    idle = read(hosted / 'IDLE-REMAINDER-FRAMES.json.gz')
    expected_idle = []
    for row in template['idle_children']:
        axes = list(map(int, phases['recipes'][row['port']]['idle_children'][row['child']]['orthogonal_axes']))[row['pending_offset']:]
        require(len(axes) == row['rank'], 'Idle pending rank')
        expected_idle.append(dict(row, orthogonal_axes=axes))
    require(idle == expected_idle, 'Actual remainder frames')
    admission = read(work / 'strict/ADMISSION-CONTROLS.json')
    bit = read(work / 'strict/BIT-CONTROLS.json')
    metadata_module = load(P / 'freeze_metadata.py', 'e4_freeze_metadata_binding')
    metadata, derivation = metadata_module.derive(work)
    require(read(work / 'discovery/FREEZE-METADATA.json')['after'] == metadata and
            read(work / 'discovery/FREEZE-METADATA.json')['derivation'] == derivation, 'Derived metadata binding')
    require({k: spec['expected'][k] for k in metadata} == metadata, 'Strict two-provider metadata')
    require(len(admission['rejected_controls']) == metadata['assembly_controls_rejected'] == 114 and
            not admission['discovery_accepted_controls'], 'Admission controls')
    require(len(bit['rejected_controls']) == 12 and bit['derived_deficit'] == 10272, 'Bit controls')
    require(controller['mutation_controls_run'] and
            len(controller['mutations_rejected']) == metadata['mutations_rejected'], 'Controller controls')
    payload = read(work / 'PAYLOAD-CONTROLS.json')
    require(payload['status'] == 'PASS_T37_PAYLOAD_BOUNDARIES_AND_STRICT_ADMISSION_MUTATIONS' and
            len(payload['boundary']) == 7 and len(payload['rejected_controls']) == 11, 'Payload boundary controls')
    require(payload['geometry_sha256'] == sha(work / 'INDEPENDENT-OWNERS.json'), 'Payload geometry input')
    payload_adapter = load(P / 'payload.py', 'e4_payload_adapter_binding')
    require((work / 'payload_controls_adapter.py').read_text() == payload_adapter.adaptation()[0], 'Exact payload adapter')
    for path, digest in payload['inputs'].items():
        require(sha(path) == digest, 'Payload control input: ' + path)
    for directory, expected in [(work / 'native', ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']),
                                 (work / 'discovery', ['bind', 'emit', 'audit', 'invoice', 'assembly', 'freeze', 'freeze-metadata']),
                                 (work / 'strict', ['bind', 'emit', 'audit', 'invoice', 'assembly', 'admission-controls', 'bit-controls'])]:
        stages = read(directory / 'STAGES.json')
        require([s['name'] for s in stages] == expected, 'Complete stage inventory')
        for stage in stages:
            require(stage['exit_code'] == 0 and stage['log_sha256'] == sha(directory / (stage['name'] + '.log')), 'Successful stage log binding')
    stages = read(work / 'STAGES.json')
    expected_stages = ['ancestry942', 'construct', 'native-e4', 'runtime', 'plan', 'independent-owners',
                       'independent-price', 'discovery', 'strict', 'payload-controls']
    names = [s['name'] for s in stages]
    if names and names[-1] == 'final-binding':
        names = names[:-1]
    require(names in (expected_stages, ['baseline942-cold'] + expected_stages), 'Complete driver stages')
    require(all(s['exit_code'] == 0 and sha(work / (s['name'] + '.log')) == s['log_sha256'] for s in stages), 'Driver log bindings')
    paths = [p for p in work.rglob('*') if p.is_file() and p.suffix in ('.json', '.gz', '.jsonl')
             and not p.is_relative_to(work / 'parent') and not p.is_relative_to(work / 'temp')
             and not p.is_relative_to(work / 'baseline942') and p != work / 'STAGES.json'
             and p.name not in ('FINAL-BINDING.json', 'RESULT.json')]
    return dict(status='PASS_COMPLETE_U8_E4_GAP_FILL_BINDINGS', kappa=claim['kappa'],
                source_manifest_sha256=sha(P / 'SOURCES.json'), base_commit=sources['base_commit'],
                adapters=adapters, actual_template_sha256=template_hash, sigma_stream=stream.hexdigest(),
                actual_sigmas=len(sigmas), baseline_binding_sha256=sha(baseline / 'FINAL-BINDING.json'),
                artifacts={str(p.relative_to(work)): sha(p) for p in sorted(paths)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--baseline942', type=Path, required=True)
    args = parser.parse_args()
    result = check(args.work, args.baseline942)
    dump(args.work / 'FINAL-BINDING.json', result)
    print(result['status'])


if __name__ == '__main__':
    main()
