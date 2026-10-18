#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent verification of open PR #3015 (Jeremy Kothe / jeremykothe2, head e244296d,
research/rank7-joint-endframes-restore-edit): one declared restore edit (R1) on PR #2979's words with PR #2979's
literal T74 allocation.  Single entry point.

PR #3015 replaces restore[178:180] of both PR #2979 words (22 -= 61; 22 -= 63 at one rank-8 frame) by three gates
(61 += 63 at the rank-7 subspace V45; 22 -= 61 at the rank-8 frame; 61 -= 63 at FULL), keeps every helper width, the
fill, order and dispatch, re-derives the cleanup, and claims the local profile {1:2443, 2:707, 3:232, 4:108, 5:18, 8:8}
(from {1:2445, 2:706, ...}), the complete profile {1:1644348, 2:470862, 3:159468, 4:71928, 5:13716, 8:5328, 48:28190},
physical stock 66813, and kappa = 0.001729150973534224428695 - 1e-46 - 1e-70 (+1.1699e-7 over PR #2979).

With code independent of both PRs (standard library only; the PRs' files are read as pinned git data and never
imported or executed) this package checks:
  A  audit_edit.py     the candidate words equal the parent words with exactly the declared hunk (own diff); the new
                       block equals the old one as a formal operator; a fresh monotone frame chain (second
                       implementation next to the vendored recount) attributes the paid delta -2H1+H2 exactly to
                       register 63's climbs 7->8->9 merging into 7->9; and a census of every adjacent same-target
                       restore pair rewritten in R1's way on the parent and on the edited words;
  B  audit_words.py    both edited words forward and dual exact through cleanup and the target endpoint (632
                       independent inputs, 36 initial corrections emulated), warp algebra, frame recount against
                       the word reports and the declared profile/inventory, the own tracker, the literal cleanup
                       against its own inverse-reverse re-derivation, the 91 private buffers;
  C  audit_fill.py     PR #2979's allocation (byte-identical in PR #3015) priced with the recounted local profiles
                       of the edited words in two implementations (271,728 roles, rules R-a..R-e, R-c recount):
                       the complete profile, PROFILE.json, CLAIM.json, the rank mass, the complete delta = 666 x
                       (-2H1+H2), unchanged idle remainders and the physical stock 66813;
  D  audit_kappa.py    the endpoint C accepted and C + 1e-24 rejected by an own rational enclosure and by the
                       vendored one of PR2804, kappa = C - 1e-46 - 1e-70, the exact gain over PR #2979's claim, the
                       improvement test, the root bracket, the census prices, and PR #3018's journal: applied to
                       PR #2979's fill it reproduces PR #3018's claimed profile and endpoint, and composed with R1
                       it gives the endpoint of the PR3015+PR3018 composition, computed here without having read
                       PR #3021 (published 19 minutes earlier) and equal to PR #3021's finite records;
     audit_controls.py the negative controls, each asserting the rule id that rejects it;
     vendor/           this contributor's earlier checkers (PR2315, PR2387, PR2804, PR2865), byte copies pinned by
                       git blob id and sha256, loaded by executing exactly the verified bytes (no .pyc can stand in).

Inputs (INPUTS) are read with `git -C <repo> show <commit>:<path>` and must match a pinned git blob id and sha256.
PR #2979 (merged) and PR2269's template are reachable from main; --fetch fetches the still-open PR #3015, PR #3018 and
PR #3021 heads into refs/audit/prN only (audit_common.ensure_commits).  GIT_CONFIG* variables are removed before the first
git call; every git subprocess drops the repository-redirecting GIT_* variables (audit_common.git_env).
The default run recomputes everything and requires the result to equal the committed RESULT.json; --out rewrites
it.  --fast runs the base provider only and the census on the parent word only (used by --mutations, which runs
every entry of MUTATIONS in a subprocess and requires each to fail).

Usage: python3 -I -B verify.py [--repo PATH] [--fetch] [--remote URL] [--out] [--fast] [--mutations [--jobs N]]
The final stdout line is PASS_T74_3015_RESTORE_EDIT_AUDIT ... or, for any exception, one line
`FAIL_T74_3015_RESTORE_EDIT_AUDIT <exception type>: <message>` with exit code 1.  Refuses python -O.
Sagar Thakrar (thakrarsagar), prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
import types
from fractions import Fraction as Q

PASS_LINE = 'PASS_T74_3015_RESTORE_EDIT_AUDIT'
FAIL_LINE = 'FAIL_T74_3015_RESTORE_EDIT_AUDIT'
if not __debug__:
    sys.stdout.write(FAIL_LINE + ' UsageError: refusing to run under python -O\n')
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
RESULT_NAME = 'RESULT.json'

# This contributor's earlier code, byte copies: rel path -> (module name, git blob id, sha256).  Loaded in this
# (sorted) order, so that each module's imports are registered.
VENDOR = {
    'vendor/pr2315/words_check.py': ('words_check', '0b646b9d5583c75a78e0c2dd7e9cfffa02055058',
                                     'b66414a39f5ac7b9cd32284027e13a550734901aca5f4457085a034689bc3ce6'),
    'vendor/pr2387/fill_check80.py': ('fill_check80', '557e0732bfe4c030436a11f5433143c10fa07821',
                                      '1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06'),
    'vendor/pr2804/audit_common.py': ('audit_common', '17c4064f01b110012b54c05e64bdee8ae498e0b2',
                                      '7ced740252ac8d8a8c66ef3cc825008e0aacf080494d0e983fb322d7dcddbf42'),
    'vendor/pr2804/check_accounting.py': ('check_accounting', 'e749057dd838b715d0630de618f32d66a38da931',
                                          'fb6aef50da586f15cd60762edc074c20e300d65f1378a80160b3d4b840762548'),
    'vendor/pr2804/check_fill.py': ('check_fill', '85d1f807c62e4ac3b5f5ec7a809333ca05d5a951',
                                    '6abf2a574de50c71b46b502d322deab841cbaa0080e326262f346a96992878fb'),
    'vendor/pr2804/check_words.py': ('check_words', '451dbb82f147ef446a1819b1ed595b4bf5547583',
                                     '5996e804fa006906abff63a982c272588a44c35dfc932fdf687ef98dd3e0905f'),
    'vendor/pr2865/audit_lib.py': ('audit_lib', 'e8e847cc89dae6bb4e90e2c3dbebc30f615b698f',
                                   'e0cf84dd959d39e3f299c1e171753c29465fd5b4457561f4ab9ec0675d8e9dc1'),
}
LOCAL_MODULES = ('audit_edit', 'audit_words', 'audit_fill', 'audit_kappa', 'audit_controls')

H3015 = 'e244296debb45fe6f4da84d29e4d64fbab55fda0'   # PR #3015 head (object under audit)
H2979 = 'be191346391661f4d35fc0d1508d0a6029572576'   # PR #2979 head (merged; parent words and allocation)
H3018 = 'ca7113157d7c959fdfa9d7cd17ef92d3877070d0'   # PR #3018 head (journal; scope D composition)
H2269 = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'   # PR #2269 (merged; T74 template and T37 inputs template)
H3021 = '217edac2ebfa6250536bd6df153de14901a69395'   # PR #3021 head (the published PR3015+PR3018 composition)
COMMITS = {3015: H3015, 2979: H2979, 3018: H3018, 2269: H2269, 3021: H3021}
P15 = 'research/rank7-joint-endframes-restore-edit/'
P79 = 'research/rank7-joint-endframes/'
P18 = 'research/rank7-integrality-exchange/'
P21 = 'research/rank7-restore-packing-composition/'
WB = ('d9aa96a93fea5f7395e7783aef0bc117c0a0ae89', 'abaf67bfcb257528658c906b612f57025617592bd7889828f92b97a5f4f4300d')
WE = ('74f6cb64595c21f7726ae77e69437868620bdcee', 'e0eaf64c4d5d324693d43889bce1b9e53e8da00402105c8c978fd102f208bed7')
# key: (PR, commit, path, git blob id, sha256)
INPUTS = {
    'edits3015': (3015, H3015, P15 + 'edits/EDITS.json', '90894fc6592951eaa3b4e25467d3a85c36b2d988',
                  'c9c68660d07bfd12ed20fd8cbfe3d36301ceb2d7bb9b4ea11350cc399b19e0b1'),
    'w3015_base': (3015, H3015, P15 + 'edits/FINAL-WORD-base.json.gz', '4f0483657396a7f735873e1b252482c53dfb2eb6',
                   '77d9be7ac47347894e034d8b67bf07ff8a5e1c317923ed5dd9257c492187dcf5'),
    'w3015_extra': (3015, H3015, P15 + 'edits/FINAL-WORD-extra.json.gz', '81f95e21ede115e8bdb6bd522c641b37b740bdf7',
                    '18d9c448ce892aa19f162e214760d0bd4ecb09f814b9b859dbf11f3ca637e9ea'),
    'claim3015': (3015, H3015, P15 + 'CLAIM.json', '70813f559e2878f0c5403c0b859eefe602f70abc',
                  'f9b9fbaaac794c0ce279c238a33a2f34f8c91a34d97ccdeb5ec98b7b8ba56d73'),
    'profile3015': (3015, H3015, P15 + 'allocation/PROFILE.json', '05766f448600d2f94699f42818aa8150f49fd934',
                    '5626c44edd6d5b209cd4e2d2a824e07bfba696e0856f3964b81fcb01c78eaad8'),
    'pw3015_base': (3015, H3015, P15 + 'data/WORD-base.json.gz') + WB,
    'pw3015_extra': (3015, H3015, P15 + 'data/WORD-extra.json.gz') + WE,
    'w2979_base': (2979, H2979, P79 + 'data/WORD-base.json.gz') + WB,
    'w2979_extra': (2979, H2979, P79 + 'data/WORD-extra.json.gz') + WE,
    'fill2979': (2979, H2979, P79 + 'allocation/FILL.json.gz', '8d4fd644d60ba2c98106dc770803b647afdf0963',
                 'c2136be9434cda511a1a8a44d98f9f72ea5376830a8426674253b4ee351c4c39'),
    'order2979': (2979, H2979, P79 + 'allocation/ORDER.json', '7409c4df1092241729739596c7648bda504e6aad',
                  '519d1d5dbb997a219fcfcad34c0b03e7838bef24199784d7e964fa10090f66e1'),
    'dispatch2979': (2979, H2979, P79 + 'allocation/DISPATCH.json', '9544fee4e6ee1f202cee22bfaeaf229ee3b2515e',
                     '65e435bd68e97243c003677271b88485a29d4d0fae2dff1354100404a145e74c'),
    'profile2979': (2979, H2979, P79 + 'allocation/PROFILE.json', '46a83eeda67ab67cccbffe8b7ad8e44368b40ea7',
                    '94a819747f3ced41f1544ada0036c983fc0c92847b9644380f877a06cd7931cf'),
    'claim2979': (2979, H2979, P79 + 'CLAIM.json', '8ec2ce4e440c0b584ee982c551e526a011c9324c',
                  '436e0d297cbdf195445d3697d496ac675e95210b79e70ce602a6a6667a4c6ce9'),
    'template2979': (2979, H2979, P79 + 'allocation/vendor/TEMPLATE.json.gz', '114808c32b1799da53524bdc25cea67efb60009e',
                     '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'),
    'tpl2269': (2269, H2269, 'research/gmx-t74-borrow43/GLOBAL-TEMPLATE.json.gz',
                '5327fc2f4e8ea82ed356c94ff040d23fc73c731f',
                '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db'),
    't37_2269': (2269, H2269, 'research/gmx-t74-borrow43/inputs/GLOBAL-TEMPLATE.json.gz',
                 '114808c32b1799da53524bdc25cea67efb60009e',
                 '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'),
    'exchange3018': (3018, H3018, P18 + 'EXCHANGE.json', '1260c8d95f573a574e007038263adf883b5ecbd2',
                     '8a103f643ad12d8074972f41e4359d9487eb8b96fc6849e1a178adb61b36578b'),
    'result3018': (3018, H3018, P18 + 'RESULT.json', 'b5b527781e2c1e03e11648727d930ab7cb5f8fa8',
                   'a9191f711b50476312c222a47f33d7b72a4ac26fdd190ec58b38889986f39b24'),
    'claim3021': (3021, H3021, P21 + 'evidence/OUTER-CLAIM.json', 'a8d657563624b98d8bb238878a6c20fa74a1f593',
                  '8beb062c36169728a8f82a5eda6638c2a83125f16e7e5de56f3a13d9cba5e1f5'),
    'finite3021': (3021, H3021, P21 + 'evidence/FINITE.json', '6f73992ff764a3d527d4fd551057dc6fa254127e',
                   'f7f6aca1e2596d7049ff2bc69c523013324f568f86fd31b1f29899b96b2617eb'),
    'composition3021': (3021, H3021, P21 + 'evidence/COMPOSITION-RESULT.json', '399bcc26f0684cced978e3a4c90f834551f62dd7',
                        'cdc4874dcb17714fbe10f003a4a4516b80a9ddccfc7199278a53baa13c5d3a04'),
}
PROVIDER_KEY = dict(base='gauge44', extra='extra')
EXPECT_COUNTS = dict(live=632, helpers=408, buffers=91, warps=72, corrections=36)
R1_DELTA = {1: -2, 2: 1}
R1_REGISTER = 63
GIT_ENV_POLICY = ('GIT_CONFIG* removed from the process environment before the first git call; every git subprocess '
                  'runs without the repository-redirecting GIT_* variables and with GIT_NO_REPLACE_OBJECTS=1 and '
                  'GIT_NO_LAZY_FETCH=1; the only write is --fetch into refs/audit/prN (audit_common)')
SCOPE_LIMITS = [
    'PR3015\'s exhaustive search over all 2-4-gate restore-phase blocks (its Stack2979 harness) is not reproduced; '
    'the census here covers one class (adjacent same-target pairs rewritten in R1\'s way with the three frames chosen '
    'as described) on both words.',
    'The frames of the three new gates are checked for legality and priced as given; whether a different frame '
    'assignment of the whole word gives a lower paid profile (a frame re-solve) is not decided here.',
    'The native chains, the bootstrap, the complete admission and the outer release of PR3015 (author-run, '
    'evidence/ in its package) are not rerun; kappa is checked as arithmetic on the complete profile under the '
    'inherited moment model (M(b) = sum n_r r (73/r)^b / (73 W)), with the inherited 24-digit grid and the '
    '-1e-46-1e-70 margins.',
    'The fixed-inventory fractional cap certificate (RELAX-CAP.json) is not re-derived.',
    'PR3018\'s journal is applied and priced; its sign proof, its own geometry checker and its physical legality '
    'claims beyond rules R-a..R-e are not re-derived.  The composed endpoint was computed here (about 18:40 UTC) without '
    'having read PR3021, which published the same composition at 2026-10-16 18:21 UTC and has priority; it is checked '
    'against PR3021\'s finite records; PR3021\'s fresh native/admission/outer release is author-run and not rerun here.',
    'The window semantics and the free interleaving of independent replica controllers are inherited modelling '
    'assumptions (as in PR2804/PR2865).',
]
POSITIVE_CONTROLS = {
    'pr2979_words_base': 'PR2979 base word through the word pipeline with its CLAIM local profile',
    'pr2979_words_extra': 'PR2979 extra word through the word pipeline with its CLAIM local profile',
    'pr2979_complete_profile': 'PR2979 fill with the parent recounts gives PR2979\'s PROFILE.json and CLAIM profile',
    'pr2979_endpoint': 'PR2979\'s C accepted and C + 1e-24 rejected on its profile (own and vendored enclosures)',
    'pr3018_journal_profile': 'PR3018\'s journal on PR2979\'s fill gives PR3018\'s RESULT profile (two implementations)',
    'pr3018_endpoint': 'the 24-digit endpoint predicted from the journaled profile is the grid point below PR3018\'s new_root bracket (bracket in [C, C + 1e-24))',
    'pr3021_composition': 'the composed profile, endpoint, kappa and gain computed here equal PR3021\'s published FINITE/OUTER-CLAIM/COMPOSITION records',
    'r1_census_pair_found': 'the census on the parent word finds the R1 pair with the delta -2H1+H2 (both carriers)',
}
PLUMBING_GROUPS = ('vendor_pins',)
# Textual mutations of the local checkers (module, old, new); each must make the audit fail (--mutations).
MUTATIONS = [
    ('audit_edit', "need(inside(cur[r], F), 'chain.monotone:", "need(True or inside(cur[r], F), 'chain.monotone:"),
    ('audit_edit', "need(states[0] == states[1], 'edit.net_operator", "need(True or states[0] == states[1], 'edit.net_operator"),
    ('audit_edit', "need(a <= p and len(po) - s <= b,", "need(True or (a <= p and len(po) - s <= b),"),
    ('audit_edit', "need(set(diff) <= set(ALLOWED_DIFF),", "need(True or set(diff) <= set(ALLOWED_DIFF),"),
    ('audit_edit', "need(changed == sorted(expected_regs),", "need(True or changed == sorted(expected_regs),"),
    ('audit_edit', "need(delta == dict(expected_delta),", "need(True or delta == dict(expected_delta),"),
    ('audit_edit', "need(chain['paid'] == dict(fr['paid']) and", "need(True or chain['paid'] == dict(fr['paid']) and"),
    ('audit_words', "    dual = AL.replay(P, True)\n", "    dual = dict(fwd, orientation='dual')\n"),
    ('audit_words', "    need([g[:-1] for g in mine] == [g[:-1] for g in w['cleanup']],", "    need(True or [g[:-1] for g in mine] == [g[:-1] for g in w['cleanup']],"),
    ('audit_words', "    need(fr['paid'] == prof and fr['inventory'] == inv,", "    need(fr['paid'] == prof or fr['inventory'] == inv,"),
    ('audit_words', "    need(got == dict(expect), 'words.counts", "    need(True or got == dict(expect), 'words.counts"),
    ('audit_words', "    need(check['final_identity'] and check['buffers_zero_after'],", "    need(True or check['final_identity'] and check['buffers_zero_after'],"),
    ('audit_fill', "    need(prof == AL.intkeys(claimed), '%s: complete profile", "    need(True or prof == AL.intkeys(claimed), '%s: complete profile"),
    ('audit_fill', "    need(delta == want, 'fill.delta", "    need(True or delta == want, 'fill.delta"),
    ('audit_fill', "    need(own_new['idle'] == own_old['idle'], 'fill.idle", "    need(True or own_new['idle'] == own_old['idle'], 'fill.idle"),
    ('audit_fill', "        need(rows[idx] == old, 'journal.preimage", "        need(True or rows[idx] == old, 'journal.preimage"),
    ('audit_fill', "    need(fc['idle'] == AL.hist(own['idle']) and fc['profile'] == AL.hist(own['profile'])", "    need(fc['idle'] == AL.hist(own['idle']) or fc['profile'] == AL.hist(own['profile'])"),
    ('audit_kappa', "def accepts(enc):\n    return enc[1] < 1", "def accepts(enc):\n    return enc[0] < 1"),
    ('audit_kappa', "def rejects(enc):\n    return enc[0] > 1", "def rejects(enc):\n    return enc[1] > 1"),
    ('audit_kappa', "    need(kappa == C - KAPPA_TERMS[0] - KAPPA_TERMS[1],", "    need(kappa <= C - KAPPA_TERMS[0] - KAPPA_TERMS[1],"),
    ('audit_kappa', "    need(gain > 0 and gain == claimed_gain,", "    need(gain > 0 or gain == claimed_gain,"),
    ('audit_kappa', "    need(max(own[0], ven[0]) <= min(own[1], ven[1]),", "    need(True or max(own[0], ven[0]) <= min(own[1], ven[1]),"),
    ('audit_kappa', "    l2 = atanh_iv(Q(1, 3))\n", "    l2 = atanh_iv(Q(1, 3) + Q(1, 10 ** 9))\n"),
]

GIT_SCRUB = dict(done=False)
AUDIT_EXCEPTIONS = ('AuditFail', 'Reject', 'CheckFailure', 'VendorPinMismatch')


def scrub_git_env(environ):
    names = sorted(k for k in environ if k.startswith('GIT_CONFIG'))
    for k in names:
        del environ[k]
    return names


def git_env_selftest():
    env = dict(GIT_CONFIG_GLOBAL='/x', GIT_CONFIG_SYSTEM='/y', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG='/z',
               GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='k', GIT_CONFIG_VALUE_0='v', GIT_CONFIG_PARAMETERS="'a.b=c'",
               HOME='/h', GIT_NO_REPLACE_OBJECTS='1', PATH='/p')
    removed = scrub_git_env(env)
    ok = sorted(env) == ['GIT_NO_REPLACE_OBJECTS', 'HOME', 'PATH'] and len(removed) == 8
    if not ok:
        raise RuntimeError('git environment self-test failed: kept %r' % sorted(env))
    return dict(removed_in_selftest=removed, kept_in_selftest=sorted(env))


class VendorPinMismatch(Exception):
    """A vendored file does not match its pinned git blob id and sha256."""


def vendor_pin(data, pin, path):
    blob, sha = hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest(), hashlib.sha256(data).hexdigest()
    if (blob, sha) != tuple(pin):
        raise VendorPinMismatch('vendored file does not match its pin: %s (git blob %s, sha256 %s)' % (path, blob, sha))
    return blob, sha


def load_module(name, path, pin=None, mutation=None):
    """Read the file once, check the pin (if any) on those bytes, apply the mutation (local modules under
    --mutations only) and execute exactly those bytes as module `name` (registered in sys.modules)."""
    with open(path, 'rb') as f:
        data = f.read()
    computed = vendor_pin(data, pin, path) if pin is not None else None
    if mutation is not None and mutation[0] == name:
        text = data.decode('utf-8')
        if text.count(mutation[1]) != 1:
            raise RuntimeError('mutation target not unique in %s: %r' % (name, mutation[1]))
        data = text.replace(mutation[1], mutation[2]).encode('utf-8')
    mod = types.ModuleType(name)
    mod.__file__ = path
    sys.modules[name] = mod
    exec(compile(data, path, 'exec'), mod.__dict__)
    return mod, computed, data


def vendor_controls(loaded, common):
    out = []
    for rel in sorted(loaded):
        name = 'vendored %s with one comment line appended (in memory)' % rel
        common.attempt(name)
        try:
            vendor_pin(loaded[rel] + b'# tampered\n', VENDOR[rel][1:], rel)
        except VendorPinMismatch as e:
            out.append(dict(control=name, expected='VendorPinMismatch', rejected_by=type(e).__name__,
                            message=str(e)[:120]))
            continue
        raise common.AuditFail('negative control ACCEPTED: ' + name)
    return out


def canonical(obj):
    return json.loads(json.dumps(obj, sort_keys=True, default=str))


def compact(d):
    return json.dumps(d, sort_keys=True, separators=(',', ':'), default=str)


def strip_tag(name):
    return name.split('] ', 1)[1] if name.startswith('[') else name


def run(args, log, mutation=None):
    vendor, vendor_bytes = {}, {}
    for rel in sorted(VENDOR):
        name, blob, sha = VENDOR[rel]
        _, computed, vendor_bytes[rel] = load_module(name, os.path.join(HERE, *rel.split('/')), (blob, sha))
        vendor[rel] = dict(git_blob=computed[0], sha256=computed[1], bytes=len(vendor_bytes[rel]),
                           computed_from='the loaded bytes (vendor_pin)')
    mods = dict((name, load_module(name, os.path.join(HERE, name + '.py'), mutation=mutation)[0])
                for name in LOCAL_MODULES)
    AC, AL, CA, CW = (sys.modules[k] for k in ('audit_common', 'audit_lib', 'check_accounting', 'check_words'))
    AE, AW, AF, AK, CT = (mods[k] for k in LOCAL_MODULES)
    AC.reset_controls()
    AL.RAN.clear()
    harness = AL.harness_selftest()
    git_selftest = git_env_selftest()
    AL.need(GIT_SCRUB['done'] and not any(k.startswith('GIT_CONFIG') for k in os.environ),
            'git_env: GIT_CONFIG* variables were not removed before the first git call')
    fetched = AC.ensure_commits(args.repo, COMMITS, args.fetch, args.remote)
    if fetched:
        log('fetched PR heads %s from %s' % (fetched, args.remote))
    inp = AC.PinnedInputs(args.repo, INPUTS)
    groups = dict((g, []) for g in ('edit', 'words', 'fill_rules', 'pricing', 'kappa', 'journal'))
    tags = ('base',) if args.fast else ('base', 'extra')
    edits, claim15, claim79 = inp.json('edits3015'), inp.json('claim3015'), inp.json('claim2979')
    declared = edits['declared']
    declared79 = dict(local_profile=claim79['local_profile'], width_inventory=claim79['width_inventory'])
    AL.need(declared['local_profile'] == claim15['local_profile'] and declared['width_inventory'] == claim15['width_inventory'],
            'claims.declared: EDITS.json declared profile/inventory != CLAIM.json')
    AL.need(edits['edits']['base'] == edits['edits']['extra'] and len(edits['edits']['base']) == 1
            and edits['edits']['base'][0]['id'] == 'R1', 'claims.edits: one edit R1, identical for both providers')
    AL.ran('wiring.edits_equal')
    # recorded facts, not checks: the pins table binds these inputs to the same blob ids, so PinnedInputs would fail first
    facts = dict(pr3015_parent_words_equal_pr2979=all(inp.raw('pw3015_' + t) == inp.raw('w2979_' + t) for t in ('base', 'extra')),
                 pr2979_template_equals_t37_inputs_template=inp.raw('template2979') == inp.raw('t37_2269'))
    edit = edits['edits']['base'][0]
    W = {}
    words_p, words_c, rec_p, rec_c, scope_a, scope_b, census = {}, {}, {}, {}, {}, {}, {}
    for tag in ('base', 'extra'):
        pid = PROVIDER_KEY[tag]
        wp, wc = inp.json('w2979_' + tag), inp.json('w3015_' + tag)
        words_p[pid], words_c[pid] = wp, wc
        if tag not in tags:
            # --fast: the extra provider's words are only recounted (the fill needs both providers' widths and profiles)
            rec_p[pid] = CW.frame_recount(AL.parse_word(wp))
            rec_c[pid] = CW.frame_recount(AL.parse_word(wc))
            continue
        d = AE.own_diff(wp, wc, edit)
        net = AE.net_operator(edit['old'], edit['new'])
        v45 = AE.v45_identity(edit['new'][0][-1])
        recp, Pp, frp = AW.word_pipeline(wp, declared79, EXPECT_COUNTS)
        AC.positive('pr2979_words_' + tag)
        recc, Pc, frc = AW.word_pipeline(wc, declared, EXPECT_COUNTS)
        chp, chc = AE.own_chain(Pp), AE.own_chain(Pc)
        ti = dict(parent=AE.two_impl(chp, frp), candidate=AE.two_impl(chc, frc))
        att = AE.attribution(chp, chc, R1_DELTA, [R1_REGISTER])
        rec_p[pid], rec_c[pid] = frp, frc
        scope_a[tag] = dict(diff=d, net_operator=net, first_new_frame=v45, two_implementations=ti, attribution=att)
        scope_b[tag] = dict(parent=recp, candidate=recc)
        W[tag] = dict(wp=wp, wc=wc, Pp=Pp, Pc=Pc, frp=frp, frc=frc, chp=chp, chc=chc)
        log('A/B [%s] hunk restore[%d:%d) -> %d gates, net operator equal; parent and candidate words exact forward+dual '
            '(%d inputs); profiles %s -> %s; delta %s attributed to register(s) %s'
            % (tag, d['declared']['start'], d['declared']['stop'], d['declared']['new_gates'], recc['independent_inputs'],
               compact(recp['profile']), compact(recc['profile']), compact(att['paid_delta']), att['dimensions_changed']))
        # census on the parent word (R1 must be found) and, unless --fast, on the edited word
        recs_p, summ_p = AE.r1_class_census(wp, Pp, chp, frp['paid'])
        r1 = [r for r in recs_p if r['index'] == edit['start'] and r['legal']]
        AL.need(len(r1) == 2 and all(AL.canon(R1_DELTA) in r['option_deltas'] for r in r1),
                'census.r1: the R1 pair at restore[%d] is not found with the delta %r in both carrier orders' % (edit['start'], R1_DELTA))
        AC.positive('r1_census_pair_found') if tag == 'base' else None
        c = dict(parent=dict(summary=summ_p, nonzero=[r for r in recs_p if r['legal'] and r['nonzero_options']]))
        if not args.fast:
            recs_c, summ_c = AE.r1_class_census(wc, Pc, chc, frc['paid'])
            c['candidate'] = dict(summary=summ_c, nonzero=[r for r in recs_c if r['legal'] and r['nonzero_options']])
        census[tag] = c
        log('A [%s] R1-class census: parent %s; candidate %s' % (tag, compact(summ_p), compact(c.get('candidate', {}).get('summary', 'skipped (--fast)'))))
    if not args.fast:
        AL.need(scope_b['base']['candidate']['profile'] == scope_b['extra']['candidate']['profile']
                and census['base']['parent']['summary'] == census['extra']['parent']['summary'],
                'wiring.providers: the two providers give different profiles or census summaries')
        AL.ran('wiring.providers_agree')
    # C: the allocation
    tpl, t37 = inp.json('tpl2269'), inp.json('t37_2269')
    order = [tuple(x) for x in inp.json('order2979')]
    dispatch_list = inp.json('dispatch2979')
    disp = AF.dispatch_map(dispatch_list, order)
    sc = AF.schedule(tpl, t37, order)
    fill_raw = inp.raw('fill2979')
    fill = inp.json('fill2979')
    AL.need(AF.fill_sha256(fill_raw) == claim15['fill_sha256'] == claim79['fill_sha256'],
            'fill.sha256: CLAIM fill_sha256 of PR3015 and PR2979 != PR2979 allocation/FILL.json.gz')
    AL.ran('fill.sha256_bound')
    profile79, profile15 = inp.json('profile2979'), inp.json('profile3015')
    pp = AF.price(fill, order, disp, words_p, rec_p, sc)
    AF.check_profile(pp['own']['profile'], profile79, 'fill.profile_file')
    AF.check_profile(pp['own']['profile'], claim79['profile'], 'fill.profile_claim')
    AC.positive('pr2979_complete_profile')
    pc = AF.price(fill, order, disp, words_c, rec_c, sc, keep_drows=True)
    AF.check_profile(pc['own']['profile'], profile15, 'fill.profile_file')
    AF.check_profile(pc['own']['profile'], claim15['profile'], 'fill.profile_claim')
    mass = AF.check_mass(pc['own']['profile'])
    delta = AF.check_delta(pc['own']['profile'], pp['own']['profile'], R1_DELTA)
    AF.check_idle(pc['own'], pp['own'])
    phys = AF.physical(pc['helpers'], pc['buffers'], claim15)
    pricing = dict(schedule=sc['info'], pr2979=AF.summary(pp), pr3015=AF.summary(pc), rank_mass=mass,
                   complete_delta_vs_pr2979=AL.hist(delta), idle_identical_to_pr2979=True, physical=phys,
                   dispatch=dict((p, sum(1 for v in disp.values() if v == p)) for p in sorted(set(disp.values()))))
    log('C complete profile %s (two implementations, %d roles) = PROFILE.json = CLAIM; delta vs PR2979 %s; idle '
        'identical; physical %d' % (compact(pricing['pr3015']['profile']), pricing['pr3015']['roles'],
                                    compact(pricing['complete_delta_vs_pr2979']), phys['physical']))
    # D: endpoint and kappa
    prof_c, prof_p = pc['own']['profile'], pp['own']['profile']
    C15, C79 = Q(claim15['complex_lower']), Q(claim79['complex_lower'])
    k15, k79 = Q(claim15['kappa']), Q(claim79['kappa'])
    AK.endpoint_format(C15)
    AK.endpoint_format(C79)
    enc_own = AK.endpoint_check(prof_c, C15)
    enc_ven = AK.endpoint_check(prof_c, C15, mom=CA.moment)
    ti_k = dict(at_C=AK.two_impl(prof_c, C15, CA.moment), at_C_plus=AK.two_impl(prof_c, C15 + AK.E24, CA.moment))
    AK.kappa_check(k15, C15)
    gain = AK.gain_check(k15, k79, Q(claim15['previous_claims']['pr2979']['gain']))
    AK.improvement(prof_p, prof_c, C15, C79)
    lo_a, hi_a, S = AK.straddle(prof_c, C15)
    AL.need(C15 <= lo_a < S < hi_a < C15 + AK.E24, 'kappa.root_bracket: bracket outside (C, C + 1e-24)')
    lo_v, hi_v, S_v = AK.straddle(prof_c, C15, mom=CA.moment)
    AL.need(lo_a <= S_v <= hi_a, 'kappa.root_bracket: the vendored straddle point is outside the own bracket')
    Cpred, kpred = AK.predict_endpoint(prof_c, C79)
    AL.need(Cpred == C15 and kpred == k15, 'kappa.predict: the endpoint predicted from the profile != CLAIM')
    AK.endpoint_check(prof_p, C79)
    AK.endpoint_check(prof_p, C79, mom=CA.moment)
    AK.kappa_check(k79, C79)
    AC.positive('pr2979_endpoint')
    # census prices at the root
    prices = {}
    for tag in census:
        for which in census[tag]:
            for r in census[tag][which]['nonzero']:
                verdicts = {}
                for o in r['nonzero_options']:
                    dlt = AL.intkeys(o['delta'])
                    lo, hi = AK.price_delta(dlt, C15)
                    AL.need(hi < 0 or lo > 0, 'census.price: undecided sign for %r' % dlt)
                    prices.setdefault(AL.canon(dlt), ['%.4e' % float(lo), '%.4e' % float(hi), bool(hi < 0)])
                    verdicts[AL.canon(dlt)] = bool(hi < 0)
                r['option_verdicts'] = verdicts
                r['improves'] = any(verdicts.values())            # some legal third frame improves
                r['loses_only'] = bool(verdicts) and not r['improves']
    improving = dict((tag, dict((which, [[r['index'], r['carrier'], r['absorbed']] for r in census[tag][which]['nonzero']
                                          if r['improves']]) for which in census[tag])) for tag in census)
    losing = dict((tag, dict((which, sum(1 for r in census[tag][which]['nonzero'] if r['loses_only']))
                             for which in census[tag])) for tag in census)
    for tag in census:
        AL.need(sorted(x[0] for x in improving[tag]['parent']) == [edit['start'], edit['start']],
                'census.unique: improving R1-class rewrites on the parent word %r are not exactly the R1 pair' % improving[tag]['parent'])
        if 'candidate' in improving[tag]:
            AL.need(improving[tag]['candidate'] == [], 'census.exhausted: an R1-class rewrite still improves the edited word: %r'
                    % improving[tag]['candidate'])
    kappa = dict(C=AK.dec(C15, 24), C_pr2979=AK.dec(C79, 24), endpoint_own=enc_own, endpoint_vendored=enc_ven,
                 two_implementations=ti_k, kappa=str(k15), kappa_decimal_70=AK.dec(k15, 70),
                 gain_over_pr2979=gain,
                 passed=['kappa.endpoint_format', 'kappa.endpoint_accept', 'kappa.endpoint_reject', 'kappa.two_impl',
                         'kappa.kappa', 'kappa.gain', 'kappa.improvement', 'kappa.root_bracket', 'kappa.predict'],
                 root_bracket=dict(lower=AK.dec(lo_a, 45), upper=AK.dec(hi_a, 45), width='%.2e' % float(hi_a - lo_a)),
                 root_bracket_vendored=dict(lower=AK.dec(lo_v, 60), upper=AK.dec(hi_v, 60), width='%.2e' % float(hi_v - lo_v)),
                 endpoint_predicted_from_profile=AK.dec(Cpred, 24),
                 census_prices_per_call_delta=prices, census_improving=improving, census_losing_only=losing)
    log('D C=%s accepted, C+1e-24 rejected (own and vendored enclosures agree); kappa = C-1e-46-1e-70; gain over PR2979 '
        '%s exact; PR2979 profile rejected at C; root in [%s, %s]' % (kappa['C'], gain['gain_float'],
                                                                      kappa['root_bracket']['lower'][:30],
                                                                      kappa['root_bracket']['upper'][:30]))
    # E: PR3018's journal and the composition
    ex, res18 = inp.json('exchange3018'), inp.json('result3018')
    AL.need(ex['source_pr'] == 2979 and ex['source_head'] == H2979, 'journal.source: EXCHANGE.json source != PR2979 head')
    fj, jrec = AF.apply_journal(fill, ex['edits'])
    pj = AF.price(fj, order, disp, words_p, rec_p, sc)
    AF.check_profile(pj['own']['profile'], res18['profile'], 'journal.profile')
    AL.need(AL.intkeys(res18['delta']) == AL.counter_delta(pj['own']['profile'], prof_p), 'journal.delta: RESULT delta')
    AC.positive('pr3018_journal_profile')
    C18, k18 = AK.predict_endpoint(pj['own']['profile'], C79)
    nr_lo, nr_hi = Q(res18['new_root'][0]), Q(res18['new_root'][1])
    AL.need(C18 <= nr_hi and C18 + AK.E24 > nr_lo, 'journal.root: predicted endpoint %s outside PR3018 new_root bracket' % C18)
    AC.positive('pr3018_endpoint')
    pjc = AF.price(fj, order, disp, words_c, rec_c, sc)
    AF.check_delta(pjc['own']['profile'], pj['own']['profile'], R1_DELTA)
    AF.check_mass(pjc['own']['profile'])
    Cc, kc = AK.predict_endpoint(pjc['own']['profile'], C15)
    AL.need(Cc > C15 and Cc > C18, 'journal.composed: the composed endpoint is not above both parts')
    # PR3021 (petalas) published this composition at 18:21 UTC: its finite records must equal the computation here
    cl21, fin21, comp21 = inp.json('claim3021'), inp.json('finite3021'), inp.json('composition3021')
    AF.check_profile(pjc['own']['profile'], fin21['profile'], 'composition.profile')
    AL.need(AL.intkeys(fin21['idle']) == dict(pjc['own']['idle']) and fin21['physical'] == phys['physical']
            and fin21['roles'] == pjc['own']['roles'], 'composition.finite: PR3021 idle/physical/roles differ')
    nr21_lo, nr21_hi = Q(fin21['new_root'][0]), Q(fin21['new_root'][1])
    AL.need(Cc <= nr21_hi and Cc + AK.E24 > nr21_lo, 'composition.root: composed endpoint outside PR3021 new_root bracket')
    AL.need(kc == Q(cl21['kappa_rational']) == Q(comp21['kappa']) and AK.dec(kc, 70) == cl21['kappa'],
            'composition.kappa: composed kappa %s != PR3021 %s' % (kc, cl21['kappa_rational']))
    AL.need(kc - k15 == Q(comp21['gain']) and Q(comp21['comparison_kappa']) == k15,
            'composition.gain: PR3021 gain over PR3015 differs')
    AC.positive('pr3021_composition')
    journal = dict(journal=jrec, pr3018_profile=AL.hist(pj['own']['profile']), pr3018_delta_vs_pr2979=AL.hist(AL.intkeys(res18['delta'])),
                   pr3018_endpoint_predicted=AK.dec(C18, 24), pr3018_new_root_bracket=[AK.dec(nr_lo, 25), AK.dec(nr_hi, 25)],
                   pr3018_kappa_predicted=AK.dec(k18, 70),
                   composed_profile=AL.hist(pjc['own']['profile']), composed_endpoint_predicted=AK.dec(Cc, 24),
                   composed_kappa_predicted=AK.dec(kc, 70),
                   composed_gain_over_pr3015='%.4e' % float(kc - k15), composed_gain_over_pr3018='%.4e' % float(kc - k18),
                   pr3021=dict(head=H3021, profile_equal=True, idle_physical_roles_equal=True, kappa=cl21['kappa'],
                               gain_over_pr3015=comp21['gain'], new_root=[AK.dec(nr21_lo, 25), AK.dec(nr21_hi, 25)]),
                   status='The composition of PR3015\'s words with PR3018\'s journal was computed here as a prediction (about '
                          '2026-10-16 18:40 UTC, before this package had read PR3021, which was published at 18:21 UTC and has '
                          'priority) and equals PR3021\'s published finite records (profile, idle, physical, roles, kappa, gain; '
                          'its root bracket lies in [C, C + 1e-24)); PR3021\'s native/admission/outer release is author-run and '
                          'not rerun here.')
    log('E PR3018 journal (%d edits, %d roles moved) reproduces its profile %s and endpoint %s; composed with R1: C %s = '
        'PR3021\'s published composition (kappa, gain and profile equal)'
        % (jrec['edits'], jrec['location_changes'], compact(journal['pr3018_profile']), journal['pr3018_endpoint_predicted'],
           journal['composed_endpoint_predicted']))
    # negative controls
    for tag in tags:
        X = W[tag]
        CT.edit_controls(tag, X['wp'], X['wc'], edit, declared, EXPECT_COUNTS, X['Pp'], X['chp'], X['frp'], groups['edit'])
        CT.word_controls(tag, X['wc'], X['wp'], declared, EXPECT_COUNTS, groups['words'])
        log('controls [%s]: edit and words done' % tag)
    fctx = dict(rows=fill['rows'], drows=pc['drows'], order=order, disp=disp, widths=pc['widths'], local=pc['local'],
                sc=sc, helpers=pc['helpers'])
    CT.fill_controls(fctx, groups['fill_rules'])
    pctx = dict(pc=pc, pp=pp, order=order, disp=disp, sc=sc, fill=fill, profile15=profile15, claim15=claim15,
                words_c=words_c, rec_c=rec_c, dispatch_list=dispatch_list, tpl=tpl, t37=t37)
    CT.pricing_controls(pctx, groups['pricing'])
    kctx = dict(profile_c=prof_c, profile_p=prof_p, C=C15, C79=C79, straddle=S, straddle_vendored=S_v, CA=CA, kappa=k15, kappa79=k79,
                claimed_gain=Q(claim15['previous_claims']['pr2979']['gain']))
    CT.kappa_controls(kctx, groups['kappa'])
    jctx = dict(fill=fill, edits=ex['edits'], profile_j=pj['own']['profile'], result18=res18, order=order, disp=disp,
                words_p=words_p, rec_p=rec_p, sc=sc, last_edit_dropped_rule=LAST_EDIT_DROPPED_RULE)
    CT.journal_controls(jctx, groups['journal'])
    log('controls: fill rules, pricing, kappa and journal done')
    AL.need(sorted(inp.used) == sorted(INPUTS), 'unused pinned inputs %r' % sorted(set(INPUTS) - set(inp.used)))
    AL.check_self_checks(AL.RAN, EXPECTED_SELF_CHECKS_FAST if args.fast else EXPECTED_SELF_CHECKS)
    groups['vendor_pins'] = vendor_controls(vendor_bytes, AC)
    semantic = [(g, c) for g, recs in sorted(groups.items()) if g not in PLUMBING_GROUPS for c in recs]
    n_neg = len(semantic)
    n_attempted = len(AC.ATTEMPTED) - len(groups['vendor_pins'])
    AL.need(n_neg == n_attempted, 'negative controls: %d attempted, %d recorded as rejected' % (n_attempted, n_neg))
    distinct = len(set((g, strip_tag(c['control'])) for g, c in semantic))
    positives = list(AC.POSITIVES)
    expected_positives = set(POSITIVE_CONTROLS) - ({'pr2979_words_extra'} if args.fast else set())
    AL.need(sorted(positives) == sorted(expected_positives), 'positive controls executed %r' % positives)
    rb = scope_b['base']['candidate']
    summary = dict(
        hunk='restore[%d:%d) -> %d gates' % (edit['start'], edit['stop'], len(edit['new'])),
        words_independent_inputs=rb['independent_inputs'],
        replay_orientations=[rb['replay_forward']['orientation'], rb['replay_dual']['orientation']],
        local_profile_parent=scope_b['base']['parent']['profile'], local_profile=rb['profile'],
        width_inventory=rb['inventory'], paid_delta=scope_a['base']['attribution']['paid_delta'],
        registers_with_changed_climbs=scope_a['base']['attribution']['dimensions_changed'],
        census=dict((tag, dict((which, dict(census[tag][which]['summary'], improving=improving[tag][which],
                                                losing_only=losing[tag][which]))
                               for which in census[tag])) for tag in census),
        complete_profile=pricing['pr3015']['profile'], roles=pricing['pr3015']['roles'],
        complete_delta_vs_pr2979=pricing['complete_delta_vs_pr2979'], physical=phys['physical'], C=kappa['C'],
        gain_over_pr2979=gain['gain_float'], pr3018_profile_reproduced=True,
        pr3018_endpoint_predicted=journal['pr3018_endpoint_predicted'],
        composed_endpoint_predicted=journal['composed_endpoint_predicted'], pr3021_composition_equal=True,
        negative_controls_attempted=n_attempted, negative_controls_rejected=n_neg, distinct_controls=distinct,
        negative_controls_by_group=dict((g, len(v)) for g, v in sorted(groups.items()) if g not in PLUMBING_GROUPS),
        plumbing_controls=len(groups['vendor_pins']),
        positive_controls_executed=positives, positive_controls=len(positives), pinned_inputs=len(INPUTS),
        fast=bool(args.fast),
        counting=('negative_controls_attempted: controls run (audit_common.attempt; vendor-pin controls excluded); '
                  'negative_controls_rejected: control records written after the rejecting rule id was asserted '
                  '(a mutation of each provider counts once per provider); distinct_controls: distinct (group, '
                  'control) pairs with the provider tag removed'))
    result = canonical(dict(schema=1, audit='independent verification of PR #3015 head %s (R1 restore edit on PR #2979 '
                                            'head %s)' % (H3015, H2979),
                            summary=summary, commits=dict((str(k), v) for k, v in COMMITS.items()), vendor=vendor, facts=facts,
                            inputs=inp.used, scope_a=scope_a, scope_b=scope_b, census=census, pricing=pricing,
                            kappa=kappa, journal=journal, controls=groups, harness_selftest=harness,
                            self_checks_ran=dict(AL.RAN), git_env=dict(policy=GIT_ENV_POLICY, selftest=git_selftest),
                            positive_controls=[POSITIVE_CONTROLS[k] for k in positives], scope_limits=SCOPE_LIMITS))
    path = os.path.join(HERE, RESULT_NAME)
    if args.out:
        with open(path, 'w') as f:
            json.dump(result, f, indent=1, sort_keys=True)
            f.write('\n')
        log('wrote ' + RESULT_NAME)
    elif args.fast:
        log('--fast: RESULT.json not compared')
    else:
        AL.need(os.path.exists(path), RESULT_NAME + ' missing; run with --out first')
        with open(path) as f:
            committed = json.load(f)
        diff = sorted(k for k in set(result) | set(committed) if result.get(k) != committed.get(k))
        AL.need(not diff, 'recomputed result differs from committed %s in %r' % (RESULT_NAME, diff))
        log('recomputed result equals committed ' + RESULT_NAME)
    return summary


EXPECTED_SELF_CHECKS = {'wiring.edits_equal': 1, 'wiring.providers_agree': 1, 'fill.sha256_bound': 1}
EXPECTED_SELF_CHECKS_FAST = dict((k, v) for k, v in EXPECTED_SELF_CHECKS.items() if k != 'wiring.providers_agree')
LAST_EDIT_DROPPED_RULE = 'R-b.prefix'


def run_mutations(args):
    """Every entry of MUTATIONS, applied in a subprocess (--fast), must end with the FAIL line and exit code 1."""
    killed, survived = [], []
    base = [sys.executable, '-I', '-B', os.path.abspath(__file__), '--repo', args.repo, '--fast']
    if args.fetch:
        base += ['--fetch', '--remote', args.remote]
    procs = []
    for k, (mod, old, new) in enumerate(MUTATIONS):
        procs.append((k, mod, subprocess.Popen(base + ['--mutation', str(k)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)))
        while len([p for p in procs if p[2].poll() is None]) >= max(1, args.jobs):
            time.sleep(2)
    for k, mod, p in procs:
        out = p.communicate()[0].decode('utf-8', 'replace')
        last = [ln for ln in out.strip().splitlines() if ln.strip()][-1] if out.strip() else ''
        # killed only by an audit rejection (a wrong answer or an accepted control), never by a crash of the mutant
        dead = (p.returncode == 1 and last.startswith(FAIL_LINE)
                and last.split(' ', 2)[1].rstrip(':') in AUDIT_EXCEPTIONS)
        (killed if dead else survived).append((k, mod, last[:200]))
        print('mutation %2d (%s): %s' % (k, mod, 'killed: ' + last[:150] if dead
                                         else 'SURVIVED (exit %r): %s' % (p.returncode, last[:150])), flush=True)
    print('%s killed=%d/%d survived=%d' % ('PASS_MUTATIONS' if not survived else 'FAIL_MUTATIONS', len(killed), len(MUTATIONS),
                                           len(survived)), flush=True)
    return 0 if not survived else 1


def main():
    ap = argparse.ArgumentParser(description='Independent verification of PR #3015 (R1 restore edit on PR #2979).')
    ap.add_argument('--repo', default=REPO_DEFAULT, help='git repository holding (or receiving) the pinned commits')
    ap.add_argument('--fetch', action='store_true', help='fetch missing pinned commits from --remote into refs/audit/pr<N>')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true', help='write RESULT.json instead of comparing with it')
    ap.add_argument('--fast', action='store_true', help='base provider only, census on the parent word only; no RESULT comparison')
    ap.add_argument('--mutations', action='store_true', help='run every entry of MUTATIONS in a subprocess; each must fail')
    ap.add_argument('--jobs', type=int, default=3, help='parallel subprocesses for --mutations')
    ap.add_argument('--mutation', type=int, default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()
    scrub_git_env(os.environ)
    GIT_SCRUB['done'] = True
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    if args.mutations:
        return run_mutations(args)
    mutation = MUTATIONS[args.mutation] if args.mutation is not None else None
    t0 = time.time()

    def log(msg):
        print('  [%5.1fs] %s' % (time.time() - t0, msg), flush=True)

    if mutation is not None:
        log('MUTATION %d applied to %s: %r -> %r' % (args.mutation, mutation[0], mutation[1][:60], mutation[2][:60]))
    try:
        summary = run(args, log, mutation)
    except BaseException as exc:
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
    cz = summary['census']
    print('%s hunk=%s words=2x%d-inputs-%s profile=%s->%s delta=%s@reg%s census_parent=%s census_candidate=%s complete=%s '
          'roles=%d complete_delta=%s physical=%d C=%s kappa=C-1e-46-1e-70 gain=%s pr3018_profile=reproduced '
          'composed_C=%s=PR3021 negative_controls=%d/%d-rejected distinct_controls=%d positive_controls=%d pinned_inputs=%d%s'
          % (PASS_LINE, summary['hunk'].replace(' ', ''), summary['words_independent_inputs'],
             '+'.join(dict(forward='fwd', dual='dual').get(o, o) for o in summary['replay_orientations']),
             compact(summary['local_profile_parent']), compact(summary['local_profile']), compact(summary['paid_delta']),
             ','.join(map(str, summary['registers_with_changed_climbs'])),
             '%d-pairs/%d-improving' % (cz['base']['parent']['adjacent_same_target_pairs'], len(cz['base']['parent']['improving'])),
             ('%d-pairs/%d-improving' % (cz['base']['candidate']['adjacent_same_target_pairs'], len(cz['base']['candidate']['improving']))
              if 'candidate' in cz['base'] else 'skipped'),
             compact(summary['complete_profile']), summary['roles'], compact(summary['complete_delta_vs_pr2979']),
             summary['physical'], summary['C'], summary['gain_over_pr2979'], summary['composed_endpoint_predicted'],
             summary['negative_controls_rejected'], summary['negative_controls_attempted'], summary['distinct_controls'],
             summary['positive_controls'], summary['pinned_inputs'], ' FAST' if summary['fast'] else ''), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
