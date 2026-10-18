# SPDX-License-Identifier: Apache-2.0
"""Rebuild a selected complex rank ledger from the emitted program it certifies (independent check).

Usage: python3 -I -B research/frontier1094-emitted-ledger-seed78/verify.py [--case NAME ...] [--write]

The selected frontier1094 certificate (ASSEMBLY.json) prices an aggregate complex_profile that its
authors' controller audit derived from the emitted hosted GLOBAL-TEMPLATE. The surcharge-free native
recurrence relies on that profile being the *exact exhaustive recursive-child profile* of the emitted
program (research/native-complex-moment552/PROOF.md). This script rebuilds the profile from the
operations themselves, using only the standard library, reading the committed replay capsule's
members in memory and importing nothing from the repository:

  * every positive-rank climb and centre event of the two dispatched LOCAL-PROGRAMS (equal to the copy
    embedded in the template), replayed register by register from the word's start to its final
    frames with F2 ranks and nesting recomputed (declared ranks only compared) and centres bound to
    their frames and carriers, summed over the calls bound to them by local_program_sha256;
  * every nonempty idle remainder, recounted from the DATA-PHASES pending axes of every idle cover
    sweep minus the hosted owner-map slices, and matched one for one with the emitted idle_children
    and their literal remainder frames;
  * with closed event and schedule vocabularies, every non-paid event (adapters, residual adapters,
    scalar operands, phase markers) bound to its register's replayed frame, the local sweeps bound to
    the calls and every owner-map slot executed by exactly one call route, so that under the PR552/559
    classification nothing else can be a paid child.

It derives W, N, m and the layout from the program, checks per-family rank conservation (every live
family carries m-1 data/pending units, so rank mass = (m-1)W + (centre mass)N and D = W - 64N), and
requires the rebuilt ledger to equal the certificate's complex_profile. This closes the link
'emitted recursive children = priced profile' under the PR552 classification rule; it does not
re-prove that rule, the no-q-adic-selector argument or the hosting semantics. Aggregates (ASSEMBLY.complex_profile,
OWNERS-AND-PROFILE.paid_profile, INDEPENDENT1094.owner.profile, the word's local_profile) are only
comparison targets. Every check raises Reject(label) through need(), so it also holds under -O.
Expected last line: PASS_FRONTIER1094_EMITTED_LEDGER
"""
import argparse
import gzip
import hashlib
import io
import json
import sys
import tarfile
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = json.loads((HERE / 'CASES.json').read_text())
PROGRAM_EVENTS = {'scalar', 'climb', 'adapter', 'residual_adapter', 'phase', 'center'}
SCHEDULE_EVENTS = {'idle_cover_sweep', 'local_cover_sweep', 'bridge', 'terminal', 'terminal_Y_translations',
                   'bank_padding_cover_sweep', 'translate_every_live_family'}
# the program phase markers, in order (both orientations); climbs carry their phase, centres sit in 'centers'
PHASES = ['zero_frame_precondition', 'entry_adapters', 'A', 'centers', 'B', 'cleanup_tail', 'final',
          'exit_adapters', 'full_frame_cleanup', 'done']


class Reject(Exception):
    """A check failed; the argument is the label of the check."""


def need(ok, label):
    if not ok:
        raise Reject(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compact(value):
    return json.dumps(value, separators=(',', ':')).encode()


# ---------------------------------------------------------------- F2 linear algebra on int bitmasks
def basis(vectors):
    piv = {}
    for v in vectors:
        while v:
            top = v.bit_length() - 1
            if top not in piv:
                piv[top] = v
                break
            v ^= piv[top]
    return piv


def inside(v, piv):
    while v:
        top = v.bit_length() - 1
        if top not in piv:
            return False
        v ^= piv[top]
    return True


def nested(small, large):
    """dim small < dim large and span(small) is contained in span(large)."""
    pl = basis(large)
    return all(inside(v, pl) for v in small)


# ---------------------------------------------------------------- binding: bytes -> decoded objects
def safe_members(tar):
    names = Counter()
    for info in tar.getmembers():
        names[info.name] += 1
        need(info.isreg() or info.isdir(), 'B2 archive members are regular files')
        need(not info.name.startswith('/') and '..' not in Path(info.name).parts, 'B2 archive member paths')
    need(all(n == 1 for n in names.values()), 'B2 archive member names are unique')
    return {info.name: info for info in tar.getmembers()}


def find_pin(obj, key, value):
    if isinstance(obj, dict):
        return any((k == key and v == value) or find_pin(v, key, value) for k, v in obj.items())
    if isinstance(obj, list):
        return any(find_pin(v, key, value) for v in obj)
    return False


def load(name, members=None, archive_path=None, overrides=None):
    """Check the byte binding of one case and return its decoded inputs.

    members, archive_path and overrides exist for the packaging controls in test_package.py.
    """
    case = dict(SOURCES['cases'][name], **(overrides or {}))
    members = dict(SOURCES['members'], **(members or {}))
    arc = case['archive']
    path = Path(archive_path) if archive_path else ROOT / arc['path']
    raw = path.read_bytes()
    need(sha(raw) == arc['sha256'], 'B1 archive digest')
    need(find_pin(json.loads((ROOT / arc['pinned_by']).read_text()), arc['path'], arc['sha256']), 'B1 archive pin')
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:     # parse exactly the hashed bytes
        index = safe_members(tar)

        def member(key):
            full = case['prefix'] + members[key]
            need(full in index, 'B2 archive member present: ' + key)
            return tar.extractfile(index[full]).read()
        got = {k: member(k) for k in members}
    asm = json.loads(got['assembly'])
    binding = dict(archive=arc['path'], archive_sha256=arc['sha256'], member_prefix=case['prefix'])
    if case['assembly']:
        repo_asm = (ROOT / case['assembly']).read_bytes()
        need(repo_asm == got['assembly'], 'B3 repository certificate equals the capsule certificate')
        binding['certificate'] = case['assembly']
        binding['certificate_sha256'] = sha(repo_asm)
    if case['record']:
        # a checkpoint record if the frontier has moved on, otherwise the selected record
        for record in case['record']:
            rec = json.loads((ROOT / record).read_text()) if (ROOT / record).is_file() else {}
            if rec.get('certificate') == case['assembly'] and rec.get('certificate_sha256') == sha(got['assembly']):
                binding['record'] = record
                break
        need('record' in binding, 'B3 record binds the certificate')
    template_raw = gzip.decompress(got['template'])
    need(sha(template_raw) == asm['template_sha256'], 'B4 template digest')
    need(sha(got['owner_audit']) == asm['input_sha256']['owner_audit'], 'B5 owner audit digest')
    audit = json.loads(got['owner_audit'])
    need(audit['template_sha256'] == asm['template_sha256'], 'B5 owner audit template')
    src = audit['source_artifacts']
    for key, art in SOURCES['source_artifact_keys'].items():
        need(sha(got[key]) == src[art], 'B6 dispatched input digest: ' + key)
    template = json.loads(template_raw)
    need(template['exact_data_phase_recipe_sha256'] == sha(got['data_phases']), 'B6 data phases bound by the template')
    receipt = json.loads(got['remainder_receipt'])
    frames_raw = gzip.decompress(got['remainder_frames'])
    need(receipt['template_sha256'] == asm['template_sha256'] and receipt['uncompressed_frames_sha256'] == sha(frames_raw)
         and receipt['source_data_phase_sha256'] == sha(got['data_phases']), 'B8 literal remainder frames')
    owners_raw = (ROOT / case['owners']).read_bytes()
    need(sha(owners_raw) == template['hosting']['owner_map_sha256'], 'B7 owner map digest')
    need(sha(owners_raw) in (ROOT / case['owners_listed_in']).read_text(), 'B7 owner map in the source manifest')
    local_replay = json.loads(got['local_replay'])
    need(local_replay['local_programs_sha256'] == sha(got['local_programs'])
         and local_replay['canonical_word_sha256'] == sha(got['canonical_word']), 'B6 local replay receipt binds the same programs and word')
    full_word = None
    if case['full_word_pin']:
        pin_path, pin_key = case['full_word_pin']
        fw_raw = gzip.decompress(got['full_word'])
        need(find_pin(json.loads((ROOT / pin_path).read_text()), pin_key, sha(fw_raw)), 'B9 full word pinned')
        full_word = json.loads(fw_raw)
    independent = None
    if case['independent_profile']:
        ind_path, *fields = case['independent_profile']
        independent = json.loads((ROOT / ind_path).read_text())
        for f in fields:
            independent = independent[f]
    binding.update(template_sha256=asm['template_sha256'], owner_audit_sha256=asm['input_sha256']['owner_audit'],
                   owner_map=case['owners'], owner_map_sha256=template['hosting']['owner_map_sha256'],
                   local_programs_gz_sha256=sha(got['local_programs']), canonical_word_gz_sha256=sha(got['canonical_word']),
                   data_phases_sha256=sha(got['data_phases']), remainder_frames_sha256=sha(frames_raw))
    return dict(template=template, programs=json.loads(gzip.decompress(got['local_programs'])),
                word=json.loads(gzip.decompress(got['canonical_word'])), phases=json.loads(got['data_phases']),
                frames=json.loads(frames_raw), owners=json.loads(gzip.decompress(owners_raw)), assembly=asm,
                audit=audit, local_replay=local_replay, full_word=full_word, independent=independent), binding


# ---------------------------------------------------------------- the ledger, from operations
def dot(a, b):
    return (a & b).bit_count() & 1


def orthonormal(vectors):
    """Pairwise F2 dot products are the identity: implies linear independence (and so a direct sum)."""
    return all(dot(a, b) == (i == j) for i, a in enumerate(vectors) for j, b in enumerate(vectors) if j >= i)


def program_ledger(program, word, orientation):
    """Replay one dispatched program over the canonical frames.

    Every register starts at word['start'], each climb must leave the register's current frame for a
    strictly larger frame containing it, and every register must end at word['final']. Centre i goes
    from word['center_frames'][i] to the empty frame (forward) or back (backward), with its carrier
    register word['centers'][i] sitting at that centre frame. Returns the rank histogram of paid
    children, per-register climb units and the centre mass.
    """
    frames = word['frames']
    dims = [len(basis(f)) for f in frames]
    start, final = list(word['start']), list(word['final'])
    current = list(start)
    hist, per_register, centre_mass, centres_seen, phases = Counter(), Counter(), 0, [], []
    for e in program:
        need(e[0] in PROGRAM_EVENTS, 'L4 closed program vocabulary')
        phase = phases[-1] if phases else None
        if e[0] == 'phase':
            phases.append(e[1])
        elif e[0] == 'climb':
            _, tag, reg, a, b, declared = e
            need(0 <= reg < len(current) and tag == phase, 'L5 climb is in its phase on a real register')
            need(a == current[reg], 'L5 climb leaves its register\'s current frame')
            rank = dims[b] - dims[a]
            need(rank > 0 and nested(frames[a], frames[b]), 'L5 climbs ascend through nested frames')
            need(rank == declared, 'L6 frame-derived climb rank')
            current[reg] = b
            hist[rank] += 1
            per_register[reg] += rank
        elif e[0] == 'center':
            _, i, a, b, declared = e
            cf, carrier = word['center_frames'][i], word['centers'][i]
            need(phase == 'centers' and (a, b) == ((cf, b) if orientation == 'forward' else (a, cf))
                 and dims[b if orientation == 'forward' else a] == 0 and current[carrier] == cf,
                 'L7 centre bound to its frame and carrier')
            rank = dims[cf]
            need(rank > 0 and rank == declared, 'L6 frame-derived centre rank')
            centres_seen.append(i)
            hist[rank] += 1
            centre_mass += rank
        elif e[0] == 'adapter':
            reg = e[2]
            need(e[1] in ('old_to_new', 'new_to_old') and 0 <= reg < len(current)
                 and e[3] == current[reg] == (start if e[1] == 'old_to_new' else final)[reg], 'L5 adapter at its register\'s frame')
        elif e[0] == 'residual_adapter':
            reg = e[2]
            need(0 <= reg < len(current) and e[3] == start[reg] and e[4:] in ([], [final[reg]]),
                 'L5 residual adapter at its register\'s frames')
        elif e[0] == 'scalar':
            op = e[1]
            for operand in op[1:]:
                if isinstance(operand, list) and operand and operand[0] == 'L':
                    need(0 <= operand[1] < len(current) and current[operand[1]] == e[2], 'L5 scalar acts at its registers\' frames')
    need(phases == PHASES, 'L4 phase sequence')
    need(current == list(word['final']), 'L5 every register ends at its final frame')
    need(sorted(centres_seen) == list(range(len(word['centers']))), 'L7 every centre exactly once')
    return hist, per_register, centre_mass


def check(d):
    T, P, CW, DP = d['template'], d['programs'], d['word'], d['phases']
    provider = T['local_providers']['gauge44']
    V, R, H = CW['v'], CW['R'], CW['h']
    need(provider['local_programs'] == P and provider['v'] == DP['ports'] == V and provider['R'] == R,
         'L3 dispatched programs are the ones embedded in the template')
    m, W = T['m'], T['live']
    locals_ = {x['stage']: x for x in T['recipe'] if x['kind'] == 'local'}
    pairs = len({x['pair'] for x in locals_.values()})
    F = 2 * pairs * V                                   # live families per replica
    cover = T['cover_final_correction']
    need(cover['charged_calls_per_cover'] == W and cover['families'] == [0, W] and W % F == 0,
         'L9 live families W from the program')
    replicas = W // F
    calls = T['calls']
    N = len(calls)
    need(sorted((c['stage'], c['replica']) for c in calls) == [(s, r) for s in sorted(locals_) for r in range(replicas)],
         'L1 call coverage: every (local stage, replica) exactly once')
    schedule = T['execution_schedule']
    for e in schedule:
        need(e['kind'] in SCHEDULE_EVENTS, 'L4 closed schedule vocabulary')
        need('replica' not in e or e.get('replicas', [e['replica']]) == [e['replica']], 'L9 schedule events act on one replica')
    need(Counter((e['stage'], e['replica'], e['provider_id']) for e in schedule if e['kind'] == 'local_cover_sweep')
         == Counter((c['stage'], c['replica'], c['provider_id']) for c in calls), 'L9 local sweeps dispatch exactly the calls')
    need(list(T['local_providers']) == ['gauge44'], 'L9 one local provider')
    idle_sweeps = Counter((e['replica'], e['pair'], tuple(e['child_indices'])) for e in schedule if e['kind'] == 'idle_cover_sweep')
    need(all(n == 1 for n in idle_sweeps.values()), 'L9 every idle sweep once')
    need(not T['bank_padding']['children'] and all(e['children_source'] == 'bank_padding.children' for e in schedule
                                                    if e['kind'] == 'bank_padding_cover_sweep'), 'L8 no bank-padding children')

    programs = {}
    for o, program in P.items():
        programs[sha(compact(program))] = (o, *program_ledger(program, CW, o))
    need(len({c for (_, _, _, c) in programs.values()}) == 1, 'L7 equal centre mass in every orientation')
    local_hist, data_units = Counter(), Counter()
    slot_keys = Counter((z['stage'], z['replica'], z['helper']) for z in d['owners'])
    need(slot_keys == Counter((c['stage'], c['replica'], i) for c in calls for i in range(R))
         and all(0 <= z['owner_replica'] < replicas for z in d['owners']), 'L11 every owner-map slot is executed by exactly one call route')
    slots_at = defaultdict(dict)
    for z in d['owners']:
        slots_at[(z['stage'], z['replica'])][z['helper']] = z
    for c in calls:
        need(c['local_program_sha256'] in programs and programs[c['local_program_sha256']][0] == c['orientation']
             and c['provider_id'] == 'gauge44', 'L3 call bound to its dispatched program')
        need(c['orientation'] == ('backward' if locals_[c['stage']]['reverse'] else 'forward')
             and c['pair'] == locals_[c['stage']]['pair'], 'L2 orientation and pair follow the recipe')
        _, hist, per, _ = programs[c['local_program_sha256']]
        local_hist.update(hist)
        owners = c['owners']
        need(len(owners) == 2 * V + R and len({fam for fam, _ in owners}) == len(owners)
             and all(0 <= fam < W for fam, _ in owners), 'L10 one route per live owner family in every call')
        active = {c['replica'] * F + (2 * c['pair'] + side) * V + port for side in (0, 1) for port in range(V)}
        need({fam for fam, desc in owners[:2 * V]} == active and all(desc[0] == 1 for _, desc in owners[:2 * V]),
             'L10 data routes are the active pair families')
        for i in range(2 * V):
            data_units[owners[i][0]] += per[i]
        for i in range(R):
            fam, desc = owners[2 * V + i]
            z = slots_at[(c['stage'], c['replica'])].get(i)
            need(z is not None and fam == z['family'] and desc[0] in (3, 4) and desc[1] == z['child'] and desc[2] == z['offset']
                 and (desc[0] == 3) == (z['width'] == 9), 'L11 helper route equals its hosted slot')
            if desc[0] == 4:
                need(desc[3] == z['width'] and len(desc[4]) == len(set(desc[4])) == 9 - z['width'], 'L12 spectators')
            need(per[2 * V + i] == z['width'] == provider['widths'][i], 'L13 helper climb total equals hosted and template width')

    # pending children of every idle cover sweep
    place, sweeps = {}, set()
    for e in T['execution_schedule']:
        if e['kind'] == 'idle_cover_sweep':
            for side, ch in enumerate(e['child_indices']):
                need(place.setdefault(ch, (e['pair'], side)) == (e['pair'], side), 'L14 child placement is consistent')
                sweeps.add((e['replica'], ch))
    axes = defaultdict(dict)
    for rec in DP['recipes']:
        for ch, item in enumerate(rec['idle_children']):
            need(len(item['orthogonal_axes']) == item['rank'], 'L14 pending axes count equals rank')
            axes[ch][rec['port']] = item['orthogonal_axes']
    need(set(next(iter(axes.values()))) == set(range(V)), 'L14 every port has a recipe')
    rank = {}
    for ch, per_port in axes.items():
        ranks = {len(a) for a in per_port.values()}
        need(len(ranks) == 1, 'L14 child rank is port independent')
        rank[ch] = ranks.pop()
    need(sweeps == {(r, ch) for r in range(replicas) for ch in place}, 'L14 every replica sweeps every placed child')
    pending = {}
    for port in range(V):
        by_slot = defaultdict(list)
        for ch, (p, s) in place.items():
            by_slot[(p, s)] += axes[ch][port]
        for key, vectors in by_slot.items():
            need(orthonormal(vectors), 'L15 sibling pending children are jointly F2-orthonormal')
            pending[key + (port,)] = len(vectors)

    need(T['hosting']['pooled_slots'] == d['owners'], 'L16 template slots equal the owner map')
    occupied = defaultdict(list)
    for z in d['owners']:
        p, s = place.get(z['child'], (None, None))
        need(p is not None and rank[z['child']] > 0 and
             z['family'] == z['owner_replica'] * F + (2 * p + s) * V + z['port'], 'L17 slot lies in a pending child')
        occupied[(z['owner_replica'], z['child'], z['port'])].append((z['offset'], z['width']))
    expect = {}
    for (rep, ch), port in ((k, q) for k in sorted(sweeps) for q in range(V)):
        if not rank[ch]:
            continue
        pos = 0
        for off, w in sorted(occupied.get((rep, ch, port), [])):
            need(off == pos, 'L18 hosted slices form a contiguous prefix')
            pos += w
        need(pos <= rank[ch], 'L18 hosted slices fit the pending child')
        if pos < rank[ch]:
            p, s = place[ch]
            expect[(rep * F + (2 * p + s) * V + port, ch)] = dict(replica=rep, port=port, hosted=pos, rank=rank[ch] - pos)
    emitted = {}
    for x in T['idle_children']:
        key = (x['family'], x['child'])
        need(key not in emitted and x['replicas'] == 1 and x['pending_offset'] == x['hosted'], 'L19 idle child records')
        emitted[key] = dict(replica=x['replica'], port=x['port'], hosted=x['hosted'], rank=x['rank'])
    need(emitted == expect, 'L19 emitted idle remainders equal the recount')
    need(len(d['frames']) == len(expect) and {(f['family'], f['child']) for f in d['frames']} == set(expect),
         'L20 one literal frame per remainder')
    for f in d['frames']:
        e = expect.get((f['family'], f['child']))
        need(e is not None and f['orthogonal_axes'] == axes[f['child']][e['port']][e['hosted']:]
             and len(f['orthogonal_axes']) == len(basis(f['orthogonal_axes'])) == e['rank'], 'L20 literal remainder frames')

    for f in range(W):
        rep, rest = divmod(f, F)
        ps, port = divmod(rest, V)
        p, s = divmod(ps, 2)
        need(data_units[f] + pending[(p, s, port)] == m - 1, 'L21 per-family rank conservation')
    idle = Counter(e['rank'] for e in expect.values())
    ledger = local_hist + idle
    mass = sum(r * n for r, n in ledger.items())
    centre = next(iter(programs.values()))[3]
    need(mass == (m - 1) * W + centre * N, 'L22 rank mass identity')
    need(d['audit']['rank_mass'] == mass and d['audit']['deficit'] == m * W - mass, 'L22 owner audit mass and deficit')
    profile = {int(k): v for k, v in d['assembly']['complex_profile'].items()}
    need(dict(ledger) == profile, 'L23 ledger equals the certificate complex_profile')
    need({int(k): v for k, v in d['audit']['paid_profile'].items()} == profile and d['audit']['live'] == W,
         'L23 ledger equals the owner-audit paid_profile')
    if d['independent'] is not None:
        need({int(k): v for k, v in d['independent'].items()} == profile, 'L23 ledger equals INDEPENDENT1094')
    if d['full_word'] is not None:
        fw = d['full_word']
        full = [1 << i for i in range(H)]
        for i in range(R):
            q = 2 * V + i
            width = len(basis(fw['helper_final'].get(str(q), full))) - len(basis(fw['start_extra'].get(str(q), [])))
            for program in programs.values():
                need(program[2][q] == width, 'L24 helper climb totals equal the pinned FULL-WORD widths')
    per_orientation = {o: dict(sorted(h.items())) for (o, h, _, _) in programs.values()}
    replayed = {o: {int(k): n for k, n in p.items()} for o, p in d['local_replay']['paid_profiles'].items()}
    need(replayed == per_orientation, 'L25 per-call ledgers equal the in-lineage local replay receipt')
    calls_per_family = Counter()
    for c in calls:
        calls_per_family[c['pair']] += 1
    calls_per_family = {p: n // replicas for p, n in sorted(calls_per_family.items())}
    return dict(W=W, N=N, m=m, replicas=replicas, ports=V, helpers=R, centre_mass_per_call=centre,
                local_profile_per_call=per_orientation, idle_histogram=dict(sorted(idle.items())),
                owner_families_per_call=dict(data=2 * V, helper=R, distinct_owners=2 * V + R),
                live_families_per_call=dict(W=W, N=N, per_replica=F, stages=len(locals_)),
                calls_per_family_by_pair=calls_per_family, local_calls=dict(sorted(Counter(c['orientation'] for c in calls).items())),
                pending_children=sum(1 for (rep, ch) in sweeps for _ in range(V) if rank[ch]),
                pending_mass=sum(pending[(p, s, q)] for (p, s, q) in pending) * replicas,
                hosted_mass=sum(z['width'] for z in d['owners']), remainders=len(expect),
                remainder_mass=sum(r * n for r, n in idle.items()), ledger=dict(sorted(ledger.items())), rank_mass=mass, deficit=m * W - mass,
                deficit_identity='D = W - %d N' % centre, family_units=m - 1)


def run(names):
    out = {}
    for name in names:
        t = time.monotonic()
        data, binding = load(name)
        result = check(data)
        out[name] = dict(binding=binding, **result)
        print('PASS', name, 'ledger', result['ledger'], 'mass', result['rank_mass'], 'D', result['deficit'],
              '%.1f s' % (time.monotonic() - t), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--case', action='append', choices=sorted(SOURCES['cases']))
    ap.add_argument('--write', action='store_true', help='write RESULT.json instead of comparing with it')
    a = ap.parse_args()
    names = a.case or list(SOURCES['cases'])
    try:
        out = run(names)
    except Reject as e:
        raise SystemExit('FAIL ' + str(e))
    text = json.dumps(dict(status='PASS_FRONTIER1094_EMITTED_LEDGER', cases=out), indent=1, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if a.write:
        target.write_text(text)
    elif names == list(SOURCES['cases']):
        if text != target.read_text():
            raise SystemExit('FAIL RESULT.json differs from this run')
        print('PASS RESULT.json reproduced byte for byte')
    else:
        print('PASS_PARTIAL', ' '.join(names), '(RESULT.json not compared)')
        return
    print('PASS_FRONTIER1094_EMITTED_LEDGER')


if __name__ == '__main__':
    main()
