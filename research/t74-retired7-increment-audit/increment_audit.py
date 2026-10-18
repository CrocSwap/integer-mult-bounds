#!/usr/bin/env python3
"""Independent adversarial audit of PR #2802's seven-stage increment over PR #2751 (retired5 stages refit5/alias5/refit5c
plus retired7 stages refit7/hostmove2/alias7/refit7c), verdict extended to PR #2818.  "retired7" in identifiers follows
#2802's package name (t74-joint-twelve-retired7); in prose it means only the last four stages.

Objects (read as pinned git blobs, never imported or executed):
  PR #2802 (mdumitrean) head 17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd, research/t74-joint-twelve-retired7/
  PR #2751 (tekuuu)     head 4cfbb0cc8314d7fb4e8e754545a49a42eb590a69, research/t74-joint-twelve/
  PR #2818 (jeremykothe2) head 175822aee7a1858ec653f7f92d7a750aec2c2795, research/gmx-t74-borrow43-handoff/
  PR #2766 (DavidAriasC) head e6df920cd0110e4b629e2ad84eddcb539001e174, research/complex-routing-leaf-fusion/ (attribution only)

Fresh standard-library code.  Every check is a named rule; the run prints one line per rule and a final
PASS/FAIL line.  Negative controls mutate the pinned inputs and must each be rejected by a named rule.

Model (the BORROW-WORD model as written in PR2226 PROOF.md and the PR2679/PR2751 lineage; restated here):
  registers 0..111 X, 112..223 Y, 224..703 helper namespace (report.R = 480); removed helpers do not exist;
  frames are GF(2)-subspaces of F_2^9 (represented here as the frozenset of all their elements);
  every framed gate climbs each incident register to the gate frame (monotone; a strict climb pays one child
  of rank = dimension increase); a B warp [pos, L, G, U, E] is applied before B[pos], needs cur(L) == U, sets
  cur(L) = E and is free (rank-zero reference change K_G); cut charges nested COPY chains; every live register
  finally climbs to its end frame; cleanup = inverse-reverse of the recorded (non-target and warp) program at
  FULL with private zero buffers for helper_final registers.  Logic: exact replay over Q<free group> with every
  live register an independent dirty symbol, forward and dual (g -> g^-T with K^-T as new free letters).
Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
import os
import random
import subprocess
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, localcontext

COMMIT = dict(c2802='17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd', c2751='4cfbb0cc8314d7fb4e8e754545a49a42eb590a69',
              c2818='175822aee7a1858ec653f7f92d7a750aec2c2795', c2766='e6df920cd0110e4b629e2ad84eddcb539001e174')
D02 = 'research/t74-joint-twelve-retired7/'
D51 = 'research/t74-joint-twelve/'
D18 = 'research/gmx-t74-borrow43-handoff/'
D66 = 'research/complex-routing-leaf-fusion/'
# key -> (commit key, path, sha256 of the blob bytes)
PINS = {
    'W_base': ('c2802', D02 + 'inputs/WORD-base.json.gz', 'dca8becca633ffc5e998985631bcbcab1123b27ca7f10ac6a96b1ec21ce69a66'),
    'W_extra': ('c2802', D02 + 'inputs/WORD-extra.json.gz', '6bcb3c2c73eaf7558ddc6ef6b484334f8d96b9d2b227e265483b657de00f4bb7'),
    'P_base': ('c2802', D02 + 'inputs/WORD2751-base.json.gz', 'ae8b6b4d62a9da29331062fae1bd68b0341edf83152f5a5ef50c5109ba578f9a'),
    'P_extra': ('c2802', D02 + 'inputs/WORD2751-extra.json.gz', '1bb44a73d5841afb954b49ae94dba2e0c536b1eea9436ae5d89de87d8a04e127'),
    'P51_base': ('c2751', D51 + 'inputs/WORD-base.json.gz', 'ae8b6b4d62a9da29331062fae1bd68b0341edf83152f5a5ef50c5109ba578f9a'),
    'P51_extra': ('c2751', D51 + 'inputs/WORD-extra.json.gz', '1bb44a73d5841afb954b49ae94dba2e0c536b1eea9436ae5d89de87d8a04e127'),
    'FILL': ('c2802', D02 + 'inputs/FILL.json.gz', '2f2a25a8d82b424b1e643a8a5167361fcc5ab33cfbc6f186f4cb7ddcaf9df7d9'),
    'FILL51': ('c2802', D02 + 'inputs/FILL2751.json.gz', '9ce94578640b4927cb9c73244692b1f79ac2999179d309f6bf0c015c06f7a2f1'),
    'FILL51_own': ('c2751', D51 + 'inputs/FILL.json.gz', '9ce94578640b4927cb9c73244692b1f79ac2999179d309f6bf0c015c06f7a2f1'),
    'PROV': ('c2802', D02 + 'inputs/PROVIDERS.json', '391075b1411a3976850c633f92f58c35ed3f046f09d55bd435d7545124543fd4'),
    'PROV51': ('c2802', D02 + 'inputs/PROVIDERS2751.json', 'ec4802a33c0e1d41369da77b19b9b783dc812b2d3246e096fee13d29f226dd66'),
    'ORDER': ('c2802', D02 + 'inputs/ORDER.json', '129e791d5b45c279443ff9e1edef5ac33d5abc51717ecbae8265abea5c247ae7'),
    'DISPATCH': ('c2802', D02 + 'inputs/DISPATCH.json.gz', '14fe756dcac93a0f3b2b7f38ba7b998dec89d56d5171b691af4fae45e5d83d11'),
    'PLAN': ('c2802', D02 + 'inputs/PLAN.json.gz', 'afb3c5c8134fc2cfce0b50a21758490c225574994b2c3c5161e53e2355acc6fa'),
    'TEMPLATE': ('c2802', D02 + 'inputs/GLOBAL-TEMPLATE.json.gz', '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'),
    'CLAIM': ('c2802', D02 + 'CLAIM.json', 'a2fcbc8a3ad3095ecbd310a26c02e9d11c28e4d105669a08bbdfb39d7704db51'),
    'PROFILE': ('c2802', D02 + 'PROFILE.json', '9d71407ded0b17496b0f94ca896355933a850dc6fc8456e39b0a1f72995b1406'),
    'K2751': ('c2802', D02 + 'evidence/PR2751-CLAIM.json', '78e99222196fca8b74a895b9e2db40a0e4afd1d69cd4fb52f38bfb157bac2438'),
    'K2751_own': ('c2751', D51 + 'CLAIM.json', '78e99222196fca8b74a895b9e2db40a0e4afd1d69cd4fb52f38bfb157bac2438'),
    'K2766': ('c2802', D02 + 'evidence/PR2766-CLAIM.json', '399e20ffb8bac62363f7d48c59021d5afef5f62bb6c51986ca847b02ec1e73a8'),
    'K2767': ('c2802', D02 + 'evidence/PR2767-OUTER-CLAIM.json', '252b7bbdbef293f643633ff95ba7d1eabbe83e1eebcd1cb06f51834256bde1f3'),
    'X_W_base': ('c2818', D18 + 'new/borrow/words/BORROW-WORD-43base.json.gz', 'dca8becca633ffc5e998985631bcbcab1123b27ca7f10ac6a96b1ec21ce69a66'),
    'X_W_extra': ('c2818', D18 + 'new/borrow/words/BORROW-WORD-43extra.json.gz', '6bcb3c2c73eaf7558ddc6ef6b484334f8d96b9d2b227e265483b657de00f4bb7'),
    'X_FILL': ('c2818', D18 + 'new/borrow-fill/FILL.json.gz', '2f2a25a8d82b424b1e643a8a5167361fcc5ab33cfbc6f186f4cb7ddcaf9df7d9'),
    'X_ORDER': ('c2818', D18 + 'new/borrow-fill/ORDER.json', '129e791d5b45c279443ff9e1edef5ac33d5abc51717ecbae8265abea5c247ae7'),
    'X_DISPATCH': ('c2818', D18 + 'new/borrow-fill/DISPATCH.json', 'fd8132ec8957b908ee6d871216848f18bafc6bd9304acd6185519ee26d97b1ca'),
    'X_PROV': ('c2818', D18 + 'new/BORROW-PROVIDERS.json', '391075b1411a3976850c633f92f58c35ed3f046f09d55bd435d7545124543fd4'),
    'X_R7_base': ('c2818', D18 + 'new/borrow/inputs/retired7_43base.json', '74daf5826d9191be4613a61447f4dc12789190fb49a3219f6a9df63075cac1e1'),
    'X_R7_extra': ('c2818', D18 + 'new/borrow/inputs/retired7_43extra.json', '25d9774b512da78f042287ce1de91c79c8658d06488b8fe94e548cbdd036f034'),
    # attribution inputs: PR #2766's own words and claim; #2802's recorded retired5 endpoint, fill hash and local profile
    'W66_base': ('c2766', D66 + 'inputs/WORD-base.json.gz', '80e309cc16d0a86a0854d32f4f43e0d856768ea3cf5b6437061b427997ae4790'),
    'W66_extra': ('c2766', D66 + 'inputs/WORD-extra.json.gz', '88e55acb7e274c62fbb0deab7f420d85fde3c2a471735222f0b5d039bc34e2e6'),
    'K2766_own': ('c2766', D66 + 'CLAIM.json', '399e20ffb8bac62363f7d48c59021d5afef5f62bb6c51986ca847b02ec1e73a8'),
    'R5_ADMISSION': ('c2802', D02 + 'evidence/retired5/ADMISSION-RESULT.json', 'e441d6bfef1554491087a5b4701a8b23b331af3b57f77a38f3de4a47d940a6bf'),
    'R5_HOOK': ('c2802', D02 + 'evidence/retired5/HOOK-RESULT.json', '76b67d54df3a6da3bb7f6fe3402f11d2926cb48353bf068dc34eeb560784771a'),
}
STAGES = ('refit5', 'alias5', 'refit5c', 'refit7', 'hostmove2', 'alias7', 'refit7c')
STAGE_SHA = {
    ('refit5', 'base'): 'ff434b1820339f0f7c2c8ba7982edc4c236e522ea30aaa56890206c0fa96f642',
    ('refit5', 'extra'): 'ff434b1820339f0f7c2c8ba7982edc4c236e522ea30aaa56890206c0fa96f642',
    ('alias5', 'base'): 'a9ef916e6afcba33345bce3fd0e33606f09f340e0378cf017e2994a9206b969d',
    ('alias5', 'extra'): 'aeff3d1ffa74e4bffa892293f88a968e2c2b0330ad61128696a6bce7bc383b46',
    ('refit5c', 'base'): 'cd8e6b7f8b8dacf21875f465e3df05bf827f12dd063fe1be7557c7281bff16f1',
    ('refit5c', 'extra'): 'cd8e6b7f8b8dacf21875f465e3df05bf827f12dd063fe1be7557c7281bff16f1',
    ('refit7', 'base'): 'c1ca4637c3b88828d2628c87a20f93088769dbceb9f487cb75ce90ec1a0ff5f7',
    ('refit7', 'extra'): 'c1ca4637c3b88828d2628c87a20f93088769dbceb9f487cb75ce90ec1a0ff5f7',
    ('hostmove2', 'base'): 'ee0f0de1ebe2f84e37e439f783a76f5d210fa1c34b3497a8d3c490296ee88e3b',
    ('hostmove2', 'extra'): 'd06b7a56b457c16ea138e8265fc6f2d1b32711f0515a76137e86325a6f77a024',
    ('alias7', 'base'): '100558d0f0ffbb2df38668b3d2bc4e4e11d5f328f629f5b4d931b0f619d49700',
    ('alias7', 'extra'): '783ed700791b1dcd4bb35422f5fb8114a0c5d82773394b87a613e5f32da51250',
    ('refit7c', 'base'): '086dc27f17448ab9bddb2e890752cf13d5965a63cd79fcf25aa7f1c9402503df',
    ('refit7c', 'extra'): '086dc27f17448ab9bddb2e890752cf13d5965a63cd79fcf25aa7f1c9402503df',
}
for (_s, _t), _h in STAGE_SHA.items():
    PINS['ST_%s_%s' % (_s, _t)] = ('c2802', D02 + 'inputs/%s_43%s.json' % (_s, _t), _h)

# Claims under test, transcribed from the PR #2802 README / CLAIM.json text (not computed from its code).
CLAIMED = dict(
    aliases=[(606, 550), (635, 551), (637, 552), (638, 553), (639, 562), (667, 401), (669, 403)],
    moves=[(30, 401, 564), (31, 403, 565)],
    local_profile={1: 2382, 2: 648, 3: 268, 4: 128, 5: 26, 8: 8},
    inventory={4: 26, 5: 2, 7: 62, 8: 78, 9: 240}, helpers=408, roles=271728,
    complete_profile={1: 1603728, 2: 431568, 3: 185082, 4: 85248, 5: 27194, 8: 5328, 32: 1, 48: 26558},
    mass=4816512, C='0.001717794984118634663827',
    margin_2766='538010651632355557/1000000000000000000000000',
    margin_2751='326698885104162859/500000000000000000000000',
)
# canonical-JSON sha256 of the reconstructed retired5 fill (recorded when its gzip bytes matched #2802's fill_sha256)
RETIRED5_FILL_JSON_SHA = 'ef4bd5d44e707b4a26391328e784aec6763a7684c7c15720c6a5e9f743fb498b'
V, H = 112, 9
NSPACE = 2 * V + 480
FULL_GENS = tuple(1 << i for i in range(H))


class Fail(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Fail(msg)


# ----------------------------------------------------------------------------------------------- inputs
def clean_env():
    env = dict(os.environ)
    for k in list(env):
        if k.startswith('GIT_'):
            env.pop(k)
    return env


def read_blob(repo, commit, path):
    r = subprocess.run(['git', '-C', repo, 'cat-file', 'blob', '%s:%s' % (commit, path)], capture_output=True, env=clean_env())
    if r.returncode != 0:
        raise Fail('cannot read %s at %s (fetch refs/pull/<n>/head first): %s' % (path, commit[:12], r.stderr.decode()[:200]))
    return r.stdout


CANON = 'https://github.com/CrocSwap/integer-mult-bounds.git'
PULLS = dict(c2802=2802, c2751=2751, c2818=2818, c2766=2766)


def fetch_missing(repo):
    """fetch refs/pull/<n>/head (then the bare commit) only for absent pinned commits; writes only FETCH_HEAD"""
    for ck, sha in sorted(COMMIT.items()):
        have = subprocess.run(['git', '-C', repo, 'cat-file', '-e', sha + '^{commit}'], capture_output=True, env=clean_env())
        if have.returncode == 0:
            continue
        for ref in ('refs/pull/%d/head' % PULLS[ck], sha):
            subprocess.run(['git', '-C', repo, 'fetch', '--no-tags', '--quiet', CANON, ref], capture_output=True, env=clean_env())
            if subprocess.run(['git', '-C', repo, 'cat-file', '-e', sha + '^{commit}'], capture_output=True, env=clean_env()).returncode == 0:
                break


def load_all(repo, blob_dir):
    raw = {}
    for key, (ck, path, sha) in sorted(PINS.items()):
        if blob_dir:
            fp = os.path.join(blob_dir, COMMIT[ck][:12], path)
            with open(fp, 'rb') as fh:
                data = fh.read()
        else:
            data = read_blob(repo, COMMIT[ck], path)
        need(hashlib.sha256(data).hexdigest() == sha, 'pin mismatch ' + key)
        raw[key] = data
    js = {}
    for key, data in raw.items():
        if PINS[key][1].endswith('.gz'):
            data = gzip.decompress(data)
        js[key] = json.loads(data.decode())
    return js


# ----------------------------------------------------------------------------------------------- GF(2) frames as element sets
_SUB = {}


def sub(gens):
    """the subspace spanned by gens, as the frozenset of all its elements"""
    key = tuple(sorted(int(g) for g in gens))
    s = _SUB.get(key)
    if s is None:
        el = {0}
        for g in key:
            if g not in el:
                el |= {x ^ g for x in el}
        s = frozenset(el)
        _SUB[key] = s
    return s


def dim(s):
    return len(s).bit_length() - 1


ZERO = sub(())
FULL = sub(FULL_GENS)


_PERP = {}


def basis_of(s):
    span, out = {0}, []
    for x in sorted(s):
        if x not in span:
            out.append(x)
            span |= {y ^ x for y in span}
    return out


def perp(s):
    p = _PERP.get(s)
    if p is None:
        b = basis_of(s)
        p = frozenset(x for x in range(1 << H) if all(bin(x & u).count('1') % 2 == 0 for u in b))
        _PERP[s] = p
    return p


def gapply(cols, x):
    y = 0
    for i in range(H):
        if (x >> i) & 1:
            y ^= cols[i]
    return y


def warp_algebra(cols, U, E):
    """G invertible, G(U)=E, dim U = dim E, G^-T(U^perp)=E^perp and the K_G symplectic image sends L_U to L_E"""
    need(len(cols) == H and all(0 <= c < (1 << H) for c in cols), 'G shape')
    table = [gapply(cols, x) for x in range(1 << H)]
    need(len(set(table)) == 1 << H, 'G singular')
    inv = [0] * (1 << H)
    for x, y in enumerate(table):
        inv[y] = x
    need(len(U) == len(E), 'dim U != dim E')
    need(frozenset(table[u] for u in U) == E, 'G(U) != E')
    # G^-T as columns: bit j of G^-T(e_i) = bit i of G^-1(e_j)
    ginv_cols = [inv[1 << j] for j in range(H)]
    git_cols = [sum(((ginv_cols[j] >> i) & 1) << j for j in range(H)) for i in range(H)]
    need(frozenset(gapply(git_cols, p) for p in perp(U)) == perp(E), 'G^-T(U^perp) != E^perp')

    def M(x, z):
        gx = gapply(cols, x)
        return gx, gx ^ gapply(git_cols, x) ^ gapply(git_cols, z)
    LU = {(u, u ^ p) for u in U for p in perp(U)}
    LE = {(e, e ^ p) for e in E for p in perp(E)}
    need({M(x, z) for x, z in LU} == LE, 'K_G(L_U) != L_E')
    # symplectic: omega((x,z),(x',z')) = x.z' + z.x' preserved on a basis of F_2^18
    basis = [(1 << i, 0) for i in range(H)] + [(0, 1 << i) for i in range(H)]

    def om(a, b):
        return (bin(a[0] & b[1]).count('1') + bin(a[1] & b[0]).count('1')) % 2
    img = [M(*b) for b in basis]
    need(all(om(img[i], img[j]) == om(basis[i], basis[j]) for i in range(2 * H) for j in range(2 * H)), 'K_G not symplectic')
    return git_cols


# ----------------------------------------------------------------------------------------------- word program
def regs(e):
    if e[0] == 'add':
        return (e[1], e[2])
    return (e[1],)


def is_t(r):
    return V <= r < 2 * V


def program(w):
    """forward chronological event list: (time, sec, idx, item); warps get sec 'W' with idx = op"""
    ev = []
    t = 0
    for i, c in enumerate(w['initial_corrections']):
        ev.append((t, 'corr', i, ('corr', c['target'], c['source'], tuple(c['operator_word']), Fraction(c['coefficient']))))
        t += 1
    for sec in ('precondition', 'compensation', 'A', 'cut'):
        for i, e in enumerate(w[sec]):
            ev.append((t, sec, i, e))
            t += 1
    at = defaultdict(list)
    for op, rec in enumerate(w['warps'], 1):
        at[rec[0]].append(op)
    for p in range(len(w['B']) + 1):
        for op in at.get(p, []):
            ev.append((t, 'W', op, ('warp', w['warps'][op - 1][1], op)))
            t += 1
        if p < len(w['B']):
            ev.append((t, 'B', p, w['B'][p]))
            t += 1
    for i, e in enumerate(w['restore']):
        ev.append((t, 'restore', i, e))
        t += 1
    return ev


def item_regs(it):
    if it[0] == 'corr':
        return (it[1], it[2])
    if it[0] == 'warp':
        return (it[1],)
    return regs(it)


def derive_cleanup(w, ev):
    npre = w['prelude_events']
    restored = {int(k) for k in w['helper_final']}

    def b(r):
        return r + NSPACE if r in restored else r
    rec = []
    for (t, sec, i, it) in ev:
        if sec in ('corr', 'precondition', 'compensation', 'cut'):
            continue
        if sec == 'A' and i < npre:
            continue
        if it[0] == 'warp' or not is_t(it[1]):
            rec.append(it)
    out = []
    for it in reversed(rec):
        if it[0] == 'warp':
            out.append(('warp', b(it[1]), -it[2]))
        elif it[0] == 'add':
            out.append(('add', b(it[1]), b(it[2]), -it[3], it[4]))
        else:
            out.append(('scale', b(it[1]), it[3], it[2]))
    return out, restored


def check_cleanup(w, ev):
    der, restored = derive_cleanup(w, ev)
    given = w['cleanup']
    need(len(given) == len(der), 'cleanup length %d != derived %d' % (len(given), len(der)))
    for k, (g, d) in enumerate(zip(given, der)):
        need(tuple(g[:-1]) == d, 'cleanup item %d differs from derived inverse-reverse' % k)
        need(sub(g[-1]) == FULL, 'cleanup item %d not at FULL' % k)
    bufs = {r - NSPACE for g in given for r in (regs(g) if g[0] != 'warp' else (g[1],)) if r >= NSPACE}
    need(bufs <= restored, 'buffer for a non-restored register')
    return der, restored


# ----------------------------------------------------------------------------------------------- frames / profile (S3, S4)
def frames(w, live, ev, record=None):
    """literal frame chain; returns (profile, inventory, starts, ends, at_warp) ; record: dict to fill with per-gate pre-frames"""
    ports = w['ports']
    start = {}
    end = {}
    for r in live:
        if r < V:
            start[r], end[r] = sub((ports[r],)), FULL
        elif r < 2 * V:
            p = ports[r - V]
            start[r], end[r] = ZERO, frozenset(x for x in range(1 << H) if bin(x & p).count('1') % 2 == 0)
        else:
            start[r] = sub(w['start_extra'][str(r)]) if str(r) in w['start_extra'] else ZERO
            end[r] = sub(w['helper_final'][str(r)]) if str(r) in w['helper_final'] else FULL
    cur = dict(start)
    paid = Counter()
    npre = w['prelude_events']
    warps_seen = {}

    def climb(q, F, where):
        need(q in cur, 'register %d not live at %s' % (q, where))
        need(cur[q] <= F, 'frame not monotone: register %d at %s' % (q, where))
        d = dim(F) - dim(cur[q])
        if d:
            paid[d] += 1
        cur[q] = F
    after_A = False
    for (t, sec, i, it) in ev:
        if sec == 'corr':
            need(is_t(it[1]) and it[2] in live and it[2] >= 2 * V, 'correction target/source')
            need(start[it[2]] == ZERO, 'correction source with nonzero entrance frame')
            need(all(w['warps'][abs(o) - 1][1] == it[2] for o in it[3]), 'correction source is not the lender of its operator')
            continue
        if sec in ('precondition', 'compensation'):
            need(it[-1] == [] and is_t(it[1]), 'wrapper gate not a zero-frame target write')
            for q in item_regs(it):
                need(q in cur, 'wrapper touches non-live %d' % q)
                need(not (q >= 2 * V and (str(q) in w['start_extra'] or str(q) in w['helper_final'])),
                     'wrapper touches an entering or restored helper %d' % q)
            continue
        if sec == 'A' and i < npre:
            if it[0] == 'warp':
                _, r, op, fr, to = it
                rec = w['warps'][abs(op) - 1]
                need(rec[1] == r, 'prelude warp lender')
                U, E = (sub(fr), sub(to))
                if op > 0:
                    warp_algebra(rec[2], U, E)
                else:
                    warp_algebra(rec[2], E, U)
                need(cur[r] == U, 'prelude warp frame mismatch on %d' % r)
                cur[r] = E
            else:
                need(is_t(it[1]), 'prelude non-target write')
                if record is not None:
                    record[(sec, i)] = {q: cur[q] for q in regs(it)}
                for q in regs(it):
                    climb(q, sub(it[-1]), 'A%d' % i)
            continue
        if sec in ('cut', 'W', 'B', 'restore') and not after_A:
            after_A = True
            lev = {int(k): sub(v) for k, v in w['target_levels'].items()}
            for tt in range(V):
                need(cur[V + tt] == lev.get(tt, ZERO), 'target %d off its level after A' % tt)
            for q, U in zip(w['centers'], w['center_frames']):
                U = sub(U)
                need(cur[q] == U, 'centre %d frame' % q)
                served = {lev.get(e[1] - V, ZERO) for e in w['cut'] if e[2] == q}
                for T in sorted(served, key=lambda s: -len(s)):
                    need(T <= U, 'centre chain not nested')
                    if T != U:
                        paid[dim(U) - dim(T)] += 1
                    U = T
        if sec == 'cut':
            need(it[-1] is None and is_t(it[1]), 'cut gate shape')
            continue
        if sec == 'W':
            op = i
            pos, L, cols, U, E = w['warps'][op - 1]
            U, E = sub(U), sub(E)
            need(L in cur and not is_t(L), 'warp %d lender not live' % op)
            warp_algebra(cols, U, E)
            need(cur[L] == U, 'warp frame mismatch: op %d lender %d (U is not the propagated frame)' % (op, L))
            warps_seen[op] = (dict(U=U, E=E, cur_before=cur[L]))
            cur[L] = E
            continue
        if sec in ('A', 'B', 'restore'):
            F = sub(it[-1])
            if record is not None:
                record[(sec, i)] = {q: cur[q] for q in regs(it)}
            for q in regs(it):
                climb(q, F, '%s%d' % (sec, i))
    for q in live:
        climb(q, end[q], 'end')
    inv = Counter(dim(end[r]) - dim(start[r]) for r in live if r >= 2 * V)
    return paid, inv, start, end, warps_seen


# ----------------------------------------------------------------------------------------------- second frame method (S3/S4)
def rref(vecs):
    """canonical reduced row-echelon basis of span(vecs) over GF(2), as a sorted tuple (second representation)"""
    rows = []
    for v in vecs:
        v = int(v)
        for b in rows:
            if v ^ b < v:
                v ^= b
        if v:
            rows = [b ^ v if b ^ v < b else b for b in rows]
            rows.append(v)
            rows.sort(reverse=True)
            # re-reduce so that every pivot (top bit) is cleared from the other rows
            out = []
            for b in rows:
                for c in out:
                    if b ^ c < b:
                        b ^= c
                out.append(b)
            rows = out
            for i in range(len(rows)):
                for j in range(len(rows)):
                    if i != j and (rows[j] >> (rows[i].bit_length() - 1)) & 1:
                        rows[j] ^= rows[i]
            rows.sort(reverse=True)
    return tuple(rows)


def r_le(a, b):
    """span(a) <= span(b) for canonical bases"""
    return rref(a + b) == b


def frames_rref(w, live):
    """independent recount: profile, inventory and every warp's U against the propagated frame, with RREF bases"""
    full = rref(FULL_GENS)
    ports = w['ports']
    cur, end, start = {}, {}, {}
    for r in live:
        if r < V:
            start[r], end[r] = rref([ports[r]]), full
        elif r < 2 * V:
            p = ports[r - V]
            start[r] = ()
            end[r] = rref([x for x in range(1, 1 << H) if bin(x & p).count('1') % 2 == 0])
        else:
            start[r] = rref(w['start_extra'].get(str(r), []))
            end[r] = rref(w['helper_final'][str(r)]) if str(r) in w['helper_final'] else full
    cur = dict(start)
    paid = Counter()

    def up(q, F):
        need(r_le(cur[q], F), 'rref: non-monotone climb on %d' % q)
        if len(F) > len(cur[q]):
            paid[len(F) - len(cur[q])] += 1
        cur[q] = F
    for e in w['A'][:w['prelude_events']]:
        if e[0] == 'warp':
            need(cur[e[1]] == rref(e[3]), 'rref: prelude warp frame')
            cur[e[1]] = rref(e[4])
        else:
            for q in regs(e):
                up(q, rref(e[-1]))
    for e in w['A'][w['prelude_events']:]:
        for q in regs(e):
            up(q, rref(e[-1]))
    lev = {int(k): rref(v) for k, v in w['target_levels'].items()}
    for q, U in zip(w['centers'], w['center_frames']):
        U = rref(U)
        need(cur[q] == U, 'rref: centre frame')
        for T in sorted({lev.get(e[1] - V, ()) for e in w['cut'] if e[2] == q}, key=len, reverse=True):
            need(r_le(T, U), 'rref: centre chain')
            if T != U:
                paid[len(U) - len(T)] += 1
            U = T
    at = defaultdict(list)
    for op, rec in enumerate(w['warps'], 1):
        at[rec[0]].append(op)
    for p in range(len(w['B']) + 1):
        for op in at.get(p, []):
            pos, L, cols, U, E = w['warps'][op - 1]
            need(cur[L] == rref(U), 'rref: warp %d U is not the propagated frame of %d' % (op, L))
            need(rref([gapply(cols, u) for u in U]) == rref(E), 'rref: G(U) != E for warp %d' % op)
            cur[L] = rref(E)
        if p < len(w['B']):
            for q in regs(w['B'][p]):
                up(q, rref(w['B'][p][-1]))
    for e in w['restore']:
        for q in regs(e):
            up(q, rref(e[-1]))
    for q in live:
        up(q, end[q])
    inv = Counter(len(end[r]) - len(start[r]) for r in live if r >= 2 * V)
    return dict(sorted(paid.items())), dict(sorted(inv.items()))


# ----------------------------------------------------------------------------------------------- free-algebra replay (S2)
class Words:
    """interned reduced words of the free group; id 0 is the empty word"""

    def __init__(self):
        self.first = [0]
        self.rest = [0]
        self.kids = {}

    def lmul(self, op, wid):
        if self.first[wid] == -op:
            return self.rest[wid]
        k = (op, wid)
        n = self.kids.get(k)
        if n is None:
            n = len(self.first)
            self.first.append(op)
            self.rest.append(wid)
            self.kids[k] = n
        return n


DUAL = 100000


def replay(w, live, ev, cleanup, restored, dual):
    W = Words()
    rows = {r: {(r, 0): Fraction(1)} for r in live}
    for c in restored:
        rows[c + NSPACE] = {}

    def addrow(dst, src, q):
        for k, x in src.items():
            y = dst.get(k, 0) + q * x
            if y:
                dst[k] = y
            else:
                dst.pop(k, None)

    def lm(row, op):
        return {(v, W.lmul(op, wid)): x for (v, wid), x in row.items()}

    def step(it):
        k = it[0]
        if k == 'corr':
            _, t, s, word, c = it
            if not dual:
                row = rows[s]
                for op in reversed(word):
                    row = lm(row, op)
                addrow(rows[t], row, c)
            else:
                row = rows[t]
                for op in word:          # (K_o1..K_ok)^T = K_ok^T..K_o1^T and K_o^T = (D_o)^-1
                    sg = 1 if op > 0 else -1
                    row = lm(row, -sg * (abs(op) + DUAL))
                addrow(rows[s], row, -c)
        elif k == 'warp':
            op = it[2]
            if dual:
                op = (1 if op > 0 else -1) * (abs(op) + DUAL)
            rows[it[1]] = lm(rows[it[1]], op)
        elif k == 'add':
            q = Fraction(it[3], it[4])
            need(it[1] != it[2], 'self add')
            if not dual:
                addrow(rows[it[1]], rows[it[2]], q)
            else:
                addrow(rows[it[2]], rows[it[1]], -q)
        elif k == 'scale':
            q = Fraction(it[2], it[3])
            need(q != 0, 'zero scale')
            if dual:
                q = 1 / q
            rows[it[1]] = {kk: q * x for kk, x in rows[it[1]].items()}
        else:
            raise Fail('unknown item ' + str(k))
    for (t, sec, i, it) in ev:
        if it[0] == 'warp' and sec == 'A':
            step(('warp', it[1], it[2]))
        else:
            step(it)
    if not dual:
        for tt in range(V):
            need(rows[V + tt] == {(V + tt, 0): 1, (tt, 0): 1}, 'forward target %d wrong before cleanup' % tt)
        for c in restored:
            need(rows[c] == {(c, 0): 1}, 'restored helper %d not its own input' % c)
            need(not any(v == c for r in live if r != c for (v, _) in rows[r]), 'restored input %d still read' % c)
            need(rows[c + NSPACE] == {}, 'buffer dirty before cleanup')
    for it in cleanup:
        step(it)
    for r in live:
        if dual and r < V:
            exp = {(r, 0): 1, (r + V, 0): -1}
        elif (not dual) and is_t(r):
            exp = {(r, 0): 1, (r - V, 0): 1}
        else:
            exp = {(r, 0): 1}
        need(rows[r] == exp, '%s endpoint wrong on register %d' % ('dual' if dual else 'forward', r))
    for c in restored:
        need(rows[c + NSPACE] == {}, 'zero buffer %d not returned to zero' % c)
    return len(W.first)


# ----------------------------------------------------------------------------------------------- second method: random matrix realisation mod p
PRIME = (1 << 61) - 1


def matmul(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) % PRIME for j in range(n)] for i in range(n)]


def matinv(A):
    n = len(A)
    M = [list(A[i]) + [1 if i == j else 0 for j in range(n)] for i in range(n)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c]), None)
        if p is None:
            return None
        M[c], M[p] = M[p], M[c]
        iv = pow(M[c][c], PRIME - 2, PRIME)
        M[c] = [x * iv % PRIME for x in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c]
                M[r] = [(x - f * y) % PRIME for x, y in zip(M[r], M[c])]
    return [row[n:] for row in M]


def realise(w, live, ev, cleanup, restored, dual, seed, d=4):
    rnd = random.Random(seed)
    K = {}
    for op in range(1, len(w['warps']) + 1):
        while True:
            A = [[rnd.randrange(PRIME) for _ in range(d)] for _ in range(d)]
            Ai = matinv(A)
            if Ai is not None:
                break
        At = [list(x) for x in zip(*A)]
        AiT = [list(x) for x in zip(*Ai)]
        # forward letters K, K^-1; dual letters D = K^-T, D^-1 = K^T
        K[op], K[-op], K[op + DUAL], K[-(op + DUAL)] = A, Ai, AiT, At
    vec = {r: [rnd.randrange(PRIME) for _ in range(d)] for r in live}
    init = {r: list(x) for r, x in vec.items()}
    for c in restored:
        vec[c + NSPACE] = [0] * d

    def mv(M, x):
        return [sum(M[i][k] * x[k] for k in range(d)) % PRIME for i in range(d)]

    def q_of(n, m):
        return n * pow(m % PRIME, PRIME - 2, PRIME) % PRIME

    def step(it):
        k = it[0]
        if k == 'corr':
            _, t, s, word, c = it
            c = q_of(c.numerator, c.denominator)
            if not dual:
                x = vec[s]
                for op in reversed(word):
                    x = mv(K[op], x)
                vec[t] = [(a + c * b) % PRIME for a, b in zip(vec[t], x)]
            else:
                x = vec[t]
                for op in word:
                    sg = 1 if op > 0 else -1
                    x = mv(K[-sg * (abs(op) + DUAL)], x)
                vec[s] = [(a - c * b) % PRIME for a, b in zip(vec[s], x)]
        elif k == 'warp':
            op = it[2]
            if dual:
                op = (1 if op > 0 else -1) * (abs(op) + DUAL)
            vec[it[1]] = mv(K[op], vec[it[1]])
        elif k == 'add':
            q = q_of(it[3], it[4])
            if not dual:
                vec[it[1]] = [(a + q * b) % PRIME for a, b in zip(vec[it[1]], vec[it[2]])]
            else:
                vec[it[2]] = [(a - q * b) % PRIME for a, b in zip(vec[it[2]], vec[it[1]])]
        else:
            q = q_of(it[2], it[3])
            if dual:
                q = pow(q, PRIME - 2, PRIME)
            vec[it[1]] = [a * q % PRIME for a in vec[it[1]]]
    for (t, sec, i, it) in ev:
        step(('warp', it[1], it[2]) if (it[0] == 'warp' and sec == 'A') else it)
    for it in cleanup:
        step(it)
    for r in live:
        if dual and r < V:
            exp = [(a - b) % PRIME for a, b in zip(init[r], init[r + V])]
        elif (not dual) and is_t(r):
            exp = [(a + b) % PRIME for a, b in zip(init[r], init[r - V])]
        else:
            exp = init[r]
        need(vec[r] == exp, 'matrix realisation (%s, seed %d) wrong on register %d' % ('dual' if dual else 'forward', seed, r))
    for c in restored:
        need(vec[c + NSPACE] == [0] * d, 'matrix realisation buffer %d nonzero' % c)


# ----------------------------------------------------------------------------------------------- S1 + occupancy timeline (S2)
def segments(w, ev):
    """per register: list of segments; segment k = (opening warp op or None, [(time, sec, idx, item)])"""
    seg = defaultdict(lambda: [[None, []]])
    for e in ev:
        t, sec, i, it = e
        if sec == 'W':
            seg[it[1]].append([it[2], [], (5, w['warps'][it[2] - 1][0] - 0.5)])
            continue
        for r in set(item_regs(it)):
            seg[r][-1][1].append(e)
    return seg


def role_map(P, W, aliases, moves):
    """declared map of parent roles (register, segment) to final registers; returns function (r, k) -> r'"""
    mp = {}
    for (h, L, op) in aliases:
        mp[(h, 0)] = (L, op)
    for (op, L0, L1, k0) in moves:
        mp[(L0, k0)] = (L1, op)
    return mp


SR = dict(corr=0, precondition=1, compensation=2, A=3, cut=4, B=5, restore=6)


def pk(e):
    return (SR[e[1]], e[2])


def s1_and_occupancy(P, W, live_W, decl, part='both'):
    """event-level diff P -> W and the per-register occupancy timeline; returns a report dict"""
    rep = {}
    if part == 'occ':
        return occupancy_only(P, W, rep)
    keys_same = ('ports', 'centers', 'center_frames', 'target_levels', 'precondition', 'compensation',
                 'initial_corrections', 'prelude_events', 'helper_final', 'cut', 'kind', 'base')
    need(set(P) == set(W), 'top-level keys differ')
    for k in keys_same:
        need(P[k] == W[k], 'field %s changed (undeclared)' % k)
    new_removed = [h for h, _ in CLAIMED['aliases']]
    need(W['removed'] == P['removed'] + new_removed, 'removed list is not parent + the seven followers')
    need({k: v for k, v in P['start_extra'].items() if int(k) not in new_removed} == W['start_extra'], 'start_extra change beyond the removed followers')
    need(all(W['report'][k] == P['report'][k] for k in ('R', 'h', 'v')), 'report R/h/v changed')
    # warps: 1..65 unchanged except 30, 31 replaced in place; 66..72 appended
    need(len(P['warps']) == 65 and len(W['warps']) == 72, 'warp counts')
    changed = [op for op in range(1, 66) if P['warps'][op - 1] != W['warps'][op - 1]]
    need(changed == [30, 31], 'warps changed in place: %s' % changed)
    need([W['warps'][op - 1][1] for op in range(66, 73)] == [L for _, L in CLAIMED['aliases']], 'appended warp lenders')
    need([(op, P['warps'][op - 1][1], W['warps'][op - 1][1]) for op in (30, 31)] == [(o, a, b) for o, a, b in CLAIMED['moves']], 'moved warp lenders')
    # A and restore: identical gates; frame changes only
    fr_changes = {}
    for sec in ('A', 'restore'):
        need(len(P[sec]) == len(W[sec]), 'section %s length' % sec)
        for i, (a, b) in enumerate(zip(P[sec], W[sec])):
            need(a[:-1] == b[:-1], 'gate %s%d changed' % (sec, i))
            if a[-1] != b[-1]:
                need(a[0] != 'warp', 'prelude warp frames changed')
                fr_changes[(sec, i)] = (a[-1], b[-1])
    # B: role-aligned comparison
    evP, evW = program(P), program(W)
    segP, segW = segments(P, evP), segments(W, evW)
    # parent segment index of each move's hostee = the segment opened by the old warp op
    moves = []
    for (op, L0, L1) in CLAIMED['moves']:
        k0 = next(k for k, s in enumerate(segP[L0]) if s[0] == op)
        moves.append((op, L0, L1, k0))
    aliases = [(h, L, 65 + j + 1) for j, (h, L) in enumerate(CLAIMED['aliases'])]
    mp = role_map(P, W, aliases, moves)
    # final register of every parent (register, time): walk the parent's segments
    target_of = {}
    for r, sl in segP.items():
        for k, s in enumerate(sl):
            dest = mp.get((r, k))
            for e in s[1]:
                target_of[(r, e[0])] = dest[0] if dest else r
    timeP = {e[0]: e for e in evP if e[1] != 'W'}
    # map parent non-warp events onto final events by (section, index)
    keyW = {(e[1], e[2]): e for e in evW if e[1] != 'W'}
    relabelled = Counter()
    for e in evP:
        t, sec, i, it = e
        if sec == 'W':
            continue
        f = keyW.get((sec, i))
        need(f is not None, 'parent event %s%d missing in final' % (sec, i))
        fit = f[3]
        if it[0] == 'corr':
            need(it == fit, 'correction changed')
            continue
        if sec in ('B',):
            exp = list(it[:-1])
            for j in ((1, 2) if it[0] == 'add' else (1,)):
                exp[j] = target_of.get((it[j], t), it[j])
            if exp != list(fit[:-1]):
                raise Fail('B%d: final gate %s is not the declared relabel %s of parent %s' % (i, fit[:-1], exp, it[:-1]))
            if exp != list(it[:-1]):
                relabelled[sec] += 1
            if it[-1] != fit[-1]:
                fr_changes[(sec, i)] = (it[-1], fit[-1])
        else:
            need(list(it) == list(fit) or (sec in ('A', 'restore')), 'event %s%d changed' % (sec, i))
    need(len([e for e in evP if e[1] == 'B']) == len([e for e in evW if e[1] == 'B']), 'B length changed')
    rep['B_relabelled_gates'] = relabelled['B']
    rep['frame_changes'] = len(fr_changes)
    # declared frames: last writer over the refit stages
    declared = {}
    for st in ('refit5', 'refit5c', 'refit7', 'refit7c'):
        for sec, i, F in decl[st]['frames']:
            declared[(sec, i)] = F
    undeclared = sorted(k for k in fr_changes if k not in declared or sub(declared[k]) != sub(fr_changes[k][1]))
    # frames of gates that the alias/hostmove stages re-emit are allowed only if unchanged or declared
    need(not undeclared, 'undeclared frame changes: %s' % undeclared[:6])
    notapplied = sorted(k for k in declared if sub(W[k[0]][k[1]][-1]) != sub(declared[k]))
    need(not notapplied, 'declared refit frames not present in the final word: %s' % notapplied[:6])
    rep['declared_frames'] = len(declared)
    rep['declared_frames_effective'] = len([k for k in declared if k in fr_changes])
    return rep, fr_changes, evW


def occupancy_only(P, W, rep):
    evP, evW = program(P), program(W)
    segP, segW = segments(P, evP), segments(W, evW)
    moves = []
    for (op, L0, L1) in CLAIMED['moves']:
        k0 = next(k for k, s in enumerate(segP[L0]) if s[0] == op)
        moves.append((op, L0, L1, k0))
    aliases = [(h, L, 65 + j + 1) for j, (h, L) in enumerate(CLAIMED['aliases'])]
    mp = role_map(P, W, aliases, moves)
    # occupancy timeline on the final word: every final segment = exactly one parent role, time-ordered
    occ = []
    for (h, L, op) in aliases:
        sP_L = segP[L]
        sW_L = segW[L]
        kWs = [k for k, s in enumerate(sW_L) if s[0] == op]
        need(len(kWs) == 1, 'OCC: alias warp %d is not on lender %d' % (op, L))
        kW = kWs[0]
        wtime = sW_L[kW][2]
        # the lender role(s) that precede the warp: all parent segments of L that stay on L
        stay = [e for k, s in enumerate(sP_L) if (L, k) not in mp for e in s[1]]
        lend_last = max(pk(e) for e in stay)
        fol = segP[h]
        need(len(fol) == 1, 'follower %d had warps in the parent' % h)
        fol_ev = fol[0][1]
        fol_first = min(pk(e) for e in fol_ev)
        need(lend_last < wtime, 'OCC: lender %d has an own event at/after its alias warp %d' % (L, op))
        need(fol_first > wtime, 'OCC: follower %d has an event before alias warp %d' % (h, op))
        need(all(e[1] in ('B', 'restore') for e in fol_ev), 'OCC: follower %d has events outside B/restore' % h)
        need(kW == len(sW_L) - 1 or all(pk(e) < sW_L[kW + 1][2] for e in fol_ev), 'OCC: follower %d outlives the segment' % h)
        # the final segment after the warp is exactly the follower's events (same times, same items up to relabel)
        segev = [(e[1], e[2]) for e in sW_L[kW][1]]
        need(segev == [(e[1], e[2]) for e in fol_ev], 'OCC: final segment of %d after warp %d is not exactly follower %d' % (L, op, h))
        need(all(e[1] == 'A' or e[1] in ('corr', 'precondition', 'compensation', 'cut') or e[1] == 'B' for e in stay), 'lender restore event')
        last_sec = next(e for e in stay if pk(e) == lend_last)
        occ.append(dict(follower=h, lender=L, op=op, warp_B_pos=W['warps'][op - 1][0],
                        lender_last=[last_sec[1], last_sec[2]], follower_first=['B', min(e[2] for e in fol_ev if e[1] == 'B')],
                        lender_events=len(stay), follower_events=len(fol_ev),
                        lender_sections=dict(Counter(e[1] for e in stay))))
    for (op, L0, L1, k0) in moves:
        host = segP[L0][k0][1]
        sW = segW[L1]
        kWs = [k for k, s in enumerate(sW) if s[0] == op]
        need(len(kWs) == 1, 'OCC: moved warp %d is not on new lender %d' % (op, L1))
        kW = kWs[0]
        wtime = sW[kW][2]
        own = [e for k, s in enumerate(segP[L1]) for e in s[1]]
        need(len(segP[L1]) == 1, 'new lender %d already a lender in the parent' % L1)
        need(max(pk(e) for e in own) < wtime, 'OCC: new lender %d acts at/after moved warp %d' % (L1, op))
        need(min(pk(e) for e in host) > wtime, 'OCC: hostee of %d enters before its moved warp' % op)
        need([(e[1], e[2]) for e in sW[kW][1]] == [(e[1], e[2]) for e in host], 'OCC: final segment of %d after warp %d is not exactly the hostee' % (L1, op))
        need(kW == len(sW) - 1, 'OCC: later warp on %d' % L1)
        # the old lender keeps no hostee event
        rest_old = [e for k, s in enumerate(segW[L0]) for e in s[1] if s[0] == op]
        need(not rest_old, 'old lender keeps the moved warp')
        last = max(own, key=pk)
        occ.append(dict(hostee_warp=op, old_lender=L0, new_lender=L1, warp_B_pos=W['warps'][op - 1][0],
                        old_warp_B_pos=P['warps'][op - 1][0], new_lender_last=[last[1], last[2]],
                        hostee_first=['B', min(e[2] for e in host if e[1] == 'B')], hostee_events=len(host)))
    # every final register: segments are exactly the mapped parent roles (complete partition)
    roles_to = defaultdict(list)
    for r, sl in segP.items():
        for k, s in enumerate(sl):
            dest = mp.get((r, k))
            if dest:
                roles_to[dest].append((r, k))
            else:
                roles_to[(r, s[0])].append((r, k))
    target_of = {}
    for r, sl in segP.items():
        for k, s in enumerate(sl):
            dest = mp.get((r, k))
            for e in s[1]:
                target_of[(r, e[0])] = dest[0] if dest else r

    def relabel(e):
        t, sec, i, it = e
        if it[0] == 'corr':
            return it
        x = list(it[:-1]) if sec in ('A', 'B', 'restore') and it[0] != 'warp' else list(it)
        if it[0] != 'warp':
            for j in ((1, 2) if it[0] == 'add' else (1,)):
                x[j] = target_of.get((it[j], t), it[j])
        return x

    def body(e):
        t, sec, i, it = e
        if it[0] == 'corr':
            return it
        return list(it[:-1]) if sec in ('A', 'B', 'restore') and it[0] != 'warp' else list(it)
    for r, sl in segW.items():
        for k, s in enumerate(sl):
            src = roles_to.get((r, s[0]), [])
            need(len(src) == 1, 'OCC: final segment (%d, opened by %s) maps to %d parent roles' % (r, s[0], len(src)))
            pr, pkk = src[0]
            pe = segP[pr][pkk][1]
            need([(e[1], e[2]) for e in s[1]] == [(e[1], e[2]) for e in pe],
                 'OCC: final segment (%d, %s) events differ from parent role (%d, %d)' % (r, s[0], pr, pkk))
            need([body(e) for e in s[1]] == [relabel(e) for e in pe],
                 'OCC: final segment (%d, %s) gate content differs from relabelled parent role (%d, %d)' % (r, s[0], pr, pkk))
    for h, _ in CLAIMED['aliases']:
        need(h not in segW or all(not s[1] for s in segW[h]), 'removed follower %d still has events' % h)
    rep['occupancy'] = occ
    rep['segments_checked'] = sum(len(sl) for sl in segW.values())
    return rep


# ----------------------------------------------------------------------------------------------- stage records vs diff
def stage_records(P, W, decl, fr_changes):
    rep = {}
    a5 = decl['alias5']['aliases']
    a7 = decl['alias7']['aliases']
    mv = decl['hostmove2']['moves']
    need([(a['h'], a['L']) for a in a5 + a7] == CLAIMED['aliases'], 'alias stage records')
    need([[a['pos'], a['L'], a['G'], a['U'], a['E']] for a in a5 + a7] == W['warps'][65:72], 'alias warp records')
    need([[m['pos'], m['L_new'], m['G'], m['U'], m['E']] for m in mv] == [W['warps'][29], W['warps'][30]], 'move warp records')
    need([m['old_record'] for m in mv] == [P['warps'][29], P['warps'][30]], 'move old records')
    need(len(decl['alias5']['declared_gate_edit']) == 70 and len(decl['hostmove2']['declared_gate_edit']) == 28 and
         len(decl['alias7']['declared_gate_edit']) == 28, 'declared gate edit counts')
    ins = Counter()
    per_stage = {}
    dels, adds = {}, {}
    for st in ('alias5', 'hostmove2', 'alias7'):
        k_st = Counter()
        for kind, i, g in decl[st]['declared_gate_edit']:
            ins[kind] += 1
            k_st[kind] += 1
            d = dels if kind == 'delete' else adds
            need(i not in d, 'B%d edited by two stages' % i)
            d[i] = g
        need(k_st['delete'] == k_st['insert'], 'stage %s: deletes and inserts do not pair up' % st)
        per_stage[st] = k_st['delete']
    rep['declared_gate_edits'] = dict(ins)
    rep['declared_edit_pairs_per_stage'] = per_stage
    # the declared edits are exactly the relabelled positions: deletes = parent gates, inserts = final gates
    moved = sorted(i for i in range(len(P['B'])) if P['B'][i][:-1] != W['B'][i][:-1])
    need(sorted(dels) == sorted(adds) == moved, 'declared gate-edit positions differ from the relabelled positions')
    need(all(dels[i] == P['B'][i][:-1] and adds[i] == W['B'][i][:-1] for i in moved), 'declared gate edits differ from parent/final gates')
    rep['relabelled_positions'] = len(moved)
    rep['refit_frames'] = {st: len(decl[st]['frames']) for st in ('refit5', 'refit5c', 'refit7', 'refit7c')}
    rep['refit7_prev'] = decl['refit7']['previous_frames']
    rep['refit7_dims'] = [[sec, i, dim(sub(F0)), dim(sub(W[sec][i][-1]))] for sec, i, F0 in decl['refit7']['previous_frames']]
    # refit7c records no previous frames; no earlier stage touches its gates, so the previous frame is the parent's
    earlier = {(sec, i) for st in ('refit5', 'refit5c', 'refit7') for sec, i, _ in decl[st]['frames']}
    need(not any((sec, i) in earlier for sec, i, _ in decl['refit7c']['frames']), 'refit7c gate also refitted earlier')
    rep['refit7c_dims'] = [[sec, i, dim(sub(P[sec][i][-1])), dim(sub(W[sec][i][-1]))] for sec, i, _ in decl['refit7c']['frames']]
    return rep


def refit_exactness(W, live, decl):
    """S3 refits: each declared frame contains the propagated floor (join of incident pre-frames); report exactness"""
    ev = program(W)
    rec = {}
    frames(W, live, ev, record=rec)
    out = []
    declared = []
    for st in ('refit5', 'refit5c', 'refit7', 'refit7c'):
        for sec, i, F in decl[st]['frames']:
            declared.append((st, sec, i, F))
    final_of = {}
    for st, sec, i, F in declared:
        final_of[(sec, i)] = st
    for st, sec, i, F in declared:
        if final_of[(sec, i)] != st:
            continue
        pre = rec[(sec, i)]
        floor = sub([x for s in pre.values() for x in s])
        Fs = sub(W[sec][i][-1])
        need(floor <= Fs, 'refit %s %s%d below the propagated floor' % (st, sec, i))
        out.append(dict(stage=st, gate='%s%d' % (sec, i), dim=dim(Fs), floor_dim=dim(floor), exact_floor=(Fs == floor)))
    return out


def above_floor_neutral(W, live, decl):
    """the declared refit frames above their propagated floor: lowering each one alone, and all of them together, to the
    floor keeps the frame chain legal (monotone climbs; every warp's U equals the propagated frame) and leaves the local
    profile unchanged, so these frames carry no cost"""
    ev = program(W)
    rec = {}
    base = dict(frames(W, live, ev, record=rec)[0])
    need(base == CLAIMED['local_profile'], 'final profile')
    above = {}
    for st in ('refit5', 'refit5c', 'refit7', 'refit7c'):
        for sec, i, F in decl[st]['frames']:
            floor = sub([x for s_ in rec[(sec, i)].values() for x in s_])
            if sub(W[sec][i][-1]) != floor:
                above[(sec, i)] = floor
    keys = sorted(above, key=lambda k: (SR[k[0]], k[1]))
    variants = [[k] for k in keys] + [keys]
    for sel in variants:
        w = dict(W)
        for sec in {k[0] for k in sel}:
            w[sec] = list(W[sec])
        for sec, i in sel:
            w[sec][i] = list(W[sec][i][:-1]) + [basis_of(above[(sec, i)])]
        paid = dict(frames(w, live, program(w))[0])
        need(paid == base, 'lowering %s to the floor changes the profile to %s' % (sel, dict(sorted(paid.items()))))
    return dict(above_floor=['%s%d dim %d floor %d' % (sec, i, dim(sub(W[sec][i][-1])), dim(above[(sec, i)])) for sec, i in keys],
                variants_checked=len(variants), profile_unchanged=True)


# ----------------------------------------------------------------------------------------------- stage chain (S1, attribution)
def apply_stage(state, name, patch):
    """own application of one declared stage: refits replace frames only; alias/move stages replace the listed
    fields and the report; the inverse-reverse cleanup is re-derived (our derive_cleanup)"""
    import copy
    w = copy.deepcopy(state)
    if name.startswith('refit'):
        for sec, i, F in patch['frames']:
            need(sec in ('A', 'B', 'restore') and w[sec][i][0] != 'warp', 'refit target %s%d' % (sec, i))
            w[sec][i] = list(w[sec][i][:-1]) + [F]
        w['report'] = dict(w['report'], local_profile=patch['local_profile'])
    else:
        need(set(patch['fields']) <= {'start_extra', 'removed', 'B', 'restore', 'warps'}, 'stage %s replaces unexpected fields' % name)
        need(patch['prelude_events'] == w['prelude_events'], 'prelude count')
        for k, v in patch['fields'].items():
            w[k] = copy.deepcopy(v)
        w['report'] = copy.deepcopy(patch['report'])
    der, _ = derive_cleanup(w, program(w))
    w['cleanup'] = [list(x) + [list(FULL_GENS[::-1])] for x in der]
    return w


def stage_chain(P, W, decl):
    """rebuild W from P through the seven declared stages; every intermediate state passes frames, profile and both replays"""
    st = P
    out = []
    states = {}
    for name in STAGES:
        st = apply_stage(st, name, decl[name])
        live = set(r for r in range(NSPACE) if r not in set(st['removed']))
        ev = program(st)
        paid, inv, _, _, _ = frames(st, live, ev)
        need(dict(paid) == {int(k): v for k, v in st['report']['local_profile'].items()}, 'stage %s profile %s' % (name, dict(paid)))
        need(dict(inv) == {int(k): v for k, v in st['report']['width_inventory'].items()}, 'stage %s inventory' % name)
        cl, restored = check_cleanup(st, ev)
        replay(st, live, ev, cl, restored, False)
        replay(st, live, ev, cl, restored, True)
        states[name] = st
        out.append(dict(stage=name, profile=dict(sorted(paid.items())), mass=sum(k * v for k, v in paid.items()),
                        helpers=len([r for r in live if r >= 2 * V])))
    norm = lambda w: json.loads(json.dumps(w))
    need(norm(st) == norm(W), 'the declared stages do not rebuild the final word')
    return out, states


# ----------------------------------------------------------------------------------------------- S5 fill
def windows_from_template(template, order):
    rank = {}
    for c in template['idle_children']:
        need(rank.get(c['child'], c['rank']) == c['rank'], 'idle child rank varies')
        rank[c['child']] = c['rank']
    pair_of_stage = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    blocks = []
    for e in template['execution_schedule']:
        if e['kind'] == 'local_cover_sweep':
            blocks.append([e])
        elif e['kind'] in ('idle_cover_sweep', 'bridge'):
            need(blocks, 'event before the first local sweep')
            blocks[-1].append(e)
    by_stage = {b[0]['stage']: b for b in blocks}
    seen = Counter()
    last = {}
    win = {}
    for t, (stage, rep) in enumerate(order):
        need(seen[rep] == stage, 'order is not stage-chronological per replica')
        seen[rep] += 1
        for e in by_stage[stage]:
            if e['kind'] == 'local_cover_sweep':
                last[(rep, pair_of_stage[stage])] = t
            elif e['kind'] == 'bridge':
                last[(rep, e['src'])] = t
                last[(rep, e['dst'])] = t
            else:
                lo = last.get((rep, e['pair']), -1)
                for c in e['child_indices']:
                    if c in rank:
                        win[(rep, c)] = (rank[c], lo, t)
    need(set(seen.values()) == {9} and len(seen) == 74, 'replica progression')
    return win


def static_widths(w, helpers):
    """hosting width of each live helper = dim(end frame) - dim(entrance frame), read from the word itself"""
    out = {}
    for r in helpers:
        s = sub(w['start_extra'][str(r)]) if str(r) in w['start_extra'] else ZERO
        e = sub(w['helper_final'][str(r)]) if str(r) in w['helper_final'] else FULL
        need(s <= e, 'entrance frame not inside end frame for %d' % r)
        out[r] = dim(e) - dim(s)
    return out


def s5_fill(js, words, live_by_tag, widths_by_tag, fill_key='FILL'):
    fill = js[fill_key]
    order = js['ORDER']
    dispatch = {(s, r): p for s, r, p in js['DISPATCH']}
    for s, r, p in fill['dispatch_overrides']:
        dispatch[(s, r)] = p
    need(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'fill columns')
    tag_of = {'gauge44': 'base', 'extra': 'extra'}
    need(live_by_tag['base'] == live_by_tag['extra'], 'live helper sets differ between words')
    live = live_by_tag['base']
    R = len(live)
    win = windows_from_template(js['TEMPLATE'], order)
    plan = js['PLAN']
    fam = {}
    used = defaultdict(int)
    per_call = [0] * len(order)
    rows = fill['rows']
    need(len(rows) == len(order) * R, 'role count %d != calls x word-derived R (%d x %d)' % (len(rows), len(order), R))
    for row in rows:
        need(len(row) == 6 and all(type(x) is int for x in row), 'role shape')
        t, h, o, c, port, off = row
        need(0 <= t < len(order) and 0 <= port < V, 'role bounds')
        need(0 <= h < R, 'FILL-HELPER-SET: helper index %d outside the word-derived inventory (R=%d)' % (h, R))
        need((o, c) in win, 'no window for owner %d child %d' % (o, c))
        cap, lo, hi = win[(o, c)]
        need(lo < t <= hi, 'role outside its window')
        need(not (per_call[t] >> h) & 1, 'helper hosted twice in one call')
        per_call[t] |= 1 << h
        fk = (t, o, 2 * plan['pairs'][str(c)] + plan['sides'][str(c)], port)
        need(fk not in fam, 'family hosts two helpers in one call')
        fam[fk] = 1
        width = widths_by_tag[tag_of[dispatch[tuple(order[t])]]][live[h]]
        need(off >= 0 and off + width <= cap, 'bin capacity')
        m = ((1 << width) - 1) << off
        b = (o, c, port)
        need(not used[b] & m, 'overlapping bin cells')
        used[b] |= m
    need(all(x == (1 << R) - 1 for x in per_call), 'FILL-HELPER-SET: some call does not host exactly the word-derived helper set')
    idle = Counter()
    for (o, c), (cap, lo, hi) in win.items():
        for port in range(V):
            m = used.get((o, c, port), 0)
            u = m.bit_length()
            need(m == (1 << u) - 1, 'bin not prefix-compact')
            if cap > u:
                idle[cap - u] += 1
    return dict(R=R, roles=len(rows), windows=len(win), idle=dict(sorted(idle.items())), dispatch=dict(Counter(dispatch[tuple(x)] for x in order)))


def fill_transform(js, liveP, liveW):
    """FILL = FILL2751 minus the seven removed followers' roles, renumbered, offsets re-tiled in old offset order"""
    gone = set(liveP) - set(liveW)
    need(sorted(gone) == sorted(h for h, _ in CLAIMED['aliases']), 'removed helper set between fills')
    newidx = {r: i for i, r in enumerate(liveW)}
    old = defaultdict(list)
    for t, h, o, c, p, off in js['FILL51']['rows']:
        r = liveP[h]
        if r in gone:
            continue
        old[(o, c, p)].append((off, t, newidx[r]))
    new = defaultdict(list)
    for t, h, o, c, p, off in js['FILL']['rows']:
        new[(o, c, p)].append((off, t, h))
    need(set(old) == set(new), 'bins differ')
    for b in old:
        a = [(t, h) for off, t, h in sorted(old[b])]
        n = [(t, h) for off, t, h in sorted(new[b])]
        need(a == n, 'bin %s: roles or their order differ from the parent fill' % (b,))
    return dict(dropped_roles=len(js['FILL51']['rows']) - len(js['FILL']['rows']), bins=len(old))


# ----------------------------------------------------------------------------------------------- S6 moment root
SLACK = Decimal('1e-70')


def moment(profile, z, prec, rounding):
    """f(z) = sum n_r (r/73)^(1-z) at `prec` significant digits (z rational, all r < 73, so f increases in z).
    Python's Decimal ln() and exp() are correctly rounded with ROUND_HALF_EVEN whatever the context rounding mode;
    `rounding` applies only to the divisions, the subtraction, the products and the sums.  The value is therefore an
    approximation, not a directed bound; root_bracket() turns it into a bound with an explicit error budget."""
    with localcontext() as ctx:
        ctx.prec = prec
        ctx.rounding = rounding
        zd = Decimal(z.numerator) / Decimal(z.denominator)
        s = Decimal(0)
        for r, n in sorted(profile.items()):
            # (r/73)^(1-z) = exp((1-z) ln(r/73)); ln(r/73) < 0, 1-z > 0
            lr = (Decimal(r) / Decimal(73)).ln()
            s += Decimal(n) * ((Decimal(1) - zd) * lr).exp()
        return s


def root_bracket(profile, total, lo, hi):
    """certify f(lo) < total < f(hi), hence a root in (lo, hi).

    Error budget at 80 digits, with u = 1e-79 bounding the relative error of one rounded operation in any mode:
    z: rel. <= u; a = 1 - z: abs. <= 2u (0 < z < 1); q = r/73: rel. <= u; ln q: abs. <= u + |ln q| u <= 5.3u
    (|ln q| <= ln 73 < 4.3); y = a ln q: abs. <= 5.3u + 4.3 * 2u + 4.3u < 19u; exp(y): rel. <= e^(19u) - 1 + u < 21u;
    the product with n and at most 8 positive summands add <= 9u.  Hence |computed - f| < 30u f = 3e-78 f, far inside
    the relative slack 1e-70.  The widening itself is done at 100 digits with directed rounding (1 +- 1e-70 is exact
    there), so f_lo_upper >= f(lo) and f_hi_lower <= f(hi) rigorously; Decimal comparisons are exact."""
    up = moment(profile, lo, 80, ROUND_CEILING)
    dn = moment(profile, hi, 80, ROUND_FLOOR)
    with localcontext() as ctx:
        ctx.prec = 100
        ctx.rounding = ROUND_CEILING
        f_lo_upper = up * (Decimal(1) + SLACK)
        ctx.rounding = ROUND_FLOOR
        f_hi_lower = dn * (Decimal(1) - SLACK)
        ok = f_lo_upper < total < f_hi_lower
        margins = ('%.4e' % (total - f_lo_upper), '%.4e' % (f_hi_lower - total))
    return ok, (str(up)[:40], str(dn)[:40], margins)


def dec(q, digits):
    with localcontext() as ctx:
        ctx.prec = digits
        return str(Decimal(q.numerator) / Decimal(q.denominator))


# ----------------------------------------------------------------------------------------------- driver
def run_all(js, quick=False, log=print, skip=()):
    res = dict(rules={})

    def rule(name, fn):
        if any(name.startswith(p) for p in skip):
            return None
        try:
            v = fn()
            res['rules'][name] = dict(ok=True, info=v)
            log('PASS %-34s %s' % (name, '' if v is None else json.dumps(v, default=str)[:160]))
            return v
        except Fail as e:
            res['rules'][name] = dict(ok=False, info=str(e))
            log('FAIL %-34s %s' % (name, e))
            return None
        except Exception as e:  # a crash is a failure too, but is labelled so that controls cannot count it
            res['rules'][name] = dict(ok=False, info='ERROR %s: %s' % (type(e).__name__, e))
            log('FAIL %-34s ERROR %s: %s' % (name, type(e).__name__, e))
            return None
    # pins and identities
    rule('PIN-2751-COPIES', lambda: need(js['P_base'] == js['P51_base'] and js['P_extra'] == js['P51_extra'] and js['FILL51'] == js['FILL51_own'] and js['K2751'] == js['K2751_own'], 'copies differ') or 'byte-identical')
    words = {}
    live = {}
    widths = {}
    profiles = {}
    r5 = {}
    for tag in ('base', 'extra'):
        P, W = js['P_' + tag], js['W_' + tag]
        decl = {st: js['ST_%s_%s' % (st, tag)] for st in STAGES}
        liveW = [r for r in range(NSPACE) if r not in set(W['removed'])]
        liveP = [r for r in range(NSPACE) if r not in set(P['removed'])]
        live[tag] = [r for r in liveW if r >= 2 * V]
        live['P_' + tag] = [r for r in liveP if r >= 2 * V]
        widths[tag] = static_widths(W, live[tag])
        widths['P_' + tag] = static_widths(P, live['P_' + tag])
        out = {}

        def s1():
            rep, fr, evW = s1_and_occupancy(P, W, liveW, decl)
            out['ev'] = evW
            out['fr'] = fr
            return rep
        rule('S1-DIFF-%s' % tag, s1)
        rule('OCC-TIMELINE-%s' % tag, lambda: s1_and_occupancy(P, W, liveW, decl, part='occ'))
        rule('S1-STAGE-RECORDS-%s' % tag, lambda: stage_records(P, W, decl, out.get('fr', {})))
        ev = program(W)

        def s3s4():
            paid, inv, start, end, ws = frames(W, set(liveW), ev)
            need(dict(paid) == CLAIMED['local_profile'], 'local profile %s' % dict(sorted(paid.items())))
            need(dict(paid) == {int(k): v for k, v in W['report']['local_profile'].items()}, 'report profile')
            prov = js['PROV']['gauge44' if tag == 'base' else 'extra']
            need(dict(paid) == {int(k): v for k, v in prov['actual_paid_profile'].items()}, 'provider profile')
            need(dict(inv) == CLAIMED['inventory'] and dict(inv) == {int(k): v for k, v in W['report']['width_inventory'].items()}, 'inventory %s' % dict(inv))
            need(len(live[tag]) == CLAIMED['helpers'], 'helper count')
            need(widths[tag] == {r: dim(end[r]) - dim(start[r]) for r in live[tag]}, 'widths')
            profiles[tag] = dict(paid)
            need([widths[tag][r] for r in live[tag]] == prov['widths'], 'provider widths differ from word-derived widths')
            news = {op: dict(U_dim=dim(ws[op]['U']), U_is_propagated=ws[op]['cur_before'] == ws[op]['U']) for op in (30, 31) + tuple(range(66, 73))}
            # frames() runs warp_algebra and the propagated-frame equality on every prelude warp item as well
            npw = sum(1 for e in W['A'][:W['prelude_events']] if e[0] == 'warp')
            return dict(profile=dict(sorted(paid.items())), mass=sum(k * v for k, v in paid.items()), inventory=dict(sorted(inv.items())),
                        helpers=len(live[tag]), warps_checked=len(ws), prelude_warp_items_checked=npw, new_or_moved=news)
        rule('S3S4-FRAMES-PROFILE-%s' % tag, s3s4)
        rule('S3-REFIT-EXACT-%s' % tag, lambda: refit_exactness(W, set(liveW), decl))
        rule('S3-ABOVE-FLOOR-NEUTRAL-%s' % tag, lambda: above_floor_neutral(W, set(liveW), decl))

        def s4b():
            prof, inv = frames_rref(W, sorted(liveW))
            need(prof == CLAIMED['local_profile'], 'rref profile %s' % prof)
            need(inv == CLAIMED['inventory'], 'rref inventory %s' % inv)
            profP, invP = frames_rref(P, sorted(liveP))
            need(profP == {int(k): v for k, v in P['report']['local_profile'].items()}, 'rref parent profile %s' % profP)
            return dict(profile=prof, inventory=inv, parent_profile=profP)
        rule('S4-FRAMES-RREF-%s' % tag, s4b)

        def chain():
            rep, states = stage_chain(P, W, decl)
            r5[tag] = states['refit5c']
            return rep
        rule('S1-STAGE-CHAIN-%s' % tag, chain)

        def s2():
            cl, restored = check_cleanup(W, ev)
            n1 = replay(W, set(liveW), ev, cl, restored, False)
            n2 = replay(W, set(liveW), ev, cl, restored, True)
            return dict(live_inputs=len(liveW), restored=len(restored), cleanup=len(cl), words_fwd=n1, words_dual=n2)
        rule('S2-REPLAY-FREE-%s' % tag, s2)

        def s2b():
            cl, restored = derive_cleanup(W, ev)
            for seed in (1, 2):
                realise(W, set(liveW), ev, cl, restored, False, seed)
                realise(W, set(liveW), ev, cl, restored, True, seed)
            return 'forward+dual, 2 seeds, 4x4 over GF(2^61-1)'
        rule('S2-REPLAY-MATRIX-%s' % tag, s2b)
        words[tag] = W

    def parent_positive():
        out = {}
        pprof = {}
        for tag in ('base', 'extra'):
            P = js['P_' + tag]
            liveP = [r for r in range(NSPACE) if r not in set(P['removed'])]
            evP = program(P)
            paid, inv, start, end, ws = frames(P, set(liveP), evP)
            prov = js['PROV51']['gauge44' if tag == 'base' else 'extra']
            need(dict(paid) == {int(k): v for k, v in P['report']['local_profile'].items()} ==
                 {int(k): v for k, v in prov['actual_paid_profile'].items()}, 'parent profile')
            need(dict(inv) == {int(k): v for k, v in P['report']['width_inventory'].items()}, 'parent inventory')
            need([widths['P_' + tag][r] for r in live['P_' + tag]] == prov['widths'], 'parent widths')
            cl, restored = check_cleanup(P, evP)
            replay(P, set(liveP), evP, cl, restored, False)
            replay(P, set(liveP), evP, cl, restored, True)
            pprof[tag] = dict(paid)
            out[tag] = dict(profile=dict(sorted(paid.items())), helpers=len(live['P_' + tag]))
        fill = s5_fill(js, None, {'base': live['P_base'], 'extra': live['P_extra']},
                       {'base': widths['P_base'], 'extra': widths['P_extra']}, fill_key='FILL51')
        prof = Counter({int(k): v for k, v in fill['idle'].items()})
        for pid, n in fill['dispatch'].items():
            for k, v in pprof['base' if pid == 'gauge44' else 'extra'].items():
                prof[k] += n * v
        need(dict(prof) == {int(k): v for k, v in js['K2751']['profile'].items()}, 'parent complete profile')
        out['fill'] = dict(R=fill['R'], roles=fill['roles'], idle=fill['idle'])
        return out
    rule('POSITIVE-PARENT-2751', parent_positive)
    rule('S5-FILL-WORD-DERIVED-R', lambda: s5_fill(js, words, {t: live[t] for t in ('base', 'extra')}, widths))
    rule('S5-FILL-TRANSFORM', lambda: fill_transform(js, live['P_base'], live['base']))

    def s6():
        need('base' in profiles and 'extra' in profiles, 'word profiles unavailable (S3S4 failed)')
        fill = s5_fill(js, words, {t: live[t] for t in ('base', 'extra')}, widths)
        prof = Counter({int(k): v for k, v in fill['idle'].items()})
        disp = fill['dispatch']
        for pid, n in disp.items():
            tag = 'base' if pid == 'gauge44' else 'extra'
            for k, v in profiles[tag].items():
                prof[k] += n * v
        need(dict(prof) == CLAIMED['complete_profile'], 'complete profile %s' % dict(sorted(prof.items())))
        need(dict(prof) == {int(k): v for k, v in js['CLAIM']['profile'].items()}, 'CLAIM profile')
        mass = sum(k * v for k, v in prof.items())
        need(mass == CLAIMED['mass'] == 73 * js['PLAN']['live'] * 2 - js['PLAN']['deficit'] * 2, 'mass')
        C = Fraction(CLAIMED['C'])
        need(Fraction(js['CLAIM']['complex_lower']) == C, 'claimed C')
        ok, vals = root_bracket(dict(prof), Decimal(66304), C, C + Fraction(1, 10 ** 24))
        need(ok, 'root not in [C, C+1e-24]: %s' % (vals,))
        ok2, _ = root_bracket(dict(prof), Decimal(66304), C + Fraction(1, 10 ** 24), C + Fraction(2, 10 ** 24))
        need(not ok2, 'bracket test vacuous')
        K = C - Fraction(1, 10 ** 46) - Fraction(1, 10 ** 70)
        need(Fraction(js['CLAIM']['kappa']) == K, 'kappa = C - 1e-46 - 1e-70')
        m51 = K - Fraction(js['K2751']['kappa'])
        m66 = K - Fraction(js['K2766']['kappa'])
        m67 = K - Fraction(js['K2767']['kappa'])
        need(m51 == Fraction(CLAIMED['margin_2751']) and m66 == Fraction(CLAIMED['margin_2766']) and m67 > 0, 'margins')
        return dict(mass=mass, root_in=[str(C), str(C + Fraction(1, 10 ** 24))], f_values=vals,
                    margin_2751=str(m51), margin_2766=str(m66), margin_2767=dec(m67, 40))
    rule('S6-PROFILE-MASS-ROOT', s6)

    def attribution():
        """retired5 (its words and fill are not published; #2802 records its endpoint, fill hash and local profile in
        evidence/retired5/) reconstructed independently: the refit5c state of both words, and PR2751's fill minus the five
        retired5 followers, re-tiled in old in-bin order.  Its complete profile must bracket the recorded retired5 root,
        and the reconstruction must equal #2802's recorded retired5 fill (hash) and local profile."""
        need('base' in r5 and 'extra' in r5, 'retired5 states unavailable (stage chain failed)')
        C5 = Fraction('0.001717409316335491643448')
        need(Fraction(js['CLAIM']['local_predecessor']['exact_kappa']) == C5 - Fraction(1, 10 ** 46) - Fraction(1, 10 ** 70), 'retired5 claim')
        need(Fraction(js['R5_ADMISSION']['complex_lower']) == C5, 'recorded retired5 endpoint')
        prof5, live5, wid5 = {}, {}, {}
        for tag in ('base', 'extra'):
            w5 = r5[tag]
            l5 = [r for r in range(NSPACE) if r not in set(w5['removed'])]
            prof5[tag] = dict(frames(w5, set(l5), program(w5))[0])
            need(prof5[tag] == {int(k): v for k, v in js['R5_HOOK']['words'][tag]['local_profile'].items()}, 'recorded retired5 local profile (%s)' % tag)
            live5[tag] = [r for r in l5 if r >= 2 * V]
            wid5[tag] = static_widths(w5, live5[tag])
        gone = set(live['P_base']) - set(live5['base'])
        need(sorted(gone) == [606, 635, 637, 638, 639], 'retired5 removed set')
        newidx = {r: i for i, r in enumerate(live5['base'])}
        order = js['ORDER']
        disp = {(a, b): p for a, b, p in js['DISPATCH']}
        bins = defaultdict(list)
        for t, h, o, c, p, off in js['FILL51']['rows']:
            r = live['P_base'][h]
            if r not in gone:
                bins[(o, c, p)].append((off, t, newidx[r]))
        rows = []
        for (o, c, p), lst in bins.items():
            pos = 0
            for off, t, h in sorted(lst):
                rows.append([t, h, o, c, p, pos])
                pos += wid5['base' if disp[tuple(order[t])] == 'gauge44' else 'extra'][live5['base'][h]]
        rows.sort(key=lambda x: (x[0], x[1]))
        js5 = dict(js)
        js5['FILL5'] = dict(js['FILL51'], rows=rows)
        fill = s5_fill(js5, None, live5, wid5, fill_key='FILL5')
        # #2802 hashes the gzip bytes of its fills; the serializer below reproduces its pinned FILL.json.gz bytes exactly
        # (checked first).  The canonical-JSON hash of the reconstruction is pinned too, for zlib builds whose deflate
        # output differs (then the gzip comparison is reported as not applicable).
        ser = lambda d: json.dumps(d, sort_keys=True, separators=(',', ':')).encode()
        gz = lambda d: gzip.compress(ser(d), compresslevel=9, mtime=0)
        serializer_ok = hashlib.sha256(gz(js['FILL'])).hexdigest() == PINS['FILL'][2]
        json_sha = hashlib.sha256(ser(js5['FILL5'])).hexdigest()
        need(json_sha == RETIRED5_FILL_JSON_SHA, 'reconstructed retired5 fill JSON %s' % json_sha)
        if serializer_ok:
            need(hashlib.sha256(gz(js5['FILL5'])).hexdigest() == js['R5_ADMISSION']['fill_sha256'], "reconstructed retired5 fill differs from #2802's recorded fill_sha256")
        prof = Counter({int(k): v for k, v in fill['idle'].items()})
        for pid, n in fill['dispatch'].items():
            for k, v in prof5['base' if pid == 'gauge44' else 'extra'].items():
                prof[k] += n * v
        ok, vals = root_bracket(dict(prof), Decimal(66304), C5, C5 + Fraction(1, 10 ** 24))
        need(ok, 'retired5 root not in [C5, C5+1e-24]')
        ok2, _ = root_bracket(dict(prof), Decimal(66304), C5 + Fraction(1, 10 ** 24), C5 + Fraction(2, 10 ** 24))
        need(not ok2, 'retired5 bracket test vacuous')
        C = Fraction(CLAIMED['C'])
        C66 = Fraction(js['K2766']['complex_lower'])
        return dict(retired5_profile=prof5['base'], retired5_idle=fill['idle'], retired5_complete=dict(sorted(prof.items())),
                    retired5_root_in=[str(C5), str(C5 + Fraction(1, 10 ** 24))], root_margins=vals[2],
                    recorded_endpoint_profile_equal=True,
                    fill_gzip_sha256_equals_recorded=(True if serializer_ok else 'not applicable: this zlib does not reproduce the pinned FILL bytes'),
                    fill_json_sha256=json_sha,
                    gain_retired5_over_2766=dec(C5 - C66, 30), gain_retired7_stages_over_retired5=str(C - C5))
    rule('ATTRIBUTION-RETIRED5', attribution)

    def attribution_2766():
        """PR #2766's own pinned words differ from W2751 only in the frame of B1151, which equals #2802's refit5c frame there;
        their recount equals PR #2766's reported local profile, and with PR #2751's fill they give PR #2766's claimed complete
        profile and root.  The other 19 refit5c frames that #2802's README lists with PR #2766's refit (A0-A11,
        B771/773/776/778/783/788, restore60) are not in PR #2766's word.  They are cost-neutral: applied alone to W2751, or
        reverted to W2751's frames in the final word, the frame chain stays legal and the local profile is unchanged."""
        need(js['K2766_own'] == js['K2766'], "#2802's copy of PR2766's claim differs from PR2766's own")
        b1151 = ('B', 1151)
        others = [('A', i) for i in range(12)] + [('B', i) for i in (771, 773, 776, 778, 783, 788)] + [('restore', 60)]
        out = {}
        profs = {}
        for tag in ('base', 'extra'):
            P, W, W66 = js['P_' + tag], js['W_' + tag], js['W66_' + tag]
            need(set(W66) == set(P), 'PR2766 word keys')
            diff_fields = sorted(k for k in P if P[k] != W66[k])
            need(diff_fields == ['B', 'report'], 'PR2766 word differs from W2751 in %s' % diff_fields)
            need(len(P['B']) == len(W66['B']), 'PR2766 B length')
            fdiff = [i for i, (a, b) in enumerate(zip(P['B'], W66['B'])) if a != b]
            need(fdiff == [1151] and P['B'][1151][:-1] == W66['B'][1151][:-1], 'PR2766 word changes B gates %s' % fdiff[:5])
            need({k: v for k, v in P['report'].items() if k != 'local_profile'} == {k: v for k, v in W66['report'].items() if k != 'local_profile'},
                 'PR2766 report differs beyond local_profile')
            frm = {(sec, i): F for sec, i, F in js['ST_refit5c_' + tag]['frames']}
            need(all(k in frm for k in others + [b1151]), 'credited frames not all in refit5c')
            need(sub(frm[b1151]) == sub(W66['B'][1151][-1]), "#2802's B1151 frame differs from PR2766's")
            l66 = [r for r in range(NSPACE) if r not in set(W66['removed'])]
            paid66 = dict(frames(W66, set(l66), program(W66))[0])
            need(paid66 == {int(k): v for k, v in W66['report']['local_profile'].items()}, 'PR2766 word profile differs from its report')
            base = {int(k): v for k, v in P['report']['local_profile'].items()}
            delta = {k: paid66.get(k, 0) - base.get(k, 0) for k in set(paid66) | set(base) if paid66.get(k, 0) != base.get(k, 0)}
            need(delta == {1: -2, 2: 1}, 'PR2766 delta %s' % delta)

            def prof_of(w):
                lw = [r for r in range(NSPACE) if r not in set(w['removed'])]
                return dict(frames(w, set(lw), program(w))[0])
            on_parent = apply_stage(P, 'refit-others', dict(frames=[[k[0], k[1], frm[k]] for k in others], local_profile=P['report']['local_profile']))
            need(prof_of(on_parent) == base, 'the 19 frames change the W2751 profile')
            all20 = apply_stage(P, 'refit-all20', dict(frames=[[k[0], k[1], frm[k]] for k in others + [b1151]], local_profile=P['report']['local_profile']))
            need(prof_of(all20) == paid66, 'the 20 frames together differ from PR2766 alone')
            reverted = apply_stage(W, 'refit-revert', dict(frames=[[k[0], k[1], P[k[0]][k[1]][-1]] for k in others], local_profile=W['report']['local_profile']))
            need(prof_of(reverted) == CLAIMED['local_profile'], 'reverting the 19 frames changes the final profile')
            profs[tag] = paid66
            out[tag] = dict(pr2766_word_change='B1151 dim %d -> %d' % (dim(sub(P['B'][1151][-1])), dim(sub(W66['B'][1151][-1]))),
                            pr2766_local_profile=dict(sorted(paid66.items())), delta=dict(sorted(delta.items())),
                            other_19_frames='cost-neutral on W2751 and on the final word')
        fill = s5_fill(js, None, {'base': live['P_base'], 'extra': live['P_extra']},
                       {'base': widths['P_base'], 'extra': widths['P_extra']}, fill_key='FILL51')
        prof = Counter({int(k): v for k, v in fill['idle'].items()})
        for pid, n in fill['dispatch'].items():
            for k, v in profs['base' if pid == 'gauge44' else 'extra'].items():
                prof[k] += n * v
        claimed = {int(k): v for k, v in js['K2766']['profile'].items()}
        need(dict(prof) == claimed, 'PR2766 complete profile %s' % dict(sorted(prof.items())))
        out['complete_profile_equals_PR2766_claim'] = True
        C66 = Fraction(js['K2766']['complex_lower'])
        ok, vals = root_bracket(dict(prof), Decimal(66304), C66, C66 + Fraction(1, 10 ** 24))
        need(ok, 'PR2766 root not in [C, C+1e-24]')
        out['PR2766_root_in'] = [str(C66), str(C66 + Fraction(1, 10 ** 24))]
        out['root_margins'] = vals[2]
        return out
    rule('ATTRIBUTION-PR2766-WORD', attribution_2766)

    def x2818():
        need(js['X_W_base'] == js['W_base'] and js['X_W_extra'] == js['W_extra'], 'words differ')
        need(js['X_FILL'] == js['FILL'] and js['X_ORDER'] == js['ORDER'] and js['X_PROV'] == js['PROV'], 'fill/order/providers differ')
        d1 = {(s, r): p for s, r, p in js['DISPATCH']}
        dx = js['X_DISPATCH']
        if isinstance(dx, dict):
            d2 = {tuple(map(int, k.split(','))): v for k, v in dx.items()}
        else:
            d2 = {(s, r): p for s, r, p in dx}
        need(d1 == d2, 'dispatch differs')
        out = {}
        for tag in ('base', 'extra'):
            pt = js['X_R7_' + tag]
            W = js['W_' + tag]
            for k, v in pt['fields'].items():
                need(W[k] == v, '#2818 retired7 field %s differs from #2802 final word' % k)
            need(pt['report'] == W['report'], 'report differs')
            out[tag] = sorted(pt['fields'])
        return dict(words='identical', fill='identical', order='identical', providers='identical', dispatch='same map', patch_fields=out)
    rule('X-2818-SAME-CONSTRUCTION', x2818)
    res['ok'] = all(v['ok'] for v in res['rules'].values())
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ap.add_argument('--blob-dir')
    ap.add_argument('--out')
    ap.add_argument('--fetch', action='store_true')
    a = ap.parse_args()
    if a.fetch and not a.blob_dir:
        fetch_missing(a.repo)
    js = load_all(a.repo, a.blob_dir)
    res = run_all(js)
    if a.out:
        with open(a.out, 'w') as fh:
            json.dump(res, fh, indent=1, sort_keys=True, default=str)
    print("PASS_T74_RETIRED7_INCREMENT_RULES" if res["ok"] else "FAIL_T74_RETIRED7_INCREMENT_RULES")
    return 0 if res['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
