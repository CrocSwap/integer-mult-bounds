# SPDX-License-Identifier: Apache-2.0
"""Shared helpers for verify_transport.py and atlas_bugs.py (standard library only).

New material prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance
(Claude Code, Anthropic). PR1043's builder/pipeline/verifier (Ali Romman, @aliromman) and
PR1345's transport atlas (hipotures) are vendored byte-for-byte under vendor/ with sha256 and
git-blob pins; main-tree inputs are read from the repository and checked against the sha256 and
git blob id they have at main commit MAIN_COMMIT. No path below is absolute.
"""
import copy
import hashlib
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_COMMIT = '0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2'
PR1043_HEAD = 'e309e17f83f5759b1ea1fa24a76f24838784cb4d'
PR1345_HEAD = 'b54a856aa79857d91cd5d65f8f7144e26c8c084f'

# repo-relative path -> (sha256, git blob id at MAIN_COMMIT)
MAIN_PINS = {
    'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz': ('e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f', '85a4499bf9e4911a705d50567a2c2ef6cf23739a'),
    'research/e8-bit-p111-tuned/tune/EXPECTED.json': ('b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4', 'e293ddc557742637f9f679f083a1a282d87b1b13'),
    'research/e8-bit-p111-tuned/tune/wlib.py': ('a37fdf3cdf5f62945c2a90193401c0e9edc9dd3cda8d8cb36a3b9c329ebe4dbc', '0e5f9a26f68cc415b793aa903cf6d105acbc8f03'),
    'research/e8-bit-p111-tuned/code/xcheck_p.py': ('af3decc877e27c00001cf56f50c6c09566e8e101297ab34c7860aed96a06d80e', '184f5dcf94a486cc7db91ca4db5865916bf26009'),
    'research/e8-bit-p111-tuned/data/selection9-p111.json': ('4ab1ed4529683cd184987f8bc3031fb7408b9cd22c25ab9cf541a8aaf896eaf1', 'e69ea66a3add357f570fc5552ab6368b3c8f9bb2'),
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/idle-axis-hosting/hosting_core.py': ('d8b90cd5d152df3c7c351230863d9e61816ad5e1f21d69bea1a86a5daad559a3', '68b536daa9e6546c0aa046934bf840aaa3c3fde3'),
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py': ('6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8', '3df12bd632f1fdba825ced57110a1fee82eb2857'),
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py': ('57e558c80a2fea6e291587b04afd76dfaee3550729997798b61f33daf90b8ec9', '8864ca9b942a3507171edca0cf6cbaaf10fcf434'),
    'research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py': ('81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482', '7d697cb45203fe72d97037403d6da41f71f3b7fd'),
    'research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/base_two_moment.py': ('aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098', '14a90fa0e788217856f070382c9e61bd7c603c61'),
    'research/native-complex-moment552/engines/moment.py': ('81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482', '7d697cb45203fe72d97037403d6da41f71f3b7fd'),
    'research/native-complex-moment552/engines/base_two_moment.py': ('aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098', '14a90fa0e788217856f070382c9e61bd7c603c61'),
    'research/native-complex-moment552/engines/outer.py': ('c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c', '43007488ad2c43187c77cc6798beff8b1cd76ad2'),
    'research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py': ('aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098', '14a90fa0e788217856f070382c9e61bd7c603c61'),
    'research/bit589-frame-optimum/frameopt.py': ('d18d5ed96a6d3146b2141b9bdd29900dd612defdcd5ebc7040542064ec89f237', '1622844ff90529c47e539f502c92b4f2371524e9'),
    'research/bit589-width-packing/packing.py': ('2bb5515807714807961289e4ee6958c3ad7e0c27bbec4d9212b138c662a6cc7b', 'a6079ee0dd4d8037be477a3c4497f472348bde07'),
    'research/bit589-width-packing/SOURCES.json': ('53fe98c8f01de7e32e3110e591d62e60292abb38cc11ecde4839f2eebd3b5fbc', 'f6a97de32691a1d426ac4819aad24c0c8414d97e'),
    'research/bit589-width7-windows-seed72/windows.py': ('a24295a51333b168ab73215f8a4bbb5bf831be829f572d1cde15fc322049c635', '4bb4f075ad5c1a49b4af310094bde6b2a4ea0c2e'),
}
# package-relative path -> (sha256, git blob id, path at the PR head)
VENDOR_PINS = {
    'vendor/pr1043/build.py': ('58f402c365eb18b9c3dd736523999676f1d1652e40c1a9b4f6967c1b7acb72df', '074d045cf6a5de84f67bd772ae422edc051d3c6e', 'research/bit-boundary-persistence/build.py'),
    'vendor/pr1043/pipeline.py': ('0adb958461b67d48cd3a32c3c235afd73692d51949083899324f090a5a9b2f22', 'a2f6eb503faf4de86143a45ec91cd5be14f32478', 'research/bit-boundary-persistence/pipeline.py'),
    'vendor/pr1043/verify.py': ('34a76019c5371acccfa8ccbf267a4bc0285ba44001ee8688f140085943cd2bc7', '8da708efb7f74e1fa7119975a10586a65f0ba5af', 'research/bit-boundary-persistence/verify.py'),
    'vendor/pr1043/CERTIFICATE.json': ('32c6cd6103006d627909cabdaf5083238c661a6582016a8b21075bd01c892eff', '56400920050c523e6e399f2455137b36c35cf528', 'research/bit-boundary-persistence/CERTIFICATE.json'),
    'vendor/pr1043/FRAME-PATHS.json': ('0d347b9e4d8a8336a707565deceb1d505cd138c97a56831643583b83d91c3b4f', 'b1862b43e1fa1ee0fb02e29b303801265638dae4', 'research/bit-boundary-persistence/FRAME-PATHS.json'),
    'vendor/pr1043/NOTICE.md': ('81136bf9a54638d69dcb8e8f5860c347843354d2133b537dce78fc5943e975ee', 'e703c9d9770a6e47919b815b70bedca0a14d3bd4', 'research/bit-boundary-persistence/NOTICE.md'),
    'vendor/pr1345/atlas.py': ('6e6e2a068fa5e40026b3ac81d7f3d88ea7c08fd0a0c0064c36f6ba33e4dfd95f', 'fe9fb21e82422a157369c28f8c5ab67cf63185ea', 'research/bit589-transport-atlas/atlas.py'),
    'vendor/pr1345/result.json': ('f7cb74c60ebd9bb1d4970e83d525ed37db1374c620b3459f63972431cf172287', '42d67d8e568f5af31c9fea66ea89d5531e271f8d', 'research/bit589-transport-atlas/result.json'),
    'vendor/pr1345/verify.sh': ('bcb29f58f9079257cf7a4fa98505e817a4ea0d80e7f9019fb58d524ea78f2d16', '4fde5cf1b3712bc9beb52171f0f698bb2761f338', 'research/bit589-transport-atlas/verify.sh'),
}

R439_REL = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
# canonical-JSON sha256 (PR1043's word_sha256 convention: sorted keys, no spaces, not gzip bytes)
CONTENT = {
    'r439': '5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b',
    'r438': '27609b6880f8913900c0e1758c63a482f8588c16fede1bd0071c6df36ef2e285',
    't154': '7aad486877b8c03866b8f1e6f909d12085da347d86aaae891f86f4e2dbc550d1',
}
# The transport (elementary A-op numbering of the R438 word, as in PR1345's atlas).
OP_INDEX, SLOT, NEW_FRAME = 2027, 154, 79
RECEIVER, SOURCE, OLD_FRAME = 444, 77, 186
ALT_SLOTS = (155, 425)          # the atlas' other improving representatives
BIRTH_SLOT = 230                # R439's helper birth position A[230] (same window segment as 425)

PROFILE = {
    'r439': {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19},
    'r438': {1: 1321, 2: 1344, 3: 78, 4: 44, 5: 102, 6: 11, 7: 18},
    't154': {1: 1322, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 18},
}
C_DEC = {
    'r439': '0.001733427039589844234749',
    'r438': '0.001734176288479865766692',
    't154': '0.001734220472884893243548',
}
M_BIT, LIVE, CALLS, REPLICAS, DEFICIT = 64, 28416, 288, 32, 10272


class Fail(Exception):
    pass


def require(ok, message):
    if not ok:
        raise Fail(message)


def refuse_optimized(tag):
    if not __debug__:
        print('FAIL_%s refusing to run under python -O (inherited checkers use assert)' % tag)
        sys.exit(2)


def default_repo(script_file):
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(script_file))))


def blob_id(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def check_bytes(data, sha, blob, label):
    require(hashlib.sha256(data).hexdigest() == sha, 'sha256 pin mismatch: ' + label)
    require(blob_id(data) == blob, 'git blob pin mismatch: ' + label)
    return data


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def content_sha(word):
    return hashlib.sha256(canonical(word)).hexdigest()


class Repo:
    def __init__(self, root):
        self.root = Path(root).resolve()
        require((self.root / 'research').is_dir() and (self.root / 'certificates').is_dir(),
                'not a repository root (use --repo): %s' % self.root.name)

    def read(self, rel):
        sha, blob = MAIN_PINS[rel]
        return check_bytes((self.root / rel).read_bytes(), sha, blob, rel)

    def path(self, rel):
        self.read(rel)
        return self.root / rel

    def verify_all(self):
        return {rel: self.read(rel) and MAIN_PINS[rel][0] for rel in MAIN_PINS}


def vendor_bytes(rel):
    sha, blob, _ = VENDOR_PINS[rel]
    return check_bytes((HERE / rel).read_bytes(), sha, blob, rel)


def verify_vendor():
    return {rel: vendor_bytes(rel) and VENDOR_PINS[rel][0] for rel in VENDOR_PINS}


def module_from_bytes(name, path, data):
    """Execute already pin-checked bytes as a module whose __file__ is `path`."""
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(data, str(path), 'exec'), mod.__dict__)
    return mod


def vendor_module(name, rel):
    return module_from_bytes(name, HERE / rel, vendor_bytes(rel))


def main_module(repo, name, rel):
    return module_from_bytes(name, repo.root / rel, repo.read(rel))


# ---------------------------------------------------------------- words
def flatten(gates):
    return [(f, t, s) for f, t, ss in gates for s in ss]


def op_gate(gates, op):
    k = 0
    for g, (_, _, ss) in enumerate(gates):
        if op < k + len(ss):
            return g, op - k
        k += len(ss)
    raise Fail('op index out of range')


def boundary(gates, slot):
    """Gate index g whose preceding gates hold exactly `slot` elementary ops, else None."""
    k = 0
    for g, (_, _, ss) in enumerate(gates):
        if k == slot:
            return g
        k += len(ss)
    return len(gates) if k == slot else None


def literal_c(word):
    """PR1043 build.py rule: C = literal reverse of A+B gates writing a source or helper, at frame 1."""
    v = word['v']
    require(len(word['frames'][1]) == v, 'frame 1 is not the full frame')
    return [[1, dst, sources[:]] for _, dst, sources in reversed(word['A'] + word['B'])
            if dst < v or dst >= 2 * v]


def move(word, slot=SLOT, frame=NEW_FRAME, op=OP_INDEX, rebuild_c=True):
    """Move elementary A-op `op` to elementary slot `slot` at `frame`, keeping the gate format."""
    A = word['A']
    g0, j = op_gate(A, op)
    require(A[g0] == [OLD_FRAME, RECEIVER, [SOURCE]] and j == 0,
            'op %d is not the single-source gate [186,444,[77]]' % op)
    k = boundary(A, slot)
    require(k is not None and k <= g0, 'slot %d is not a gate boundary before the op' % slot)
    new = copy.deepcopy(word)
    new['A'] = A[:k] + [[frame, RECEIVER, [SOURCE]]] + A[k:g0] + A[g0 + 1:]
    if rebuild_c:
        new['C'] = literal_c(new)
    return new


def split_move(word, wlib, slot=SLOT, frame=NEW_FRAME, op=OP_INDEX):
    """The scouting/atlas application: every A gate split into single-source gates, C by wlib.rebuild_C."""
    new = copy.deepcopy(word)
    ops = flatten(new['A'])
    o = ops.pop(op)
    ops.insert(slot, (frame, o[1], o[2]))
    new['A'] = [[f, t, [s]] for f, t, s in ops]
    new['C'] = wlib.rebuild_C(new)
    return new


def retarget_birth(r439, build):
    """R439 with the helper birth A[230] (q += x at frame79) retargeted to r += x and the read A[1993]
    (r += q) deleted; helper470 removed with PR1043's renaming; C and D rebuilt with PR1043's rules."""
    require(r439['A'][build.BIRTH] == [79, build.HELPER, [build.SOURCE]], 'R439 birth changed')
    require(r439['A'][build.READ] == [79, build.RECEIVER, [build.HELPER]], 'R439 read changed')
    w = copy.deepcopy(r439)
    w['A'] = [[79, build.RECEIVER, [build.SOURCE]] if i == build.BIRTH else g
              for i, g in enumerate(r439['A']) if i != build.READ]
    w['C'] = [[1, dst, s[:]] for _, dst, s in reversed(w['A'] + w['B'])
              if dst < w['v'] or dst >= 2 * w['v']]
    remap = lambda row: row - (row > build.HELPER)
    for phase in ('A', 'B', 'C'):
        w[phase] = [[f, remap(d), [remap(x) for x in s]] for f, d, s in w[phase]]
    w['start'].pop(build.HELPER)
    w['final'].pop(build.HELPER)
    w['ret'] = [remap(x) for x in w['ret']]
    w['R'] -= 1
    w['stats']['extra_carriers'] -= 1
    w['D'] = build.rebuild_compensation(w)
    return w


def int_keys(d):
    return {int(k): v for k, v in d.items()}


def save_word(path, word):
    import gzip
    Path(path).write_bytes(gzip.compress(canonical(word), mtime=0))


# ---------------------------------------------------------------- pricing (assemble9.py lines)
ENGINE_DIR = 'research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/'


def engines(repo):
    return (main_module(repo, 'c2_moment', ENGINE_DIR + 'moment.py'),
            main_module(repo, 'c2_base_two_moment', ENGINE_DIR + 'base_two_moment.py'))


def side(M, O, P, z, W=LIVE, m=M_BIT):
    """'accept' if both engines (with the inherited bad-residue surcharge) put the moment below 1 at z,
    'reject' if both put it above 1, else 'undecided'."""
    fb = 32 * m * m * sum(P.values())
    lo1, hi1 = M.moment(P, m, W, z, True)
    lo2, hi2 = O.moment(m, W, list(P.items()), z)
    bl, bh = O.moment(m, W, [(1, fb)], z)
    lo2 += bl / 10 ** 16
    hi2 += bh / 10 ** 16
    if hi1 < 1 and hi2 < 1:
        return 'accept'
    if lo1 > 1 and lo2 > 1:
        return 'reject'
    return 'undecided'


def certify(M, O, P, W=LIVE, m=M_BIT):
    """assemble9.py's endpoint: M.certify lower/upper, then the base-two engine with the surcharge
    accepts the lower endpoint and rejects the upper one; plus both engines at c and c + 10^-24."""
    root = M.certify(P, m, W, True)
    c, chi = Q(root['lower']), Q(root['upper'])
    E = sum(P.values())
    fb = 32 * m * m * E
    lo, hi = O.moment(m, W, list(P.items()), c)
    bl, bh = O.moment(m, W, [(1, fb)], c)
    require(hi + bh / 10 ** 16 < 1, 'assemble9: lower endpoint not accepted')
    lo2, hi2 = O.moment(m, W, list(P.items()), chi)
    bl2, bh2 = O.moment(m, W, [(1, fb)], chi)
    require(lo2 + bl2 / 10 ** 16 > 1, 'assemble9: upper endpoint not rejected')
    require(chi == c + Q(1, 10 ** 24), 'endpoint bracket is not one 10^-24 grid step')
    require(side(M, O, P, c) == 'accept' and side(M, O, P, c + Q(1, 10 ** 24)) == 'reject',
            'two-engine check at c / c+1e-24')
    return dict(lower=str(c), decimal=root['lower'], next_grid_point_rejected=str(chi),
                children=E, rank_mass=sum(r * n for r, n in P.items()))


def hosted_profile(local, remainders):
    H = Counter({r: CALLS * n for r, n in local.items()})
    for r, n in remainders.items():
        H[int(r)] += REPLICAS * n
    return dict(sorted((+H).items()))


# ---------------------------------------------------------------- subprocesses
def run_parallel(jobs, workers):
    """jobs: {name: argv}; returns {name: dict(rc, stdout, stderr, seconds)}."""
    pending = list(jobs.items())
    running, done = {}, {}
    while pending or running:
        while pending and len(running) < max(1, workers):
            name, argv = pending.pop(0)
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            running[name] = (proc, time.time())
        for name in list(running):
            proc, t0 = running[name]
            if proc.poll() is not None:
                out, err = proc.communicate()
                done[name] = dict(rc=proc.returncode, stdout=out, stderr=err, seconds=round(time.time() - t0, 1))
                del running[name]
        time.sleep(0.05)
    return done


def python_argv(script, *args):
    return [sys.executable, '-I', '-B', str(script), *map(str, args)]


# ---------------------------------------------------------------- PR1345 atlas variants
ATLAS_REL = 'research/bit589-transport-atlas/atlas.py'
ATLAS_PATCH_PIN = '05fc6199313c5f2e6082dc3dae4073a3a55abb63852ff89e547fae75b3a9248e'
ATLAS_C_LINE = 28
ATLAS_C589 = 'C = Q(1733427039589844234749, 10**24)\n'


def parse_patch(text):
    hunks = []
    for block in re.split(r'(?m)^(?=@@ )', text)[1:]:
        head, *body = block.splitlines(keepends=True)
        m = re.match(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', head)
        require(m is not None, 'malformed hunk header')
        hunks.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), body))
    require(text.startswith('--- a/' + ATLAS_REL + '\n+++ b/' + ATLAS_REL + '\n'), 'patch target')
    return hunks


def apply_patch(source, text, only=None):
    """Strict unified-diff application (every context and removed line must match exactly)."""
    lines = source.splitlines(keepends=True)
    out, pos = [], 0
    for h, (a, alen, b, blen, body) in enumerate(parse_patch(text)):
        if only is not None and h not in only:
            continue
        start = a - 1
        require(start >= pos, 'overlapping hunks')
        out += lines[pos:start]
        old = [l[1:] for l in body if l[:1] in (' ', '-')]
        new = [l[1:] for l in body if l[:1] in (' ', '+')]
        require(len(old) == alen and len(new) == blen, 'hunk length')
        require(lines[start:start + alen] == old, 'hunk %d does not match the source' % h)
        out += new
        pos = start + alen
    out += lines[pos:]
    return ''.join(out)


def atlas_patch_text():
    data = (HERE / 'atlas.patch').read_bytes()
    require(hashlib.sha256(data).hexdigest() == ATLAS_PATCH_PIN, 'atlas.patch pin mismatch')
    return data.decode()


def atlas_source(variant, c=None):
    """variant: 'pristine' (PR1345 head bytes), 'fix1' (first hunk only), 'patched' (all hunks).
    c: optional Fraction substituted for the hard-coded PR589 saving on line 28 (not part of the fix)."""
    src = vendor_bytes('vendor/pr1345/atlas.py').decode()
    if variant == 'fix1':
        src = apply_patch(src, atlas_patch_text(), only={0})
    elif variant == 'patched':
        src = apply_patch(src, atlas_patch_text())
    else:
        require(variant == 'pristine', 'unknown atlas variant')
    if c is not None:
        lines = src.splitlines(keepends=True)
        require(lines[ATLAS_C_LINE - 1] == ATLAS_C589 and src.count('C = Q(') == 1, 'atlas C line moved')
        lines[ATLAS_C_LINE - 1] = 'C = Q(%d, %d)\n' % (c.numerator, c.denominator)
        src = ''.join(lines)
    return src


def atlas_tree(repo, base, name, source):
    """A minimal tree so the atlas' ROOT = parents[2] finds the pinned wlib and engine copies."""
    root = Path(base) / name
    for rel, data in ((ATLAS_REL, source.encode()),
                      ('research/e8-bit-p111-tuned/tune/wlib.py', repo.read('research/e8-bit-p111-tuned/tune/wlib.py')),
                      ('research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py',
                       repo.read('research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py'))):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return root / ATLAS_REL


def traceback_tail(stderr, filename='atlas.py'):
    lines = [l for l in stderr.strip().splitlines()]
    frames = re.findall(r'File "[^"]*%s", line (\d+)' % re.escape(filename), stderr)
    return (int(frames[-1]) if frames else None), (lines[-1] if lines else '')


def environment():
    return dict(python=sys.version.split()[0], implementation=platform.python_implementation(),
                platform=platform.platform())


def write_receipt(path, receipt):
    Path(path).write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str) + '\n')
