#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent audit of open PR #2530 (head b4012098, research/source-partner-lifetimes): single entry point.

PR #2530 (T74 complex supplier, "source-partner lifetimes") removes eight width-8 helpers from PR2462's words by
letting eight source registers lend themselves after an exact restoration, re-times the 666 calls in a diagonal
order, ships a new owner fill and claims kappa = C - 1e-70 - 1e-46 with C = 0.001713737921547504346752.  This
package re-checks that claim with code written independently of the PR (standard library only):

  check_words.py      scope A: the two changed words (endpoint, warps, profile, diff, restorations, cleanup)
  check_fill.py       scope B: order, windows, owner fill (R-a..R-e by two implementations, R-g by the vendored
                      pending_axes_and_charts; R-f replaced by an own stock and namespace-receipt check), physical stock
  check_accounting.py scope C: overrides, recovered source, stock/precision arithmetic, endpoint, kappa, PR2474
  audit_common.py     the failure type and the pinned-input reader shared by the three scopes
  vendor/pr2315/words_check.py, vendor/pr2387/fill_check80.py: this contributor's earlier checkers (pinned below)

Inputs: every PR file is read with `git -C <repo> show <commit>:<path>` at a pinned commit and must match a pinned
git blob id and sha256 (INPUTS below); two package trees are pinned by tree id and every tree object below them is
re-hashed.  PR content is data only: it is decoded as JSON/gzip/tar/text and never imported or executed.  Every git
subprocess runs with GIT_DIR, GIT_WORK_TREE and the other repository-redirecting variables and the GIT_CONFIG_*
injections removed and GIT_NO_REPLACE_OBJECTS=1 (audit_common.git_env), so it reads exactly --repo's own objects;
without --fetch nothing is written to the repository.  --fetch fetches a missing pinned commit from
refs/pull/N/head (or by sha) of --remote into the namespaced ref refs/audit/pr<N> of the --repo repository (created
or force-updated) and writes nothing else: no FETCH_HEAD, no other ref, no reflog, no commit-graph, no gc or
maintenance, no hook (audit_common.FETCH_OPTIONS, FETCH_CONFIG; git >= 2.29); the commit must then be present and
reachable from that ref, so that it survives git gc.  The default run recomputes everything and requires the result
to equal the committed RESULT.json; --out rewrites RESULT.json.  Refuses python -O.

Controls (RESULT.json "controls", counted in "summary"): every negative control names the check that must reject
it and asserts that this check, not another, rejected it.  The PASS line prints negative_controls=<rejected>/
<attempted>-rejected from two counters: attempted = controls run (audit_common.attempt, called by every control
helper before its mutant runs), rejected = control records written after the rejecting check was asserted (a
mutation of one word counts once per word); the run fails unless they are equal.  distinct_controls counts distinct
(mutant, check) pairs, a mutation applied to both words once; the injected-climb controls are checker plumbing
(non-vacuity of the zero-climb check, not a property of the words) and are reported separately, outside these
counts.  positive_controls counts the positive controls executed and passed (audit_common.positive; they must be
exactly POSITIVE_CONTROLS).  The 'fwd+dual' token is derived from the orientations recorded by the replays that
ran, and the kappa token from the grid quantities 1/F and B.  The vendored-pin check has its own controls
(tampered in-memory bytes must raise VendorPinMismatch), and RESULT.json records the git blob id and sha256
computed from the vendored bytes actually loaded.

Not covered (SCOPE_LIMITS below and README): the physical identity of each K_op shared by the A prelude and the B
handoff (Clifford phases, monomial lifts), native precision (prefix_l1 recomputation), the PR's emit/audit/invoice/
native pipeline under the new order, the inherited window/interleaving semantics, and the 63 outer inequalities.
A local-only re-run of PR2462's outer scripts on #2530's SPEC (which regenerated #2530's ledger byte-for-byte) is
documented in the README only; this package never runs PR code.

Usage: python3 -I -B verify.py [--repo PATH] [--fetch] [--remote URL] [--out]
  (--fetch needs git >= 2.29 (--no-write-fetch-head) and network access to --remote; it writes the fetched objects
  and refs/audit/pr<N> in the --repo repository for each pinned commit it has to fetch, nothing else; a failed fetch
  is reported with git's exit code and stderr)
The run time is printed on its own line; the final stdout line starts with PASS_T74_2530_INDEPENDENT_AUDIT or, for
any exception (a failed check, a vendored-pin mismatch, a missing git, a malformed input), is the single line
`FAIL_T74_2530_INDEPENDENT_AUDIT <exception type>: <message>` with exit code 1; it carries no timing, so it is
identical between runs.  (Command-line usage errors are reported by argparse with exit code 2.)
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import traceback
import types

PASS_LINE = 'PASS_T74_2530_INDEPENDENT_AUDIT'
FAIL_LINE = 'FAIL_T74_2530_INDEPENDENT_AUDIT'
if not __debug__:
    sys.stdout.write(FAIL_LINE + ' UsageError: refusing to run under python -O\n')
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
RESULT_NAME = 'RESULT.json'

# Vendored checkers of this contributor (byte copies from fork branch research/t74-2435-fill-independent-check at
# a3aabff9; originally PR2315 research/t74-borrow43-independent-check and PR2387 research/t74-80alias-owner-fill).
VENDOR = {
    'vendor/pr2315/words_check.py': ('words_check', '0b646b9d5583c75a78e0c2dd7e9cfffa02055058',
                                     'b66414a39f5ac7b9cd32284027e13a550734901aca5f4457085a034689bc3ce6'),
    'vendor/pr2387/fill_check80.py': ('fill_check80', '557e0732bfe4c030436a11f5433143c10fa07821',
                                      '1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06'),
}
LOCAL_MODULES = ('audit_common', 'check_words', 'check_fill', 'check_accounting')

H2530 = 'b4012098048e12500b2d33d2e84be281915a27ac'   # PR #2530 head (object under audit)
H2462 = 'ef34071fee6dfb0286e9850a5cec4e36d9eb126d'   # PR #2462 head (predecessor words/order, overridden files)
H2435 = '324d7d3590dc21003940a44cb0cbdc32b3620f25'   # PR #2435 head (source-archive provenance, stock rule)
H2269 = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'   # PR #2269 head (T74 GLOBAL-TEMPLATE, DATA-PHASES)
H2474 = '5298f86c5193db65f869121eab3cac16d557196c'   # PR #2474 head (latest-claim comparison)
COMMITS = {2530: H2530, 2462: H2462, 2435: H2435, 2269: H2269, 2474: H2474}
P30 = 'research/source-partner-lifetimes/'
PHO = 'research/gmx-t74-borrow43-handoff/'
# key: (PR, commit, path, git blob id (tree id for trees), sha256 (None for trees))
INPUTS = {
    'w2530_base': (2530, H2530, P30 + 'evidence/eight-alias-base.json.gz', '67e93052bd455c14b5b256d6e67209ebbeb81c67',
                   'cdb8ae51947bd8ce8269192286b6e47e93688a23a7a2f682cca468bf14fbbbc1'),
    'w2530_extra': (2530, H2530, P30 + 'evidence/eight-alias-extra.json.gz', '3760f5c273d23957e888edab7a044f0eda807cfa',
                    'c152ed4d85ea16523e0ef938029283cb4392ffa154f48d7d25ecb4df03eae7b5'),
    'providers2530': (2530, H2530, P30 + 'evidence/eight-providers.json', 'a678492aece195bf9b3e35a72cc518dd1e2ada31',
                      '13d5abb0f5dccf32703a04334209d0d47516e985db4a51809a593538f45c1f45'),
    'fill2530': (2530, H2530, P30 + 'evidence/eight-fill.json.gz', '6e293d78ef20c2e0562ab2a81f35c5348c49d5c8',
                 '82f59244fff1bf2b2b6ea519913b1ff68c69f0783e3e034a58bdaef5f2eaef4b'),
    'order2530': (2530, H2530, P30 + 'evidence/eight-order.json', 'a7de9f93b6b95a4f8b0b65459e135cd73836a9dd',
                  'e48b51a7d6a315971fff8b8e51748251750ff4ed8fe30b8b023de1a1a8019783'),
    'plan2530': (2530, H2530, P30 + 'evidence/PLAN.json.gz', 'e6ffd4ce0f2a6b2cd8ebc7e0449b4cc1b4c90217',
                 '194c52961dad9d11f52e4660a6bf942ef63de641f5d0b059a9a727252cff7ce0'),
    'screen2530': (2530, H2530, P30 + 'evidence/order-screen.json.gz', 'ce6871ae6d425448e4a7d37ea2fa19d4c1b9840c',
                   '67b7d594128cd84fc424989f7373b1cdf669ebd3f5c6e782433207e392e7330c'),
    'profile2530': (2530, H2530, P30 + 'PROFILE.json', '8cfcfbef80789666a2c38cdd4d926c44526e5585',
                    'f10bd6dd8d69d8d224909b23882f6ca68f851792af14868cb0e415048aabe88b'),
    'spec2530': (2530, H2530, P30 + 'SPEC.json', '9e36503889210253a6d8342f346411b286d907b0',
                 'f4fdda46e5aa90e7377b006e273bec470f0d21cfb1a4dac22867c95687a6822a'),
    'claim2530': (2530, H2530, P30 + 'CLAIM.json', '60cadf69ecdd7a3a5ac4d830f0592b76850e906a',
                  'a5278674e54818d451968921f4cae0fead826ba1fb7f68769c6cdb44e8245351'),
    'ledger2530': (2530, H2530, P30 + 'evidence/OUTER-LEDGER.json', 'ad15a7efa51c5ea60be2b28f0bc5549387f48b1f',
                   '549d88fe1a5ac9008f4fee41d16bc57bf1ac12209d875a08410b4a7f2c229ae8'),
    'iglobal2530': (2530, H2530, P30 + 'receipts/INDEPENDENT-GLOBAL.json', 'c061a581da3ad9ed06b8d6f93796c0b5dfd18d06',
                    'f7f70ed969ba8dd0ace4fa981803b3765d76efe9ade9a1f9186c577881e1b7f6'),
    'ilocal2530_base': (2530, H2530, P30 + 'receipts/base-INDEPENDENT-LOCAL-REPLAY.json',
                        '6e8579d0a2cad7cc7ea8033bdcbfbc005b7ed70e',
                        '7c158e73ea14d9b7f9985b29d774141c2fef955a42bcf99ec3206087f57d323d'),
    'ilocal2530_extra': (2530, H2530, P30 + 'receipts/extra-INDEPENDENT-LOCAL-REPLAY.json',
                         '3f7d935973965c1ed17c64db656dd9627e4a5869',
                         'eb83a1666c3a7500c669cf222e2a09559721f8e695d6d31ebe1f03b29bd00327'),
    'overrides2530': (2530, H2530, P30 + 'OVERRIDES.json', 'ff72e97694491b442301f92163823aa2a73fae60',
                      'bf35523acace6d8300750a37b3a552b0ad74e9112a0859fcc6bfacc311cc63f5'),
    'ic2530': (2530, H2530, P30 + 'independent_core.py', '1ff1320d7b3eea33deb7bea38a290bbe060280ef',
               '3a09f71d67b3d75344f48ec3bc0cffed5d27f0cec2b4366d9cfcb1a5f302ae15'),
    'rebind2530': (2530, H2530, P30 + 'rebind.py', 'b0d04e911d638486ffdfac3b69526e2be9eb4478',
                   '52f8b4cec2dab69cbe590e1fd0f7a68e1b35de5a540bd22fd2adfce07a92b46b'),
    'overlay2530': (2530, H2530, P30 + 'pr2462-overlay.tar.gz', '0f5cd04d4c49855dbc31feeebb4ce6776e7e0f10',
                    '1fc0dba4b2e78d73068269b273e194ad2fe1ad45305aaa7bcec91b35372f3344'),
    'src2435_tar2530': (2530, H2530, 'research/t74-owner-consolidation/source-pr2435.tar.gz',
                        '94878b26080479788d0870b4e536a2f2e111a996',
                        'f8937eabaa59667831f21ecbcb68eb163de02dd3154c5c51dd3f814a949ae0ff'),
    'claim2474_copy2530': (2530, H2530, P30 + 'evidence/PR2474-OUTER-CLAIM.json',
                           'bbc3da80f0f7256d9cc44f9c86cfe72cd45c972d',
                           '512d036e6816caa219bcf85785bac4d410822840c69a29923e3edcbaf388297b'),
    'w2462_base': (2462, H2462, PHO + 'new/borrow/words/BORROW-WORD-43base.json.gz',
                   '0bc4e8c167de63931e5cc208527ad684573a373c',
                   '3506c84203f126900326ff4d22aaceda819734e5f96fa4622d43fbb78b946ece'),
    'w2462_extra': (2462, H2462, PHO + 'new/borrow/words/BORROW-WORD-43extra.json.gz',
                    '33f39e6826d181f4e0aead30b427e8de3c107a9a',
                    'ec7103c196b32de7af79a6f43952cbe998c085a00f1a8e740f5556c774589099'),
    'tpl2462': (2462, H2462, PHO + 'GLOBAL-TEMPLATE.json.gz', '5327fc2f4e8ea82ed356c94ff040d23fc73c731f',
                '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db'),
    'tpl_t37_2462': (2462, H2462, PHO + 'inputs/GLOBAL-TEMPLATE.json.gz', '114808c32b1799da53524bdc25cea67efb60009e',
                     '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'),
    'order2462': (2462, H2462, PHO + 'new/borrow-fill/ORDER.json', '92be92120d33d5f78de541ff2d855324a793da7f',
                  'f693a8f0b78eaa803d4e7860b3cc71112dafb323db27998cea132d5b0f18dd84'),
    'dispatch2462': (2462, H2462, PHO + 'new/borrow-fill/DISPATCH.json', 'f971db25d5c1ccf614f21c311b05f8e86ff72e88',
                     'e7a20e652d6bd8371e48f9463d266a2d23c6c5cd3d41b7c039ef9efa8fc3cd3e'),
    'ic2462': (2462, H2462, PHO + 'independent_core.py', 'a63d39a35a42f55546e3d3ed9a5efbdbaf238d2d',
               '15acc8bb3e00eeaf12783942099735572875ac3c977e8e40817bef73ac81a7f6'),
    'rebind2462': (2462, H2462, PHO + 'new/rebind.py', 'a0453d3e956d80c2088b9f69650095dcae800343',
                   'faf283eb4edd2e6a1ccb40b3cb3ba30ae54338eaf5ea0a10d84d11d7939502af'),
    'spec2462': (2462, H2462, PHO + 'new/SPEC.json', 'e7c9c1c4464215e0ece962dcb49ce18c54ada9c1',
                 '78ba65d4591deb74b1c91b2dfbb2e67e1f3ce4aed916c4cebd5c2684bb450ecf'),
    'outer_b2462': (2462, H2462, PHO + 'outer/B.json', 'a96cddda3c5b0727ab45638e080556d39790c90f',
                    '703631aeefdf4d3f59f8206e875d72a0f6a8151e486d7bff525de258c71ffdc2'),
    'tree2462': (2462, H2462, PHO.rstrip('/'), '2b232cffca48dd38132674e08134f088ee26d90e', None),
    'rebind2435': (2435, H2435, PHO + 'new/rebind.py', 'a0453d3e956d80c2088b9f69650095dcae800343',
                   'faf283eb4edd2e6a1ccb40b3cb3ba30ae54338eaf5ea0a10d84d11d7939502af'),
    'spec2435': (2435, H2435, PHO + 'new/SPEC.json', '5263146bfdfb3c92bdae12bc59dd375362a6b971',
                 'dd0bdfc8c7b871d627eac981af185dee061ab1bd564ce7c3ebfdccec4aa965d3'),
    'w2435_base': (2435, H2435, PHO + 'new/borrow/words/BORROW-WORD-43base.json.gz',
                   '7e382c2d03ab32a62c3b0aa3d799612a126068af',
                   '46924868825e07168c2e8149dada6b1157afa444b316eb00c16555ec8a4004db'),
    'tree2435': (2435, H2435, PHO.rstrip('/'), '4ca7214c586e19a8e24620a1d75772094cc828aa', None),
    'tpl2269': (2269, H2269, 'research/gmx-t74-borrow43/GLOBAL-TEMPLATE.json.gz',
                '5327fc2f4e8ea82ed356c94ff040d23fc73c731f',
                '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db'),
    'phases2269': (2269, H2269, 'research/community-cold617-audit/pr600/replay/mixed-global/base/work/'
                   'complex-nine-native/DATA-PHASES.json', 'd9a4f84211182ca200c081ea061d724c8a2cfb70',
                   'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
    'claim2474': (2474, H2474, PHO + 'outer/OUTER-CLAIM.json', 'bbc3da80f0f7256d9cc44f9c86cfe72cd45c972d',
                  '512d036e6816caa219bcf85785bac4d410822840c69a29923e3edcbaf388297b'),
}
SCOPE_LIMITS = [
    'K_op identity: warp letters are abstract; the K_op applied in the A prelude (port line -> [30]) and at the B '
    'handoff (U -> E) is assumed to be one physical operator; Clifford phases and monomial lifts are not checked',
    'native precision: prefix_l1 values are taken from the PR receipts; only their bit arithmetic is checked',
    'window semantics and free interleaving of replica controllers are inherited assumptions, not re-derived',
    'the PR emit/audit/invoice/native pipeline under the new order is not run (receipts only)',
    'the 63 outer inequalities are not re-derived beyond the grid-maximum conditions',
    'local-only, not in this package: PR2462 outer/check_ledger.py and independent_check.py re-run on the #2530 SPEC '
    'regenerated OUTER-LEDGER.json and OUTER-INDEPENDENT.json byte-for-byte',
]
# Positive controls: id (recorded by audit_common.positive when the control has passed) -> description.
POSITIVE_CONTROLS = {
    'pr2462_base_word': 'PR2462 base word reproduces PR2462 claims (profile, widths, 654 inputs) with the same word '
                        'checker',
    'pr2462_extra_word': 'PR2462 extra word reproduces PR2462 claims (profile, widths, 654 inputs) with the same word '
                         'checker',
    'moment_enclosure_C2462': 'the moment enclosure [lo, hi] at PR2462\'s 3000-digit endpoint C2462 satisfies lo <= 1 '
                              'and hi >= 1 - 1e-2990; C2462 - 1e-150 is accepted and C2462 + 1e-150 rejected',
}
POSITIVE_CONTROLS_NOTE = ('The unmutated PR2530 words passing with the own re-derived cleanup is part of the main '
                          'check (cleanup independence), not a positive control.')
PLUMBING_GROUPS = ('plumbing_inserted_climbs',)


class VendorPinMismatch(Exception):
    """A vendored checker does not match its pinned git blob id and sha256."""


def vendor_pin(data, pin, path):
    """(git blob id, sha256) computed from the bytes `data` of a vendored checker; raises VendorPinMismatch unless
    both equal pin = (blob, sha256)."""
    blob, sha = hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest(), hashlib.sha256(data).hexdigest()
    if (blob, sha) != tuple(pin):
        raise VendorPinMismatch('vendored file does not match its pin: %s (git blob %s, sha256 %s)' % (path, blob, sha))
    return blob, sha


def load_module(name, path, pin=None):
    """Load one package module by path and register it under `name` (so later modules can import it).  The file is
    read once and exactly those bytes are compiled and executed (no import machinery, so no cached .pyc can stand in
    for them); with a pin the bytes are first checked by vendor_pin.  Returns (module, (git blob id, sha256) computed
    from the executed bytes, or None without a pin, bytes)."""
    with open(path, 'rb') as f:
        data = f.read()
    computed = vendor_pin(data, pin, path) if pin is not None else None
    mod = types.ModuleType(name)
    mod.__file__ = path
    sys.modules[name] = mod
    exec(compile(data, path, 'exec'), mod.__dict__)
    return mod, computed, data


def vendor_controls(loaded, common):
    """Negative controls of the pin check: each vendored file's bytes with one comment line appended (in memory)
    must raise VendorPinMismatch in vendor_pin."""
    out = []
    for rel in sorted(loaded):
        name = 'vendored %s with one comment line appended (in memory)' % rel
        common.attempt(name)
        try:
            vendor_pin(loaded[rel] + b'# tampered\n', VENDOR[rel][1:], rel)
        except VendorPinMismatch as e:
            out.append(dict(control=name, mutant=name, expected='VendorPinMismatch', rejected_by=type(e).__name__,
                            rejected=str(e)[:120]))
            continue
        raise common.AuditFail('negative control ACCEPTED: ' + name)
    return out


def canonical(obj):
    """JSON round trip (tuples -> lists, int keys -> strings) so that recomputed and committed results compare."""
    return json.loads(json.dumps(obj, sort_keys=True))


def compact(d):
    return json.dumps(d, sort_keys=True, separators=(',', ':'))


def control_counts(controls):
    """(negative controls rejected, distinct controls, distinct mutants, plumbing records) of the controls dict; the
    rejections are the recorded control records (a control is recorded only once its rejection has been checked)."""
    semantic = [(g, c) for g, recs in sorted(controls.items()) if g not in PLUMBING_GROUPS for c in recs]
    distinct = len(set((g, c['control']) for g, c in semantic))
    mutants = len(set(c['mutant'] for _, c in semantic))
    plumbing = sum(len(controls.get(g, [])) for g in PLUMBING_GROUPS)
    return len(semantic), distinct, mutants, plumbing


def run(args, log):
    """Load the modules, run the three scopes and compare with (or write) RESULT.json; returns the summary."""
    vendor, vendor_bytes = {}, {}
    for rel in sorted(VENDOR):
        name, blob, sha = VENDOR[rel]
        _, computed, vendor_bytes[rel] = load_module(name, os.path.join(HERE, *rel.split('/')), (blob, sha))
        vendor[rel] = dict(git_blob=computed[0], sha256=computed[1], bytes=len(vendor_bytes[rel]),
                           computed_from='the loaded bytes (vendor_pin)')
    mods = dict((name, load_module(name, os.path.join(HERE, name + '.py'))[0]) for name in LOCAL_MODULES)
    common = mods['audit_common']
    common.reset_controls()
    fetched = common.ensure_commits(args.repo, COMMITS, args.fetch, args.remote)
    if fetched:
        log('fetched PR heads %s from %s' % (fetched, args.remote))
    inp = common.PinnedInputs(args.repo, INPUTS)
    words, ctl_words = mods['check_words'].run(inp, log)
    fill, ctl_fill = mods['check_fill'].run(inp, log, words)
    acc, ctl_acc = mods['check_accounting'].run(inp, log, words)
    common.need(sorted(inp.used) == sorted(INPUTS), 'unused pinned inputs %r' % sorted(set(INPUTS) - set(inp.used)))
    ctl_vendor = dict(vendor_pins=vendor_controls(vendor_bytes, common))
    controls = {}
    for part in (ctl_words, ctl_fill, ctl_acc, ctl_vendor):
        common.need(not set(part) & set(controls), 'duplicate control groups %r' % sorted(set(part) & set(controls)))
        controls.update(part)
    n_neg, n_distinct, n_mutants, n_plumbing = control_counts(controls)
    n_attempted = len(common.ATTEMPTED)
    common.need(n_neg == n_attempted, 'negative controls: %d attempted, %d recorded as rejected' % (n_attempted, n_neg))
    positives = list(common.POSITIVES)
    common.need(sorted(positives) == sorted(POSITIVE_CONTROLS), 'positive controls executed %r != %r'
                % (positives, sorted(POSITIVE_CONTROLS)))
    replays = [words[tag]['pr2530'][k]['orientation'] for tag in ('base', 'extra') for k in ('replay_forward', 'replay_dual')]
    summary = dict(words_independent_inputs=words['base']['pr2530']['live'], local_profile=words['base']['pr2530']['profile'],
                   word_replay_orientations=replays,
                   roles=fill['fill']['roles'], idle=fill['fill']['idle'], physical=fill['physical']['physical'],
                   charts=fill['charts']['actual_73column_charts'], C=acc['endpoint']['C'],
                   kappa=acc['endpoint']['kappa'], kappa_terms=[acc['endpoint']['outer']['grid']['one_over_F'],
                                                                acc['endpoint']['outer']['B']],
                   negative_controls_attempted=n_attempted, negative_controls_rejected=n_neg,
                   distinct_controls=n_distinct, distinct_mutants=n_mutants,
                   negative_controls_by_group=dict((k, len(v)) for k, v in controls.items() if k not in PLUMBING_GROUPS),
                   plumbing_controls=dict((k, len(controls.get(k, []))) for k in PLUMBING_GROUPS),
                   plumbing_injections=sum(c['injections'] for k in PLUMBING_GROUPS for c in controls.get(k, [])),
                   positive_controls_executed=positives, positive_controls=len(positives), pinned_inputs=len(INPUTS),
                   counting=('negative_controls_attempted: negative controls run (audit_common.attempt); '
                             'negative_controls_rejected: recorded rejections, each by its named check (a word '
                             'mutation counts once per word); distinct_controls: distinct (group, control) pairs, i.e. '
                             '(mutant, check) pairs with the two words counted once; distinct_mutants: distinct '
                             'mutated objects; plumbing controls (checker non-vacuity) are outside these counts; '
                             'positive_controls: positive controls executed and passed (audit_common.positive)'))
    result = canonical(dict(schema=1, audit='independent audit of PR #2530 head ' + H2530, summary=summary,
                            commits=dict((str(k), v) for k, v in COMMITS.items()), vendor=vendor,
                            inputs=inp.used, words=words, fill=fill, accounting=acc, controls=controls,
                            positive_controls=[POSITIVE_CONTROLS[k] for k in positives],
                            positive_controls_note=POSITIVE_CONTROLS_NOTE,
                            scope_limits=SCOPE_LIMITS))
    path = os.path.join(HERE, RESULT_NAME)
    if args.out:
        with open(path, 'w') as f:
            json.dump(result, f, indent=1, sort_keys=True)
            f.write('\n')
        log('wrote ' + RESULT_NAME)
    else:
        common.need(os.path.exists(path), RESULT_NAME + ' missing; run with --out first')
        with open(path) as f:
            committed = json.load(f)
        diff = sorted(k for k in set(result) | set(committed) if result.get(k) != committed.get(k))
        common.need(not diff, 'recomputed result differs from committed %s in %r' % (RESULT_NAME, diff))
        log('recomputed result equals committed ' + RESULT_NAME)
    return summary


def main():
    ap = argparse.ArgumentParser(description='Independent audit of PR #2530 (see module docstring).')
    ap.add_argument('--repo', default=REPO_DEFAULT, help='git repository holding (or receiving) the pinned commits')
    ap.add_argument('--fetch', action='store_true',
                    help='fetch missing pinned commits from --remote into refs/audit/pr<N> of --repo (objects and '
                         'that ref only)')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true', help='write RESULT.json instead of comparing with it')
    args = ap.parse_args()
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    t0 = time.time()

    def log(msg):
        print('  [%5.1fs] %s' % (time.time() - t0, msg), flush=True)

    try:
        summary = run(args, log)
    except BaseException as exc:      # any failure, including SystemExit and KeyboardInterrupt, ends with one FAIL line
        audit_types = tuple(t for t in (getattr(sys.modules.get('audit_common'), 'AuditFail', None),
                                        getattr(sys.modules.get('words_check'), 'Reject', None),
                                        getattr(sys.modules.get('fill_check80'), 'CheckFailure', None),
                                        VendorPinMismatch) if t is not None)
        if not isinstance(exc, audit_types):
            traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print('  run time %.1fs' % (time.time() - t0))
        print('%s %s: %s' % (FAIL_LINE, type(exc).__name__, ' '.join(str(exc).split()) or repr(exc)), flush=True)
        return 1
    print('  run time %.1fs' % (time.time() - t0))
    short = dict(forward='fwd', dual='dual')
    orient = []
    for o in summary['word_replay_orientations']:
        if short.get(o, o) not in orient:
            orient.append(short.get(o, o))
    print('%s words=2x%d-inputs-%s profile=%s roles=%d idle=%s physical=%d charts=%d C=%s kappa=C-%s-%s '
          'negative_controls=%d/%d-rejected distinct_controls=%d positive_controls=%d pinned_inputs=%d'
          % (PASS_LINE, summary['words_independent_inputs'], '+'.join(orient), compact(summary['local_profile']),
             summary['roles'], compact(summary['idle']), summary['physical'], summary['charts'], summary['C'],
             summary['kappa_terms'][0], summary['kappa_terms'][1], summary['negative_controls_rejected'],
             summary['negative_controls_attempted'], summary['distinct_controls'], summary['positive_controls'],
             summary['pinned_inputs']), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
