#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent verification of open PR #2751 (tekuuu, head 4cfbb0cc, research/t74-joint-twelve) and reconciliation
with open PR #2720 (petalas, head 813fae62, research/t74-inherited-centre-floor): single entry point.

PR #2751 changes the four partner-source aliases of PR2733's T74 words (sources 33, 55, 74, 85 take the roles of
removed helpers 696, 697, 698, 700 instead of 640, 641, 642, 644; the eight R assignments are PR2696's), recovers each
partner pair with x += y/2; y -= x, lifts targets 21, 37, 47, 110 instead of 23, 34, 50, 108 and so leaves all eight
centre children rank eight: a cut of 8H8 instead of PR2733's 4H7 + 4H1 + 4H8, i.e. 4(H8-H7-H1) per word and
2664(H8-H7-H1) in the complete profile.  PR #2720 shows that under its hypotheses 1-3 the partner correction has
rank four on rows 23, 34, 50, 108 and, under its extra cut-bill premises, the cut costs at least 4H7 + 4H1 + 4H8.
With code independent of both PRs (standard library only) this package checks:

  A  audit_words.py      both changed words (forward and dual exact replay in the free-operator model through
                         cleanup and target endpoint, 36 initial corrections emulated exactly, warp algebra, frame
                         recount, cut census, lifted targets, the 12 lender rows, the 4 pair recoveries) and the
                         wiring self-check that both providers ran the identical spec;
  B  audit_diff.py       the exact structural change from PR2733@2761b52b and the per-word delta 4(H8-H7-H1);
  C  audit_reconcile.py  PR2720's matrix, determinant, omitted-correction error E_P = F_P - I_P, continuation and cut
                         floor on its own input words, the same objects on PR2751's words, the echo identities, and
                         one computed boolean per quoted PR2720 hypothesis clause (README lines quoted verbatim from
                         the pinned README; premises not evaluated are listed);
  D  audit_pricing.py    the complete profile from PR2751's 276,390-row FILL (two implementations, comparison
                         recorded for every priced fill), the complete delta against PR2733@2761b52b, the physical
                         stock, the endpoint enclosure and kappa, and the comparison with PR2733's head refit a63c55ff;
  E  audit_others.py     the #2766/#2767 complete profiles, #2767's two PROFILE.json files (the top-level one against
                         PR2733@2761b52b's complete profile as computed in scope D, wiring self-checked), and
  F                      (data only, parsed from the pinned bytes read, blob id and sha256 recomputed) the four pair
                         recoveries, ops 47-50 charts and lifted targets of the words of #2802, #2818, #2824, #2827
                         and #2833 against PR2751's (each required to be a different word: 72 warp records, not 65);
     audit_controls.py   the negative controls, each asserting the rule id that rejects it;
     audit_lib.py        shared helpers (parse with corrections, own exact tracker, linear algebra, control records).
  vendor/                this contributor's earlier checkers, byte copies pinned by git blob id and sha256 (VENDOR)

Inputs: every PR file is read with `git -C <repo> show <commit>:<path>` and must match a pinned git blob id and
sha256 (INPUTS).  PR content is data only: it is decoded as JSON/gzip/text and never imported or executed.  At
startup verify.py removes every GIT_CONFIG* variable (GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM, GIT_CONFIG_NOSYSTEM, ...)
from its environment (scrub_git_env, self-tested); every git subprocess then drops the repository-redirecting and
config-injection GIT_* variables and sets GIT_NO_REPLACE_OBJECTS=1 and GIT_NO_LAZY_FETCH=1 (audit_common.git_env).
Without --fetch nothing is written to the repository; --fetch fetches a missing pinned commit (refs/pull/N/head, then
the sha) into refs/audit/prN only, with --no-write-fetch-head and -c gc.auto=0 -c maintenance.auto=false
(audit_common.ensure_commits; git >= 2.29).  PR2733 has two pinned commits: 2761b52b (PR2751's comparison base) is an
ancestor of the head a63c55ff, so refs/audit/pr2733 anchors both.
The default run recomputes everything and requires the result to equal the committed RESULT.json; --out rewrites it.

Controls: every negative control is counted when attempted (audit_common.attempt) and recorded only after its
rejecting rule id (and replay stage, where named) was asserted; the run fails unless attempted == rejected.
Controls of hypothesis booleans also assert the word and the exact list of flipped booleans.  Self-checks: words
wiring (both providers ran the identical full spec), two-implementation comparison recorded for every priced fill,
hypothesis booleans equal between providers, verbatim PR2720 quotes (exact, non-blank-bounded line ranges), the #2767
comparator is the computed PR2733 profile object (others.pr2767_comparator), and every scope-F word is parsed from the
bytes read, whose blob id and sha256 are recomputed (downstream.input), and is not PR2751's (downstream.distinct).
distinct_controls counts controls with the provider tag removed.  Plumbing controls (checker non-vacuity, not word
properties) are reported separately.  positive_controls lists the positive controls executed (they must be exactly
POSITIVE_CONTROLS).  Every vendored module is loaded by executing exactly the bytes whose pin was verified (no import
machinery, so no cached .pyc can stand in), and tampered in-memory bytes must raise VendorPinMismatch.

Usage: python3 -I -B verify.py [--repo PATH] [--fetch] [--remote URL] [--out]
The final stdout line is PASS_T74_2751_JOINT_TWELVE_AUDIT ... (no timing) or, for any exception, the single line
`FAIL_T74_2751_JOINT_TWELVE_AUDIT <exception type>: <message>` with exit code 1.  Refuses python -O.
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

PASS_LINE = 'PASS_T74_2751_JOINT_TWELVE_AUDIT'
FAIL_LINE = 'FAIL_T74_2751_JOINT_TWELVE_AUDIT'
if not __debug__:
    sys.stdout.write(FAIL_LINE + ' UsageError: refusing to run under python -O\n')
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
RESULT_NAME = 'RESULT.json'

# This contributor's earlier code, byte copies (see vendor/NOTICE.md and vendor/pr2804/NOTICE.md): rel path ->
# (module name, git blob id, sha256).  Loaded in this (sorted) order, so that each module's imports are registered.
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
}
LOCAL_MODULES = ('audit_lib', 'audit_words', 'audit_diff', 'audit_reconcile', 'audit_pricing', 'audit_others',
                 'audit_controls')

H2751 = '4cfbb0cc8314d7fb4e8e754545a49a42eb590a69'   # PR #2751 head (object under audit)
H2733 = '2761b52b17590b8cf94f2e410004a8252d5592dc'   # PR #2733 commit named as PR2751's comparison base
H2720 = '813fae623dcf3181fb9f535852ae4c82b1b369b5'   # PR #2720 head (reconciliation)
H2696 = '5a42add713e09a8798a84d0be7a8276626d9e785'   # PR #2696 head (PR2720's input words)
H2269 = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'   # PR #2269 head (T74 template)
H2766 = 'e6df920cd0110e4b629e2ad84eddcb539001e174'   # PR #2766 head (optional scope E)
H2767 = 'e8b771ba132fe632796b28c1742a8d096c04519f'   # PR #2767 head (optional scope E)
H2733_HEAD = 'a63c55ff56aaa8645d64d1162d1f017b59ded42a'   # PR #2733 head (2761b52b is its ancestor; scope D comparison)
H2802 = '17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd'   # PR #2802 head (scope F, words only)
H2818 = '175822aee7a1858ec653f7f92d7a750aec2c2795'   # PR #2818 head (scope F)
H2824 = 'f1826afe1f487333f2c1e5bf862bae2211ce8dd9'   # PR #2824 head (scope F)
H2827 = '4dc1286a476874447f76826885c6af99409a1d46'   # PR #2827 head (scope F)
H2833 = 'e9307b48d7d1b690939935ecef0f8e524e6d92f4'   # PR #2833 head (scope F)
COMMITS = {2751: H2751, 2733: H2733, 2720: H2720, 2696: H2696, 2269: H2269, 2766: H2766, 2767: H2767, 2802: H2802,
           2818: H2818, 2824: H2824, 2827: H2827, 2833: H2833}
COMMITS_HEADS = {2733: H2733_HEAD}       # a second pinned commit of a PR (ensure_commits takes one per PR per call)
P51 = 'research/t74-joint-twelve/'
P33 = 'research/concentrated-prelife-composition/'
P96 = 'research/t74-concentrated-source-partners/'
P20 = 'research/t74-inherited-centre-floor/'
P66 = 'research/complex-routing-leaf-fusion/'
P67 = 'research/gmx-t74-borrow43-handoff/'
P02 = 'research/t74-joint-twelve-retired7/inputs/'
P18 = 'research/gmx-t74-borrow43-handoff/new/borrow/words/'
P24 = 'research/replica-tail-gain/vendor/frontier/inputs/'
P27 = 'research/superior-replica-kappa/vendor/frontier/inputs/'
W02_BASE = ('91bd9c68f209ac29e27cac566ff7a78339788553', 'dca8becca633ffc5e998985631bcbcab1123b27ca7f10ac6a96b1ec21ce69a66')
W02_EXTRA = ('6c4a9a4395cfd407b435833908f783db4b3c6a4b', '6bcb3c2c73eaf7558ddc6ef6b484334f8d96b9d2b227e265483b657de00f4bb7')
# key: (PR, commit, path, git blob id, sha256)
INPUTS = {
    'w2751_base': (2751, H2751, P51 + 'inputs/WORD-base.json.gz', 'f1fc67a6eaf4bcc5dfa852b448aa2659070fa5f8',
                   'ae8b6b4d62a9da29331062fae1bd68b0341edf83152f5a5ef50c5109ba578f9a'),
    'w2751_extra': (2751, H2751, P51 + 'inputs/WORD-extra.json.gz', 'f06e80c4dddb9741d0051cb85a57d356e673f687',
                    '1bb44a73d5841afb954b49ae94dba2e0c536b1eea9436ae5d89de87d8a04e127'),
    'providers2751': (2751, H2751, P51 + 'inputs/PROVIDERS.json', '26be26b6d25be67327ae77623c2eaa0a9fe463dc',
                      'ec4802a33c0e1d41369da77b19b9b783dc812b2d3246e096fee13d29f226dd66'),
    'fill2751': (2751, H2751, P51 + 'inputs/FILL.json.gz', '17129e917b31b15625c53181d303b68e17ffed55',
                 '9ce94578640b4927cb9c73244692b1f79ac2999179d309f6bf0c015c06f7a2f1'),
    'order2751': (2751, H2751, P51 + 'inputs/ORDER.json', 'c202d6ec222a257a64b2017eb1bbb0f9d2682669',
                  '129e791d5b45c279443ff9e1edef5ac33d5abc51717ecbae8265abea5c247ae7'),
    'dispatch2751': (2751, H2751, P51 + 'inputs/DISPATCH.json.gz', '4f4c2138d6be71dc649b8ee746385f059c242f21',
                     '14fe756dcac93a0f3b2b7f38ba7b998dec89d56d5171b691af4fae45e5d83d11'),
    'claim2751': (2751, H2751, P51 + 'CLAIM.json', '48ad23a430def28e485ee311ac92828ac9664a0c',
                  '78e99222196fca8b74a895b9e2db40a0e4afd1d69cd4fb52f38bfb157bac2438'),
    'profile2751': (2751, H2751, P51 + 'PROFILE.json', '080d9e165dbc951c9e8d3eb027bf2b187e932c5d',
                    '36e76f32570bac074cf70a6076b7c54e6d5b0fc3b505f404bc58fd02abf7967d'),
    'readme2751': (2751, H2751, P51 + 'README.md', '77ab0d3121069a8aa365bf0f6c35ee8e5ac15ac8',
                   'd8501fbc11b3dc87fc618122c83f10a56cd4457c7abdab792e2f9506bab4666e'),
    'w2733_base': (2733, H2733, P33 + 'expected/words/base.json.gz', 'f676bd51840ace560c3e91469c0bc4c2f6d0e04d',
                   'ff85b16fa4bdebab6af9ea2d77fcfa81dcb8f4bc3511cf6ea4c34f5ad7684f30'),
    'w2733_extra': (2733, H2733, P33 + 'expected/words/extra.json.gz', '721d01777aadfbc30603a6f88c108bc3b7eba680',
                    'e89f28aa8577d2c7c26ed9b5b878e4ad25a8decb9a1b70b837970db7627dd94b'),
    'providers2733': (2733, H2733, P33 + 'expected/PROVIDERS.json', 'a6d377a9fb6319a109004cd8131961eda345f9bc',
                      '0c4a84791ebe1e462be8b0c7a6c6d56098f5803b77c2b187da15ec2682376d75'),
    'fill2733': (2733, H2733, P33 + 'expected/FILL.json.gz', '2a28b4da07450d251caf1efe93ae2fa0c16197f5',
                 'bf67e3a93a319e66ada7dd171c7b17490ce3e10e46a7172862b73e5f21a2ee45'),
    'order2733': (2733, H2733, P33 + 'expected/ORDER.json', '7141bd58cc465e28f0189345713ddd366c814ca4',
                  'aa7c53c188c90fd74421a804f4c6fb13aa1187c06dbac51fa147830a40e00667'),
    'dispatch2733': (2733, H2733, P33 + 'independent-inputs/DISPATCH.json', '693ed0d022791c43d59000718521fded1ef8def7',
                     'fd8132ec8957b908ee6d871216848f18bafc6bd9304acd6185519ee26d97b1ca'),
    'claim2733': (2733, H2733, P33 + 'CLAIM.json', 'e97166d50158786e666c8e0d97d12f79a098df29',
                  '8e08f71a18e6a30259c1e2ea19b4069b9d3e3b656b38c57065ec2b9db367282b'),
    'w2696_base': (2696, H2696, P96 + 'inputs/candidate/eight-alias-base.json.gz',
                   '83de7694ddb850cf7c7afec165b2a1aa4db07f53',
                   '26494325101672261441286bdde7949b13b747469cf3c5e6dc2f451a5b56f8d5'),
    'w2696_extra': (2696, H2696, P96 + 'inputs/candidate/eight-alias-extra.json.gz',
                    '82ee0c84902c21ea335aa208185eb4b7c6a0b77b',
                    '735e6c7808d5169f05ce263455dfc7efed44a14098cecd6344cf85624b355bd8'),
    'claim2696': (2696, H2696, P96 + 'CLAIM.json', '69a3a6502fb8dbd39ea2241132618ac00310f79b',
                  '104e1982b212e2976d472d4a6f79e634f3c55d249b1da5d6375bb0b04d74ebb2'),
    'w2720_base': (2720, H2720, P20 + 'inputs/eight-alias-base.json.gz', '83de7694ddb850cf7c7afec165b2a1aa4db07f53',
                   '26494325101672261441286bdde7949b13b747469cf3c5e6dc2f451a5b56f8d5'),
    'w2720_extra': (2720, H2720, P20 + 'inputs/eight-alias-extra.json.gz', '82ee0c84902c21ea335aa208185eb4b7c6a0b77b',
                    '735e6c7808d5169f05ce263455dfc7efed44a14098cecd6344cf85624b355bd8'),
    'result2720': (2720, H2720, P20 + 'RESULT.json', 'f775a6e18c7d07265284aca4ecf6d8570f5fcd37',
                   '63078b869e147c75061befdc31aae0c8c42412bfa9a36beef7c0bfa794e707f1'),
    'tpl2269': (2269, H2269, 'research/gmx-t74-borrow43/GLOBAL-TEMPLATE.json.gz',
                '5327fc2f4e8ea82ed356c94ff040d23fc73c731f',
                '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db'),
    't37_2269': (2269, H2269, 'research/gmx-t74-borrow43/inputs/GLOBAL-TEMPLATE.json.gz',
                 '114808c32b1799da53524bdc25cea67efb60009e',
                 '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'),
    'w2766_base': (2766, H2766, P66 + 'inputs/WORD-base.json.gz', '9a49a9096504bf59e7037b7da398a54c4608f81e',
                   '80e309cc16d0a86a0854d32f4f43e0d856768ea3cf5b6437061b427997ae4790'),
    'w2766_extra': (2766, H2766, P66 + 'inputs/WORD-extra.json.gz', 'a3fdc91b1b1452866e0ea2f3dfb6af728717b709',
                    '88e55acb7e274c62fbb0deab7f420d85fde3c2a471735222f0b5d039bc34e2e6'),
    'claim2766': (2766, H2766, P66 + 'CLAIM.json', 'd352e67b80455a435b2527880bd5690806097a7d',
                  '399e20ffb8bac62363f7d48c59021d5afef5f62bb6c51986ca847b02ec1e73a8'),
    'fill2766': (2766, H2766, P66 + 'vendor/pr2751/inputs/FILL.json.gz', '17129e917b31b15625c53181d303b68e17ffed55',
                 '9ce94578640b4927cb9c73244692b1f79ac2999179d309f6bf0c015c06f7a2f1'),
    'order2766': (2766, H2766, P66 + 'vendor/pr2751/inputs/ORDER.json', 'c202d6ec222a257a64b2017eb1bbb0f9d2682669',
                  '129e791d5b45c279443ff9e1edef5ac33d5abc51717ecbae8265abea5c247ae7'),
    'dispatch2766': (2766, H2766, P66 + 'vendor/pr2751/inputs/DISPATCH.json.gz',
                     '4f4c2138d6be71dc649b8ee746385f059c242f21',
                     '14fe756dcac93a0f3b2b7f38ba7b998dec89d56d5171b691af4fae45e5d83d11'),
    'w2767_base': (2767, H2767, P67 + 'new/borrow/words/BORROW-WORD-43base.json.gz',
                   '79b9663e5e3f555a8cbde093b5c48db03ce77178',
                   'f619788dafe250ab5dba109fb942e1f40c17057f4107f591219fcfeed606b202'),
    'w2767_extra': (2767, H2767, P67 + 'new/borrow/words/BORROW-WORD-43extra.json.gz',
                    '1f53979df720bcc4645d382c900f7d76824d80ca',
                    '8b9e5200a059ebd07fb19fb3c7f6dd0409b15e4a047425892ec9a391e3c8a921'),
    'fill2767': (2767, H2767, P67 + 'new/borrow-fill/FILL.json.gz', '388bd2d5a7100a12b6550d4b262a5d3600c1accf',
                 '2082ce3a68f27f38e9b5198a92802efd98d39c5c82d836784f7bc532136ee324'),
    'order2767': (2767, H2767, P67 + 'new/borrow-fill/ORDER.json', '7141bd58cc465e28f0189345713ddd366c814ca4',
                  'aa7c53c188c90fd74421a804f4c6fb13aa1187c06dbac51fa147830a40e00667'),
    'dispatch2767': (2767, H2767, P67 + 'new/borrow-fill/DISPATCH.json', '693ed0d022791c43d59000718521fded1ef8def7',
                     'fd8132ec8957b908ee6d871216848f18bafc6bd9304acd6185519ee26d97b1ca'),
    'profile2767': (2767, H2767, P67 + 'new/PROFILE.json', '81d35c08602244d1cea7a275e76c2dce64ef6dc1',
                    '25a5c41e34d15457cce19d3e7db360849ff40f59b85839348b40cac556411ace'),
    'profile2767_top': (2767, H2767, P67 + 'PROFILE.json', '0a1699010430bf5b886d8bbb584468de307dab2a',
                        '29f9fd0046b849568676e92ac91de81f0b5218d265c39624889b2719951681ef'),
    'readme2720': (2720, H2720, P20 + 'README.md', '00fd063ba2835cab0510e5b2142dbabbddd573b5',
                   'b1786740feaaa1edcf1854d9474eb5aa9a363179a198893c9a358c4344253de1'),
    'claim2733_head': (2733, H2733_HEAD, 'research/concentrated-prelife-refit/CLAIM.json',
                       '4d848d5466e2b9b203891ac8a2ad75fd97124c9b',
                       '7402be1dcf6225f36fe727f0d0d5ae801de3b5dfda5bf18f8c1290e71d6f25c1'),
    'w2802_base': (2802, H2802, P02 + 'WORD-base.json.gz') + W02_BASE,
    'w2802_extra': (2802, H2802, P02 + 'WORD-extra.json.gz') + W02_EXTRA,
    'w2818_base': (2818, H2818, P18 + 'BORROW-WORD-43base.json.gz') + W02_BASE,
    'w2818_extra': (2818, H2818, P18 + 'BORROW-WORD-43extra.json.gz') + W02_EXTRA,
    'w2824_base': (2824, H2824, P24 + 'WORD-base.json.gz') + W02_BASE,
    'w2824_extra': (2824, H2824, P24 + 'WORD-extra.json.gz') + W02_EXTRA,
    'w2827_base': (2827, H2827, P27 + 'WORD-base.json.gz') + W02_BASE,
    'w2827_extra': (2827, H2827, P27 + 'WORD-extra.json.gz') + W02_EXTRA,
    'w2833_base': (2833, H2833, P18 + 'BORROW-WORD-43base.json.gz', 'd3878e3be59c50ef60ef1d758215547554134c39',
                   'dda9878455b3a3bec64ca16b1ac7789bbf5ffb603d5713b8df8644485e85b1b7'),
    'w2833_extra': (2833, H2833, P18 + 'BORROW-WORD-43extra.json.gz', '0638b6ad9d29eec2be61bdb46140c0c5b7b0d21b',
                    'bbe6bcba59e45e827a8e932ee4b23650d56ed4a0b8e0875c14f23c36b9e47eac'),
}
DOWNSTREAM = (2802, 2818, 2824, 2827, 2833)
PROVIDER_KEY = {'base': 'gauge44', 'extra': 'extra'}
POSITIVE_CONTROLS = {
    'pr2733_words_base': 'PR2733@2761b52b base word passes the same word pipeline (replays, cleanup, lenders, pairs) '
                         'and reproduces PR2733 CLAIM.json local_profile, helpers and private buffers',
    'pr2733_words_extra': 'PR2733@2761b52b extra word passes the same word pipeline (replays, cleanup, lenders, '
                          'pairs) and reproduces PR2733 CLAIM.json local_profile, helpers and private buffers',
    'pr2696_words_base': 'PR2696 base word (= PR2720 input) passes the same word pipeline and reproduces PR2696 '
                         'CLAIM.json local_profile, helpers and private buffers',
    'pr2696_words_extra': 'PR2696 extra word (= PR2720 input) passes the same word pipeline and reproduces PR2696 '
                          'CLAIM.json local_profile, helpers and private buffers',
    'pr2733_pr2720_hypotheses_base': 'PR2733 base word satisfies every computed PR2720 hypothesis (and so sits on '
                                     'PR2720\'s floor 4H7+4H1+4H8)',
    'pr2733_pr2720_hypotheses_extra': 'PR2733 extra word satisfies every computed PR2720 hypothesis (and so sits on '
                                      'PR2720\'s floor 4H7+4H1+4H8)',
    'pr2733_complete_profile': 'PR2733 FILL priced by the same two implementations reproduces PR2733 CLAIM.json '
                               'global_profile',
    'pr2733_endpoint': 'the endpoint check used for PR2751 accepts PR2733\'s C and rejects C + 1e-24 on PR2733\'s '
                       'recounted profile, and PR2733\'s kappa = C - 1e-46 - 1e-70',
    'pr2733_head_endpoint': 'the endpoint check used for PR2751 accepts the C of PR2733\'s head refit (a63c55ff, '
                            'research/concentrated-prelife-refit/CLAIM.json) and rejects C + 1e-24 on its complete '
                            'profile',
}
SCOPE_LIMITS = [
    'warp letters are abstract: the physical identity of each K_op shared by the A prelude and the B handoff (Clifford '
    'phases, monomial lifts) and the new charts of ops 47-50 are checked only in the GF(2)/symplectic chart algebra',
    'the 36 initial corrections (PR2679 pre-life hosting) are uncharged in the frame recount, as in PR2679, PR2733 and '
    'PR2751; they are an identical multiset in PR2733 and PR2751',
    'native precision, strict supplier/global admission and the 63 modern outer inequalities are not re-derived; '
    'kappa = C - 1e-46 - 1e-70 is checked as arithmetic on the claimed C, given those author-checked stages',
    'the window semantics and free interleaving of replica controllers, and the stock terms 8 and 2, are inherited',
    'the reconciliation evaluates PR2720\'s hypotheses (quoted verbatim from its README at 813fae62) through computed '
    'proxies, one boolean per clause (reconcile.pr2720_hypotheses); two cut-bill premises are not evaluated (the '
    'descending private-copy model is assumed by construction; target chart changes and nonmonotone target frame '
    'paths are not evaluated); PR2720\'s theorem is not re-proved',
    'scope E (PR #2766, #2767) checks only the frame recounts and complete profiles of those PRs, not their word '
    'replays, endpoints or kappas',
    'scope F (PR #2802, #2818, #2824, #2827, #2833) parses their words as data and compares the four pair recoveries, '
    'the ops 47-50 charts and the lifted targets with PR2751\'s; their replays, recounts, fills, endpoints and kappas '
    'are not checked',
    'the comparison with PR2733\'s head refit (a63c55ff) uses that head\'s CLAIM.json complete profile and C as '
    'stated; its words and fill are not recounted',
]
GIT_ENV_POLICY = ('verify.py removes every GIT_CONFIG* variable (including GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM and '
                  'GIT_CONFIG_NOSYSTEM) from its environment before the first git call; audit_common.git_env then '
                  'drops the redirection and config-injection variables of every git call')
PLUMBING_GROUPS = ('plumbing',)
# Self-checks and scope-F checks that must have run (and passed) exactly this often (audit_lib.ran).
EXPECTED_SELF_CHECKS = {'reconcile.quotes': 1, 'reconcile.providers': 1, 'words.wiring': 1, 'pricing.two_impl_ran': 1,
                        'pricing.head': 1, 'others.pr2767_top_profile': 1, 'downstream.input': 10,
                        'downstream.structure': 10, 'downstream.coverage': 1}


GIT_SCRUB = dict(done=False)


def scrub_git_env(environ):
    """Remove every GIT_CONFIG* variable (GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM, GIT_CONFIG_NOSYSTEM, GIT_CONFIG,
    GIT_CONFIG_PARAMETERS, GIT_CONFIG_COUNT, GIT_CONFIG_KEY_*, GIT_CONFIG_VALUE_*) from environ; returns their names."""
    names = sorted(k for k in environ if k.startswith('GIT_CONFIG'))
    for k in names:
        del environ[k]
    return names


def git_env_selftest():
    """scrub_git_env on a synthetic environment removes exactly the GIT_CONFIG* variables."""
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


def load_module(name, path, pin=None):
    """Read the file once, check the pin (if any) on those bytes, and execute exactly those bytes as module `name`
    (registered in sys.modules so later modules import it)."""
    with open(path, 'rb') as f:
        data = f.read()
    computed = vendor_pin(data, pin, path) if pin is not None else None
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
    return json.loads(json.dumps(obj, sort_keys=True))


def compact(d):
    return json.dumps(d, sort_keys=True, separators=(',', ':'))


def strip_tag(name):
    return name.split('] ', 1)[1] if name.startswith('[') else name


def run(args, log):
    vendor, vendor_bytes = {}, {}
    for rel in sorted(VENDOR):
        name, blob, sha = VENDOR[rel]
        _, computed, vendor_bytes[rel] = load_module(name, os.path.join(HERE, *rel.split('/')), (blob, sha))
        vendor[rel] = dict(git_blob=computed[0], sha256=computed[1], bytes=len(vendor_bytes[rel]),
                           computed_from='the loaded bytes (vendor_pin)')
    mods = dict((name, load_module(name, os.path.join(HERE, name + '.py'))[0]) for name in LOCAL_MODULES)
    AC = sys.modules['audit_common']
    AL, AW, AD, AR, AP, AO, CT = (mods[k] for k in LOCAL_MODULES)
    AC.reset_controls()
    AL.RAN.clear()
    harness = AL.harness_selftest()
    git_selftest = git_env_selftest()
    AL.need(GIT_SCRUB['done'] and not any(k.startswith('GIT_CONFIG') for k in os.environ),
            'git_env: GIT_CONFIG* variables were not removed before the first git call')
    fetched = AC.ensure_commits(args.repo, COMMITS, args.fetch, args.remote)
    fetched += AC.ensure_commits(args.repo, COMMITS_HEADS, args.fetch, args.remote)
    if fetched:
        log('fetched PR heads %s from %s' % (fetched, args.remote))
    inp = AC.PinnedInputs(args.repo, INPUTS)
    groups = dict((g, []) for g in ('words_pipeline', 'words_function', 'plumbing', 'diff', 'reconcile_pipeline',
                                    'reconcile_function', 'fill_rules', 'pricing', 'others', 'downstream', 'wiring'))
    claim33, claim96 = inp.json('claim2733'), inp.json('claim2696')
    spec33 = dict(profile=AL.intkeys(claim33['local_profile']), helpers=claim33['helpers'],
                  buffers=claim33['private_zero_buffers'])
    spec96 = dict(profile=AL.intkeys(claim96['local_profile']), helpers=claim96['helpers'],
                  buffers=claim96['private_zero_buffers'])
    prov51, prov33 = inp.json('providers2751'), inp.json('providers2733')
    readme2720 = inp.text('readme2720')
    quotes = AR.check_quotes(readme2720)
    words, diffs, recon, W = {}, {}, {}, {}
    for tag in ('base', 'extra'):
        pid = PROVIDER_KEY[tag]
        w51, w33, w96 = inp.json('w2751_' + tag), inp.json('w2733_' + tag), inp.json('w2696_' + tag)
        r51, P51, fr51 = AW.word_pipeline(w51, AW.SPEC_2751, prov51[pid])
        r33, P33, fr33 = AW.word_pipeline(w33, spec33, prov33[pid])
        AC.positive('pr2733_words_' + tag)
        r96, P96, fr96 = AW.word_pipeline(w96, spec96)
        AC.positive('pr2696_words_' + tag)
        words[tag] = dict(pr2751=r51, pr2733=r33, pr2696=r96)
        log('A [%s] PR2751 word: %d inputs, forward+dual exact through %d cleanup items, profile %s, 12 lenders, 4 '
            'pairs; PR2733 and PR2696 positive controls pass' % (tag, r51['independent_inputs'],
                                                                 r51['cleanup']['items'], compact(r51['profile'])))
        d, echo = AD.word_diff(w51, w33, fr51, fr33, r51['sections'], r33['sections'])
        diffs[tag] = d
        log('B [%s] change set vs PR2733@2761b52b explained exactly; delta %s' % (tag, compact(d['profile_delta'])))
        raw20, raw96 = inp.raw('w2720_' + tag), inp.raw('w2696_' + tag)
        blob20 = AR.check_inputs(raw20, raw96)
        ana = dict(a96=AR.analyse(w96), a33=AR.analyse(w33), a51=AR.analyse(w51))
        pub = inp.json('result2720')['providers'][tag]
        rc = AR.reconcile_checks(ana['a96'], ana['a33'], ana['a51'], pub, echo)
        AC.positive('pr2733_pr2720_hypotheses_' + tag)
        rc['pr2720_input_blob_equals_pr2696'] = blob20
        recon[tag] = rc
        log('C [%s] PR2720 Q det %s reproduced on PR2696; PR2751: zero on 23,34,50,108, det %s on %s; hypotheses '
            'changed: %s' % (tag, rc['pr2696']['det'], rc['pr2751']['det'], rc['pr2751']['support'],
                             sorted(k for k, v in rc['pr2751']['hypotheses'].items() if not v)))
        W[tag] = dict(w51=w51, w33=w33, w96=w96, fr51=fr51, fr33=fr33, r51=r51, r33=r33, echo=echo, ana=ana,
                      pub=pub, raw=(raw20, raw96))
    wiring = dict(words=AW.check_wiring(dict((tag, words[tag]['pr2751']) for tag in words)))
    hyp = AR.reconciliation_record(
        quotes, recon,
        dict(pr2733_B=[e['old'] for e in diffs['base']['B']['renamed_edits'] if e['kind'] == 'pairs_deleted'],
             pr2751_B=[e['new'] for e in diffs['base']['B']['renamed_edits'] if e['kind'] == 'pair_inserted']))
    # D pricing
    tpl, t37 = inp.json('tpl2269'), inp.json('t37_2269')
    order51 = [tuple(x) for x in inp.json('order2751')]
    order33 = [tuple(x) for x in inp.json('order2733')]
    sc51 = AP.schedule(tpl, t37, order51)
    sc33 = sc51 if order33 == order51 else AP.schedule(tpl, t37, order33)
    dispatch51 = inp.json('dispatch2751')
    disp51, disp33 = AP.dispatch_map(dispatch51, order51), AP.dispatch_map(inp.json('dispatch2733'), order33)
    words51 = dict(gauge44=W['base']['w51'], extra=W['extra']['w51'])
    words33 = dict(gauge44=W['base']['w33'], extra=W['extra']['w33'])
    rec51 = dict(gauge44=W['base']['fr51'], extra=W['extra']['fr51'])
    rec33 = dict(gauge44=W['base']['fr33'], extra=W['extra']['fr33'])
    fill51, fill33 = inp.json('fill2751'), inp.json('fill2733')
    p51 = AP.price(fill51, order51, disp51, words51, rec51, sc51, keep_drows=True)
    p33 = AP.price(fill33, order33, disp33, words33, rec33, sc33)
    AP.check_profile_claim(p33['own']['profile'], dict(profile=claim33['global_profile']))
    AC.positive('pr2733_complete_profile')
    claim51, profile51, readme51 = inp.json('claim2751'), inp.json('profile2751'), inp.text('readme2751')
    local_delta = dict((int(k), v) for k, v in diffs['base']['profile_delta'].items())
    AL.need(diffs['base']['profile_delta'] == diffs['extra']['profile_delta'], 'pricing.delta: providers differ')
    phys_counts = (p51['helpers'], p51['buffers'])
    pc, C = AP.pricing_checks(p51, p33, claim51, profile51, claim33, local_delta, readme51, phys_counts)
    C33 = AL.Fraction(claim33['complex_lower'])
    AP.endpoint_check(p33['own']['profile'], C33, AL.Fraction(claim33['complex_upper']))
    AP.kappa_check(AL.Fraction(claim33['kappa']), C33)
    AC.positive('pr2733_endpoint')
    claim_head = inp.json('claim2733_head')
    head = AP.head_comparison(p51['own']['profile'], claim_head, C, H2733)
    head['head_endpoint'] = AP.endpoint_check(AL.intkeys(claim_head['global_profile']),
                                              AL.Fraction(claim_head['complex_lower']),
                                              AL.Fraction(claim_head['complex_upper']))
    AC.positive('pr2733_head_endpoint')
    lo_a, hi_a, S = AP.straddle(p51['own']['profile'], C)
    AL.need(C <= lo_a < S < hi_a < C + AP.E24, 'pricing.root_bracket: bracket outside (C, C + 1e-24)')
    CA = sys.modules['check_accounting']
    pc['root_bracket'] = dict(lower=CA.dec(lo_a, 60), upper=CA.dec(hi_a, 60),
                              width='%.2e' % float(hi_a - lo_a),
                              root_minus_C_e25=CA.dec((lo_a - C) * 10 ** 25, 6))
    pricing = dict(schedule=sc51['info'], orders_equal=order33 == order51, pr2751=AP.summary(p51),
                   pr2733=AP.summary(p33),
                   pr2733_equals_its_claim=p33['own']['profile'] == AL.intkeys(claim33['global_profile']), checks=pc,
                   dispatch=dict((p, sum(1 for v in disp51.values() if v == p)) for p in sorted(set(disp51.values()))),
                   pr2733_head_a63c55ff=head)
    log('D complete profile %s (two implementations, %d roles), delta vs PR2733 %s, physical %d, C=%s accepted and '
        'C+1e-24 rejected; PR2733 head a63c55ff: PR2751 - head %s, head rejected at C, gap %s'
        % (compact(pc['complete_profile']), pricing['pr2751']['roles'], compact(pc['complete_delta_vs_pr2733']),
           pc['physical']['physical'], pc['C'], compact(head['pr2751_minus_head']), head['C_gap_approx']))
    # E (optional): PR2766 and PR2767 complete profiles
    AO.check_inputs(dict((k, inp.raw(k + '2766')) for k in ('fill', 'order', 'dispatch')),
                    dict((k, inp.raw(k + '2751')) for k in ('fill', 'order', 'dispatch')))
    words66 = dict((PROVIDER_KEY[t], inp.json('w2766_' + t)) for t in ('base', 'extra'))
    words67 = dict((PROVIDER_KEY[t], inp.json('w2767_' + t)) for t in ('base', 'extra'))
    rec66, rec67, inl = {}, {}, {}
    for pid in ('gauge44', 'extra'):
        rec66[pid], _ = AO.recount(words66[pid])
        rec67[pid], inl[pid] = AO.recount(words67[pid])
    order67 = [tuple(x) for x in inp.json('order2767')]
    sc67 = sc33 if order67 == order33 else AP.schedule(tpl, t37, order67)
    disp67 = AP.dispatch_map(inp.json('dispatch2767'), order67)
    fill67 = inp.json('fill2767')
    p66 = AP.price(fill51, order51, disp51, words66, rec66, sc51)
    p67 = AP.price(fill67, order67, disp67, words67, rec67, sc67)
    pricing['two_impl_compared'] = AP.check_two_impl_ran(dict(pr2751=p51, pr2733=p33, pr2766=p66, pr2767=p67))
    claim66, profile67, profile67_top = inp.json('claim2766'), inp.json('profile2767'), inp.json('profile2767_top')
    others = AO.others_checks(p66, p67, claim66, profile67)
    # comparator: PR2733@2761b52b's complete profile as computed above (p33, already equal to its CLAIM.json
    # global_profile); the wiring self-check others.pr2767_comparator requires this very object
    others['pr2767_profile_files'] = AO.check_pr2767_profiles(profile67_top, profile67, p67['own']['profile'],
                                                              p33['own']['profile'], p33,
                                                              inp.used['fill2733']['commit'])
    others['local_profiles'] = dict(pr2766=dict((p, AL.hist(rec66[p]['paid'])) for p in rec66),
                                    pr2767=dict((p, AL.hist(rec67[p]['paid'])) for p in rec67))
    others['pr2767_inline_B_warps'] = inl
    log('E #2766 and #2767 complete profiles identical: %s' % compact(others['pr2766']['profile']))
    # F: downstream word structure (data only)
    downstream = {}
    for pr in DOWNSTREAM:
        recs = {}
        for tag in ('base', 'extra'):
            key = 'w%d_%s' % (pr, tag)
            wd, ident = AO.downstream_word(inp.raw(key), INPUTS[key][3:])   # parsed from the bytes read here
            recs[tag] = dict(AO.downstream_structure(wd, W[tag]['w51']), path=INPUTS[key][2], **ident)
        downstream[str(pr)] = dict(commit=COMMITS[pr], words=recs)
    AO.check_downstream_coverage(downstream, DOWNSTREAM)
    log('F later PRs %s keep the four pair recoveries (PR2751 frames), the ops 47-50 line-45 charts and the twelve '
        'lifted targets' % ','.join(map(str, DOWNSTREAM)))
    # negative controls
    report33 = dict(W['base']['w33']['report']['local_profile'])
    for tag in ('base', 'extra'):
        X = W[tag]
        CT.word_controls(tag, X['w51'], prov51[PROVIDER_KEY[tag]], report33, groups)
        CT.diff_controls(tag, X['w51'], X['w33'], X['fr51'], X['fr33'], X['r51']['sections'], X['r33']['sections'],
                         groups['diff'])
        CT.reconcile_controls(tag, X['ana'], X['pub'], X['echo'], X['raw'], groups['reconcile_pipeline'],
                              groups['reconcile_function'])
        log('controls [%s]: words, diff and reconcile done' % tag)
    CT.quote_controls(readme2720, recon, quotes, groups['reconcile_function'])
    CT.wiring_controls(words, EXPECTED_SELF_CHECKS, groups['wiring'])
    fctx = dict(rows=fill51['rows'], drows=p51['drows'], order=order51, disp=disp51, widths=p51['widths'],
                local=p51['local'], sc=sc51, helpers=p51['helpers'])
    CT.fill_controls(fctx, groups['fill_rules'])
    pctx = dict(p51=p51, p33=p33, claim51=claim51, profile51=profile51, claim33=claim33, local_delta=local_delta,
                readme51=readme51, phys_counts=phys_counts, order51=order51, disp51=disp51, sc51=sc51,
                fill51=fill51, words51=words51, recounts51=rec51, fill33=fill33, order33=order33, disp33=disp33,
                sc33=sc33, words33=words33, recounts33=rec33, C=C, straddle=S, tpl=tpl, t37=t37,
                dispatch51=dispatch51, claim_head=claim_head, H2733=H2733)
    CT.pricing_controls(pctx, groups['pricing'])
    CT.others_controls(dict(p66=p66, p67=p67, claim66=claim66, profile67=profile67, fill67=fill67, order67=order67,
                            disp67=disp67, sc67=sc67, words67=words67, recounts67=rec67, profile67_top=profile67_top,
                            claim33=claim33,
                            p33=p33, commit33=inp.used['fill2733']['commit'],
                            raw66=dict((k, inp.raw(k + '2766')) for k in ('fill', 'order', 'dispatch')),
                            raw51=dict((k, inp.raw(k + '2751')) for k in ('fill', 'order', 'dispatch'))),
                       groups['others'])
    CT.downstream_controls(dict((pr, dict((tag, inp.json('w%d_%s' % (pr, tag))) for tag in ('base', 'extra')))
                                for pr in DOWNSTREAM), dict((tag, W[tag]['w51']) for tag in W), downstream, DOWNSTREAM,
                           groups['downstream'], dict((k, (inp.raw(k), INPUTS[k][3:]))
                                                      for k in ('w2833_base', 'w2802_base', 'w2751_base')))
    log('controls: fill rules, pricing, others and downstream done')
    AL.need(sorted(inp.used) == sorted(INPUTS), 'unused pinned inputs %r' % sorted(set(INPUTS) - set(inp.used)))
    AL.check_self_checks(AL.RAN, EXPECTED_SELF_CHECKS)
    groups['vendor_pins'] = vendor_controls(vendor_bytes, AC)
    semantic = [(g, c) for g, recs in sorted(groups.items()) if g not in PLUMBING_GROUPS for c in recs]
    n_neg = len(semantic)
    n_plumb = sum(len(groups[g]) for g in PLUMBING_GROUPS)
    n_attempted = len(AC.ATTEMPTED) - sum(c['injections'] for g in PLUMBING_GROUPS for c in groups[g])
    AL.need(n_neg == n_attempted, 'negative controls: %d attempted, %d recorded as rejected' % (n_attempted, n_neg))
    distinct = len(set((g, strip_tag(c['control'])) for g, c in semantic))
    positives = list(AC.POSITIVES)
    AL.need(sorted(positives) == sorted(POSITIVE_CONTROLS), 'positive controls executed %r' % positives)
    orient = []
    for tag in ('base', 'extra'):
        for k in ('replay_forward', 'replay_dual'):
            o = words[tag]['pr2751'][k]['orientation']
            if o not in orient:
                orient.append(o)
    r51b = words['base']['pr2751']
    summary = dict(
        words_independent_inputs=r51b['independent_inputs'], replay_orientations=orient,
        local_profile=r51b['profile'], local_profiles_equal_between_providers=r51b['profile'] ==
        words['extra']['pr2751']['profile'],
        centre_paths=sorted(set(compact(p['children']) for p in r51b['centre_paths'])),
        lenders_exact=len(r51b['lenders']['lenders']), pair_recoveries=len(r51b['pairs']['pairs']),
        delta_vs_pr2733=diffs['base']['profile_delta'],
        pr2720_Q_det_on_pr2696=recon['base']['pr2696']['det'], pr2751_det=recon['base']['pr2751']['det'],
        pr2751_support=recon['base']['pr2751']['support'],
        pr2720_hypotheses_changed_by_pr2751=hyp['pr2751_changed'],
        pr2720_hypotheses_kept_by_pr2751=hyp['pr2751_kept'],
        complete_profile=pc['complete_profile'], roles=pricing['pr2751']['roles'],
        complete_delta_vs_pr2733=pc['complete_delta_vs_pr2733'], physical=pc['physical']['physical'], C=pc['C'],
        vs_pr2733_head=dict(delta=head['pr2751_minus_head'], C_gap=head['C_gap'], C_gap_approx=head['C_gap_approx']),
        pr2766_pr2767_complete_profiles_identical=others['identical'],
        downstream_prs_keeping_pair_recoveries_charts_and_lifts=sorted(int(k) for k in downstream),
        negative_controls_attempted=n_attempted, negative_controls_rejected=n_neg, distinct_controls=distinct,
        negative_controls_by_group=dict((g, len(v)) for g, v in sorted(groups.items()) if g not in PLUMBING_GROUPS),
        plumbing_controls=n_plumb, plumbing_injections=sum(c['injections'] for g in PLUMBING_GROUPS for c in groups[g]),
        positive_controls_executed=positives, positive_controls=len(positives), pinned_inputs=len(INPUTS),
        counting=('negative_controls_attempted: controls run (audit_common.attempt, plumbing injections excluded); '
                  'negative_controls_rejected: control records written after the rejecting rule id was asserted '
                  '(a mutation of each provider counts once per provider); distinct_controls: distinct (group, '
                  'control) pairs with the provider tag removed; plumbing controls are outside these counts'))
    commits = dict((str(k), v) for k, v in COMMITS.items())
    commits.update(('%d_head' % k, v) for k, v in COMMITS_HEADS.items())
    result = canonical(dict(schema=1, audit='independent verification of PR #2751 head %s and reconciliation with '
                                            'PR #2720 head %s' % (H2751, H2720),
                            summary=summary, commits=commits, vendor=vendor,
                            inputs=inp.used, words=words, diff=diffs, reconcile=recon, pr2720_hypotheses=hyp,
                            pricing=pricing, others=others, downstream=downstream, wiring=wiring,
                            controls=groups, harness_selftest=harness, self_checks_ran=dict(AL.RAN),
                            git_env=dict(policy=GIT_ENV_POLICY, selftest=git_selftest),
                            positive_controls=[POSITIVE_CONTROLS[k] for k in positives],
                            scope_limits=SCOPE_LIMITS))
    path = os.path.join(HERE, RESULT_NAME)
    if args.out:
        with open(path, 'w') as f:
            json.dump(result, f, indent=1, sort_keys=True)
            f.write('\n')
        log('wrote ' + RESULT_NAME)
    else:
        AL.need(os.path.exists(path), RESULT_NAME + ' missing; run with --out first')
        with open(path) as f:
            committed = json.load(f)
        diff = sorted(k for k in set(result) | set(committed) if result.get(k) != committed.get(k))
        AL.need(not diff, 'recomputed result differs from committed %s in %r' % (RESULT_NAME, diff))
        log('recomputed result equals committed ' + RESULT_NAME)
    return summary


def main():
    ap = argparse.ArgumentParser(description='Independent audit of PR #2751 and reconciliation with PR #2720.')
    ap.add_argument('--repo', default=REPO_DEFAULT, help='git repository holding (or receiving) the pinned commits')
    ap.add_argument('--fetch', action='store_true',
                    help='fetch missing pinned commits from --remote into refs/audit/pr<N> of --repo')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true', help='write RESULT.json instead of comparing with it')
    args = ap.parse_args()
    scrub_git_env(os.environ)          # before any git call (GIT_ENV_POLICY)
    GIT_SCRUB['done'] = True
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
    print('%s words=2x%d-inputs-%s profile=%s centres=8x%s lenders=%d pairs=%d delta_vs_2733=%s '
          'Q2720_det=%s Q2751_det=%s@%s changed=%s complete=%s roles=%d complete_delta=%s physical=%d C=%s '
          'kappa=C-1e-46-1e-70 vs_2733_head=%s@gap%s pr2766_eq_pr2767=%s downstream=%s '
          'negative_controls=%d/%d-rejected distinct_controls=%d positive_controls=%d pinned_inputs=%d'
          % (PASS_LINE, summary['words_independent_inputs'],
             '+'.join(short.get(o, o) for o in summary['replay_orientations']), compact(summary['local_profile']),
             '/'.join(summary['centre_paths']), summary['lenders_exact'], summary['pair_recoveries'],
             compact(summary['delta_vs_pr2733']), summary['pr2720_Q_det_on_pr2696'], summary['pr2751_det'],
             ','.join(map(str, summary['pr2751_support'])),
             ','.join(summary['pr2720_hypotheses_changed_by_pr2751']),
             compact(summary['complete_profile']), summary['roles'], compact(summary['complete_delta_vs_pr2733']),
             summary['physical'], summary['C'], compact(summary['vs_pr2733_head']['delta']),
             summary['vs_pr2733_head']['C_gap_approx'], summary['pr2766_pr2767_complete_profiles_identical'],
             ','.join(map(str, summary['downstream_prs_keeping_pair_recoveries_charts_and_lifts'])),
             summary['negative_controls_rejected'],
             summary['negative_controls_attempted'], summary['distinct_controls'], summary['positive_controls'],
             summary['pinned_inputs']), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
