"""Check the owner repair and replay the literal constant-sector word."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
ROOT = LANES.parents[2]
ARCHIVE = ROOT/'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
PINS = {
    'source-domain/productive-owner-drift/SKELETON.json.gz': '653b5f47d14d88cab23420796597e860a8bab73e86aa31fd471c3843c079e6d0',
    'source-domain/productive-owner-drift/REPAIRED-SKELETON.json.gz': 'fc9b441fbb8c41aaa9ed41df3cb4ec853008affededadf328dc0185bb4614e00',
    'source-domain/productive-owner-drift/REPAIR.json': '847c35e0709f115f57543d3cb6f5fca1d30b58ace17807d3b5c61398b21ddd40',
    'source-domain/productive-owner-drift/repair.py': '579889368029946edc2bdba05c21beff09a35e79b2803f969904103ff2e65252',
    'source-domain/productive-owner-drift/PROOF.md': '50f1af3b6614fd0a687b0557ff7b00539cfc23743ef747b576fad75fe72fdcab',
    'source-domain/PAIRED-OWNER-PATCH.json': 'f39e8e0a39e423a5218a63590f40910b5c46216b170bc8ebe3b6dc61831b38c0',
    'history-encoding/FULL-MODE-PROGRAMS.json.gz': 'f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205',
    'residual-syndrome/physical-algebra/ORIGINAL-PAIRED-GAP-PROGRAMS.json.gz': '42aeb0902d8b2330f9050718c6d949993111a9fd898acad599ec867bb63a2b20',
    'encoded-controller/PRODUCTIVE-OWNER-DRIFT.json': '50ce5fa78259a44c036f261d9f4d123af77bb22293dda1f0d616aa6b4156f066',
    'encoded-controller/PRODUCTIVE-OWNER-DRIFT.md': 'afc421177ab5ac693d6a0f7fa9f3fcd56b9f324f3bedbcf0061826139223a691',
    'encoded-controller/check_productive_owner_drift.py': 'b7107d6cae2851d20f394f2f445bae73c1cec9e6e75390b8286d21604dcdd857',
    'encoded-controller/REPAIRED-OWNER-DRIFT.json': '7cf0ee03ac7ec5741acf574e613eabab6d00f35cfa29dca5d6157abf1b50cda6',
    'encoded-controller/REPAIRED-OWNER-DRIFT.md': 'c34df7c493b38cbd1c7c77c21cb31fef6cc84e33ce1f51c60aeca780aff82ce0',
    'encoded-controller/check_repaired_owner_drift.py': 'ef55586a7ef81060de4b9e103b496049c77dbf144ea6ca028a333709d57c2640',
    'temporal-reuse/PAIRED-OWNER-PATCH-REVIEW.json': '9acaae3a055d33665c12f938cbc1ee03e2d248f8cdbf493cb1b14ef9954bb882',
    'coherent-port/ORIGINAL-PAIRED-GAP-NATIVE-REVIEW.json': 'e79603bee7c4077b3637f9b7891bac59719183e922a71d5994aaf9d405d5322f',
    'interface-proof/FULL-MODE-PORT-REVIEW.json': 'ff123b08b3ac58f20d12d4fbec575472086ace1708d3242519884dbffe534372',
}
MODES = (225, 226, 229, 232, 241, 242, 257, 258)


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(value):
    return sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def load():
    data = {}
    for name, pin in PINS.items():
        raw = (LANES/name).read_bytes()
        if name.endswith('.gz'):
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, 'The frozen input: '+name)
        if name.endswith(('.json', '.json.gz')):
            data[name] = json.loads(raw)
    need(sha256(ARCHIVE.read_bytes()).hexdigest() == 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6', 'The archive')
    with tarfile.open(ARCHIVE) as archive:
        for key, name, pin in (
            ('template', 'candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz', '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
            ('canonical', 'candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219')):
            raw = archive.extractfile(name).read()
            need(sha256(raw).hexdigest() == pin, 'The exact archive member')
            data[key] = json.loads(gzip.decompress(raw))
    return data


def check_repair(data):
    old = data['source-domain/productive-owner-drift/SKELETON.json.gz']
    new = data['source-domain/productive-owner-drift/REPAIRED-SKELETON.json.gz']
    receipt = data['source-domain/productive-owner-drift/REPAIR.json']
    patch = data['source-domain/PAIRED-OWNER-PATCH.json']
    template, canonical = data['template'], data['canonical']
    jobs = template['hosting']['pooled_slots']
    source_jobs = list(range(69120))
    for item in patch['helper_owner_replacements']:
        source_jobs[item['target_role_index']] = item['source_role_index']
    need(old['execution_schedule'] == new['execution_schedule'] and len(old['execution_schedule']) == 626,
         'All retimed event positions stay fixed')
    for position, (item, event) in enumerate(zip(patch['schedule'], old['execution_schedule'])):
        if 'original_event' in item:
            source = item['original_event']
            expected = dict(template['execution_schedule'][source], original_event=source, position=position)
        else:
            expected = dict(item, orientation=template['calls'][item['times'][0]]['orientation'], position=position)
        need(event == expected, 'Every skeleton event is bound to its actual source event')
    incidences = []
    for a, b in zip(old['calls'][::2], old['calls'][1::2]):
        for family in set(a['owner_families']) & set(b['owner_families']):
            ra, rb = a['owner_families'].index(family), b['owner_families'].index(family)
            if ra in MODES or rb in MODES:
                kind = 'mode_mode' if ra in MODES and rb in MODES else (
                    'first_mode_second_helper' if ra in MODES else 'second_mode_first_helper')
                incidences.append((a['time'], b['time'], family, ra, rb, kind))
    recorded = [(x['times'][0], x['times'][1], x['family'], x['first_role'], x['second_role'], x['kind'])
                for x in old['cross_core_incidences']]
    need(sorted(incidences) == sorted(recorded) and len(incidences) == 36,
         'All original cross-core incidences are independently reconstructed')
    need(Counter(x[-1] for x in incidences) == {'mode_mode': 1, 'first_mode_second_helper': 15,
                                              'second_mode_first_helper': 20}, 'The exact incidence types')
    widths = {role: len(canonical['frames'][canonical['final'][role]])-
              len(canonical['frames'][canonical['start'][role]]) for role in range(224, 704)}
    exchanges = {(row['time'], row['promoted_role']): row for row in receipt['exchanges']}
    need(len(exchanges) == len(receipt['exchanges']) == 37, 'All exchanges are distinct')
    bad = []
    all_changed = []
    bad_calls = set()
    matching_rows = {row['time']: row for row in receipt['matchings']}
    for time, (a, b) in enumerate(zip(old['calls'], new['calls'])):
        need(a['time'] == b['time'] == time and all(a[k] == b[k] == template['calls'][time][k]
             for k in ('replica', 'stage', 'pair', 'orientation')), 'Every call retains its source context')
        need(a['helper_source_roles'] == source_jobs[480*time:480*(time+1)], 'The old accepted job permutation')
        need(a['data_families'] == b['data_families'] == [x[0] for x in template['calls'][time]['owners'][:224]],
             'The selected active data stays fixed')
        need(set(a['owner_families']) == set(b['owner_families']) and len(set(b['owner_families'])) == 704,
             'The complete owner set stays fixed and distinct')
        need(sorted(a['helper_source_roles']) == sorted(b['helper_source_roles']), 'Every job stays at its original call')
        other = set(old['calls'][time ^ 1]['owner_families'])
        bad_here = [role for role in MODES if a['owner_families'][role] in other]
        donors = [role for role in range(224, 704) if role not in MODES and widths[role] == 9
                  and a['owner_families'][role] not in other]
        expected_families = a['owner_families'][:]
        expected_jobs = a['helper_source_roles'][:]
        used = set()
        if bad_here:
            bad_calls.add(time)
            need(matching_rows[time]['bad_mode_roles'] == bad_here and
                 matching_rows[time]['admissible_ordinary_roles'] == donors, 'Every exact donor set')
        for role in bad_here:
            bad.append((time, role))
            row = exchanges[time, role]
            donor = row['ordinary_role']
            need(donor in donors and donor not in used, 'Each bad mode has a distinct legal ordinary donor')
            used.add(donor)
            need(row['old_mode_owner'] == a['owner_families'][role] and
                 row['new_mode_owner'] == a['owner_families'][donor], 'Exact old and new mode owners')
            need((row['mode_job'], row['ordinary_job']) ==
                 (a['helper_source_roles'][role-224], a['helper_source_roles'][donor-224]), 'Both exact whole jobs')
            for r in (role, donor):
                need(widths[r] == 9 and canonical['frames'][canonical['start'][r]] == [] and
                     len(canonical['frames'][canonical['final'][r]]) == 9, 'The complete I-to-FULL local contract')
            expected_families[role], expected_families[donor] = expected_families[donor], expected_families[role]
            expected_jobs[role-224], expected_jobs[donor-224] = expected_jobs[donor-224], expected_jobs[role-224]
        need(expected_families == b['owner_families'] and expected_jobs == b['helper_source_roles'],
             'Only the declared disjoint exchanges change the literal call')
        need(b['mode_families'] == [b['owner_families'][r] for r in MODES], 'The exact new mode roles')
        need(not set(b['mode_families']) & set(new['calls'][time ^ 1]['owner_families']), 'No cross-core mode alias')
        for helper, source in enumerate(b['helper_source_roles']):
            job = jobs[source]
            need(job['width'] == widths[224+helper] and job['family'] == b['owner_families'][224+helper],
                 'The original whole job and its width reach the new local slot')
        all_changed.extend((time, r) for r, (x, y) in enumerate(zip(a['owner_families'], b['owner_families'])) if x != y)
    need((len(bad), len(bad_calls), len(all_changed)) == (37, 14, 74), 'The exact repair size and attained role bound')
    need(not new['cross_core_incidences'] and new['same_call_job_exchanges'] == receipt['exchanges'], 'Complete alias removal')
    shared = 0
    for a, b in zip(new['calls'][::2], new['calls'][1::2]):
        both = set(a['owner_families']) & set(b['owner_families'])
        shared += len(both)
        for family in both:
            ra, rb = a['owner_families'].index(family), b['owner_families'].index(family)
            need(ra >= 224 and rb >= 224 and ra not in MODES and rb not in MODES, 'Every remaining shared owner is ordinary')
            ja, jb = jobs[a['helper_source_roles'][ra-224]], jobs[b['helper_source_roles'][rb-224]]
            need(ja['child'] == jb['child'] and
                 (ja['offset']+ja['width'] <= jb['offset'] or jb['offset']+jb['width'] <= ja['offset']),
                 'Shared ordinary jobs use the same chart and disjoint pending axes')
    need(shared == 1369, 'All shared ordinary occurrences')
    profile = {int(k): v for k, v in data['temporal-reuse/PAIRED-OWNER-PATCH-REVIEW.json']['complete_profile'].items()}
    need(sum(k*v for k, v in profile.items())-1152*8 == 1032192, 'The conditional centre-removed native mass')
    return {'same_call_exchanges': 37, 'changed_roles': 74, 'changed_calls': 14,
            'old_jobs_preserved': 69120, 'shared_ordinary_occurrences': shared,
            'minimum_changed_roles_in_fixed_call_class': 74, 'conditional_native_mass': 1032192}


def scalar_core(core, reverse=False):
    result = []
    for event in reversed(core) if reverse else core:
        if event[0] != 'scalar':
            need(event[0] in ('phase', 'climb', 'adapter', 'residual_adapter'), 'Every other core event is native or a phase marker')
            continue
        op = event[1]
        need(op[0] in ('add', 'scale') and op[1][0] == 'L', 'The literal core has no private erasure')
        c = Fraction(op[-2], op[-1])
        if op[0] == 'add':
            need(op[2][0] == 'L' and op[1][1] != op[2][1], 'An off-diagonal literal ADD')
            result.append(('add', op[1][1], op[2][1], -c if reverse else c))
        else:
            result.append(('scale', op[1][1], None, 1/c if reverse else c))
    return result


def replay(skeleton, paired, cores, initial, signs, reverse=False):
    values = initial[:]
    traces = []
    graph_count = core_count = 0
    for event in reversed(skeleton['execution_schedule']) if reverse else skeleton['execution_schedule']:
        watched = [values[f] for f in (0, 112, 7280, 13005)]
        kind = event['kind']
        if kind in ('paired_input_boundary', 'paired_output_boundary'):
            calls = [skeleton['calls'][t] for t in event['times']]
            if reverse and signs and kind == 'paired_output_boundary':
                for call in reversed(calls):
                    for family in reversed(call['mode_families']):
                        values[family] = -values[family]
            part = 'prefix' if kind == 'paired_input_boundary' else 'suffix'
            gates = paired['programs'][event['orientation']][part]
            for gate in reversed(gates) if reverse else gates:
                if gate['kind'] == 'physical_translation':
                    continue
                need(gate['kind'] == 'physical_add', 'Every paired gate is accounted for')
                tr, ts = gate['target']
                sr, ss = gate['source']
                target, source = calls[tr]['owner_families'][ts], calls[sr]['owner_families'][ss]
                need(target != source, 'Every paired ADD remains off-diagonal')
                c = Fraction(gate['coefficient'])
                if values[source]:
                    values[target] += (-c if reverse else c)*values[source]
                graph_count += 1
            if not reverse and signs and kind == 'paired_output_boundary':
                for call in calls:
                    for family in call['mode_families']:
                        values[family] = -values[family]
        elif kind == 'local_cover_sweep':
            call = skeleton['calls'][event['time']]
            owners = call['owner_families']
            local = [values[f] for f in owners]
            for op, target, source, c in cores[call['orientation'], reverse]:
                if op == 'scale':
                    if local[target]:
                        local[target] *= c
                elif local[source]:
                    local[target] += c*local[source]
                core_count += 1
            for family, value in zip(owners, local):
                values[family] = value
        elif kind == 'bridge':
            base = 896*event['replica']
            dst, src = event['dst'], event['src']
            c = event['coefficient']*(-1 if reverse else 1)
            for p in range(112):
                values[base+224*dst+p] += c*values[base+224*src+p]
                values[base+224*src+112+p] -= c*values[base+224*dst+112+p]
        elif kind == 'terminal':
            for pair in range(4):
                base = 896*event['replica']+224*pair
                for p in range(112):
                    x, y = values[base+p], values[base+112+p]
                    values[base+p], values[base+112+p] = (-y, x) if reverse else (y, -x)
        else:
            need(kind in ('idle_cover_sweep', 'terminal_Y_translations', 'bank_padding_cover_sweep',
                          'translate_every_live_family'), 'Every remaining event fixes the constant sector')
        if not reverse:
            for family, before in zip((0, 112, 7280, 13005), watched):
                if values[family] != before:
                    traces.append({'position': event['position'], 'kind': kind, 'family': family,
                                   'before': str(before), 'after': str(values[family])})
    return values, traces, {'literal_core_scalars': core_count, 'paired_ADDs': graph_count}


def main():
    data = load()
    repair = check_repair(data)
    paired = data['residual-syndrome/physical-algebra/ORIGINAL-PAIRED-GAP-PROGRAMS.json.gz']
    raw_core = data['history-encoding/FULL-MODE-PROGRAMS.json.gz']
    need(paired['core_payload_sha256'] == PINS['history-encoding/FULL-MODE-PROGRAMS.json.gz'], 'The exact literal core dependency')
    cores = {(o, rev): scalar_core(raw_core[o], rev) for o in ('forward', 'backward') for rev in (False, True)}
    need(all(len(word) == 20389 for word in cores.values()), 'Every retained scalar core event')
    results = []
    for name, file, expected_file in (
        ('unchanged', 'SKELETON.json.gz', 'PRODUCTIVE-OWNER-DRIFT.json'),
        ('repaired', 'REPAIRED-SKELETON.json.gz', 'REPAIRED-OWNER-DRIFT.json')):
        skeleton = data['source-domain/productive-owner-drift/'+file]
        expected = data['encoded-controller/'+expected_file]
        initial = [Fraction(0)]*14336
        initial[13005] = Fraction(1)
        for signs in (False, True):
            output, traces, counts = replay(skeleton, paired, cores, initial, signs)
            need(replay(skeleton, paired, cores, output, signs, True)[0] == initial, 'The inverse of every literal event restores the input')
            differences = [[i, str(v-initial[i])] for i, v in enumerate(output) if v != initial[i]]
            expected_variant = expected['variants'][int(signs)]
            need(digest(differences) == expected_variant['defect_sha256'] and
                 len(differences) == expected_variant['nonzero_defect_families'], 'The complete independently reproduced defect vector')
            need(output[112] == Fraction(-1, 4) and differences[0] == [112, '-1/4'], 'The exact first wrong output')
            need(any(x == {'position': 1, 'kind': 'local_cover_sweep', 'family': 112,
                           'before': '0', 'after': '-1/4'} for x in traces), 'The first actual damaging owner-to-data edge')
            results.append({'assignment': name, 'mode_signs': signs, 'defect_sha256': digest(differences),
                            'defect_families': len(differences), 'first_defect': differences[0],
                            'trace': traces, 'inverse': 'PASS', 'counts': counts})
            print(name, signs, differences[0], len(differences), flush=True)
    receipt = {'status': 'PASS_INDEPENDENT_PRODUCTIVE_OWNER_DRIFT_AND_ALIAS_REPAIR', 'pins': PINS,
               'repair': repair, 'variants': results, 'producer_imports': [],
               'literal_core_replay': True, 'raw_core_formula_used': False,
               'deep_owner_patch_audit_repeated': False, 'new_native_kernel_sweep': False,
               'scope': 'Two fixed old-owner assignments and two sign conventions fail on one exact constant-sector input. The same-call alias repair preserves all whole jobs conditionally on the retained slot-specific native contracts. No arbitrary-owner-controller obstruction or supplier admission.',
               'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE/'REVIEW.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()
