#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""X2 acceptance-boundary audit for the selected CrocSwap/integer-mult-bounds#1094 supplier owner map.

Navinor, with help from opencode. Apache-2.0.

One named obligation of the selected complex supplier (certificates/selected-result.json,
CrocSwap/integer-mult-bounds#1094 frozen OWNERS/PLAN/SPEC at audited head 0fc329d0bec93ca7cd288eaea1295172e8789810):

  X2  pending axes of distinct idle children of one physical family are disjoint,
      so a family's hosts on different children never share a cell.

X2 is checked by geometry() in Josie Elliston's independent owner audit
(research/t16-owner-audit-seed67/verify.py, CrocSwap/integer-mult-bounds#1091), composed onto CrocSwap/integer-mult-bounds#1094 by
research/community-batch1099-audit/check_frontier1094.py. This package traces
where that check actually executes, and builds the smallest semantic
counterexample it rejects: a one-integer mutation of the pinned DATA-PHASES
pending axes that preserves every role-level and window-level aggregate.

Checks in this file:
  1. Positive control: the pinned inputs pass the complete R1-R7/X1/X2 audit.
  2. M1 (minimal adversarial instance): one pending axis of one idle child is
     replaced by an axis already pending for a distinct idle child of the same
     physical family at the same port. Superficial aggregates (ranks, windows,
     role counts, widths, profile) are unchanged. geometry() must reject at X2.
  2b. Witness: under M1, exhibit the exact physical cell written twice (family,
      axis) by two roles that every role-level rule accepts.
  3. M2 failure control: one axis duplicated inside a single child's pending
     list. geometry() must reject at X2 as well.
  4. Blindness: with only the X2 need() suppressed, geometry() returns an
     identical geometry object and the complete R1-R7/X1 rule set accepts the
     M1 fixture. The X2 rule is the only rule that reads pending axes. This is
     a semantic-layer measurement on in-memory mutated bytes; it is not an
     end-to-end acceptance claim for a mutated pinned input (see 7).
  5. Coverage inventory: the existing 11 owner-audit controls and the frozen
     verifier's 6 independent-t16 controls contain no X2-directed mutant.
  6. Enforcement trace (static, recorded with exact excerpts): the selected
     reproduce command and the CI workflow do not execute the CrocSwap/integer-mult-bounds#1094 owner
     composition, and the frozen CrocSwap/integer-mult-bounds#1087 verifier chain keys hosted cells per
     (owner, child, port), so cross-child cell sharing is outside its rule set.
  7. Source-bound acceptance path (executed): the hash/pin layer and the
     semantic layer are distinguished. The M1 mutation is applied to a copy of
     the pinned DATA-PHASES bytes in a scratch tree and the real source-bound
     entrypoints are run against it: both reject the mutated pinned input at
     their source-hash pins before any semantic rule runs, while intact bytes
     pass the pins and reach the semantic layer. Missing semantic
     recomputation on the reproduce path is therefore not the same as
     end-to-end acceptance of a mutated pinned input; full mutated-chain
     acceptance remains unexecuted (RESULT.json, README).

Unrun obligations are listed in RESULT.json and the README.
"""
import copy
import gzip
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    path = Path(path)
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())


def text(path):
    return Path(path).read_text(encoding='utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError('X2 boundary audit: ' + message)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- inputs

a = load_module('owner_audit', ROOT / 'research/t16-owner-audit-seed67/verify.py')
pins = read(ROOT / 'research/t16-owner-audit-seed67/SOURCES.json')['inputs']
require(sha(ROOT / a.TEMPLATE) == pins['template_sha256'], 'template pin')
require(sha(ROOT / a.PHASES) == pins['data_phases_sha256'], 'DATA-PHASES pin')
require(hashlib.sha256(gzip.decompress(a.WORD.read_bytes())).hexdigest() == pins['word_content_sha256'],
        'seven-slot word pin')

word = read(a.WORD)
template = read(ROOT / a.TEMPLATE)
phases = read(ROOT / a.PHASES)
widths = a.word_widths(word)
local = a.as_profile(word['report']['local_profile'])

pkg = ROOT / 'research/complex-t16-rare-pattern-exchanges'
spec = read(pkg / 'data/SPEC.json')
plan = read(pkg / 'data/PLAN.json')
roles = read(pkg / 'data/OWNERS.json.gz')
expected_idle = a.as_profile(spec['expected']['idle_remainder_profile'])
T = 16

# ---------------------------------------------------------------- 1. positive control

geo0 = a.geometry(template, phases)
owned0 = a.audit(geo0, widths, local, roles, plan, expected_idle, T)
require(owned0['roles'] == len(roles), 'positive control role count')

# ---------------------------------------------------------------- M1 fixture

place, rank = geo0['place'], geo0['rank']
children = sorted(rank)


def axes_lists(ph):
    """Yield mutable (recipe_index, child_key, list) pending-axis lists."""
    for ri, recipe in enumerate(ph['recipes']):
        kids = recipe['idle_children']
        items = enumerate(kids) if isinstance(kids, list) else ((int(k), v) for k, v in kids.items())
        for child, item in items:
            yield ri, child, item['orthogonal_axes']


axes_map = {}
for ri, child, raw in axes_lists(phases):
    axes_map[child, phases['recipes'][ri]['port']] = [int(x) for x in raw]

groups = {}
for child in children:
    groups.setdefault(place[child], []).append(child)

candidate = None
for where, siblings in sorted(groups.items()):
    for i, c1 in enumerate(siblings):
        for c2 in siblings[i + 1:]:
            for port in range(112):
                l1 = axes_map.get((c1, port))
                l2 = axes_map.get((c2, port))
                if not l1 or not l2:
                    continue
                shared = [x for x in l1 if x not in l2]
                if not shared:
                    continue
                for k in range(len(l2)):
                    if l2[k] not in l1:
                        candidate = dict(where=where, c1=c1, c2=c2, port=port,
                                         value=shared[0], c1_index=l1.index(shared[0]), c2_index=k)
                        break
                if candidate:
                    break
            if candidate:
                break
        if candidate:
            break
    if candidate:
        break
require(candidate is not None, 'no cross-child axis locus found')

phases_m1 = copy.deepcopy(phases)
port_index = next(ri for ri, r in enumerate(phases_m1['recipes']) if r['port'] == candidate['port'])
kids = phases_m1['recipes'][port_index]['idle_children']
entry = kids[candidate['c2']] if isinstance(kids, list) else kids[str(candidate['c2'])]
before = int(entry['orthogonal_axes'][candidate['c2_index']])
entry['orthogonal_axes'][candidate['c2_index']] = candidate['value']

# Single-locus and superficial-aggregate guards.
raw_delta = sum(1 for (_, _, old), (_, _, new) in zip(axes_lists(phases), axes_lists(phases_m1))
                for u, v in zip(old, new) if int(u) != int(v))
require(raw_delta == 1, 'M1 must be a one-integer mutation')
geo_m1_x2suppressed = None

rejects = {}
for name, ph in (('M1_cross_child_axis', phases_m1),):
    try:
        a.geometry(template, ph)
    except a.Reject as exc:
        rejects[name] = str(exc)
require(rejects.get('M1_cross_child_axis', '').startswith('X2:'),
        'M1 must be rejected at X2, got: ' + rejects.get('M1_cross_child_axis'))

# ---------------------------------------------------------------- 2b. cell-collision witness

c1, c2, port = candidate['c1'], candidate['c2'], candidate['port']
pair, side = place[c1]
require(place[c2] == (pair, side), 'witness children must share the physical family')
value = candidate['value']
axis_index_in_bases = None


def covers(role, child, port_, index):
    return (role['child'] == child and role['port'] == port_
            and role['offset'] <= index < role['offset'] + role['width'])


witness = None
for owner in range(T):
    left = [z for z in roles if z['owner_replica'] == owner and covers(z, c1, port, candidate['c1_index'])]
    right = [z for z in roles if z['owner_replica'] == owner and covers(z, c2, port, candidate['c2_index'])]
    if left and right:
        z1, z2 = left[0], right[0]
        family = owner * a.FAMILIES_PER_REPLICA + (2 * pair + side) * a.V + port
        require(z1['family'] == family and z2['family'] == family, 'witness family identity')
        witness = dict(owner_replica=owner, family=family, shared_axis=value,
                       role_a={k: z1[k] for k in ('time', 'stage', 'replica', 'helper', 'child', 'port', 'offset', 'width')},
                       role_b={k: z2[k] for k in ('time', 'stage', 'replica', 'helper', 'child', 'port', 'offset', 'width')},
                       note='Both roles resolve pending-axis %d of family %d at port %d; the R1-R7/X1 rule set '
                            'keys cells per (owner, child, port) and accepts both.' % (value, family, port))
        break
require(witness is not None, 'no colliding role pair found for M1')

# ---------------------------------------------------------------- 3. M2 failure control

phases_m2 = copy.deepcopy(phases)
m2 = None
for ri, child, raw in axes_lists(phases_m2):
    vals = [int(x) for x in raw]
    if len(vals) >= 2:
        duplicate = vals[0]
        if duplicate not in vals[1:]:
            kids = phases_m2['recipes'][ri]['idle_children']
            entry = kids[child] if isinstance(kids, list) else kids[str(child)]
            entry['orthogonal_axes'][-1] = duplicate
            m2 = dict(recipe_index=ri, child=child, index=len(vals) - 1,
                      port=phases_m2['recipes'][ri]['port'], value=duplicate)
            break
require(m2 is not None, 'no within-child duplicate locus found')
require((m2['recipe_index'], m2['child'], m2['index'])
        != (port_index, candidate['c2'], candidate['c2_index']), 'M1 and M2 must use different loci')
try:
    a.geometry(template, phases_m2)
except a.Reject as exc:
    rejects['M2_within_child_duplicate'] = str(exc)
require(rejects.get('M2_within_child_duplicate', '').startswith('X2:'),
        'M2 must be rejected at X2, got: ' + rejects.get('M2_within_child_duplicate'))

# ---------------------------------------------------------------- 4. blindness of R1-R7/X1

original_need = a.need


def need_x2_suppressed(ok, rule, msg):
    if rule == 'X2':
        return
    original_need(ok, rule, msg)


a.need = need_x2_suppressed
try:
    geo_m1_x2suppressed = a.geometry(template, phases_m1)
    owned_m1 = a.audit(geo_m1_x2suppressed, widths, local, roles, plan, expected_idle, T)
finally:
    a.need = original_need
require(geo_m1_x2suppressed == geo0, 'geometry object must not depend on pending axes')
require(owned_m1 == owned0, 'R1-R7/X1 must be blind to the X2 violation')

# ---------------------------------------------------------------- 5. control inventory

controls = a.controls(geo0, widths, local, roles, plan, expected_idle, T)
control_names = [c['name'] for c in controls]
require(len(control_names) == 11 and all(c['rejected_by'] != 'X2' or c['name'] == 'plan_window_truncated'
                                        for c in controls), 'unexpected owner-audit control battery')

tar_path = pkg / 'upstream1087.tar.gz'
frozen = {}
with tarfile.open(tar_path) as tar:
    for name in ('verify_t16.py', 't16/indep16.py', 'code/audit_allcold.py', 'code/emit_allcold.py'):
        frozen[name] = tar.extractfile(name).read().decode('utf-8')
indep_controls = re.findall(r"candidates\.append\(\('([a-z0-9_]+)'", frozen['t16/indep16.py'])
require(len(indep_controls) == 6, 'frozen independent-t16 control battery size')
require('X2' not in ''.join(frozen.values()), 'frozen verifier unexpectedly mentions X2')

# ---------------------------------------------------------------- 6. enforcement trace

makefile = text(ROOT / 'Makefile')
m = re.search(r'frontier1094-verify:.*?(?=\n\S)', makefile, re.S)
require(m is not None, 'frontier1094-verify target missing')
target = m.group(0)
verify_frontier = text(ROOT / 'scripts/verify_frontier1094.py')
selected_record_check = text(ROOT / 'scripts/verify_selected_result.py')
ci = text(ROOT / '.github/workflows/community-batch1099.yml')
claim_prs = [c['pr'] for c in read(ROOT / 'research/t16-owner-audit-seed67/SOURCES.json')['claims']]
require('check_frontier1094' not in target and 'check_frontier1094' not in verify_frontier
        and 'check_frontier1094' not in selected_record_check, 'reproduce path unexpectedly runs the composition')
require('check_frontier1094' not in ci, 'CI unexpectedly runs the composition')
require('research/t16-owner-audit-seed67/verify.py --fetch' in ci, 'CI owner-audit step missing')
require(1094 not in claim_prs, 'CrocSwap/integer-mult-bounds#1094 unexpectedly inside the owner-audit claim list')
require('bin_key = (owner, child, port)' in frozen['t16/indep16.py'], 'indep16 bin keying changed')
require('orthogonal_axes' in frozen['code/audit_allcold.py']
        and 'len(pend)==prank[i]' in frozen['code/audit_allcold.py'], 'audit_allcold pending-axis read changed')

# ------------------------------------------------- 7. source-bound acceptance path

# 7a. Code order: both source-bound entrypoints that read the fixture hash-pin
# its bytes before any semantic rule can see them.
cf_text = text(ROOT / 'research/community-batch1099-audit/check_frontier1094.py')
cf_lines = cf_text.splitlines()
cf_pin = next(i for i, line in enumerate(cf_lines, 1) if 'data_phases_sha256' in line)
cf_geo = next(i for i, line in enumerate(cf_lines, 1) if 'a.geometry(' in line)
cf_spec = next(i for i, line in enumerate(cf_lines, 1) if "'data/SPEC.json'" in line)
require(cf_pin < cf_geo, 'composition must pin DATA-PHASES before geometry')

audit_text = text(ROOT / 'research/t16-owner-audit-seed67/verify.py')
audit_lines = audit_text.splitlines()
audit_pin = next(i for i, line in enumerate(audit_lines, 1) if 'data_phases_sha256' in line)
audit_geo = next(i for i, line in enumerate(audit_lines, 1) if 'geo = geometry(' in line)
audit_blob = next(i for i, line in enumerate(audit_lines, 1) if "'cat-file'" in line)
audit_claims = next(i for i, line in enumerate(audit_lines, 1) if 'get = {name: load(blob(' in line)
require(audit_pin < audit_geo, 'owner audit must pin DATA-PHASES before geometry')

# 7b. Record/manifest layer: what scripts/verify_selected_result.py covers.
selected = read(ROOT / 'certificates/selected-result.json')
source_manifest = read(ROOT / selected['source_manifest'])
fixture_under_root = any(a.PHASES.startswith(root + '/') for root in source_manifest['package_roots'])
phase_copies = sorted((name, digest) for name, digest in source_manifest['files'].items()
                      if name.endswith('DATA-PHASES.json'))
require(not fixture_under_root, 'audit fixture unexpectedly covered by the record package roots')
require(phase_copies and all(digest == pins['data_phases_sha256'] for _, digest in phase_copies),
        'vendored DATA-PHASES copies must be pinned at the fixture digest')
require(selected['proof_supplements']['research/community-batch1099-audit/check_frontier1094.py']
        == sha(ROOT / 'research/community-batch1099-audit/check_frontier1094.py'),
        'proof_supplements must pin the composition bytes')

# 7c. Frozen chain: emit-time self-consistency binding, not an external pin.
require('source_artifacts' in frozen['code/emit_allcold.py']
        and 'exact_data_phase_recipe_sha256' in frozen['code/audit_allcold.py'],
        'frozen chain DATA-PHASES binding changed')

# 7d. Executed: run the real source-bound entrypoints against the M1-mutated
# pinned bytes (one integer token replaced in a scratch copy; tracked files
# untouched) and against intact bytes. The mutated run must stop at the hash
# pin before geometry(); the intact run must pass the pins and reach later code.
raw_phases = (ROOT / a.PHASES).read_bytes()
text_phases = raw_phases.decode('utf-8')
require(candidate['c2_index'] == 0, 'text-locus search assumes the first axes slot')
anchor = '{"orthogonal_axes":[' + str(before)
anchor_at = text_phases.find(anchor, text_phases.find('"recipes":'))
require(anchor_at > 0, 'M1 text locus not found')
token_at = anchor_at + len('{"orthogonal_axes":[')
require(text_phases[token_at:token_at + len(str(before))] == str(before), 'M1 text token')
mut_phases = (text_phases[:token_at] + str(value) + text_phases[token_at + len(str(before)):]).encode('utf-8')
require(json.loads(mut_phases) == phases_m1, 'text mutation must equal the in-memory M1 fixture')
require(len(raw_phases) - len(mut_phases) == len(str(before)) - len(str(value)), 'M1 text byte delta')

scratch = Path(tempfile.mkdtemp(prefix='x2-boundary-'))
run_receipts = []
try:
    def stage(relative, data):
        target = scratch / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    stage('research/t16-owner-audit-seed67/verify.py', audit_text.encode('utf-8'))
    stage('research/t16-owner-audit-seed67/SOURCES.json',
          (ROOT / 'research/t16-owner-audit-seed67/SOURCES.json').read_bytes())
    stage('research/t16-owner-audit-seed67/inputs/k8-seven-slot-word.json.gz', a.WORD.read_bytes())
    stage(a.TEMPLATE, (ROOT / a.TEMPLATE).read_bytes())
    stage('research/community-batch1099-audit/check_frontier1094.py', cf_text.encode('utf-8'))

    def run(label, entry, argv, phases_bytes):
        stage(a.PHASES, phases_bytes)
        env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        env.pop('PYTHONOPTIMIZE', None)
        proc = subprocess.run([sys.executable, '-B', str(scratch / entry), *argv], cwd=scratch,
                              capture_output=True, env=env)
        out = (proc.stdout + proc.stderr).decode('utf-8', 'replace').replace(str(scratch), '<scratch>')
        basename = entry.rsplit('/', 1)[-1]
        frames = [int(line) for file_, line in
                  re.findall(r'File "[^"]*[/\\]([^"\\/]+\.py)", line (\d+)', out) if file_ == basename]
        require(proc.returncode != 0, label + ' must fail')
        run_receipts.append(dict(label=label, entrypoint=entry, exit_code=proc.returncode,
                                 traceback_frames=sorted(set(frames)),
                                 fail_marker=[line for line in out.splitlines() if line.startswith('FAIL ')]))
        return out, frames

    composition = 'research/community-batch1099-audit/check_frontier1094.py'
    owner_audit = 'research/t16-owner-audit-seed67/verify.py'
    require('DATA-PHASES hash' in audit_lines[audit_pin - 1], 'pin line must carry the FAIL marker')

    out1, frames1 = run('composition_m1_mutated_pinned_input', composition, ['x.json', 'y.json'], mut_phases)
    require('Independent PR1094 check failed' in out1 and cf_pin in frames1 and cf_geo not in frames1
            and all(line <= cf_pin for line in frames1),
            'composition must reject M1 at the DATA-PHASES hash pin before geometry, frames: %s' % frames1)

    out2, frames2 = run('owner_audit_m1_mutated_pinned_input', owner_audit, ['--repo', str(scratch)], mut_phases)
    require('FAIL input: DATA-PHASES hash' in out2 and 'PASS' not in out2,
            'owner audit must reject M1 at the DATA-PHASES hash pin, output: ' + out2)

    out3, frames3 = run('composition_intact_control', composition, ['x.json', 'y.json'], raw_phases)
    require('FileNotFoundError' in out3 and cf_spec in frames3
            and 'Independent PR1094 check failed' not in out3,
            'intact composition control must pass the pins and geometry, frames: %s' % frames3)

    out4, frames4 = run('owner_audit_intact_control', owner_audit, ['--repo', str(scratch)], raw_phases)
    require('CalledProcessError' in out4 and audit_blob in frames4
            and 'FAIL input: DATA-PHASES hash' not in out4,
            'intact owner-audit control must pass the pins and geometry, frames: %s' % frames4)
finally:
    shutil.rmtree(scratch, ignore_errors=True)

# ---------------------------------------------------------------- result

result = dict(
    status='PASS_PR1094_X2_ACCEPTANCE_BOUNDARY_AUDIT',
    scope=dict(
        obligation='X2: pending axes of distinct idle children of one physical family are disjoint',
        object='selected CrocSwap/integer-mult-bounds#1094 frozen OWNERS/PLAN/SPEC data (research/complex-t16-rare-pattern-exchanges/data)',
        audited_head='0fc329d0bec93ca7cd288eaea1295172e8789810',
        selected_kappa='836330098538459/500000000000000000',
    ),
    pins=dict(template_sha256=pins['template_sha256'], data_phases_sha256=pins['data_phases_sha256'],
              word_content_sha256=pins['word_content_sha256'],
              owners_sha256=sha(pkg / 'data/OWNERS.json.gz'), plan_sha256=sha(pkg / 'data/PLAN.json'),
              spec_sha256=sha(pkg / 'data/SPEC.json'),
              owner_audit_sha256=sha(ROOT / 'research/t16-owner-audit-seed67/verify.py'),
              composition_sha256=sha(ROOT / 'research/community-batch1099-audit/check_frontier1094.py'),
              upstream1087_sha256=sha(tar_path)),
    positive_control=dict(idle=owned0['idle'], profile=owned0['profile'], rank_mass=owned0['rank_mass'],
                          deficit=owned0['deficit'], calls=owned0['calls'], roles=owned0['roles'],
                          windows=owned0['windows'], x2_child_ports=geo0['x2_child_ports']),
    minimal_adversarial_instance=dict(
        mutation='one integer in DATA-PHASES pending axes',
        locus=dict(where=list(candidate['where']), children=[c1, c2], port=port,
                   replaced_index_in_c2=candidate['c2_index'], old_value=before, new_value=value,
                   taken_from_child=c1, index_in_c1=candidate['c1_index']),
        mutated_differing_integers=raw_delta,
        rejected_by=rejects,
        cell_collision_witness=witness),
    blindness=dict(
        method='X2 need() suppressed only to measure what the remaining semantic rule set sees; '
               'in-memory mutated bytes, not an end-to-end acceptance claim for a mutated pinned input',
        geometry_identical=geo_m1_x2suppressed == geo0,
        rule_set_accepts=owned_m1 == owned0,
        rule_set='R1-R7 plus X1 (owner-audit rule bodies), semantic layer only'),
    source_bound_acceptance=dict(
        claim_scope='Missing semantic recomputation on the reproduce path is demonstrated; end-to-end '
                    'acceptance of a mutated pinned input is not. The semantic rule set does not reject M1 '
                    '(executed in memory), but the source-hash layer rejects the mutated pinned bytes before '
                    'any semantic rule runs (executed at both source-bound entrypoints). Full mutated-chain '
                    'acceptance was not executed.',
        layer_order=['record/manifest hashes (scripts/verify_selected_result.py)',
                     'source input pins (check_frontier1094.py, t16-owner-audit-seed67/verify.py)',
                     'semantic rules (R1-R7/X1, X2; frozen indep16/audit_allcold)'],
        record_manifest_layer=dict(
            script='scripts/verify_selected_result.py',
            fixture_covered_by_package_roots=fixture_under_root,
            fixture_note='the top-level audit fixture is outside the record manifest package roots, so this '
                         'layer alone neither accepts nor rejects it; it is pinned separately by '
                         'research/t16-owner-audit-seed67/SOURCES.json inputs.data_phases_sha256',
            vendored_phase_copies_pinned=[name for name, _ in phase_copies],
            vendored_phase_copies_digest=pins['data_phases_sha256'],
            composition_pinned_by_proof_supplements=True),
        input_pin_layer=dict(
            pins_from='research/t16-owner-audit-seed67/SOURCES.json inputs.data_phases_sha256',
            composition=dict(script='research/community-batch1099-audit/check_frontier1094.py',
                             pin_line=cf_pin, geometry_line=cf_geo,
                             order='hash pin before geometry()/X2'),
            owner_audit=dict(script='research/t16-owner-audit-seed67/verify.py',
                             pin_line=audit_pin, geometry_line=audit_geo,
                             order='hash pin before geometry()/X2')),
        executed=dict(
            mutation='one integer token %d -> %d at byte offset %d (recipes[0].idle_children[1].'
                     'orthogonal_axes[0]); equals the in-memory M1 fixture; tracked files untouched, '
                     'scratch tree deleted' % (before, value, token_at),
            byte_delta=len(raw_phases) - len(mut_phases),
            runs=run_receipts),
        frozen_chain_layer=dict(
            binding='emit_allcold.py records source_artifacts sha at emit time; audit_allcold.py asserts '
                    'template exact_data_phase_recipe_sha256 equals the current file sha (self-consistency '
                    'binding, not an external pin to the frozen digest)',
            semantic_gap='no cross-child pending-axis rule (code trace)')),
    control_inventory=dict(owner_audit_controls=control_names,
                           frozen_independent_t16_controls=indep_controls,
                           x2_directed_mutants_before_this_package=0),
    enforcement_trace=dict(
        reproduce_target=target.strip().splitlines(),
        reproduce_stages=['historical-source', 'baseline1042-cold (or baseline reuse)', 'rare-pattern-exchanges'],
        selected_record_check='scripts/verify_selected_result.py validates the selected record, its certificate, '
                              'the SELECTED-SOURCE package inventory and its proof_supplement hashes; it imports no '
                              'subprocess module and executes no composition; the top-level audit fixture is outside '
                              'its package roots (see source_bound_acceptance.record_manifest_layer)',
        ci_workflow='.github/workflows/community-batch1099.yml runs research/t16-owner-audit-seed67/verify.py --fetch '
                    '(its pinned claim list excludes the selected supplier) and check_pr1048_counterexample.py; '
                    'it does not run check_frontier1094.py',
        x2_checked_by='research/t16-owner-audit-seed67/verify.py geometry(), composed on CrocSwap/integer-mult-bounds#1094 by '
                      'research/community-batch1099-audit/check_frontier1094.py at batch1099 review time',
        frozen_chain='upstream1087.tar.gz verify_t16.py stages lift16/audit_allcold/indep16; indep16 keys cells per '
                     '(owner, child, port); audit_allcold asserts only len(pending) == rank per child',
    ),
    unrun_obligations=[
        'Full make frontier1094-verify cold replay with the M1-mutated DATA-PHASES (needs the frontier1042 cold '
        'baseline; out of session budget), so end-to-end acceptance of a mutated pinned input is not claimed and '
        'the structural-blindness claim is limited to missing semantic recomputation. What is executed: the semantic '
        'layer accepts M1 in memory (R1-R7/X1) and rejects at X2, and the source-bound entrypoints reject the '
        'mutated pinned bytes at their source-hash pins before any semantic rule runs. The frozen chain carries no '
        'cross-child pending-axis rule (code trace); its DATA-PHASES hash handling is an emit-time self-consistency '
        'binding, not an external pin.',
        'No T8/T16 claim other than CrocSwap/integer-mult-bounds#1094 was re-audited; the historical owner-boundary-audit package was not rerun.',
        'No kappa, supplier adoption, or multiplication-theorem claim is made or tested here.',
    ],
)
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(result['status'], 'M1 rejected at', rejects['M1_cross_child_axis'][:60])
