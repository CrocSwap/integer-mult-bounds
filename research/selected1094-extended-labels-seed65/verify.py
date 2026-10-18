#!/usr/bin/env python3
"""selected1094-extended-labels-seed65: Lemma G hypothesis H1 (extended labels) on the selected #1094 local programs,
the admission gap of the frame-only replay (three exact mutants), and the published Lemma G checker run three ways.

Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.  Apache-2.0.

Standard library only.  Every check raises ValueError (never `assert`), so `python -O` cannot weaken it.  Pinned
producer scripts run in fresh `-I -B` subprocesses from byte copies whose SHA-256 was checked against SOURCES.json, so
their own assertions stay active.  Run from the repository root:

    python3 -B research/selected1094-extended-labels-seed65/verify.py [--keep DIR]

Stages (README.md / PROOF.md give the mathematics):
  0  pins: every live input against SOURCES.json; quoted source lines that PROOF.md relies on; the patched checker copy
     rebuilt byte-for-byte from the pinned original.
  1  selected pins: SLOT-PINS-k8 and the #1094 PLAN provider registry name the same four hashes.
  2  regeneration from committed bytes: PR635 transport -> canonical payload, PR635 emitter -> both programs, PR635
     frame-only replay (PASS, 25 controls), PR558 phases_full -> CLIFFORD-RECIPES (run concurrently).
  3  (a) independent HPE-aware extended-label checker, both orientations, two readings; adapter/wrapper bridge;
     independent exact scalar shadow (H3); structural facts used by the all-words lemma; failure controls of the
     checker (pinned counts).
  4  (b) three scalar-neutral mutants (exit straddle X, entry straddle Y, exit-adapter block moved into phase B, Z):
     accepted by the pinned frame-only replay, rejected by both label checkers and by the recommended adapter rule;
     exact segment algebra; the preconditions of the physical-consequence argument.  Then every clause of label_check
     is weakened alone, in memory, and re-run on every pinned input (the surviving weakenings are pinned).
  5  endpoint adapters: all 224 rank-0 records are non-identity monomials (independent evaluator, cross-checked against
     the pinned clifford_exact circuit semantics on the port-0 witnesses).
  6  (c) the published Lemma G checker: as published, with the 5th field stripped, and as the patched copy.
  7  every number is compared with EXPECTED.json.
"""
import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import types
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]

WORD = 'research/k8-frame-antichain/inputs/SEVEN-SLOT-WORD.json.gz'
ROUTING = ('research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/inputs/'
           'phase-baseline/CANONICAL-WORD.json.gz')
PR635 = 'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code/'
TRANSPORT, EMIT, AUDIT = PR635 + 'hpe_audit_and_transport.py', PR635 + 'hpe_emit_local.py', PR635 + 'hpe_audit_local.py'
PHASES = 'research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/code/phases_full.py'
CLIFFORD = ('research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/'
            'vendor/clifford/clifford_exact.py')
SLOTPINS = 'research/gauge44-slots/construction/slots/SLOT-PINS-k8.json'
PLAN = 'research/complex-t16-rare-pattern-exchanges/data/PLAN.json'
LG_CHECK = 'research/e8-lemma-g-lean/code/check_extended_labels.py'
STREAM_LEAN = 'research/e8-lemma-g-lean/LemmaG/Stream.lean'
LG_PROOF = 'research/e8-lemma-g-lean/PROOF.md'
LG_README = 'research/e8-lemma-g-lean/README.md'
HPE_PROOF = 'research/hyperplane-end-lean/PROOF.md'
LG_PHYS = 'research/e8-complex-gauge-kernel/code/lemmaG/lg_phys.py'
BIT_R420 = 'research/e8-bit-r420/README.md'
BIT_P111 = 'research/e8-bit-p111-tuned/tune/README.md'
CARRYOVER = 'research/post-center-rank4-global/proof/PR510-MUTABLE-SOURCE-CARRYOVER.md'
PATCHED = PKG / 'patched' / 'check_extended_labels_hpe.py'

FULL = 1                       # frame-table row of FULL (row 0 is the zero frame)
T = ('T',)                     # the word's family tag
FREE = 'free'                  # label of a cleared private register under the permissive reading
PHASE_ORDER = ['zero_frame_precondition', 'entry_adapters', 'A', 'centers', 'B', 'cleanup_tail', 'final',
               'exit_adapters', 'full_frame_cleanup', 'done']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def digest(obj):
    return sha(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode())


# ------------------------------------------------------------------------------------------------ stage 0: pins
SOURCES = json.loads((PKG / 'SOURCES.json').read_text(encoding='utf-8'))
PINS = {row['path']: row for row in SOURCES['files']}


def pinned(path):
    row = PINS.get(path)
    need(row is not None and row['usage'] == 'input', 'not a declared input: ' + path)
    data = (ROOT / path).read_bytes()
    need(sha(data) == row['sha256'] and git_blob(data) == row['git_blob'], 'input differs from its pin: ' + path)
    return data


def line_of(text, needle, path):
    need(text.count(needle) == 1, 'quoted source text not found exactly once in ' + path + ': ' + needle[:80])
    return text[:text.index(needle)].count('\n') + 1


# Exact source text that PROOF.md cites.  Each must occur exactly once in the pinned bytes; its line is recorded.
QUOTES = {
    STREAM_LEAN: {
        'conj_matrix': ('theorem conj_matrix (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))\n'
                        '    (l : ι → Λ) (h : ι → M) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (r : ι) :\n'
                        '    physRun rec es h r = T (labRun es l r) (∑ s, S es r s • (T (l s)).symm (h s)) := by'),
        'WellLabelled': 'def WellLabelled : List (Event ι Λ K) → (ι → Λ) → Prop',
        'RecipesExact': ('def RecipesExact (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K)) : Prop :=\n'
                         '  ∀ r A B, Event.relabel r A B ∈ es → ∀ v, rec A B v = T B ((T A).symm v)'),
        'Admissible_add': '  | add t s _, l => l t = l s',
    },
    LG_PROOF: {'theorem1': '**Theorem 1 (common-frame conjugation)** [`Stream.conj`, `Stream.conj\'`, `Stream.conj_matrix`].',
               'extended_labels': '**Extended labels.** A label is a pair (tag, frame `F`).'},
    LG_README: {'H1_row': '| H1 | the emitted stream is well labelled (extended labels: tag × frame) |'},
    HPE_PROOF: {'G0_row': '| `hw`, tail shape, `hmv` | G0 in `cleanup_tail`; no later gate relabels `h` | `audit_local.py` (`cur[r] == f` for both operands;'},
    AUDIT: {'frame_only_scalar_check': ("if r[0]=='L':assert cur[r[1]]==f and (r[1] not in wset or (r[1] in pre_seen and "
                                        "r[1] not in post_seen)),('common frame / wrapper order',r,cur[r[1]],f)"),
            'adapter_event_check': "elif tag=='adapter':\n            assert event[3]==(c['start'] if event[1]=='old_to_new' else c['final'])[event[2]]",
            'entry_list_at_A': "if event[1]=='A':assert entry==[(r,f) for r,f in enumerate(c['start']) if r in plain]",
            'exit_list_at_cleanup': ("if event[1]=='full_frame_cleanup':assert cur==c['final'] and "
                                     "exit==[(r,f) for r,f in enumerate(c['final']) if r not in hpe]"),
            'wrapper_frame_only_hpe_post': "if end and kind=='post':assert cur[r]==end[0]"},
    EMIT: {'precondition_start_zero': ("    event(['phase','zero_frame_precondition'])\n"
                                       "    for e in c['precondition']+c['compensation']:\n"
                                       "        regs=[e[1]]+([e[2]] if e[0]=='add' else [])\n"
                                       "        assert all(c['start'][r]==0 for r in regs)\n"
                                       "        scal(scalar(e,back),0)\n"
                                       "    event(['phase','entry_adapters'])"),
           'wrapped_set': 'wrapped=sorted(set(entering)|hpe)',
           'climb_before_gate': "                for r in regs:climb(r,e[-1],part)\n                scal(scalar(e,back),e[-1])",
           'centre_levels_asserted': "            assert all(cur[r]==lv(r) for r in range(v,2*v))",
           'centre_frame_asserted': "                cf=c['center_frames'][k];assert cur[r]==cf",
           'entry_phase_adapters_only': ("        else:event(['adapter','old_to_new',r,f])\n    def climb(r,f,part):"),
           'exit_phase': ("    event(['phase','exit_adapters'])\n    for r,f in enumerate(c['final']):\n"
                          "        if r not in hpe:event(['adapter','new_to_old',r,f])"),
           'cleanup_full_only': ("    event(['phase','full_frame_cleanup'])\n    for e in c['cleanup']:\n"
                                 "        regs=[e[1]]+([e[2]] if e[0]=='add' else [])\n"
                                 "        assert all(c['final'][r]==1 for r in regs)\n        scal(scalar(e,back),1)")},
    TRANSPORT: {'no_cold_hpe_in_precondition': "zero-frame precondition/compensation touches a cold hyperplane-ended helper before its wrapper'",
                'no_entering_in_precondition': "'zero-frame precondition/compensation touches an entering helper'",
                'ports_from_routing': "assert len(set(ports)) == v and set(map(tau, word['ports'])) == set(ports)",
                'source_start_lines': "canonical['start'] = [fid([p]) for p in ports] + [0]*(v+helpers)",
                'target_final_hyperplanes': "[fid(x for x in range(1, 1 << h) if (x & p).bit_count() % 2 == 0) for p in ports] +",
                'hpe_final_not_full': "assert all(len(frames[canonical['final'][r]]) < h for r in helper_final)"},
    LG_PHYS: {'target_exit_inverted': ("fr, circ = model.tgt_ad[r - model.v]; assert fr == f\n"
                                       "                    if x is not None: x.apply_circ(circ, inverse=True)"),
              'source_entry_direct': ("fr, circ = model.src_ad[r]; assert fr == f\n"
                                      "                    if x is not None: x.apply_circ(circ)"),
              'identity_exit_is_a_no_op': "else: assert f == 1, ('unexpected non-identity exit adapter', r, f)"},
    # the bit supplier's common-label / mutable-basis realization: retained, and not touched by this package
    BIT_R420: {'bit_side_realization': (
        "On the bit side, the realization\nis the role-independent common-label pullback of #472's PROOF.md (\"Shared "
        "physical labels\"), written out in #535's\n`PR510-MUTABLE-SOURCE-CARRYOVER.md`: an XOR between two registers at "
        "the same label commutes with that label,\nwhatever the registers are called and whether or not a source still "
        "holds its input, and nested climbs compose. That\nargument is also order-independent. The mutable-basis "
        "realization remains a listed conditional interface, as in\n#472, #493 and #510.")},
    BIT_P111: {'retained_mutable_source': ('All retained assumptions of #555 apply unchanged (mutable-source realization, '
                                           'whole-call hosting, the all-size compiler,')},
    CARRYOVER: {'mutable_basis_contract': ('Its nine-stage mutable-source realization is covered by the same role-independent\n'
                                           'common-label/mutable-basis contract already retained by PR493 and PR531.')},
}

# The patched copy = the pinned original with exactly these replacements (each must match once).
PATCH_HEADER = (
    "# PATCHED COPY (seed65) of research/e8-lemma-g-lean/code/check_extended_labels.py at base 0b1cccf8:\n"
    "#   original git blob bc1d9c32180a115e13c1a4d0ea670ecc7f51c819,\n"
    "#   original sha256   9e072754d350e79e5657196bee30cd18ed0a0677628aa66d16a15ce2aab1d2ea.\n"
    "# Patched by Sagar Thakrar with Anthropic Claude assistance (Apache-2.0).  Apart from this header, only the three lines\n"
    "# marked PATCH(seed65) differ from the original: cold hyperplane-ended helpers (start frame 0, terminal frame U != FULL)\n"
    "# are wrapped like entering helpers, and an HPE wrapper event carries a 5th field U that must equal the helper's terminal\n"
    "# frame.  Everything else is verbatim, including the 50-entry violation cap and the lg_lib import used only by main().\n"
    "# research/selected1094-extended-labels-seed65/verify.py rebuilds this file from the pinned original and compares bytes.\n")
PATCHES = [
    ("# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.\n",
     "# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.\n" + PATCH_HEADER),
    ("    entering = {r for r in range(2 * v, n) if start[r] != 0}\n",
     "    entering = {r for r in range(2 * v, n) if start[r] != 0 or final[r] != FULL}   # PATCH(seed65): + cold-HPE helpers (wrapped)\n"),
    ("            _, side, r, f = e; x = ('L', r)\n",
     "            _, side, r, f, *U = e; x = ('L', r)   # PATCH(seed65): an HPE wrapper carries a 5th field U\n"
     "            if U != ([final[r]] if final[r] != FULL else []): bad(f'wrapper {idx}: {r} names terminal frame {U} not its final {final[r]}')   # PATCH(seed65)\n"),
]
CAP_LINE = 'bad = lambda m: viol.append(m) if len(viol) < 50 else None'


def stage0():
    out = {}
    for path, quotes in QUOTES.items():
        text = pinned(path).decode('utf-8')
        out[path] = {name: line_of(text, needle, path) for name, needle in quotes.items()}
    original = pinned(LG_CHECK).decode('utf-8')
    rebuilt = original
    for old, new in PATCHES:
        need(rebuilt.count(old) == 1, 'patch anchor not unique in the pinned original: ' + old[:60])
        rebuilt = rebuilt.replace(old, new)
    patched = PATCHED.read_bytes()
    need(patched == rebuilt.encode('utf-8'), 'patched/check_extended_labels_hpe.py is not the documented patch of the pinned original')
    need(PINS[LG_CHECK]['git_blob'] == 'bc1d9c32180a115e13c1a4d0ea670ecc7f51c819'
         and PINS[LG_CHECK]['sha256'] == '9e072754d350e79e5657196bee30cd18ed0a0677628aa66d16a15ce2aab1d2ea',
         'patched-copy header names a different original than SOURCES.json')
    need(original.count(CAP_LINE) == 1, 'cap line of the published checker not found exactly once')
    marked = [line for line in patched.decode('utf-8').splitlines() if 'PATCH(seed65)' in line and not line.startswith('#')]
    return {'quoted_lines': out, 'patched_copy_marked_lines': len(marked), 'patched_copy_sha256': sha(patched)}


# ------------------------------------------------------------------------------------------------ stage 1: selected pins
def stage1():
    slot = json.loads(pinned(SLOTPINS))
    plan = json.loads(pinned(PLAN))
    reg = plan['provider_registry']['gauge44']
    names = {
        'word': slot['word_sha256'],
        'canonical': slot['canonical_sha256'],
        'forward': slot['program_sha256']['forward'],
        'backward': slot['program_sha256']['backward'],
        'recipes': slot['clifford_recipes_sha256'],
    }
    need(reg['artifact_semantic_sha256']['CANONICAL-WORD.json.gz'] == names['canonical'], 'PLAN canonical != SLOT-PINS')
    need(reg['orientation_program_sha256'] == {'forward': names['forward'], 'backward': names['backward']}, 'PLAN programs != SLOT-PINS')
    need(reg['artifact_sha256']['CLIFFORD-RECIPES.json'] == names['recipes'] ==
         reg['artifact_semantic_sha256']['CLIFFORD-RECIPES.json'], 'PLAN recipes != SLOT-PINS')
    calls = Counter(call['local_program_sha256'] for call in plan['provider_calls'])
    need(set(calls) == {names['forward'], names['backward']}, 'a provider call names another local program')
    return dict(names, plan_provider_calls={'forward': calls[names['forward']], 'backward': calls[names['backward']]})


# ------------------------------------------------------------------------------------------------ stage 2: regeneration
def run(argv, cwd, timeout, expect):
    proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    need(proc.returncode == 0, 'pinned script failed: ' + str(argv[3]) + '\n' + proc.stderr[-2000:])
    for line in expect:
        need(line in proc.stdout, 'pinned script output lacks ' + repr(line))
    return proc


def stage2_start(tmp, pins):
    code = tmp / 'code'; clif = tmp / 'clifford'; inp = tmp / 'in'
    for d in (code, clif, inp):
        d.mkdir()
    for path in (TRANSPORT, EMIT, AUDIT, PHASES):
        (code / Path(path).name).write_bytes(pinned(path))
    (clif / 'clifford_exact.py').write_bytes(pinned(CLIFFORD))
    (inp / 'SEVEN-SLOT-WORD.json.gz').write_bytes(pinned(WORD))
    (inp / 'ROUTING-CANONICAL-WORD.json.gz').write_bytes(pinned(ROUTING))
    local = tmp / 'local'
    py = [sys.executable, '-I', '-B']
    run(py + [str(code / 'hpe_audit_and_transport.py'), '--raw', str(inp / 'SEVEN-SLOT-WORD.json.gz'),
              '--routing', str(inp / 'ROUTING-CANONICAL-WORD.json.gz'), '--out', str(local)], tmp, 120,
        ['PASS_CHANGED_WORD_ALL_COLUMNS_AND_NATIVE_FRAMES'])
    receipt = json.loads((local / 'SCALAR-FRAME-AUDIT.json').read_text())
    payload = gzip.decompress((local / 'CANONICAL-WORD.json.gz').read_bytes())
    need(sha(payload) == pins['canonical'] == receipt['canonical_content_sha256'], 'canonical payload != selected pin')
    need(receipt['input_content_sha256'] == pins['word'], 'transport read another word')
    # phases_full only reads CANONICAL-WORD; it runs concurrently with the rest and writes its own files.
    log = open(tmp / 'phases_full.log', 'w')
    phases = subprocess.Popen(py + [str(code / 'phases_full.py'), str(local), str(clif)], cwd=tmp, stdout=log,
                              stderr=subprocess.STDOUT)
    run(py + [str(code / 'hpe_emit_local.py'), str(local)], tmp, 120,
        ['PASS emitted forward 24767 events', 'PASS emitted backward 24767 events'])
    progs = json.loads(gzip.decompress((local / 'LOCAL-PROGRAMS.json.gz').read_bytes()))
    need(digest(progs['forward']) == pins['forward'] and digest(progs['backward']) == pins['backward'],
         'regenerated programs != selected pins')
    replay = audit_local(py, code, local, tmp)
    c = json.loads(payload)
    out = dict(transport=dict(status=receipt['status'], scalar_operations=receipt['scalar_operations'],
                              compensation_additions=receipt['compensation_additions'], helpers=receipt['helpers'],
                              frames=receipt['frames'], directed_edges=receipt['directed_edges'],
                              cold_hyperplane_ended_helpers=len(receipt['cold_hyperplane_ended_helpers']),
                              hyperplane_ended_helpers=len(receipt['hyperplane_ended_helpers']),
                              local_profile=receipt['local_profile']),
               frame_only_replay_honest=replay)
    return c, progs, phases, log, out


def audit_local(py, code, directory, tmp):
    """Run the pinned PR635 frame-only replay on a directory; return its verdict and controls."""
    proc = subprocess.run(py + [str(code / 'hpe_audit_local.py'), str(directory)], cwd=tmp, capture_output=True,
                          text=True, timeout=240)
    accepted = proc.returncode == 0 and 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY' in proc.stdout
    controls = None
    if accepted:
        res = json.loads((directory / 'INDEPENDENT-LOCAL-REPLAY.json').read_text())
        controls = len(res['negative_controls_rejected'])
    return dict(exit_code=proc.returncode, accepted=accepted, controls_rejected=controls)


# ------------------------------------------------------------------------------------------------ stage 3: label checker
def operands(op):
    return [tuple(op[1]), tuple(op[2])] if op[0] in ('add', 'copy') else [tuple(op[1])]


def label_check(c, events, reading):
    """Independent, HPE-aware Lemma G H1 check in the extended labels (tag, frame) of PROOF.md.

    Every climb, centre step, data adapter and wrapper is read as Lean's `relabel r A B` and must find its register at
    label A.  Scalar events, two readings:
      'strict'     clear C at f sets (T, f); add/scale/copy need every operand at (T, f) (G0, stronger than Lean's
                   Admissible, which asks only lt = ls for add and lr = F for copy);
      'permissive' clear leaves a private label unconstrained until its next touch, the frame annotation is ignored,
                   and only Lean's Admissible is asked (add: lt = ls; copy: none, it sets lc := lr; scale: none).
    Acceptance under 'strict' implies acceptance under 'permissive'; a rejection under 'permissive' means no reading of
    the private clears makes the stream WellLabelled.  The adapter/wrapper bridge and end labels are checked as well.
    Returns (violations, statistics)."""
    v, R = c['v'], c['R']; n = 2 * v + R; start, final = c['start'], c['final']
    hpe = {r for r in range(2 * v, n) if final[r] != FULL}
    entering = {r for r in range(2 * v, n) if start[r] != 0}
    wrapped = hpe | entering
    lab = {('L', r): (('pre', r) if r < v else ('prew', r) if r in wrapped else T, start[r]) for r in range(n)}
    first_private = {}
    viol = []; st = Counter(); src = Counter(); by_phase = Counter(); phases = []
    entry, exit_, pre, post = Counter(), Counter(), Counter(), Counter()
    phase = None

    def bad(idx, why):
        viol.append([idx, phase, why])

    for idx, e in enumerate(events):
        kind = e[0]; st['events'] += 1
        if kind == 'phase':
            phase = e[1]; phases.append(phase); continue
        if kind == 'scalar':
            op, f = e[1], e[2]; regs = operands(op); st['scalar_' + op[0]] += 1; by_phase[phase] += 1
            for x in regs:
                if x[0] == 'C' and x not in first_private:
                    # Lean leaves a private register's initial label free; record whether its dirty initial content
                    # can be read (a hygiene fact, not a label violation).
                    first_private[x] = op[0] if (op[0] == 'clear' or (op[0] == 'copy' and x == regs[0])) else 'read'
                    lab.setdefault(x, FREE)
            if op[0] in ('add', 'scale') and regs[0][0] == 'L' and regs[0][1] < v:
                src[phase] += 1
            want = (T, f)
            if op[0] == 'clear':
                lab[regs[0]] = want if reading == 'strict' else FREE
            elif op[0] == 'copy':
                t, s = regs
                if reading == 'strict':
                    if lab.get(s) != want: bad(idx, f'copy source {s} at {lab.get(s)} not {want}')
                    lab[t] = want
                else:
                    lab[t] = lab.get(s)
            elif op[0] == 'add':
                t, s = regs
                if reading == 'strict':
                    for x in (t, s):
                        if lab.get(x) == FREE and x[0] == 'C': lab[x] = want
                    off = [(x, lab.get(x)) for x in (t, s) if lab.get(x) != want]
                    if off: bad(idx, f'add operands {off} not at {want}')
                else:
                    if lab.get(t) == FREE: lab[t] = lab.get(s)
                    if lab.get(s) == FREE: lab[s] = lab.get(t)
                    if lab.get(t) != lab.get(s): bad(idx, f'add {t} at {lab.get(t)} but {s} at {lab.get(s)}')
            elif op[0] == 'scale':
                if reading == 'strict':
                    x = regs[0]
                    if lab.get(x) == FREE and x[0] == 'C': lab[x] = want
                    if lab.get(x) != want: bad(idx, f'scale operand {x} at {lab.get(x)} not {want}')
            else:
                bad(idx, 'unknown scalar ' + str(op[0]))
            continue
        if kind == 'climb':
            _, part, r, a, b, rank = e; x = ('L', r); st['climb'] += 1
            if lab[x] != (T, a): bad(idx, f'climb of {r} from {lab[x]} not (T,{a})')
            lab[x] = (T, b)
        elif kind == 'center':
            _, k, a, b, rank = e; x = ('C', k); st['centre_step'] += 1
            if lab.get(x) == FREE: lab[x] = (T, a)
            if lab.get(x) != (T, a): bad(idx, f'centre step of {x} from {lab.get(x)} not (T,{a})')
            lab[x] = (T, b)
        elif kind == 'adapter':
            _, way, r, f = e; x = ('L', r)
            if way == 'old_to_new':
                entry[r] += 1; st['entry_adapter'] += 1
                if r < v:
                    if f != start[r] or lab[x] != (('pre', r), f): bad(idx, f'source entry adapter of {r} at {lab[x]}, frame {f}')
                    lab[x] = (T, f)
                else:
                    if r in wrapped or f != 0 or lab[x] != (T, 0): bad(idx, f'identity entry adapter of {r} at {lab[x]}, frame {f}')
            elif way == 'new_to_old':
                exit_[r] += 1; st['exit_adapter'] += 1
                if v <= r < 2 * v:
                    if f != final[r] or lab[x] != (T, f): bad(idx, f'target exit adapter of {r} at {lab[x]}, frame {f}')
                    lab[x] = (('post', r), f)
                else:
                    if r in hpe or f != FULL or lab[x] != (T, FULL): bad(idx, f'identity exit adapter of {r} at {lab[x]}, frame {f}')
            else:
                bad(idx, 'unknown adapter ' + str(way))
        elif kind == 'residual_adapter':
            _, side, r, f, *U = e; x = ('L', r)
            if r not in wrapped or f != start[r] or U != ([final[r]] if r in hpe else []):
                bad(idx, f'wrapper key of {r}: frame {f}, terminal {U}')
            if side == 'pre':
                pre[r] += 1; st['pre_wrapper'] += 1
                if lab[x] != (('prew', r), start[r]): bad(idx, f'pre wrapper of {r} at {lab[x]}')
                lab[x] = (T, start[r])
            elif side == 'post':
                post[r] += 1; st['post_wrapper'] += 1
                if lab[x] != (T, final[r]): bad(idx, f'post wrapper of {r} at {lab[x]}')
                lab[x] = (('done', r), final[r])
            else:
                bad(idx, 'unknown wrapper side ' + str(side))
        else:
            bad(idx, 'unknown event ' + str(kind))
    phase = 'end'
    if phases != PHASE_ORDER: bad(len(events), 'phase order ' + str(phases))
    for r in range(n):
        want_end = ((T, FULL) if r < v else (('post', r), final[r]) if r < 2 * v
                    else (('done', r), final[r]) if r in wrapped else (T, FULL))
        if lab[('L', r)] != want_end: bad(len(events), f'register {r} ends at {lab[("L", r)]} not {want_end}')
        want_entry = 0 if r in wrapped else 1
        want_exit = 0 if r in hpe else 1
        want_wrap = 1 if r in wrapped else 0
        if (entry[r], exit_[r], pre[r], post[r]) != (want_entry, want_exit, want_wrap, want_wrap):
            bad(len(events), f'bridge of {r}: entry {entry[r]} exit {exit_[r]} pre {pre[r]} post {post[r]}')
    stats = dict(private_first_touch_reads=sum(first == 'read' for first in first_private.values()),events=st['events'], phases=len(phases), scalar_events=sum(by_phase.values()),
                 scalar_by_kind={k[7:]: z for k, z in sorted(st.items()) if k.startswith('scalar_')},
                 scalar_by_phase=dict(sorted(by_phase.items())), climbs=st['climb'], centre_steps=st['centre_step'],
                 entry_adapters=st['entry_adapter'], exit_adapters=st['exit_adapter'], pre_wrappers=st['pre_wrapper'],
                 post_wrappers=st['post_wrapper'], private_registers=len(first_private),
                 source_writes=sum(src.values()), source_writes_by_phase=dict(sorted(src.items())))
    return viol, stats


STRICT_ONLY = 'strict only: '   # prefix of controls that only the strict reading must reject


def control_edits(c, events):
    """Failure controls for label_check: edits of an honest program.  Every edit must be rejected under BOTH readings,
    except those named STRICT_ONLY + ..., which only the strict reading (G0 at every scalar) must reject.
    The first five are the edits of the published checker's mutants(); the next two are HPE-specific; the rest each aim
    at one clause of label_check, so that weakening that clause alone changes a pinned count (see clause_weakenings).
    An edit that relocates an adapter or wrapper keys it, where stated, at the frame its register then sits at."""
    v = c['v']; n = 2 * v + c['R']; start, final = c['start'], c['final']; ev = list(events)
    hpe = sorted(r for r in range(2 * v, n) if final[r] != FULL)
    wrapped = set(hpe) | {r for r in range(2 * v, n) if start[r] != 0}
    first = lambda pred: next(x for x, e in enumerate(ev) if pred(e))
    last_climb = lambda r, hi: max(x for x in range(hi) if ev[x][0] == 'climb' and ev[x][2] == r)
    is_add_on = lambda e, x: e[0] == 'scalar' and e[1][0] == 'add' and x in operands(e[1])
    put = lambda x, new: ev[:x] + [new] + ev[x + 1:]                         # replace event x
    move = lambda x, q, new: ev[:q] + [new] + ev[q:x] + ev[x + 1:]          # event x, as `new`, moved to before q < x
    insert = lambda x, new: ev[:x] + new + ev[x:]
    i = first(lambda e: e[0] == 'adapter' and e[1] == 'old_to_new' and e[2] < v)
    j = first(lambda e: e[0] == 'adapter' and e[1] == 'new_to_old' and v <= e[2] < 2 * v)
    k = max(x for x, e in enumerate(ev[:j]) if is_add_on(e, ('L', ev[j][2])))
    w = first(lambda e: e[0] == 'residual_adapter' and e[1] == 'pre')
    p = first(lambda e: e[0] == 'residual_adapter' and e[1] == 'post')
    kp = max(x for x, e in enumerate(ev[:p]) if is_add_on(e, ('L', ev[p][2])))
    h5 = first(lambda e: e[0] == 'residual_adapter' and len(e) == 5)
    tail = ev.index(['phase', 'cleanup_tail']); full = ev.index(['phase', 'full_frame_cleanup'])
    g = next(x for x in range(tail, full) if ev[x][0] == 'scalar')
    moved = [ev[g][0], ev[g][1], FULL]
    edits = {
        'drop a source entry adapter': ev[:i] + ev[i + 1:],
        'duplicate a source entry adapter': ev[:i + 1] + [ev[i]] + ev[i + 1:],
        'target exit adapter before its last add': ev[:k] + [ev[j]] + ev[k:j] + ev[j + 1:],
        'drop a pre wrapper': ev[:w] + ev[w + 1:],
        "post wrapper before the helper's last add": ev[:kp] + [ev[p]] + ev[kp:p] + ev[p + 1:],
        'hpe wrapper without its terminal field': ev[:h5] + [ev[h5][:4]] + ev[h5 + 1:],
        'hpe tail gate moved into the FULL cleanup': ev[:g] + ev[g + 1:full + 1] + [moved] + ev[full + 1:],
    }
    # (a) a target exit adapter at a frame other than final_t: before the target's last climb, keyed at the frame it sits at
    t = ev[j][2]; qt = last_climb(t, j); need(ev[qt][3] != final[t], 'control (a): the last climb starts at the final frame')
    edits['target exit adapter at a non-final frame'] = move(j, qt, ['adapter', 'new_to_old', t, ev[qt][3]])
    edits['target exit adapter before its last climb'] = move(j, qt, ev[j])
    # (b) identity entry adapters: an unwrapped helper's at a nonzero frame; one added to a (cold) wrapped helper at (T, 0)
    u = first(lambda e: e[0] == 'adapter' and e[1] == 'old_to_new' and e[2] >= 2 * v and e[2] not in wrapped)
    edits['identity entry adapter of an unwrapped helper at a nonzero frame'] = put(u, ['adapter', 'old_to_new', ev[u][2], FULL])
    cold = min(r for r in hpe if start[r] == 0)
    wc = first(lambda e: e[0] == 'residual_adapter' and e[1] == 'pre' and e[2] == cold)
    edits['identity entry adapter added for a wrapped helper'] = insert(wc + 1, [['adapter', 'old_to_new', cold, 0]])
    ut = first(lambda e: e[0] == 'adapter' and e[1] == 'old_to_new' and v <= e[2] < 2 * v)
    qa = first(lambda e: e[0] == 'climb' and e[2] == ev[ut][2])
    edits['target identity entry adapter after its first climb'] = ev[:ut] + ev[ut + 1:qa + 1] + [ev[ut]] + ev[qa + 1:]
    # (c) identity exit adapters: one added for an HPE helper (first climbed to FULL, so only the HPE condition fires);
    #     a source's keyed at a non-FULL frame (in place, so the source itself sits at FULL)
    hh = hpe[0]; xa = ev.index(['phase', 'exit_adapters'])
    up = ['climb', 'exit_adapters', hh, final[hh], FULL, c['h'] - len(c['frames'][final[hh]])]
    edits['identity exit adapter added for an HPE helper'] = insert(xa + 1, [up, ['adapter', 'new_to_old', hh, FULL]])
    sx = first(lambda e: e[0] == 'adapter' and e[1] == 'new_to_old' and e[2] < v)
    edits['identity exit adapter keyed at a non-FULL frame'] = put(sx, ['adapter', 'new_to_old', ev[sx][2], 0])
    # (d) a post wrapper moved before the helper's final climb
    edits["post wrapper before the helper's final climb"] = move(p, last_climb(ev[p][2], p), ev[p])
    # (e) a source entry adapter keyed at a frame other than start_i
    edits['source entry adapter keyed at a frame other than its start'] = put(i, ['adapter', 'old_to_new', ev[i][2], FULL])
    # (f) a centre step whose source frame is wrong
    ce = first(lambda e: e[0] == 'center')
    edits['centre step from a wrong source frame'] = put(ce, ['center', ev[ce][1], FULL if ev[ce][2] != FULL else 0] + ev[ce][3:])
    # (g) a phase marker dropped; two phase markers swapped
    pc = ev.index(['phase', 'centers']); pb = ev.index(['phase', 'B'])
    edits['phase marker dropped'] = ev[:pc] + ev[pc + 1:]
    swapped = list(ev); swapped[pb], swapped[tail] = ev[tail], ev[pb]
    edits['phase markers swapped'] = swapped
    # (h) unknown kinds, one per dispatch (wrapper keyed correctly, so only the side is unknown)
    pa = ev.index(['phase', 'A'])
    edits['unknown event kind'] = insert(pa + 1, [['barrier']])
    edits['unknown scalar kind'] = insert(pa + 1, [['scalar', ['negate', ['L', v]], 0]])
    edits['unknown adapter direction'] = insert(pa + 1, [['adapter', 'sideways', v, 0]])
    edits['unknown wrapper side'] = insert(w + 1, [['residual_adapter', 'mid'] + ev[w][2:]])
    # wrapper keys and counts
    ew = first(lambda e: e[0] == 'residual_adapter' and e[1] == 'pre' and start[e[2]] != 0)
    edits['entering wrapper keyed at frame 0'] = put(ew, ev[ew][:3] + [0] + ev[ew][4:])
    edits['wrapper added for an unwrapped helper'] = insert(w, [['residual_adapter', 'pre', ev[u][2], 0]])
    edits['duplicate a pre wrapper'] = insert(w + 1, [ev[w]])
    edits['drop a post wrapper'] = ev[:p] + ev[p + 1:]
    # (i) forward only: the centre copy C_k <- L_r taken from a register that sits at another frame
    cp = next((x for x, e in enumerate(ev) if e[0] == 'scalar' and e[1][0] == 'copy'), None)
    if cp is not None:
        cur = list(start)
        for e in ev[:cp]:
            if e[0] == 'climb': cur[e[2]] = e[4]
        cf = ev[cp][2]; other = min(r for r in range(n) if cur[r] != cf)
        edits['centre copy from a register at a wrong frame'] = put(cp, ['scalar', ['copy', ev[cp][1][1], ['L', other]], cf])
    # strict reading only: G0 at a scale (Lean's Admissible asks nothing of scale)
    sc = first(lambda e: e[0] == 'scalar' and e[1][0] == 'scale')
    edits[STRICT_ONLY + 'scale annotated at a wrong frame'] = put(sc, ['scalar', ev[sc][1], FULL if ev[sc][2] != FULL else 0])
    return edits


def own_controls(c, edits):
    """Run label_check on every control edit; return {name: [strict violations, permissive violations]}."""
    out = {}
    for name, mut in edits.items():
        strict, _ = label_check(c, mut, 'strict'); perm, _ = label_check(c, mut, 'permissive')
        if name.startswith(STRICT_ONLY):
            need(strict and not perm, 'strict-only control not separated by the two readings: ' + name)
        else:
            need(strict and perm, 'label checker accepted control: ' + name)
        out[name] = [len(strict), len(perm)]
    return out


# Single-clause weakenings of label_check: (clause, exact text in label_check, the same text with that one clause off).
_SRC_ENTRY = "if f != start[r] or lab[x] != (('pre', r), f)"
_ID_ENTRY = 'if r in wrapped or f != 0 or lab[x] != (T, 0)'
_TGT_EXIT = 'if f != final[r] or lab[x] != (T, f)'
_ID_EXIT = 'if r in hpe or f != FULL or lab[x] != (T, FULL)'
_WRAP_KEY = 'if r not in wrapped or f != start[r] or U != ([final[r]] if r in hpe else [])'
_BRIDGE = ('(entry[r], exit_[r], pre[r], post[r])', '(want_entry, want_exit, want_wrap, want_wrap)')
WEAKENINGS = [
    ('copy source at (T, f) (strict)', "if lab.get(s) != want: bad(idx, f'copy", "if False: bad(idx, f'copy"),
    ('add target at (T, f) (strict)', 'for x in (t, s) if lab.get(x) != want]', 'for x in (s,) if lab.get(x) != want]'),
    ('add source at (T, f) (strict)', 'for x in (t, s) if lab.get(x) != want]', 'for x in (t,) if lab.get(x) != want]'),
    ('add operands equal (permissive)', 'if lab.get(t) != lab.get(s): bad(', 'if False: bad('),
    ('scale operand at (T, f) (strict)', "if lab.get(x) != want: bad(idx, f'scale", "if False: bad(idx, f'scale"),
    ('unknown scalar kind', "bad(idx, 'unknown scalar ' + str(op[0]))", 'pass'),
    ('climb source label', 'if lab[x] != (T, a): bad(', 'if False: bad('),
    ('centre-step source label', 'if lab.get(x) != (T, a): bad(', 'if False: bad('),
    ('source entry: frame is start', _SRC_ENTRY, _SRC_ENTRY.replace('f != start[r]', 'False')),
    ('source entry: label is (pre, f)', _SRC_ENTRY, _SRC_ENTRY.replace("lab[x] != (('pre', r), f)", 'False')),
    ('identity entry: register not wrapped', _ID_ENTRY, _ID_ENTRY.replace('r in wrapped', 'False')),
    ('identity entry: frame 0', _ID_ENTRY, _ID_ENTRY.replace('f != 0', 'False')),
    ('identity entry: label (T, 0)', _ID_ENTRY, _ID_ENTRY.replace('lab[x] != (T, 0)', 'False')),
    ('target exit: frame is final', _TGT_EXIT, _TGT_EXIT.replace('f != final[r]', 'False')),
    ('target exit: label (T, f)', _TGT_EXIT, _TGT_EXIT.replace('lab[x] != (T, f)', 'False')),
    ('identity exit: register not HPE', _ID_EXIT, _ID_EXIT.replace('r in hpe', 'False')),
    ('identity exit: frame FULL', _ID_EXIT, _ID_EXIT.replace('f != FULL', 'False')),
    ('identity exit: label (T, FULL)', _ID_EXIT, _ID_EXIT.replace('lab[x] != (T, FULL)', 'False')),
    ('unknown adapter direction', "bad(idx, 'unknown adapter ' + str(way))", 'pass'),
    ('wrapper key: register wrapped', _WRAP_KEY, _WRAP_KEY.replace('r not in wrapped', 'False')),
    ('wrapper key: start frame', _WRAP_KEY, _WRAP_KEY.replace('f != start[r]', 'False')),
    ('wrapper key: terminal field', _WRAP_KEY, _WRAP_KEY.replace('U != ([final[r]] if r in hpe else [])', 'False')),
    ('pre wrapper label', "if lab[x] != (('prew', r), start[r]): bad(", 'if False: bad('),
    ('post wrapper label', 'if lab[x] != (T, final[r]): bad(', 'if False: bad('),
    ('unknown wrapper side', "bad(idx, 'unknown wrapper side ' + str(side))", 'pass'),
    ('unknown event kind', "bad(idx, 'unknown event ' + str(kind))", 'pass'),
    ('phase order', 'if phases != PHASE_ORDER: bad(', 'if False: bad('),
    ('end labels', "if lab[('L', r)] != want_end: bad(", 'if False: bad('),
] + [('bridge: %s count' % what, '%s != %s' % _BRIDGE,
      '(%s) != (%s)' % tuple(', '.join(x for z, x in enumerate(side[1:-1].split(', ')) if z != drop) for side in _BRIDGE))
     for drop, what in enumerate(('entry adapter', 'exit adapter', 'pre wrapper', 'post wrapper'))]


def clause_weakenings(c, inputs):
    """Weaken one clause of label_check at a time, in memory, and re-run it on every pinned input (`inputs`: name ->
    (events, detail), detail meaning that the violation indices and first violation are pinned, not only the counts).
    A weakening is caught iff some pinned value changes.  Returns the clause count and the surviving clauses."""
    text = Path(__file__).read_text(encoding='utf-8')
    a = text.index('\ndef label_check(') + 1
    src = text[a:text.index('\n\n\ndef ', a)]

    def pinned_values(check):
        for name, (events, detail) in inputs.items():
            for reading in ('strict', 'permissive'):
                viol, _ = check(c, events, reading)
                yield (name, reading), (([x[0] for x in viol], viol[0] if viol else None) if detail else len(viol))
    base = dict(pinned_values(label_check))
    surviving = []
    for clause, old, new in WEAKENINGS:
        need(src.count(old) == 1 and old != new, 'weakening anchor is not one exact clause: ' + clause)
        ns = dict(globals())
        exec(compile(src.replace(old, new), 'label_check weakened: ' + clause, 'exec'), ns)
        if all(base[key] == value for key, value in pinned_values(ns['label_check'])):   # stops at the first change
            surviving.append(clause)
    return dict(clauses=len(WEAKENINGS), inputs=len(inputs), caught=len(WEAKENINGS) - len(surviving), surviving=surviving)


def shadow(c, events, back, capture=()):
    """Independent exact scalar shadow (H3): rows over the input columns, relabels deleted.  Private registers start as
    their own columns, so a zero private column proves dirty private inputs never reach the output."""
    v, n = c['v'], 2 * c['v'] + c['R']
    rows = {('L', r): {('L', r): Q(1)} for r in range(n)}
    snaps = {}
    for idx, e in enumerate(events):
        if idx in capture:
            snaps[idx] = {k: rows.get(k, {}).copy() for k in capture[idx]}
        if e[0] != 'scalar':
            continue
        op = e[1]; t = tuple(op[1])
        if t not in rows: rows[t] = {t: Q(1)}
        if op[0] == 'clear':
            rows[t] = {}
        elif op[0] == 'copy':
            s = tuple(op[2]); rows.setdefault(s, {s: Q(1)}); rows[t] = dict(rows[s])
        elif op[0] == 'scale':
            q = Q(op[2], op[3]); need(q != 0, 'zero scale'); rows[t] = {j: q * x for j, x in rows[t].items()}
        else:
            s = tuple(op[2]); rows.setdefault(s, {s: Q(1)}); q = Q(op[3], op[4]); need(s != t, 'self add')
            row = rows[t]
            for j, x in list(rows[s].items()):
                z = row.get(j, Q(0)) + q * x
                if z: row[j] = z
                else: row.pop(j, None)
    for r in range(n):
        expected = {('L', r): Q(1)}
        if back and r < v: expected[('L', v + r)] = Q(-1)
        if not back and v <= r < 2 * v: expected[('L', r - v)] = Q(1)
        need(rows[('L', r)] == expected, f'scalar shadow row {r} is not the data shear')
    privates = [k for k in rows if k[0] == 'C']
    need(all(not rows[k] for k in privates), 'a private register is not cleared at the end')
    return len(privates), snaps


def structural(c, events):
    """Facts used by the all-words lemma, read off one emitted stream."""
    v, n = c['v'], 2 * c['v'] + c['R']; start, final = c['start'], c['final']
    hpe = {r for r in range(2 * v, n) if final[r] != FULL}
    wrapped = hpe | {r for r in range(2 * v, n) if start[r] != 0}
    phase = None; pre_regs, cleanup_regs = set(), set()
    for e in events:
        if e[0] == 'phase':
            phase = e[1]
        elif e[0] == 'scalar':
            need(phase not in ('entry_adapters', 'exit_adapters', 'done'), 'scalar event in an adapter phase')
            regs = {x[1] for x in operands(e[1]) if x[0] == 'L'}
            if phase == 'zero_frame_precondition':
                need(e[2] == 0, 'precondition scalar off frame 0'); pre_regs |= regs
            if phase == 'full_frame_cleanup':
                need(e[2] == FULL, 'cleanup scalar off FULL'); cleanup_regs |= regs
    need(all(start[r] == 0 and r not in wrapped and r >= v for r in pre_regs), 'precondition touches a nonzero-start or wrapped register')
    need(all(final[r] == FULL and not v <= r < 2 * v for r in cleanup_regs), 'cleanup touches a non-FULL-final register or a target')
    return dict(precondition_registers=len(pre_regs), precondition_targets=sum(v <= r < 2 * v for r in pre_regs),
                cleanup_registers=len(cleanup_regs), cleanup_sources=sum(r < v for r in cleanup_regs))


def frame_facts(c, routing):
    v, h, frames = c['v'], c['h'], c['frames']
    parity = lambda x: x.bit_count() & 1
    ports = routing['ports']
    need(len(ports) == v == len(set(ports)) and all(0 < p < 1 << h for p in ports), 'routing ports must be 112 distinct nonzero 9-bit values')
    need(c['ports'] == ports and frames[0] == [] and len(frames[FULL]) == h, 'frame table rows / port order')
    for i, p in enumerate(ports):
        need(frames[c['start'][i]] == [p], 'source start is not span{p}')
        U = frames[c['final'][v + i]]
        need(len(U) == h - 1 and all(parity(u & p) == 0 for u in U), 'target final is not the hyperplane p-perp')
    n = 2 * v + c['R']
    hpe = [r for r in range(2 * v, n) if c['final'][r] != FULL]
    entering = [r for r in range(2 * v, n) if c['start'][r] != 0]
    # Lemma S (ii): the only frame condition the emitter does not enforce itself is that every cut gate writes a target
    need(all(e[0] == 'add' and v <= e[1] < 2 * v and e[2] in c['centers'] for e in c['cut']),
         'a cut gate does not write a target from a centre')
    return dict(v=v, R=c['R'], h=h, frames=len(frames), centres=len(c['centers']),
                cut_gates=len(c['cut']), cut_gates_write_targets_from_centres=True,
                centres_that_are_sources=sum(r < v for r in c['centers']),
                entering_helpers=len(entering), hyperplane_ended_helpers=len(hpe),
                cold_hyperplane_ended_helpers=sum(c['start'][r] == 0 for r in hpe),
                wrapped_helpers=len(set(hpe) | set(entering)), routing_ports_nonzero_distinct=True,
                source_starts_are_port_lines=True, target_finals_are_port_hyperplanes=True)


# ------------------------------------------------------------------------------------------------ stage 4: mutants
def straddle(events, adapter_event, frame, reg):
    """[C0 += L; L -= C0] adapter [L += C0; C0 -= L; clear C0], all at the adapter's frame."""
    i = events.index(adapter_event)
    need(events.count(adapter_event) == 1, 'adapter event not unique')
    C0, L = ['C', 0], ['L', reg]
    before = [['scalar', ['add', C0, L, 1, 1], frame], ['scalar', ['add', L, C0, -1, 1], frame]]
    after = [['scalar', ['add', L, C0, 1, 1], frame], ['scalar', ['add', C0, L, -1, 1], frame], ['scalar', ['clear', C0], frame]]
    return events[:i] + before + [events[i]] + after + events[i + 1:], i


def _axpy(dst, src, q):
    """dst + q * src on formal linear combinations {word: coefficient}."""
    out = dict(dst)
    for w, z in src.items():
        out[w] = out.get(w, Q(0)) + q * z
        if not out[w]: del out[w]
    return out


def _fmt(vec):
    return sorted([' '.join(w), str(z)] for w, z in vec.items())


def segment_algebra(adapter_name):
    """Physical semantics of the honest adapter and of the straddle segment on (L, C0) = (a, c), with the adapter an
    abstract linear operator X (formal words).  Returns the final contents as sorted term lists."""
    def apply_X(vec):
        return {(adapter_name,) + w: z for w, z in vec.items()}
    a, c = {('a',): Q(1)}, {('c',): Q(1)}
    honest = {'L': apply_X(a), 'C0': c}
    L, C = a, c
    C = _axpy(C, L, Q(1)); L = _axpy(L, C, Q(-1)); L = apply_X(L); L = _axpy(L, C, Q(1)); C = _axpy(C, L, Q(-1))
    need(C == apply_X(c), 'segment algebra: C0 before its final clear')
    C = {}
    return dict(honest_L=_fmt(honest['L']), mutant_L=_fmt(L), mutant_C0_after_clear=_fmt(C))


def swap_algebra(adapter_name, q):
    """Honest [L += q S; X on L] against mutant Z's [X on L; L += q S], on (L, S) = (a, b), X an abstract operator that
    touches only L.  Returns both final contents of L and honest - mutant as sorted term lists."""
    X = lambda vec: {(adapter_name,) + w: z for w, z in vec.items()}
    a, b = {('a',): Q(1)}, {('b',): Q(1)}
    honest = X(_axpy(a, b, q)); mutant = _axpy(X(a), b, q)
    return dict(honest_L=_fmt(honest), mutant_L=_fmt(mutant), honest_minus_mutant=_fmt(_axpy(honest, mutant, Q(-1))))


def adapter_rule(c, events):
    """The hardening README (b) recommends next to the frame-only replay (a sketch, not proved sufficient for H1): every
    data adapter and wrapper sits in its own phase at cur[r] == its frame, and per-register adapter state is tracked as
    the replay tracks wrappers: no scalar or climb touches a source before its entry adapter or a target after its exit
    adapter.  Returns the indices of offending events."""
    v = c['v']; cur = list(c['start']); phase = None; entered, exited = set(), set(); bad = []
    for idx, e in enumerate(events):
        kind = e[0]; regs = []
        if kind == 'phase':
            phase = e[1]; continue
        if kind == 'scalar':
            regs = [x[1] for x in operands(e[1]) if x[0] == 'L']
        elif kind == 'climb':
            regs = [e[2]]
        elif kind == 'adapter':
            _, way, r, f = e
            if phase != ('entry_adapters' if way == 'old_to_new' else 'exit_adapters') or cur[r] != f:
                bad.append(idx)
            (entered if way == 'old_to_new' else exited).add(r)
        elif kind == 'residual_adapter':
            _, side, r, f, *U = e
            if (phase, cur[r]) != (('entry_adapters', c['start'][r]) if side == 'pre' else ('full_frame_cleanup', c['final'][r])):
                bad.append(idx)
        if any((r < v and r not in entered) or (v <= r < 2 * v and r in exited) for r in regs):
            bad.append(idx)
        if kind == 'climb':
            cur[e[2]] = e[4]
    return bad


def exit_block_move(c, events):
    """Mutant Z: the exit adapters of registers 0 .. t (t = v, the target of port 0), in order, moved to just before the
    last scalar event on L_t ahead of its exit adapter.  Returns (mutant, insertion index, first and last moved index)."""
    t = c['v']
    xs = [x for x, e in enumerate(events) if e[0] == 'adapter' and e[1] == 'new_to_old' and e[2] <= t]
    need([events[x][2] for x in xs] == list(range(t + 1)) and xs == list(range(xs[0], xs[-1] + 1)),
         'the exit adapters of registers 0..t are not one ordered block')
    g = max(x for x in range(xs[0]) if events[x][0] == 'scalar' and ('L', t) in operands(events[x][1]))
    return events[:g] + events[xs[0]:xs[-1] + 1] + events[g:xs[0]] + events[xs[-1] + 1:], g, xs[0], xs[-1]


def touches(e, reg):
    if e[0] == 'scalar':
        return reg in operands(e[1])
    if e[0] in ('climb', 'adapter', 'residual_adapter'):
        return reg == ('L', e[2])
    if e[0] == 'center':
        return reg == ('C', e[1])
    return False


def stage4(c, progs, py, code, tmp, local):
    v = c['v']; fw = progs['forward']
    t, s = v + 0, 0
    exit_ev = ['adapter', 'new_to_old', t, c['final'][t]]
    entry_ev = ['adapter', 'old_to_new', s, c['start'][s]]
    mut_exit, ie = straddle(fw, exit_ev, c['final'][t], t)
    mut_entry, ia = straddle(fw, entry_ev, c['start'][s], s)
    # preconditions of the physical argument (PROOF.md section 4)
    need(not any(touches(e, ('L', t)) for e in fw[ie + 1:]), 'an event after the exit adapter touches the target')
    last_c0 = max(i for i in range(ie) if touches(fw[i], ('C', 0)))
    need(fw[last_c0] == ['scalar', ['clear', ['C', 0]], fw[last_c0][2]], 'C0 is not cleared before the exit straddle')
    need(not any(touches(e, ('L', s)) for e in fw[:ia]), 'an event before the entry adapter touches the source')
    need(not any(touches(e, ('C', 0)) for e in fw[:ia]), 'C0 is touched before the entry straddle')
    first_c0 = min(i for i in range(ia + 1, len(fw)) if touches(fw[i], ('C', 0)))
    need(fw[first_c0][0] == 'scalar' and fw[first_c0][1][0] == 'clear', 'C0 is not cleared at its first later touch')
    # mutant Z: the exit adapters of registers 0..t moved, in order, to before the last scalar on L_t (phase B)
    mut_block, g, x0, x1 = exit_block_move(c, fw)
    gate = fw[g]
    phase_of = lambda idx: [e[1] for e in fw[:idx + 1] if e[0] == 'phase'][-1]
    need(gate[0] == 'scalar' and gate[1][0] == 'add' and tuple(gate[1][1]) == ('L', t) and gate[1][2][0] == 'L'
         and gate[1][2][1] < v and gate[2] == c['final'][t] and phase_of(g) == 'B',
         'Z: the insertion point is not a phase-B add L_t += q L_s (s a source) at final_t')
    q_gate = Q(gate[1][3], gate[1][4]); src = tuple(gate[1][2])
    need(x1 == ie and not any(touches(e, ('L', t)) for e in fw[g + 1:x1]), 'Z: an event between the add and the exit adapter touches L_t')
    need(all(fw[x][3] == FULL == c['final'][fw[x][2]] for x in range(x0, x1)), 'Z: a moved source exit adapter is not an identity at FULL')
    _, snaps = shadow(c, fw, False, capture={ie: [('L', t)], ia: [('L', s)], g: [('L', t), src]})
    need(snaps[ie][('L', t)] == {('L', t): Q(1), ('L', s): Q(1)}, 'target row before its exit adapter is not e_t + e_s')
    need(snaps[ia][('L', s)] == {('L', s): Q(1)}, 'source row before its entry adapter is not e_s')
    col_src, col_tgt = snaps[g][src].get(src, Q(0)), snaps[g][('L', t)].get(src, Q(0))
    need(col_src == 1 and col_tgt + q_gate * col_src == 0, 'Z: the witness column is not (1 on L_s, -q on L_t)')
    res, programs = {}, {}
    for name, mut, inserted in (('exit_straddle_target112_frame%d' % c['final'][t], mut_exit, 5),
                                ('entry_straddle_source0_frame%d' % c['start'][s], mut_entry, 5),
                                ('exit_block_registers0to%d_before_event%d' % (t, g), mut_block, 0)):
        d = tmp / name; d.mkdir()
        shutil.copy(local / 'CANONICAL-WORD.json.gz', d / 'CANONICAL-WORD.json.gz')
        payload = json.dumps({'forward': mut, 'backward': progs['backward']}, sort_keys=True, separators=(',', ':')).encode()
        (d / 'LOCAL-PROGRAMS.json.gz').write_bytes(gzip.compress(payload, mtime=0))
        replay = audit_local(py, code, d, tmp)
        n_priv, _ = shadow(c, mut, False)
        strict, _ = label_check(c, mut, 'strict')
        perm, _ = label_check(c, mut, 'permissive')
        need(len(mut) - len(fw) == inserted, name + ': unexpected event count')
        res[name] = dict(events=len(mut), inserted_scalar_events=len(mut) - len(fw),
                         forward_program_sha256=digest(mut), frame_only_replay=replay,
                         scalar_shadow_equals_honest=True,
                         label_violations_strict=len(strict), label_violations_permissive=len(perm),
                         violation_event_indices_strict=[x[0] for x in strict],
                         violation_event_indices_permissive=[x[0] for x in perm],
                         first_violation_strict=strict[0] if strict else None,
                         first_violation_permissive=perm[0] if perm else None,
                         recommended_adapter_rule_violations=len(adapter_rule(c, mut)))
        need(replay['accepted'], name + ': the pinned frame-only replay was expected to accept')
        need(perm and strict, name + ': a label checker accepted the mutant')
        need(adapter_rule(c, mut), name + ': the recommended adapter rule accepted the mutant')
        programs[name] = mut
    argument = dict(exit_adapter_event_index=ie, entry_adapter_event_index=ia,
                    C0_last_event_before_exit_straddle=last_c0, C0_first_event_after_entry_straddle=first_c0,
                    target_row_before_exit_adapter='e112 + e0', source_row_before_entry_adapter='e0',
                    exit_segment=segment_algebra('A_t'), entry_segment=segment_algebra('M_0'),
                    exit_block=dict(moved_event_indices=[x0, x1], moved_exit_adapters=x1 - x0 + 1,
                                    moved_identity_exit_adapters_at_FULL=x1 - x0, insertion_event_index=g,
                                    insertion_event=gate, insertion_phase=phase_of(g), source_register=src[1],
                                    source_start_frame=c['start'][src[1]], target_untouched_until_its_exit_adapter=True,
                                    witness_column_coefficients_before_insertion={'L_s': str(col_src), 'L_t': str(col_tgt)},
                                    swap_segment=swap_algebra('A_t', q_gate)))
    return res, argument, programs


# ------------------------------------------------------------------------------------------------ stage 5: adapters
def mono_eval(rec, h):
    """Image of each basis vector e_y under a serialized rank-0 record: D(Q, alpha), then P(G), then X(b), then i^phase
    (the gate order of clifford_exact.monomial).  Returns [(z, p)] meaning e_y -> i^p e_z."""
    parity = lambda x: x.bit_count() & 1
    G, Qr, alpha, b, ph = rec['matrix_rows'], rec['quadratic_rows'], rec['linear_Z4'], rec['offset'], rec['phase']
    out = []
    for y in range(1 << h):
        q = (sum(alpha[i] for i in range(h) if y >> i & 1)
             + 2 * sum(parity((Qr[i] >> (i + 1)) & (y >> (i + 1))) for i in range(h) if y >> i & 1)) % 4
        z = sum(parity(row & y) << i for i, row in enumerate(G)) ^ b
        out.append((z, (q + ph) % 4))
    need(sorted(z for z, _ in out) == list(range(1 << h)), 'record is not a monomial (G not invertible)')
    return out


def clifford_oracle(rec, h):
    """The same record evaluated with the pinned clifford_exact circuit semantics (zero_state on every basis vector)."""
    ns = {'__name__': 'clifford_exact_pinned'}
    exec(compile(pinned(CLIFFORD), CLIFFORD, 'exec'), ns)
    op = ns['diag'](h, tuple(rec['quadratic_rows']), tuple(rec['linear_Z4'])).then(ns['perm'](h, tuple(rec['matrix_rows'])))
    op = op.then(ns['xgate'](h, rec['offset'])).then(ns['Op'](h, ns['identity'](h), [('phase', rec['phase'])]))
    out = []
    for y in range(1 << h):
        vec, den = op.zero_state(y)
        nz = [(z, a) for z, a in enumerate(vec) if a != (0, 0)]
        need(den == 0 and len(nz) == 1, 'oracle: not a monomial column')
        z, a = nz[0]
        out.append((z, [(1, 0), (0, 1), (-1, 0), (0, -1)].index(a)))
    return out


def stage5(c, local, pins, phases, log):
    code = phases.wait(timeout=420)
    log.close()
    need(code == 0, 'phases_full failed: ' + (local.parent / 'phases_full.log').read_text()[-2000:])
    raw = (local / 'CLIFFORD-RECIPES.json').read_bytes()
    need(sha(raw) == pins['recipes'], 'regenerated CLIFFORD-RECIPES != selected pin')
    review = json.loads((local / 'CLIFFORD-REVIEW.json').read_text())
    need(review['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES', 'phases_full review status')
    rec = json.loads(raw); v, h = c['v'], c['h']
    ad = {(a['role'], a['port']): a for a in rec['endpoint_adapters']}
    need(len(ad) == len(rec['endpoint_adapters']) == 2 * v, 'adapter inventory')
    fixed = {'source': [], 'target': []}
    for (role, i), a in sorted(ad.items()):
        need(a['frame'] == (c['start'][i] if role == 'source' else c['final'][v + i]), 'adapter frame')
        need(a['rank'] == 0 and a['right'] is None, 'adapter is not a rank-0 monomial record')
        img = mono_eval(a['left'], h)
        fixed[role].append(sum(img[y] == (y, 0) for y in range(1 << h)))
    need(all(f < (1 << h) for fs in fixed.values() for f in fs), 'an endpoint adapter is the identity')
    src0, tgt0 = ad['source', 0]['left'], ad['target', 0]['left']
    m0, n0 = mono_eval(src0, h), mono_eval(tgt0, h)
    need(clifford_oracle(src0, h) == m0 and clifford_oracle(tgt0, h) == n0, 'evaluator disagrees with clifford_exact')
    n0_inv = {z: (y, (-p) % 4) for y, (z, p) in enumerate(n0)}
    return dict(recipes_sha256=sha(raw), child_records=len(rec['children']), ranks=dict(sorted(review['ranks'].items())),
                endpoint_adapters=len(ad), non_identity_monomials=sum(f < (1 << h) for fs in fixed.values() for f in fs),
                fixed_basis_vectors_min_max={r: [min(fs), max(fs)] for r, fs in fixed.items()},
                port0_source_frame=ad['source', 0]['frame'], port0_target_frame=ad['target', 0]['frame'],
                port0_target_register=v + 0,
                M0_e1=list(m0[1]), N_t_e0=list(n0[0]), executed_exit_N_t_inverse_e0=list(n0_inv[0]),
                N_t_fixed_basis_vectors=sum(n0[y] == (y, 0) for y in range(1 << h)),
                oracle_cross_check_columns=2 * (1 << h))


# ------------------------------------------------------------------------------------------------ stage 6: Lemma G checker
def load_checker(source, filename):
    """Exec a Lemma G checker module from bytes.  Its top-level `from lg_lib import load` (#484's loader, used only by its
    main()) is served by a stub; check() and mutants() are called directly."""
    saved_path, saved_mod = list(sys.path), sys.modules.get('lg_lib')
    stub = types.ModuleType('lg_lib'); stub.load = None
    sys.modules['lg_lib'] = stub
    try:
        ns = {'__name__': 'lemma_g_checker', '__file__': filename}
        exec(compile(source, filename, 'exec'), ns)
    finally:
        sys.path[:] = saved_path
        if saved_mod is None: sys.modules.pop('lg_lib', None)
        else: sys.modules['lg_lib'] = saved_mod
    return ns


def stage6(c, progs, mutant_programs):
    original = pinned(LG_CHECK).decode('utf-8')
    published = load_checker(original, str(ROOT / LG_CHECK))
    uncapped = load_checker(original.replace(CAP_LINE, 'bad = lambda m: viol.append(m)'), str(ROOT / LG_CHECK))
    patched = load_checker(PATCHED.read_text(encoding='utf-8'), str(PATCHED))
    strip = lambda ev: [e[:4] if e[0] == 'residual_adapter' else e for e in ev]
    out = {'as_published': {}, 'fifth_field_stripped': {}, 'patched_copy': {}}
    for o in ('forward', 'backward'):
        ev = progs[o]
        first5 = next(i for i, e in enumerate(ev) if e[0] == 'residual_adapter' and len(e) == 5)
        try:
            published['check'](c, ev)
        except ValueError as exc:
            msg = str(exc)
            print(f'published checker, {o}, as published: ValueError: {msg}', flush=True)
            need(msg.startswith('too many values to unpack (expected 4'), 'unexpected published-checker failure: ' + msg)
            out['as_published'][o] = dict(exception='ValueError', message_prefix='too many values to unpack (expected 4',
                                          first_five_field_event_index=first5, first_five_field_event=ev[first5])
        else:
            raise ValueError('the published checker was expected to fail on the 5-field HPE wrapper events')
        capped, counts = published['check'](c, strip(ev))
        full, _ = uncapped['check'](c, strip(ev))
        kinds = Counter('pre wrapper tag' if x.startswith('pre wrapper') else
                        'register end tag' if x.startswith('register') else x.split(':')[0] for x in full)
        cold = sorted({int(x.split(' ')[3].rstrip(':')) if x.startswith('pre wrapper') else int(x.split(' ')[1])
                       for x in full})
        hpe_cold = sorted(r for r in range(2 * c['v'], 2 * c['v'] + c['R']) if c['final'][r] != FULL and c['start'][r] == 0)
        need(cold == hpe_cold, 'stripped-run violations are not exactly the cold HPE helpers')
        out['fifth_field_stripped'][o] = dict(violations_as_published_capped=len(capped), violations_uncapped=len(full),
                                              by_kind=dict(sorted(kinds.items())), registers_are_the_cold_hpe_helpers=True,
                                              counts=counts)
        viol, counts = patched['check'](c, ev)
        need(not viol, 'patched copy: violations on the selected program ' + str(viol[:3]))
        m = patched['mutants'](c, ev)
        need(all(x > 0 for x in m.values()), 'patched copy accepted one of its own mutants')
        out['patched_copy'][o] = dict(violations=len(viol), counts=counts, own_mutants_violations=m)
    patched_text = PATCHED.read_text(encoding='utf-8')
    need(patched_text.count(CAP_LINE) == 1, 'cap line of the patched copy not found exactly once')
    patched_uncapped = load_checker(patched_text.replace(CAP_LINE, 'bad = lambda m: viol.append(m)'), str(PATCHED))
    out['patched_copy']['admission_gap_mutants_capped_uncapped'] = {
        name: [len(patched['check'](c, mut)[0]), len(patched_uncapped['check'](c, mut)[0])] for name, mut in mutant_programs.items()}
    need(all(x[0] for x in out['patched_copy']['admission_gap_mutants_capped_uncapped'].values()),
         'patched copy accepted an admission-gap mutant')
    return out


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--keep', type=Path, help='copy the temporary working directory here (inspection only)')
    args = ap.parse_args()
    began = time.monotonic()
    expected = json.loads((PKG / 'EXPECTED.json').read_text(encoding='utf-8'))
    result = {'stage0_bindings': stage0()}
    pins = stage1(); result['stage1_selected_pins'] = pins
    tmp = Path(tempfile.mkdtemp(prefix='seed65-'))
    phases = log = None
    try:
        c, progs, phases, log, regen = stage2_start(tmp, pins)
        result['stage2_regeneration'] = regen
        routing = json.loads(gzip.decompress(pinned(ROUTING)))
        result['stage3_word_facts'] = frame_facts(c, routing)
        labels = {}
        for o in ('forward', 'backward'):
            strict, stats = label_check(c, progs[o], 'strict')
            perm, _ = label_check(c, progs[o], 'permissive')
            need(not strict and not perm, f'{o}: extended-label violations {strict[:3]} {perm[:3]}')
            need(stats['private_first_touch_reads'] == 0, f'{o}: a private register is read before it is cleared')
            n_priv, _ = shadow(c, progs[o], o == 'backward')
            rule = adapter_rule(c, progs[o])
            need(not rule, f'{o}: the recommended adapter rule rejects the selected program at {rule[:3]}')
            labels[o] = dict(violations_strict=len(strict), violations_permissive=len(perm), **stats,
                             scalar_shadow_is_data_shear=True, private_registers_cleared=n_priv,
                             recommended_adapter_rule_violations=len(rule), **structural(c, progs[o]))
        result['stage3_extended_labels'] = labels
        edits = {o: control_edits(c, progs[o]) for o in ('forward', 'backward')}
        result['stage3_checker_controls_strict_permissive'] = {o: own_controls(c, edits[o]) for o in ('forward', 'backward')}
        mutants, argument, mprogs = stage4(c, progs, [sys.executable, '-I', '-B'], tmp / 'code', tmp, tmp / 'local')
        result['stage4_admission_mutants'] = mutants
        result['stage4_physical_argument'] = argument
        # every pinned label_check input: the honest programs and controls (counts), the mutants (indices pinned too)
        inputs = {o: (progs[o], False) for o in ('forward', 'backward')}
        inputs.update({(o, name): (mut, False) for o in ('forward', 'backward') for name, mut in edits[o].items()})
        inputs.update({name: (mut, True) for name, mut in mprogs.items()})
        result['stage4_label_check_clause_weakenings'] = clause_weakenings(c, inputs)
        result['stage5_endpoint_adapters'] = stage5(c, tmp / 'local', pins, phases, log)
        result['stage6_published_lemma_g_checker'] = stage6(c, progs, mprogs)
        if args.keep:
            shutil.copytree(tmp, args.keep)
    finally:
        if phases is not None and phases.poll() is None:
            phases.kill(); phases.wait()
        if log is not None and not log.closed:
            log.close()
        shutil.rmtree(tmp, ignore_errors=True)
    result = json.loads(json.dumps(result))
    if result != expected['result']:
        sys.stderr.write(json.dumps(result, indent=1, sort_keys=True) + '\n')
        diffs = [k for k in sorted(set(result) | set(expected['result'])) if result.get(k) != expected['result'].get(k)]
        raise ValueError('result differs from EXPECTED.json in: ' + ', '.join(diffs))
    a = result['stage3_extended_labels']; m = result['stage4_admission_mutants']
    w = result['stage4_label_check_clause_weakenings']
    print(json.dumps({'forward': {k: a['forward'][k] for k in ('events', 'violations_strict', 'violations_permissive', 'source_writes')},
                      'backward': {k: a['backward'][k] for k in ('events', 'violations_strict', 'violations_permissive', 'source_writes')},
                      'admission_mutants_replay_accepts_permissive_strict': {
                          k: [x['frame_only_replay']['accepted'], x['label_violations_permissive'], x['label_violations_strict']]
                          for k, x in m.items()},
                      'controls_per_orientation': {o: len(v) for o, v in result['stage3_checker_controls_strict_permissive'].items()},
                      'clause_weakenings_caught': '%d/%d' % (w['caught'], w['clauses']), 'surviving_weakenings': w['surviving'],
                      'published_checker': {o: result['stage6_published_lemma_g_checker']['fifth_field_stripped'][o]['violations_uncapped']
                                            for o in ('forward', 'backward')}}, sort_keys=True))
    print('PASS_SELECTED1094_EXTENDED_LABELS_AND_ADMISSION_GAP seconds=%.1f python=%s'
          % (time.monotonic() - began, sys.version.split()[0]))


if __name__ == '__main__':
    main()
