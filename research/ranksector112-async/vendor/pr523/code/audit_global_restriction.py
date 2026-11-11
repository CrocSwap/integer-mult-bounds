"""Independently check the 112-port global data restriction of PR514.

Uses only the serialized old/new artifacts and the Python standard library.
Imports neither the restriction emitter nor the local/global emitters.
Usage: python audit_global_restriction.py OLD_BASE NEW_BASE REPORT.json

The verified object here is the restricted data/controller interface.  The
final complete whole-owner placement and its finite invoice are separate
audits.  In particular, no execution of the parent's obsolete rank-one-only
bank-padding display field is asserted here.
"""
from pathlib import Path
from collections import Counter
import argparse
import copy
import gzip
import hashlib
import json
import sys


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def objhash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('old_base', type=Path, help='Replayed pinned PR514 base directory')
parser.add_argument('new_base', type=Path, help='Restricted 112-port base directory')
parser.add_argument('report', type=Path, help='Destination JSON audit receipt')
args = parser.parse_args()
if sys.version_info < (3, 10):
    parser.error('Python 3.10 or later is required for exact integer bit_count')
OLD, NEW, REPORT = (p.resolve() for p in (args.old_base, args.new_base, args.report))
OS, NS = OLD / 'split-centres', NEW / 'split-centres'
old = read(OS / 'GLOBAL-TEMPLATE.json.gz')
oldcan = read(OS / 'CANONICAL-WORD.json.gz')
oldphase = read(OLD / 'work/complex-nine-native/DATA-PHASES.json')
can = read(NS / 'CANONICAL-WORD.json.gz')
checks = read(NS / 'LOCAL-CHECKS.json')
programs = read(NS / 'LOCAL-PROGRAMS.json.gz')
local_replay = read(NS / 'INDEPENDENT-REPLAY.json')
local_phase = read(NS / 'CLIFFORD-REVIEW.json')
restriction = read(NS / 'RESTRICTION.json')
transport = read(NS / 'TRANSPORT.json')
state = dict(template=read(NS / 'GLOBAL-TEMPLATE.json.gz'),
             phase=read(NEW / 'work/complex-nine-native/DATA-PHASES.json'),
             mapping=read(NS / 'PORT-MAPPING.json'),
             invoice=read(NS / 'INTEGRATION.json'))

bindings = {
    'canonical': filehash(NS / 'CANONICAL-WORD.json.gz'),
    'canonical_content': hashlib.sha256(gzip.decompress((NS / 'CANONICAL-WORD.json.gz').read_bytes())).hexdigest(),
    'programs': filehash(NS / 'LOCAL-PROGRAMS.json.gz'),
    'local_phase': filehash(NS / 'CLIFFORD-RECIPES.json'),
    'adapters': filehash(NS / 'RESIDUAL-ADAPTERS.json'),
    'old_template': filehash(OS / 'GLOBAL-TEMPLATE.json.gz'),
    'old_template_content': hashlib.sha256(gzip.decompress((OS / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest(),
    'old_phase': filehash(OLD / 'work/complex-nine-native/DATA-PHASES.json'),
    'phase': filehash(NEW / 'work/complex-nine-native/DATA-PHASES.json'),
}
need(local_replay['canonical_word_sha256'] == local_phase['canonical_word_sha256']
     == transport['canonical_sha256'] == bindings['canonical'],
     'Local independent receipts must bind this canonical word')
need(local_replay['local_programs_sha256'] == bindings['programs'],
     'Local replay must bind this expanded program')
need(local_phase['recipe_sha256'] == bindings['local_phase']
     and local_phase['all_child_equalities_include_global_phase'],
     'Local phase receipt must include the scalar phase')
need(transport['independently_recomputed_helper_compensations_match'] == 12094,
     'Arbitrary helper dirt transport was not independently certified')
for orientation, program in programs.items():
    need(objhash(program) == checks[orientation]['sha256'], 'Local program hash')
    need(local_replay['local'][orientation]['all_exact_columns'] == 784
         and local_replay['local'][orientation]['private_work_erased'],
         'Local replay must cover all data/helper columns and cleanup')
    need(local_replay['paid_profiles'][orientation]
         == checks[orientation]['paid_profile'], 'Local paid profiles')


def audit(s):
    t, ph, mp, inv = (s[k] for k in ('template', 'phase', 'mapping', 'invoice'))
    nto = mp['new_to_old']
    omitted = [i for i in range(120) if i not in nto]
    need(len(nto) == len(set(nto)) == 112 and nto == sorted(nto), 'Port injection')
    need(omitted == [0, 13, 22, 35, 40, 51, 54, 119], 'Exactly the eight axis ports')
    need(omitted == restriction['removed_canonical_source_indices'], 'Local/global selection')
    need({str(p): i for i, p in enumerate(nto)} == mp['old_to_new'], 'Inverse port map')
    otn = {p: i for i, p in enumerate(nto)}
    need((can['h'], can['v'], can['R'], len(can['centers'])) == (9, 112, 560, 8),
         'Local dimensions and private center count')
    need(can['ports'] == [oldcan['ports'][p] for p in nto], 'Actual binary port labels')
    need(can['frames'] == oldcan['frames']
         and can['start'][224:] == oldcan['start'][240:]
         and can['final'][224:] == oldcan['final'][240:], 'Helper frames unchanged')
    need(t['m'] == 73 and (t['live'], t['physical']) == (12208, 12778),
         'Live and private stock')
    need(t['private_namespace'] == dict(centers=[12208, 12216],
                                      reserved_tableau=[12216, 12776],
                                      coefficient=[12776, 12778]), 'Private ranges')
    need(t['local_programs'] == programs, 'Use the new verified local program')
    for key in ('recipe', 'loop_order', 'cover', 'adapter_policy', 'route_semantics',
                'expanded_scalar_interface'):
        need(t[key] == old[key], 'Inherited controller field ' + key)
    need('each local invocation completes before the next' in t['loop_order'].lower(),
         'Complete invocations must remain indivisible')
    need(t['exact_data_phase_recipe_sha256'] == bindings['phase']
         and t['exact_local_clifford_recipe_sha256'] == bindings['local_phase']
         and t['residual_adapter_sha256'] == bindings['adapters'], 'Global recipe hashes')
    provenance = t['port_restriction']
    need(provenance['new_to_old'] == nto
         and provenance['parent_global_template_content_sha256'] == bindings['old_template_content']
         and provenance['parent_data_phase_sha256'] == bindings['old_phase']
         and provenance['canonical_word_content_sha256'] == bindings['canonical_content'], 'Provenance')

    # The old polynomial verification applies to each selected literal recipe.
    # This comparison includes every axis, every Z4 translation, and the
    # terminal correction; it is stronger than comparing only rank histograms.
    need(ph['m'] == 73 and ph['ports'] == 112 and len(ph['recipes']) == 112,
         'Data phase dimensions')
    for key in ('status', 'cover_correction', 'global_phase_argument'):
        need(ph[key] == oldphase[key], 'Inherited phase statement ' + key)
    need(ph['source_parent_sha256'] == bindings['old_phase'], 'Parent phase provenance')
    for p, op in enumerate(nto):
        got = copy.deepcopy(ph['recipes'][p])
        need(got['port'] == p and got['q'] == can['ports'][p], 'Phase port labels')
        got['port'] = op
        need(got == oldphase['recipes'][op], 'Exact per-port phase recipe restriction')
        q = can['ports'][p]
        z = next(i for i in range(9) if not ((q >> i) & 1))
        a = q ^ (1 << z)
        order = list(range(9))
        order[0], order[z] = order[z], order[0]
        basis = [(1 << i) ^ (a if (a >> i) & 1 else 0) for i in order]
        basis += [1 << i for i in range(9, 73)]
        need(all(((x & y).bit_count() & 1) == (i == j)
                 for i, x in enumerate(basis) for j, y in enumerate(basis)),
             'Orthogonal 73-dimensional port chart')
        for child in got['idle_children']:
            axes = child['orthogonal_axes']
            need(len(axes) == len(set(axes)) == child['rank']
                 and set(axes) <= set(basis), 'Literal idle child axes')
    need(ph['terminal_omission_controls_rejected'] == 112, 'Terminal control count')

    # The source event list acts separately at every port after a complete
    # verified local invocation.  Preserve all events and all replica order.
    schedule = copy.deepcopy(old['execution_schedule'])
    correction = dict(old['cover_final_correction'], families=[0, 12208],
                      charged_calls_per_cover=12208)
    for event in schedule:
        if event['kind'] == 'bank_padding_cover_sweep':
            event['families'] = [7168, 12208]
        elif event['kind'] == 'translate_every_live_family':
            event.update(correction)
    need(t['execution_schedule'] == schedule and t['cover_final_correction'] == correction,
         'Exact inherited event order and terminal cover correction')
    want_idle = []
    for child in old['idle_children']:
        if child['port'] in otn:
            want_idle.append(dict(child, port=otn[child['port']]))
    need(t['idle_children'] == want_idle and len(want_idle) == 2016,
         'Every selected idle child with unchanged multiplicity')
    need(t['bank_padding'] == dict(old['bank_padding'], families=list(range(7168, 12208))),
         'Inherited bank metadata and exact renumbering')

    need(len(t['calls']) == len(old['calls']) == 72, 'Number of complete invocations')
    need([(c['stage'], c['replica']) for c in t['calls']]
         == [(s, r) for s in range(9) for r in range(8)], 'Invocation order')
    bank_cells = {}
    paid = Counter()
    helper_roles = 0
    data_roles = 0
    for call, parent in zip(t['calls'], old['calls']):
        for key in ('orientation', 'stage', 'replica', 'pair', 'window'):
            need(call[key] == parent[key], 'Inherited call ' + key)
        need(call['local_program_sha256'] == checks[call['orientation']]['sha256'],
             'Call-local word binding')
        owners = call['owners']
        need(len(owners) == 784, 'Local owner count')
        rep, pair, stage = (call[k] for k in ('replica', 'pair', 'stage'))
        for side in range(2):
            for p, op in enumerate(nto):
                need(owners[112 * side + p]
                     == [896 * rep + 112 * (2 * pair + side) + p, [1, stage, p]],
                     'Literal new data family')
                need(parent['owners'][120 * side + op]
                     == [960 * rep + 120 * (2 * pair + side) + op, [1, stage, op]],
                     'Literal source data family')
                data_roles += 1
        multiplicities = Counter(f for f, route in owners)
        for h, (family, route) in enumerate(owners[224:]):
            oldfamily, oldroute = parent['owners'][240 + h]
            need(family == oldfamily - 512 and route == oldroute, 'Helper bank route unchanged')
            need(7168 <= family < 12208, 'Bank owner stock bounds')
            width = 9 - len(can['frames'][can['start'][224 + h]])
            need(route[0] == 2, 'Bank routing kind')
            if width < 9:
                need(multiplicities[family] == 1, 'Entering helper has one whole owner')
                need(len(route) == 4 and route[2] == width
                     and len(route[3]) == 9 - width, 'Entering width and spectators')
            off = 9 * route[1] if len(route) == 2 else route[1]
            cells = set(range(off, off + width))
            need(0 <= off and off + width <= 73, 'Bank residual interval')
            previous = bank_cells.setdefault(family, set())
            need(not previous & cells, 'Disjoint bank residual intervals')
            previous.update(cells)
            helper_roles += 1
        paid.update({int(r): n for r, n in checks[call['orientation']]['paid_profile'].items()})
    need(helper_roles == 40320 and data_roles == 16128, 'All literal owner roles')
    need(set(bank_cells) == set(range(7168, 12208)), 'Every retained bank accounted for')
    pads = Counter()
    for cells in bank_cells.values():
        need(cells == set(range(len(cells))), 'Bank used cells form the literal prefix')
        leftover = 73 - len(cells)
        need(0 < leftover <= 51, 'One legal complementary bank child suffices')
        pads[leftover] += 1
    need(pads == Counter({1: 3492, 9: 1386, 17: 162}), 'Actual bank remainder spectrum')
    paid.update(pads)
    for child in t['idle_children']:
        need(child['rank'] == ph['recipes'][child['port']]['idle_children'][child['child']]['rank'],
             'Paid idle rank equals literal phase recipe')
        paid[child['rank']] += child['replicas']
    mass = sum(r * n for r, n in paid.items())
    need(mass == 888624 and 73 * 12208 - mass == 2560, 'Unhosted rank-mass identity')
    need(inv['live'] == 12208 and inv['physical'] == 12778
         and inv['rank_mass'] == mass and inv['deficit'] == 2560,
         'Invoice stock and rank mass')
    need(inv['global_profile'] == {str(r): n for r, n in paid.items()}
         and inv['bank_remainder_profile'] == {str(r): n for r, n in pads.items()},
         'Invoice must use literal remainders, not obsolete bank display rank')
    return dict(retained_ports=112, deleted_canonical_ports=omitted, data_owner_roles=data_roles,
                helper_owner_roles=helper_roles, complete_invocations=72,
                exact_port_phase_recipes=112, exact_stage_alignments=1008,
                exact_idle_axis_recipes=2240, paid_idle_children=2016,
                replicated_paid_idle_children=sum(x['replicas'] for x in want_idle),
                bank_families=5040, bank_remainder_profile=dict(sorted(pads.items())),
                unhosted_paid_profile=dict(sorted(paid.items())),
                unhosted_rank_mass=mass, unhosted_live=12208, unhosted_physical=12778,
                deficit=2560)


result = audit(state)
need(objhash(state['template']) == state['invoice']['global_template_sha256'],
     'Invoice template content hash')
controls = []


def reject(name, mutation):
    changed = copy.deepcopy(state)
    mutation(changed)
    try:
        audit(changed)
    except (AssertionError, KeyError, IndexError, ValueError, TypeError):
        controls.append(name)
    else:
        raise AssertionError('Accepted negative control: ' + name)


reject('duplicate selected port', lambda s: s['mapping']['new_to_old'].__setitem__(0, 2))
reject('wrong phase port label', lambda s: s['phase']['recipes'][0].__setitem__('q', 1))
reject('wrong inherited idle axis', lambda s: s['phase']['recipes'][0]['idle_children'][0]['orthogonal_axes'].__setitem__(0, 1))
reject('missing terminal port correction', lambda s: s['phase']['recipes'][0].__setitem__('terminal_Y_translation', 0))
reject('wrong data owner family', lambda s: s['template']['calls'][0]['owners'][0].__setitem__(0, 1))
reject('wrong canonical data route', lambda s: s['template']['calls'][0]['owners'][0][1].__setitem__(2, 1))
reject('stale local program hash', lambda s: s['template']['calls'][0].__setitem__('local_program_sha256', 'old'))
reject('changed entering bank owner', lambda s: s['template']['calls'][0]['owners'][224].__setitem__(0, 7168))
reject('missing complete invocation', lambda s: s['template']['calls'].pop())
reject('missing paid idle child', lambda s: s['template']['idle_children'].pop())
reject('missing cover correction', lambda s: s['template']['execution_schedule'].pop())
reject('understated private reserve', lambda s: s['template'].__setitem__('physical', 12777))
reject('unpaid bank remainder', lambda s: s['invoice']['global_profile'].__setitem__('17', 0))

report = dict(status='PASS_INDEPENDENT_GLOBAL_DATA_PORT_RESTRICTION',
              **result, source_bindings=bindings, negative_controls_rejected=controls,
              local_scalar_replay_receipt_sha256=filehash(NS / 'INDEPENDENT-REPLAY.json'),
              local_phase_receipt_sha256=filehash(NS / 'CLIFFORD-REVIEW.json'),
              template_content_sha256=objhash(state['template']),
              scope='Exact restriction of all inherited global data routes, phase recipes, complete-call order, idle axes and terminal corrections. Local arbitrary-dirt identities are supplied by the newly hash-bound independent local replay. Actual bank remainders are recounted for the conservative parent invoice. Final whole-owner placement, executable global program, finite compilation and outer exponent require their separate fresh audits.')
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('status', 'retained_ports', 'data_owner_roles',
      'helper_owner_roles', 'unhosted_rank_mass', 'deficit', 'negative_controls_rejected')}, indent=2))
