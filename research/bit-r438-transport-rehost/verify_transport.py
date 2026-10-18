#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One improving transport on PR1043's R438 bit word (finite certificate; no new kappa).

(1) Rebuild PR1043's R438 word with its own stdlib builder (vendored, pinned) from the pinned PR589
    word and check it against PR1043's CERTIFICATE.json and FRAME-PATHS.json.
(2) Move elementary A-op 2027, receiver444 += source77 at frame186, to elementary slot 154 at frame79,
    keeping the original multi-source gate format (no gate is split); rebuild C by PR1043's rule and
    check that D is unchanged. The atlas' equivalent slots 155 and 425, and the literal R439 birth
    position 230, are built and compared.
(3) Verify the word with PR1043's replay (arbitrary dirty endpoint on all 660 columns) and with
    research/e8-bit-p111-tuned/code/xcheck_p.py (H1-H5, K = D, C = U^-1, F2 replay on all columns);
    recount the local paid profile.
(4) Host it with PR1043's own selection() code on the global_k-anchored schedule of
    research/bit589-width7-windows-seed72 and price it with assemble9.py's endpoint lines and both engines.
(5) Local optimality: PR886's frameopt.py (0 improving components, degraded positive control) and,
    with --full, PR1345's transport atlas with atlas.patch applied (0 improving singles / pairs).

Usage (from the repository root, or pass --repo):
    python3 -I -B research/<slug>/verify_transport.py [--full] [--out [RECEIPT.json]] [--jobs N]
The last line starts with PASS_ or FAIL_.

New material by Sagar Thakrar (thakrarsagar) with substantial AI assistance (Claude Code, Anthropic).
"""
import argparse
import copy
import gzip
import importlib.util
import json
import sys
import tempfile
import time
from fractions import Fraction as Q
from pathlib import Path

TAG = 'R438_T154_TRANSPORT'
if not __debug__:
    print('FAIL_%s refusing to run under python -O (inherited checkers use assert)' % TAG)
    sys.exit(2)

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('c2_transport_lib', HERE / 'lib.py')
L = importlib.util.module_from_spec(_spec)
sys.modules['c2_transport_lib'] = L
_spec.loader.exec_module(L)
require = L.require

EXPECTED_REL = 'research/e8-bit-p111-tuned/tune/EXPECTED.json'
SELECTION_REL = 'research/e8-bit-p111-tuned/data/selection9-p111.json'
XCHECK_REL = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
FRAMEOPT_REL = 'research/bit589-frame-optimum/frameopt.py'
WINDOWS_REL = 'research/bit589-width7-windows-seed72/windows.py'
PACKING_REL = 'research/bit589-width-packing/packing.py'
WORD_FILE = 'words/r438-t154.json.gz'
WORD_GZ_SHA256 = 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022'


def expect_reject(fn, reason):
    try:
        fn()
    except ValueError as error:
        require(str(error) == reason, 'control rejected for another reason: %s' % error)
        return str(error)
    raise L.Fail('control accepted (expected %r)' % reason)


def section1(repo, B, V, cert, rec):
    r439 = json.loads(gzip.decompress(repo.read(L.R439_REL)))
    require(B.BASE == '8bddbee377e2f3ce1f1247196c4b290d55767d20' and B.WORD == L.R439_REL, 'PR1043 source word')
    life = B.lifetime(r439)
    r438 = B.build(r439)
    rep439, _ = B.replay(r439)
    rep438, _ = B.replay(r438)
    for name, rep in (('r439', rep439), ('r438', rep438)):
        require(rep['word_sha256'] == L.CONTENT[name], name + ' content sha256')
        require(rep['profile'] == L.PROFILE[name], name + ' local profile')
    for key, rep in (('baseline', rep439), ('candidate', rep438)):
        ref = cert['local'][key]
        require({k: v for k, v in rep.items() if k != 'paths'} ==
                {k: (L.int_keys(v) if k == 'profile' else v) for k, v in ref.items()},
                'PR1043 certificate local receipt differs: ' + key)
    paths_ref = json.loads(L.vendor_bytes('vendor/pr1043/FRAME-PATHS.json'))
    require({'baseline': rep439['paths'], 'candidate': rep438['paths']} == paths_ref, 'FRAME-PATHS.json differs')
    controls = V.local_controls(r439, r438)
    require(len(controls['rejected']) == 5, 'PR1043 local controls')
    rec['1_r438_rebuild'] = dict(
        builder='vendor/pr1043/build.py @ ' + L.PR1043_HEAD, source_word=L.R439_REL,
        source_word_sha256=L.MAIN_PINS[L.R439_REL][0], lifetime=life,
        r439={k: rep439[k] for k in ('word_sha256', 'helpers', 'adds', 'records', 'profile', 'rank_mass')},
        r438={k: rep438[k] for k in ('word_sha256', 'helpers', 'adds', 'records', 'profile', 'rank_mass',
                                     'forward_bound', 'reverse_bound', 'local_bits', 'nine_stage_bits')},
        matches_pr1043_certificate=True, matches_frame_paths=True, pr1043_own_local_controls=controls)
    return r439, r438, rep439, rep438


def window(ops, i):
    commute = lambda a, b: a[1] != b[2] and b[1] != a[2]
    lo = i
    while lo > 0 and commute(ops[i], ops[lo - 1]):
        lo -= 1
    hi = i
    while hi < len(ops) - 1 and commute(ops[i], ops[hi + 1]):
        hi += 1
    t, s = ops[i][1], ops[i][2]
    events = [j for j in range(lo, hi + 1) if j != i and (t in ops[j][1:] or s in ops[j][1:])]
    return lo, hi, events


def section2(repo, B, r439, r438, rec):
    wlib = L.main_module(repo, 'c2_wlib', 'research/e8-bit-p111-tuned/tune/wlib.py')
    ops = L.flatten(r438['A'])
    require(ops[L.OP_INDEX] == (L.OLD_FRAME, L.RECEIVER, L.SOURCE), 'op 2027 changed')
    lo, hi, events = window(ops, L.OP_INDEX)
    t154 = L.move(r438)
    require(L.content_sha(t154) == L.CONTENT['t154'], 'moved word content sha256')
    # gate format: same gate count, same multi-source gates, only A and C differ from R438
    multi = lambda w: [g for g in w['A'] if len(g[2]) > 1]
    require(len(t154['A']) == len(r438['A']) == 2074 and multi(t154) == multi(r438) and len(multi(r438)) == 18,
            'gate format changed')
    require(len(t154['C']) == len(r438['C']) == 2573, 'C gate count')
    require({k for k in r438 if r438[k] != t154[k]} == {'A', 'C'}, 'fields other than A and C changed')
    require(B.rebuild_compensation(t154) == t154['D'] == r438['D'], 'D compensation changed')
    require(t154['A'][L.SLOT] == [L.NEW_FRAME, L.RECEIVER, [L.SOURCE]], 'new gate position')
    # the split (scouting / atlas) application is the same elementary sequence, but not the same format
    split = L.split_move(r438, wlib)
    require(L.flatten(split['A']) == L.flatten(t154['A']), 'elementary op order differs from the atlas move')
    rs, _ = B.replay(split)
    rt, _ = B.replay(t154)
    require(rs['adds'] == rt['adds'] and rs['profile'] == rt['profile'], 'split form price differs')
    require(L.content_sha(split) != L.content_sha(t154), 'split form should differ in format')
    # alternatives: atlas slots 155 and 425, and the R439 helper-birth position 230
    alts = {}
    for slot in L.ALT_SLOTS + (L.BIRTH_SLOT,):
        w = L.move(r438, slot)
        rep, _ = B.replay(w)
        require(rep['profile'] == L.PROFILE['t154'] and rep['adds'] == rt['adds'] and rep['records'] == rt['records']
                and B.rebuild_compensation(w) == w['D'], 'alternative slot %d differs' % slot)
        require(rep['paths'] == rt['paths'], 'alternative slot %d changes a frame path' % slot)
        alts[str(slot)] = dict(word_sha256=rep['word_sha256'], profile=rep['profile'], adds=rep['adds'],
                               same_paths_as_slot154=True)
    birth = L.retarget_birth(r439, B)
    require(L.content_sha(birth) == alts[str(L.BIRTH_SLOT)]['word_sha256'],
            'slot 230 is not the retargeted R439 birth')
    stored = HERE / WORD_FILE
    require(stored.exists(), WORD_FILE + ' is missing')
    stored_bytes = stored.read_bytes()
    require(L.hashlib.sha256(stored_bytes).hexdigest() == WORD_GZ_SHA256, WORD_FILE + ' gzip sha256 pin')
    stored_ok = L.content_sha(json.loads(gzip.decompress(stored_bytes))) == L.CONTENT['t154']
    require(stored_ok, WORD_FILE + ' content differs')
    rec['2_transport'] = dict(
        op=dict(index=L.OP_INDEX, gate=L.op_gate(r438['A'], L.OP_INDEX)[0], frame=L.OLD_FRAME,
                receiver=L.RECEIVER, source=L.SOURCE),
        commutation_window=[lo, hi], events_on_receiver_or_source_in_window=events,
        chosen=dict(slot=L.SLOT, gate_index=L.SLOT, frame=L.NEW_FRAME, word_sha256=L.CONTENT['t154']),
        gate_format=dict(choice='re-merged: original multi-source gate format kept (no gate split)',
                         A_gates=len(t154['A']), multi_source_A_gates=len(multi(t154)), C_gates=len(t154['C']),
                         D_gates=len(t154['D']), D_unchanged=True, C_rule='PR1043 build.py literal reverse at frame 1',
                         split_form=dict(A_gates=len(split['A']), C_gates=len(split['C']),
                                         same_elementary_sequence=True, adds=rs['adds'], profile=rs['profile'],
                                         word_sha256=rs['word_sha256'], used=False)),
        alternatives=alts,
        slot230_equals_r439_birth_retarget=True,
        stored_word=dict(file=WORD_FILE, content_sha256_ok=stored_ok))
    return t154, wlib, alts


def section3(repo, B, wlib, r439, r438, t154, rep439, rep438, cert, rec, tmp, jobs, frameopt_c):
    rep, _ = B.replay(t154)
    require(rep['profile'] == L.PROFILE['t154'] and rep['rank_mass'] == 5121 and rep['adds'] == 24248
            and rep['records'] == 27175 and rep['helpers'] == 438 and rep['registers'] == 660,
            'PR1043 replay of the moved word')
    require((rep['forward_bound'], rep['reverse_bound'], rep['local_bits'], rep['nine_stage_bits'])
            == (49347, 1113070, 93, 177), 'precision bounds changed')
    require(wlib.paid(t154) == L.PROFILE['t154'], 'wlib recount')
    changed = {r: [a, b] for r, (a, b) in enumerate(zip(rep438['paths'], rep['paths'])) if a != b}
    require(changed == {444: [[0, 186, 509, 392, 513, 1], [0, 79, 509, 392, 513, 1]]}, 'changed paths')
    old = [p for r, p in enumerate(rep439['paths']) if r != 470]
    require(rep['paths'] == old, 'surviving paths are not exactly PR589 R439 paths')
    # words for the subprocess checkers and controls
    words = {'t154': t154, 'r438': r438}
    words['nc_late_frame79_read_slot426'] = L.move(r438, 426)
    words['nc_moved_keeping_frame186'] = L.move(r438, L.SLOT, L.OLD_FRAME)
    stale = copy.deepcopy(t154)
    stale['C'] = copy.deepcopy(r438['C'])
    words['nc_stale_C'] = stale
    dropd = copy.deepcopy(t154)
    dropd['D'][0][2].pop(0)
    words['nc_dropped_D_operand'] = dropd
    files = {}
    for name, w in words.items():
        files[name] = Path(tmp) / (name + '.json.gz')
        L.save_word(files[name], w)
    controls = {}
    controls['nc_late_frame79_read_slot426'] = dict(pr1043_replay=expect_reject(
        lambda: B.replay(words['nc_late_frame79_read_slot426']), 'Frame descent'))
    controls['nc_moved_keeping_frame186'] = dict(pr1043_replay=expect_reject(
        lambda: B.replay(words['nc_moved_keeping_frame186']), 'Frame descent'))
    srep, _ = B.replay(stale)  # C only reordered across commuting gates: F2-correct, but not literal
    controls['nc_stale_C'] = dict(pr1043_replay='accepted (C reordered across commuting gates)',
                                  adds=srep['adds'])
    controls['nc_dropped_D_operand'] = dict(pr1043_replay=expect_reject(
        lambda: B.replay(dropd), 'Wrong arbitrary-dirty endpoint'))
    neutral = copy.deepcopy(t154)
    dup = [0, neutral['D'][0][1], [neutral['D'][0][2][0]]]
    neutral['D'][0:0] = [copy.deepcopy(dup), dup]
    nrep, _ = B.replay(neutral)
    require(nrep['adds'] == rep['adds'] + 2 and nrep['profile'] == rep['profile'], 'neutral pair')
    controls['pc_neutral_ADD_pair_paid'] = dict(extra_adds=2, same_profile=True)
    # subprocesses: xcheck_p on every word, frameopt on t154 / r438 / degraded t154
    xcheck = repo.path(XCHECK_REL)
    frameopt = repo.path(FRAMEOPT_REL)
    repo.read('research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py')
    argv = {}
    for name in words:
        argv['xcheck:' + name] = L.python_argv(xcheck, files[name], '--json', Path(tmp) / (name + '.xcheck.json'))
    c154, c438 = frameopt_c
    argv['frameopt:t154'] = L.python_argv(frameopt, files['t154'], c154)
    argv['frameopt:t154:degrade'] = L.python_argv(frameopt, files['t154'], c154, '--degrade')
    argv['frameopt:r438'] = L.python_argv(frameopt, files['r438'], c438)
    runs = L.run_parallel(argv, jobs)
    xc = {}
    for name in words:
        r = runs['xcheck:' + name]
        out = r['stdout'].strip().splitlines()
        js = Path(tmp) / (name + '.xcheck.json')
        xc[name] = dict(rc=r['rc'], last=out[-1] if out else '', stdout=out, seconds=r['seconds'],
                        json=json.loads(js.read_text()) if js.exists() else None)
    x = xc['t154']
    require(x['rc'] == 0 and x['json']['status'] == 'PASS_EXACT_REPLAY_AND_INTERLEAVED_INTERFACE', 'xcheck t154')
    require(all(x['json']['hypotheses'].values()) and len(x['json']['hypotheses']) == 5, 'H1-H5')
    require(all(x['json']['conclusion'].values()) and x['json']['conclusion']['K_equals_D']
            and x['json']['conclusion']['C_is_U_inverse'], 'K = D, C = U^-1')
    require(x['json']['gates'] == {'D': 111, 'A': 2074, 'B': 712, 'C': 2573} and x['json']['columns'] == 660
            and x['json']['copy_ranks'] == [7] * 9, 'xcheck gate counts / columns')
    require(xc['r438']['rc'] == 0 and xc['r438']['json'] == cert['native']['candidate']['interface'],
            'xcheck on R438 does not reproduce PR1043 certificate interface receipt')
    require(xc['nc_late_frame79_read_slot426']['rc'] == 1
            and xc['nc_late_frame79_read_slot426']['last'].startswith('REJECT climb not nested: register 77'),
            'xcheck accepted the late frame79 read')
    require(xc['nc_moved_keeping_frame186']['rc'] == 1
            and xc['nc_moved_keeping_frame186']['last'].startswith('REJECT climb not nested: register 77'),
            'xcheck accepted the early frame186 read')
    require(xc['nc_stale_C']['rc'] == 1 and xc['nc_stale_C']['json'] is not None
            and xc['nc_stale_C']['json']['hypotheses']['H4_C_literal_reverse_at_full'] is False
            and xc['nc_stale_C']['last'] == 'REJECT interface', 'xcheck accepted a stale C')
    require(xc['nc_dropped_D_operand']['rc'] == 1
            and xc['nc_dropped_D_operand']['last'].startswith('REJECT targets not y + x'), 'xcheck accepted bad D')
    for name in ('nc_late_frame79_read_slot426', 'nc_moved_keeping_frame186', 'nc_stale_C', 'nc_dropped_D_operand'):
        controls[name]['xcheck_p'] = xc[name]['last']
    fo = {k.split(':', 1)[1]: dict(json.loads(v['stdout'].strip().splitlines()[-1]), seconds=v['seconds'])
          for k, v in runs.items() if k.startswith('frameopt:') and v['rc'] == 0}
    require(len(fo) == 3, 'frameopt run failed: %s' % {k: v['stderr'][-300:] for k, v in runs.items()
                                                      if k.startswith('frameopt:') and v['rc']})
    require(fo['t154']['improving_components'] == 0 and fo['t154']['smallest_alternative_delta'] > 0
            and L.int_keys(fo['t154']['start_profile']) == L.PROFILE['t154'], 'frameopt t154')
    require(fo['t154:degrade']['improving_components'] > 0
            and L.int_keys(fo['t154:degrade']['optimum_profile']) == L.PROFILE['t154'], 'frameopt degraded control')
    require(fo['r438']['improving_components'] == 0 and L.int_keys(fo['r438']['start_profile']) == L.PROFILE['r438'],
            'frameopt r438')
    rec['3_verification'] = dict(
        pr1043_replay={k: v for k, v in rep.items() if k != 'paths'},
        changed_paths_vs_r438={str(k): v for k, v in changed.items()},
        surviving_paths_equal_pr589_r439=True, wlib_recount=wlib.paid(t154),
        xcheck_p={k: dict(rc=v['rc'], stdout=v['stdout'], json=v['json'], seconds=v['seconds']) for k, v in xc.items()},
        xcheck_r438_equals_pr1043_certificate_interface=True,
        controls=controls)
    rec['5_local_optimality'] = dict(frameopt=fo)
    return rep, files


def section4(repo, V, cert, rec, rep439, rep154):
    M, O = L.engines(repo)
    W72 = L.main_module(repo, 'c2_seed72_windows', WINDOWS_REL)
    sched = W72.schedule()
    win = W72.checked_windows(sched)
    PK = L.main_module(repo, 'c2_packing', PACKING_REL)
    model = PK.slot_model(json.loads(repo.read(EXPECTED_REL)), json.loads(repo.read(SELECTION_REL)))
    require({i: r for i, (r, st) in win.items()} == model['caps'], 'window capacities != packing slot model')
    with tempfile.TemporaryDirectory(prefix='c2-hosting-') as td:
        hc = V.pipeline.selection(repo.root, Path(td), {'schedule': copy.deepcopy(sched)})
    ch = cert['hosting_change']
    require([list(x) for x in hc['removed_slots']] == ch['removed_slots'], 'removed slots')
    require(L.int_keys(ch['old_remainders']) == hc['old_remainders'], 'old remainders')
    require(L.int_keys(ch['new_remainders']) == hc['new_remainders'], 'new remainders')
    require(hc['returned_idle_rank_per_replica'] == 72 and hc['hosted_helpers_per_replica'] == 9 * 438, 'hosting')
    H = {'r439': L.hosted_profile(L.PROFILE['r439'], hc['old_remainders']),
         'r438': L.hosted_profile(L.PROFILE['r438'], hc['new_remainders']),
         't154': L.hosted_profile(L.PROFILE['t154'], hc['new_remainders'])}
    require(H['r439'] == L.int_keys(cert['hosted']['baseline']['audit']['profile']), 'R439 hosted profile')
    require(H['r438'] == L.int_keys(cert['hosted']['candidate']['audit']['profile']), 'R438 hosted profile')
    for P in H.values():
        require(sum(r * n for r, n in P.items()) == 1808352 and L.M_BIT * L.LIVE - 1808352 == L.DEFICIT
                and max(P) == 42 and 2 * 42 ** 2 < L.M_BIT ** 2, 'hosted mass / maxchild')
    require(sum(H['t154'].values()) == sum(H['r438'].values()) == 904320, 'paid children')
    # PR1043's own complete recount and idle control, applied to the new word against the PR589 audit
    result = {'baseline': {'hosted': copy.deepcopy(cert['hosted']['baseline'])},
              'candidate': {'hosted': {'audit': {'profile': {str(k): v for k, v in H['t154'].items()},
                                                 'live': L.LIVE, 'deficit': L.DEFICIT}}},
              'hosting_change': hc}
    local = {'baseline': {'profile': rep439['profile']}, 'candidate': {'profile': rep154['profile']}}
    recount = V.check_hosted_change(result, local)
    idle = V.idle_control(result, local)
    prices = {name: L.certify(M, O, P) for name, P in H.items()}
    for name in prices:
        require(prices[name]['decimal'] == L.C_DEC[name], name + ' endpoint')
    require(prices['r439']['lower'] == cert['hosted']['baseline']['invoice']['bit_lower'], 'PR589 invoice')
    require(prices['r438']['lower'] == cert['hosted']['candidate']['invoice']['bit_lower'], 'PR1043 invoice')
    c154, c438 = Q(prices['t154']['lower']), Q(prices['r438']['lower'])
    neg = dict(r438_profile_at_new_c=L.side(M, O, H['r438'], c154),
               t154_profile_at_new_c_plus_1e24=L.side(M, O, H['t154'], c154 + Q(1, 10 ** 24)),
               t154_profile_at_r438_c=L.side(M, O, H['t154'], c438))
    require(neg == dict(r438_profile_at_new_c='reject', t154_profile_at_new_c_plus_1e24='reject',
                        t154_profile_at_r438_c='accept'), 'pricing controls')
    # selected context, read from git objects at the pinned main commit (the working tree may move on)
    def at_main(rel):
        return L.subprocess.run(['git', '-C', str(repo.root), 'show', L.MAIN_COMMIT + ':' + rel],
                                capture_output=True, check=True).stdout
    sel = json.loads(at_main('certificates/selected-result.json'))
    asm_bytes = at_main(sel['certificate'])
    require(L.hashlib.sha256(asm_bytes).hexdigest() == sel['certificate_sha256'], 'selected certificate hash')
    asm = json.loads(asm_bytes)
    require(asm['binding'] == 'complex' and Q(asm['complex_lower']) < Q(asm['bit_lower']) < c154,
            'selected context: bit side would bind')
    rec['4_pricing'] = dict(
        hosting=dict(code='vendor/pr1043/pipeline.py:selection @ ' + L.PR1043_HEAD,
                     schedule='research/bit589-width7-windows-seed72/windows.py schedule(), anchored to global_k.py',
                     window_capacities={str(i): r for i, (r, st) in sorted(win.items())},
                     window_stages={str(i): list(st) for i, (r, st) in sorted(win.items())},
                     equals_pr1043_certificate_hosting_change=True,
                     old_remainders=hc['old_remainders'], new_remainders=hc['new_remainders']),
        hosted_profiles={k: {str(r): n for r, n in v.items()} for k, v in H.items()},
        pr1043_recount=recount, pr1043_idle_control=idle, prices=prices,
        gain=dict(vs_r438=str(c154 - c438), vs_r438_decimal='%.6e' % float(c154 - c438),
                  vs_r438_percent='%.6f' % float(100 * (c154 - c438) / c438),
                  vs_pr589=str(c154 - Q(prices['r439']['lower'])),
                  vs_pr589_percent='%.6f' % float(100 * (c154 - Q(prices['r439']['lower'])) / Q(prices['r439']['lower']))),
        controls=neg,
        selected_context=dict(certificate=sel['certificate'], kappa=asm['kappa'], kappa_decimal=asm['kappa_decimal'],
                              complex_lower=asm['complex_decimal'], bit_lower=asm['bit_decimal'],
                              binding=asm['binding'], no_new_kappa=True))
    return c154, c438


def atlas_full(repo, rec, tmp, files, c154):
    src = L.atlas_source('patched', c154)
    path = L.atlas_tree(repo, Path(tmp) / 'atlas', 'patched_t154', src)
    runs = L.run_parallel({'t154': L.python_argv(path, files['t154'])}, 1)
    r = runs['t154']
    require(r['rc'] == 0, 'patched atlas failed on the moved word: ' + r['stderr'][-400:])
    out = json.loads(r['stdout'].strip().splitlines()[-1])
    for sec in 'AB':
        require(out[sec]['improving'] == [] and 'improving_count' not in out[sec]
                and out[sec].get('unresolved', 0) == 0, 'atlas: improving single transport in ' + sec)
    for p in out['simultaneous_pairs']:
        require(p.get('improving', 0) == 0 and p.get('unresolved', 0) == 0 and p['best_improving'] is None,
                'atlas: improving shared-register pair')
    require(len(out['replay_spot_check']) == 8, 'atlas spot checks')
    summary = dict(c=out['c'], seconds=r['seconds'],
                   singles={sec: {k: v for k, v in out[sec].items() if k != 'improving'} for sec in 'AB'},
                   improving_singles=0, improving_pairs=0,
                   pairs=out['simultaneous_pairs'],
                   components_over_budget=[{k: v for k, v in s.items() if not k.endswith('combos')}
                                           for s in out['simultaneous']])
    rec['5_local_optimality']['atlas_patched'] = summary
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=L.default_repo(__file__), help='repository root')
    ap.add_argument('--out', nargs='?', const=str(HERE / 'verify_transport.receipt.json'),
                    help='write a JSON receipt (default: next to this script)')
    ap.add_argument('--full', action='store_true', help='also run the patched PR1345 atlas (about 2 minutes)')
    ap.add_argument('--jobs', type=int, default=4, help='parallel subprocesses')
    args = ap.parse_args()
    t0 = time.time()
    rec = dict(status='RUNNING', script='verify_transport.py', environment=L.environment(),
               main_commit_of_pins=L.MAIN_COMMIT, pr1043_head=L.PR1043_HEAD, pr1345_head=L.PR1345_HEAD)
    try:
        repo = L.Repo(args.repo)
        rec['pins'] = dict(main=repo.verify_all(), vendor=L.verify_vendor())
        tampered = bytearray(repo.read(L.R439_REL))
        tampered[len(tampered) // 2] ^= 1
        try:
            L.check_bytes(bytes(tampered), *L.MAIN_PINS[L.R439_REL], L.R439_REL)
        except L.Fail as error:
            rec['pin_control'] = str(error)
        else:
            raise L.Fail('a flipped byte passed the pin check')
        B = L.vendor_module('pr1043_build', 'vendor/pr1043/build.py')
        V = L.vendor_module('pr1043_verify', 'vendor/pr1043/verify.py')
        cert = json.loads(L.vendor_bytes('vendor/pr1043/CERTIFICATE.json'))
        r439, r438, rep439, rep438 = section1(repo, B, V, cert, rec)
        t154, wlib, alts = section2(repo, B, r439, r438, rec)
        rep154, _ = B.replay(t154)
        c154, c438 = section4(repo, V, cert, rec, rep439, rep154)
        with tempfile.TemporaryDirectory(prefix='c2-verify-') as tmp:
            rep154, files = section3(repo, B, wlib, r439, r438, t154, rep439, rep438, cert, rec, tmp, args.jobs,
                                     (c154, c438))
            atlas = atlas_full(repo, rec, tmp, files, c154) if args.full else None
        negatives = dict(rec['3_verification']['controls'])
        negatives.pop('pc_neutral_ADD_pair_paid')
        negatives.update({'pricing:' + k: v for k, v in rec['4_pricing']['controls'].items() if v == 'reject'})
        negatives['hosting:' + rec['4_pricing']['pr1043_idle_control']['name']] = \
            rec['4_pricing']['pr1043_idle_control']['rejection']
        negatives['pin:flipped_byte_in_pr589_word'] = rec['pin_control']
        rec['negative_controls'] = negatives
        ncontrols = len(negatives)
        rec['status'] = 'PASS'
        rec['seconds'] = round(time.time() - t0, 1)
        line = ('PASS_%s R=438 op2027(186:444+=77)->slot154@frame79 profile=%s ADDs=24248 '
                'c=%s->%s frameopt_improving=0 atlas=%s neg_controls=%d (plus 5 PR1043 controls on R438/R439) no_new_kappa'
                % (TAG, ','.join('%d:%d' % kv for kv in L.PROFILE['t154'].items()), L.C_DEC['r438'], L.C_DEC['t154'],
                   'singles0/pairs0' if atlas else 'not_run(--full)', ncontrols))
        rec['final_line'] = line
        if args.out:
            L.write_receipt(args.out, rec)
        print(line)
    except Exception as error:  # every failure ends in one FAIL_ line
        rec['status'] = 'FAIL'
        rec['error'] = '%s: %s' % (type(error).__name__, error)
        rec['seconds'] = round(time.time() - t0, 1)
        if args.out:
            try:
                L.write_receipt(args.out, rec)
            except Exception:
                pass
        print('FAIL_%s %s' % (TAG, rec['error']))
        sys.exit(1)


if __name__ == '__main__':
    main()
