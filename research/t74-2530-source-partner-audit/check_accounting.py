# SPDX-License-Identifier: Apache-2.0
"""Scope C and provenance: verifier overrides, recovered source, stock/precision accounting, endpoint, kappa, PR2474.

What is proved:
  * overrides: OVERRIDES.json's old hashes are PR2462's independent_core.py and new/rebind.py (rebind also equals
    PR2435's); the new hashes are PR #2530's files; ignoring CRLF, independent_core.py changes exactly two exact-
    equality pins (independent_core_change) and rebind.py exactly one expression, physical += zero buffers
    (rebind_change).  The pins, parsed as literals (never executed), equal what the words give: 16 line-[30] lifted
    targets and centre children {1:8, 7:8} (old pins = PR2462's words).  No other .py file of the PR2462 package
    carries the old pins (old_pin_files); all three checks are functions of the file bytes;
  * recovered source: PR #2530's source-pr2435.tar.gz (438 members) equals the PR2435 package tree (438 files) and,
    with pr2462-overlay.tar.gz (40 members) applied, equals the PR2462 package tree (443 files), including the
    overlay words (reconstruct; recon.pr2435_tree, recon.pr2462_tree, recon.overlay_words); archives are read in
    memory as data and nothing in them is executed or written to disk;
  * stock: physical = W + 8 + R + Z + 2 gives 66814 (R=422, Z=78 counted from the words) and reproduces PR2462's
    SPEC 66822 (R=430) and PR2435's SPEC 66826 (R=434); local mass falls 5315 -> 5251 = 8 x 8;
  * precision arithmetic: receipt prefix_l1 values give 62/69 bits (valid upper bounds); the global prefix computed
    from them, 69+37+666+666+4 = 1442, equals receipts/INDEPENDENT-GLOBAL.json prefix_bits and fits the payload 2048
    (= its charged_prefix_bits) (global_prefix); the row coefficient is the receipt's 19545 for every physical stock
    66736..66830; the receipt values are recorded next to the own ones;
  * endpoint: a rigorous integer fixed-point enclosure (2^-640, directed rounding, atanh/exp series with tail
    bounds) of M(a) = (1/W) sum n_r (r/73)^(1-a) on PROFILE.json; an endpoint is accepted only if the upper end of
    the enclosure is below 1 (accepts) and rejected only if the lower end is above 1 (rejects).  C =
    0.001713737921547504346752 is accepted and C + 1e-24 rejected; bisection brackets the root, so C is its
    24-digit floor; the conservative endpoint is likewise accepted/rejected; the ledger's two 2^-527 native moments
    bracket the enclosure at b;
  * kappa = C - 10^-70 - 10^-46 with the ledger's b = C - r0, q = C - 2 r0, delta = (1025/1024) r0, and the
    DIG = 24 instance of PR2462's grid-maximum rule (outer_grid, rule outer.grid): C*F integer, 0 < C - eps*q
    (= 2.0017e-104, recorded) < 1/F, floor(F eps q)/F - B = kappa (floor(F eps q) = C*F - 1, recorded);
  * PR2474 comparison: the pinned OUTER-CLAIM equals the file at the PR2474 commit; the gain computed from the two
    kappas equals CLAIM's latest_claim_gain exactly (latest_gain, rule pr2474.gain) and the percentage string is its
    100-digit truncation;
  * enclosure soundness guards: every exp series argument lies in [0, 1) in fixed point (the precondition of the
    "2 x next term" tail bound) and every lower end is <= its upper end;
  * positive control: the same moment checker's enclosure [lo, hi] at PR2462's certified 3000-digit endpoint
    C2462 (where 1 - 1e-2999 < M <= 1) satisfies lo <= 1 and hi >= 1 - 1e-2990, so an upper end that falls below
    the true moment by more than about 1e-2990 (an unsound exp upper rounding) is caught; C2462 - 1e-150 is
    accepted and C2462 + 1e-150 rejected;
  * negative controls, each asserting its rule (and, where one rule has several conditions, the condition) and each
    run through the function the main check uses.  accounting (8): the acceptance check fails at C + 1e-24, at the
    conservative C' + 1e-24 and at C2462 + 1e-150; at C2462 the enclosure straddles 1 (lo < 1 < hi), so the
    acceptance check must fail at C2462 + 1e-3000 and the rejection check at C2462 (a predicate on the wrong end of
    the enclosure would pass either); a wrong target pin; a reconstruction that keeps PR2435's base word; and the
    stock rule without the zero-buffer term (the pre-PR2530 rebind formula, 66736 != 66814).  outer_grid (3):
    kappa + 1e-70 (floor equality), q - 2e-70 (C - eps*q > 1/F) and q = C/eps (C - eps*q = 0).  overrides_diff
    (5): independent_core.py with one more line (a require) commented out, rebind.py with one more line (an assert)
    commented out, each once before and once after the allowed lines, and an extra .py file carrying the old target
    pin.  provenance_accounting (6): the source archive with one extra and with one missing member
    (recon.pr2435_tree), the overlay with one extra member and missing one of the files it adds (recon.pr2462_tree),
    CLAIM's gain + 1e-40 (pr2474.gain), and the global prefix from the largest receipt prefix_l1 doubled
    (precision.global_prefix).
Scope limits: the 63 outer inequalities are not re-derived; prefix_l1 is taken from the PR's receipts (only its
bit arithmetic is checked); the ledger was not regenerated here (PR2462's outer code is not run by this package).
"""
import ast
import io
import posixpath
import re
import tarfile
from collections import Counter
from fractions import Fraction as Q

import fill_check80 as FC
from audit_common import AuditFail, attempt, git_blob_id, need, positive, sha256

V, M, W, T, CALLS = 112, 73, 66304, 74, 666
PKG_HANDOFF = 'research/gmx-t74-borrow43-handoff/'
IC_PIN_LINES = (72, 93)          # 1-based lines of independent_core.py that may change
REBIND_LINE = 52
REBIND_SUFFIX = " + max(len(rd(d / 'CANONICAL-WORD.json.gz').get('zero_buffers', [])) for d in locs.values()))"
OLD_PIN_PATTERNS = (r'23,\s*34,\s*50,\s*108', r'1:\s*4,\s*7:\s*4,\s*8:\s*4')


def dec(q, digits):
    """Truncated decimal string of a non-negative Fraction."""
    n = q.numerator * 10 ** digits // q.denominator
    s = str(n).rjust(digits + 1, '0')
    return s[:-digits] + '.' + s[-digits:]


# ------------------------------------------------------------------------------------------ overrides ---
def _lines(raw):
    return raw.decode('utf-8').replace('\r\n', '\n').split('\n')


def changed_lines(old_raw, new_raw):
    old, new = _lines(old_raw), _lines(new_raw)
    need(len(old) == len(new), 'overrides: line count changed')
    return [(i + 1, old[i].strip(), new[i].strip()) for i in range(len(old)) if old[i] != new[i]]


def pin_literals(ic_text_lines):
    """Parse (never execute) the two pins of independent_core.py as Python literals."""
    targets = re.search(r'set\(levels\) == (\{[0-9, ]*\})', ic_text_lines[0])
    children = re.search(r'forward\) == (\{[0-9:, ]*\})', ic_text_lines[1])
    need(targets is not None and children is not None, 'overrides: pin lines not recognised')
    return sorted(ast.literal_eval(targets.group(1))), dict(ast.literal_eval(children.group(1)))


def pins_match_words(ic_new_line_pair, ic_old_line_pair, words):
    """New pins must equal the PR2530 words (both providers), old pins the PR2462 words."""
    for tag in ('base', 'extra'):
        for lines, key in ((ic_new_line_pair, 'pr2530'), (ic_old_line_pair, 'pr2462')):
            targets, children = pin_literals(lines)
            wsum = words[tag][key]
            need(targets == wsum['lifted_targets'], 'overrides: %s target pin != %s %s words' % (key, key, tag))
            need(Counter(children) == Counter(d for _, ch in wsum['copy_paths'] for d in ch),
                 'overrides: %s centre-child pin != %s %s words' % (key, key, tag))


def independent_core_change(old_raw, new_raw):
    """independent_core.py (bytes, CRLF ignored) changes exactly the lines IC_PIN_LINES; returns the changes."""
    ic = changed_lines(old_raw, new_raw)
    need([c[0] for c in ic] == list(IC_PIN_LINES), 'overrides: independent_core changed lines %r' % [c[0] for c in ic])
    return ic


def rebind_change(old_raw, new_raw):
    """rebind.py (bytes, CRLF ignored) changes exactly line REBIND_LINE, by appending the zero-buffer term to the
    physical stock expression; returns the change."""
    rb = changed_lines(old_raw, new_raw)
    need([c[0] for c in rb] == [REBIND_LINE] and rb[0][1].endswith('+ 8 + R + 2)')
         and rb[0][2] == rb[0][1][:-1] + REBIND_SUFFIX, 'overrides: rebind change %r' % [c[0] for c in rb])
    return rb


def old_pin_files(py_files, listing):
    """py_files: {relative path: bytes} of the .py files of the PR2462 package; listing: the .py paths of the pinned
    tree, which the scan must cover exactly.  Only independent_core.py may carry the old pins (any other file would
    also have needed editing); returns the files that carry them."""
    need(sorted(py_files) == sorted(listing), 'overrides: old-pin scan covers %d of %d .py files' % (len(py_files), len(listing)))
    hits = sorted(rel for rel, data in py_files.items()
                  if any(re.search(p, data.decode('utf-8', 'replace')) for p in OLD_PIN_PATTERNS))
    need(hits == ['independent_core.py'], 'overrides: old pins also in %r' % hits)
    return hits


def overrides(inp, words):
    ov = inp.json('overrides2530')
    need(sorted(ov) == ['independent_core.py', 'new/rebind.py'], 'overrides: entries')
    need(ov['independent_core.py']['old_sha256'] == sha256(inp.raw('ic2462')), 'overrides: independent_core old hash != PR2462 file')
    need(ov['independent_core.py']['new_sha256'] == sha256(inp.raw('ic2530')), 'overrides: independent_core new hash')
    need(ov['new/rebind.py']['old_sha256'] == sha256(inp.raw('rebind2462')) == sha256(inp.raw('rebind2435')),
         'overrides: rebind old hash != PR2462 (= PR2435) file')
    need(ov['new/rebind.py']['new_sha256'] == sha256(inp.raw('rebind2530')), 'overrides: rebind new hash')
    ic = independent_core_change(inp.raw('ic2462'), inp.raw('ic2530'))
    pins_match_words([c[2] for c in ic], [c[1] for c in ic], words)
    rb = rebind_change(inp.raw('rebind2462'), inp.raw('rebind2530'))
    # no other .py file of the PR2462 package carries the old pins (they would also have needed editing)
    tree = inp.tree('tree2462')
    py_files = dict((rel, inp.show_blob(inp.table['tree2462'][1], PKG_HANDOFF + rel, tree[rel]))
                    for rel in sorted(tree) if rel.endswith('.py'))
    hits = old_pin_files(py_files, [rel for rel in tree if rel.endswith('.py')])
    return dict(independent_core_changed=[list(c) for c in ic], rebind_changed=[list(c) for c in rb],
                old_files_crlf=b'\r\n' in inp.raw('ic2462') and b'\r\n' in inp.raw('rebind2462'),
                new_files_crlf=b'\r\n' in inp.raw('ic2530') or b'\r\n' in inp.raw('rebind2530'),
                py_files_scanned_for_old_pins=len(py_files), files_with_old_pins=hits), ic, py_files


# ------------------------------------------------------------------------------- source reconstruction ---
def tar_blobs(raw, prefix=''):
    """{path relative to prefix: git blob id} of the regular files of a .tar.gz, read in memory (data only)."""
    out = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tf:
        for m in tf.getmembers():
            name = m.name
            if m.isdir():
                continue
            need(not name.startswith('/') and '..' not in name.split('/') and posixpath.normpath(name) == name,
                 'tar: unsafe member name %r' % name)
            need(m.isfile(), 'tar: non-regular member %r' % name)
            need(name.startswith(prefix), 'tar: member outside %s: %r' % (prefix, name))
            rel = name[len(prefix):]
            need(rel not in out, 'tar: duplicate member %r' % name)
            out[rel] = git_blob_id(tf.extractfile(m).read())
    return out


def same_tree(got, want, label):
    """Two {path: git blob id} maps are equal: no missing, no extra and no differing file ('<label>: ...')."""
    missing, extra = sorted(set(want) - set(got)), sorted(set(got) - set(want))
    diff = sorted(k for k in set(want) & set(got) if want[k] != got[k])
    need(not (missing or extra or diff), '%s: missing %r extra %r differing %r' % (label, missing[:3], extra[:3], diff[:3]))


OVERLAY_WORDS = (('w2462_base', 'new/borrow/words/BORROW-WORD-43base.json.gz'),
                 ('w2462_extra', 'new/borrow/words/BORROW-WORD-43extra.json.gz'))


def reconstruct(archive, overlay, tree2435, tree2462, word_blobs):
    """The archive member map equals the PR2435 tree (recon.pr2435_tree); archive + overlay equals the PR2462 tree
    (recon.pr2462_tree); the overlay words are PR2462's pinned word blobs (word_blobs {path: blob}).  Returns the
    reconstructed map."""
    same_tree(archive, tree2435, 'recon.pr2435_tree: source-pr2435.tar.gz vs PR2435 tree')
    recon = dict(archive)
    recon.update(overlay)
    same_tree(recon, tree2462, 'recon.pr2462_tree: archive + pr2462-overlay vs PR2462 tree')
    for rel, blob in sorted(word_blobs.items()):
        need(overlay.get(rel) == blob, 'recon.overlay_words: overlay word %s != PR2462 git blob' % rel)
    return recon


def source_reconstruction(inp):
    archive = tar_blobs(inp.raw('src2435_tar2530'), PKG_HANDOFF)
    overlay = tar_blobs(inp.raw('overlay2530'))
    tree2435, tree2462 = inp.tree('tree2435'), inp.tree('tree2462')
    word_blobs = dict((rel, inp.table[key][3]) for key, rel in OVERLAY_WORDS)
    recon = reconstruct(archive, overlay, tree2435, tree2462, word_blobs)
    return dict(pr2435_files=len(tree2435), pr2462_files=len(tree2462), archive_files=len(archive),
                overlay_files=len(overlay), reconstructed_files=len(recon),
                overlay_replaced=sum(1 for k in overlay if k in archive),
                overlay_added=sum(1 for k in overlay if k not in archive),
                overlay_words_equal_pr2462_blobs=all(overlay[rel] == blob for rel, blob in word_blobs.items())), \
        (archive, overlay, tree2435, tree2462, word_blobs)


# ----------------------------------------------------------------------------- stock and precision ---
def physical_rule(R, Z):
    return W + 8 + R + Z + 2


def stock_rule_matches(name, R, Z, spec_phys):
    """The stock rule W + 8 + R + Z + 2 with R helpers and Z zero buffers counted from the words must give the
    SPEC's physical stock."""
    need(physical_rule(R, Z) == int(spec_phys), 'stock: %s rule %d != SPEC %s' % (name, physical_rule(R, Z), spec_phys))
    return physical_rule(R, Z)


def stock_and_precision(inp, words):
    out = {}
    w2435 = inp.json('w2435_base')
    cases = (('pr2530', words['base']['pr2530']['helpers'], words['base']['pr2530']['buffers'],
              inp.json('spec2530')['expected']['physical']),
             ('pr2462', words['base']['pr2462']['helpers'], words['base']['pr2462']['buffers'],
              inp.json('spec2462')['expected']['physical']),
             ('pr2435', w2435['report']['R'] - len(w2435['removed']), len(w2435['helper_final']),
              inp.json('spec2435')['expected']['physical']))
    for name, R, Z, spec_phys in cases:
        out[name] = dict(helpers=R, zero_buffers=Z, physical=stock_rule_matches(name, R, Z, spec_phys))
    R, Z = cases[0][1], cases[0][2]
    # documentation only (an identity): the pre-PR2530 rebind formula W + 8 + R + 2 omits the Z zero buffers
    out['documentation'] = dict(old_rebind_formula_pr2530=W + 8 + R + 2, zero_buffer_term=Z)
    m_new, m_old = words['base']['pr2530']['mass'], words['base']['pr2462']['mass']
    need(m_old - m_new == 8 * 8, 'stock: local mass drop != 8 removed width-8 helpers')
    out['local_mass'] = [m_old, m_new]
    # prefix_l1 bit arithmetic (values from the PR's receipts / SPECs; not recomputed from native programs)
    bits = prefix_bits_of

    def collect(obj, key, acc):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    acc.add(v)
                collect(v, key, acc)
        elif isinstance(obj, list):
            for v in obj:
                collect(v, key, acc)
        return acc
    prefix = {}
    for tag in ('base', 'extra'):
        loc = inp.json('ilocal2530_%s' % tag)['local']
        for d in ('forward', 'backward'):
            need(bits(loc[d]['prefix_l1_upper']) == loc[d]['prefix_bits_upper'] and loc[d]['charged_payload_bits'] == 192,
                 'precision: %s %s prefix bits' % (tag, d))
            prefix['%s_%s' % (tag, d)] = [loc[d]['prefix_l1_upper'], loc[d]['prefix_bits_upper']]
    spec_vals = collect(inp.json('spec2530'), 'prefix_l1', set())
    need(spec_vals == set(v[0] for v in prefix.values()), 'precision: SPEC prefix_l1 != receipts')
    old_vals = sorted(collect(inp.json('spec2462'), 'prefix_l1', set()), key=lambda s: Q(s))
    need(len(old_vals) == 2 and [bits(s) for s in old_vals] == [62, 69], 'precision: PR2462 prefix_l1')
    out['prefix_l1'] = dict(pr2530=sorted(spec_vals, key=lambda s: Q(s)), pr2462=old_vals,
                            bits=[bits(s) for s in sorted(spec_vals, key=lambda s: Q(s))])
    local_bits = max(out['prefix_l1']['bits'])
    ig = inp.json('iglobal2530')
    gp, payload = global_prefix(local_bits, CALLS, ig)
    g = FC.stock_group()
    rows = dict((str(p), 2 * (g * p).bit_length() + 9909 + 252 + 2 * payload) for p in (66736, 66814, 66822, 66826, 66830))
    need(set(rows.values()) == {ig['physical_row_coefficient']} and ig['physical_row_coefficient'] < ig['row_limit'],
         'precision.row_coefficient: own %r, receipt %r' % (rows, ig['physical_row_coefficient']))
    out.update(global_prefix_bits=gp, payload_bits=payload, row_coefficient_by_physical=rows, local_prefix_bits=local_bits,
               receipt_independent_global=dict(prefix_bits=ig['prefix_bits'], charged_prefix_bits=ig['charged_prefix_bits'],
                                               physical_row_coefficient=ig['physical_row_coefficient'],
                                               row_limit=ig['row_limit']))
    return out


def global_prefix(local_bits, calls, ig):
    """Global prefix bits = local prefix bits + (m + 1)/2 + 2 x calls + 4, computed from the receipts' local prefix
    bits; it must equal receipts/INDEPENDENT-GLOBAL.json prefix_bits and fit the charged payload (own computation =
    receipt charged_prefix_bits).  Returns (prefix bits, payload bits)."""
    payload = 1 << (192 + (M + 1) // 2 + 2 * calls + 4).bit_length()
    gp = local_bits + (M + 1) // 2 + calls + calls + 4
    need(gp == ig['prefix_bits'] and payload == ig['charged_prefix_bits'] and gp <= payload,
         'precision.global_prefix: own %d (payload %d), receipt %r (payload %r)' % (gp, payload, ig['prefix_bits'],
                                                                                  ig['charged_prefix_bits']))
    return gp, payload


def prefix_bits_of(s):
    """Bits b with prefix_l1 < 2^b (the receipts' prefix_bits_upper rule)."""
    q = Q(s)
    b = q.numerator.bit_length() - q.denominator.bit_length() + 1
    need(q < 2 ** b, 'precision: bit bound')
    return b


# ------------------------------------------------------------------------------ rigorous moment enclosure ---
K = 640
ONE = 1 << K
_LN = []


def _atanh(p, q, N=400):
    """atanh(p/q), 0 < p/q < 1, as an exact Fraction interval (partial sum, partial sum + geometric tail)."""
    z = Q(p, q)
    s, zp, z2 = Q(0), z, z * z
    for j in range(N):
        s += zp / (2 * j + 1)
        zp *= z2
    return s, s + zp / (2 * N + 1) / (1 - z2)


def ln_tables():
    """Intervals of ln r for r in {1,2,3,4,5,7,8,16,32,48} and of ln 73, from ln2, ln(3/2), ln(5/4), ln(7/8),
    ln(73/64) as 2*atanh series (computed once)."""
    if not _LN:
        ln2 = tuple(2 * v for v in _atanh(1, 3))
        ln32 = tuple(2 * v for v in _atanh(1, 5))
        ln54 = tuple(2 * v for v in _atanh(1, 9))
        a78 = _atanh(1, 15)
        ln78 = (-2 * a78[1], -2 * a78[0])
        ln7364 = tuple(2 * v for v in _atanh(9, 137))

        def comb(c2, extra=(Q(0), Q(0))):
            return c2 * ln2[0] + extra[0], c2 * ln2[1] + extra[1]
        _LN.append({1: (Q(0), Q(0)), 2: comb(1), 3: comb(1, ln32), 4: comb(2), 5: comb(2, ln54), 7: comb(3, ln78),
                    8: comb(3), 16: comb(4), 32: comb(5), 48: comb(5, ln32)})
        _LN.append(comb(6, ln7364))
    return _LN[0], _LN[1]


def _exp_fixed(y_lo, y_hi, N=120):
    """Fixed-point (scale 2^K) enclosure of exp(y) for 0 <= y_lo <= y <= y_hi < 1: floor partial sum (lower) and
    ceiling partial sum + 2 * next term (upper).  The tail bound sum_{j>=N} y^j/j! <= 2 y^N/N! needs y <= (N+1)/2,
    which y < 1 (checked) guarantees."""
    need(0 <= y_lo <= y_hi < ONE and N >= 2, 'moment: exp argument outside the tail-bound range [0, 1)')
    t = s = ONE
    for j in range(1, N):
        t = (t * y_lo >> K) // j
        s += t
    lo = s
    t = s = ONE
    for j in range(1, N):
        t = -((-(t * y_hi)) >> K)
        t = -((-t) // j)
        s += t
    tn = -((-(t * y_hi)) >> K)
    tn = -((-tn) // N)
    hi = s + 2 * tn + 1
    need(lo <= hi, 'moment: exp enclosure inverted')
    return lo, hi


def accepts(enc):
    """Rigorous acceptance of an endpoint a from an enclosure [lo, hi] of M(a): the upper end is below 1."""
    return enc[1] < 1


def rejects(enc):
    """Rigorous rejection of an endpoint a from an enclosure [lo, hi] of M(a): the lower end is above 1."""
    return enc[0] > 1


def moment(profile, a, m=M, live=W):
    """Exact Fraction interval enclosing M(a) = (1/live) sum_r n_r (r/m)^(1-a) = sum_r r n_r exp(a ln(m/r)) / (m live)."""
    lnr, ln73 = ln_tables()
    need(m == 73, 'moment: m')
    s_lo = s_hi = 0
    for r, n in profile.items():
        L_lo, L_hi = ln73[0] - lnr[r][1], ln73[1] - lnr[r][0]
        need(L_lo > 0, 'moment: rank')
        x_lo, x_hi = a * L_lo, a * L_hi
        y_lo = (x_lo.numerator << K) // x_lo.denominator
        y_hi = -((-(x_hi.numerator << K)) // x_hi.denominator)
        e_lo, e_hi = _exp_fixed(y_lo, y_hi)
        s_lo += r * n * e_lo
        s_hi += r * n * e_hi
    need(s_lo <= s_hi, 'moment: enclosure inverted')
    return Q(s_lo, m * live * ONE), Q(s_hi, m * live * ONE)


def endpoint(inp):
    prof = dict((int(k), v) for k, v in inp.json('profile2530').items())
    claim, spec, led = inp.json('claim2530'), inp.json('spec2530'), inp.json('ledger2530')
    C = Q(claim['complex_lower'])
    need(C == Q(spec['expected']['complex_lower']) == Q(led['complex_lower_pinned']['rational']), 'endpoint: C differs')
    need(dict((int(k), int(v)) for k, v in led['profile'].items()) == prof and int(led['m']) == M and int(led['W']) == W,
         'endpoint: ledger profile/m/W')
    need((C * 10 ** 24).denominator == 1, 'endpoint: C has 24 digits')
    mass = sum(r * n for r, n in prof.items())
    need(M * W - mass == 23680 and M * M > 2 * max(prof) ** 2, 'endpoint: profile identities')
    r0 = Q(1, 10 ** 104)
    b = Q(led['complex_lower_short']['rational'])
    pts = dict(C=C, b=b, C_plus_1e24=C + Q(1, 10 ** 24), C_minus_1e24=C - Q(1, 10 ** 24))
    enc = dict((k, moment(prof, a)) for k, a in pts.items())
    need(accepts(enc['C']) and accepts(enc['b']) and accepts(enc['C_minus_1e24']), 'endpoint: C not accepted')
    need(rejects(enc['C_plus_1e24']), 'endpoint: C + 1e-24 not rejected')
    lo_a, hi_a = C - Q(1, 10 ** 24), C + Q(1, 10 ** 24)
    for _ in range(80):
        mid = (lo_a + hi_a) / 2
        e_mid = moment(prof, mid)
        if accepts(e_mid):
            lo_a = mid
        elif rejects(e_mid):
            hi_a = mid
        else:
            break
    need(lo_a >= C and hi_a < C + Q(1, 10 ** 24) and hi_a - lo_a < Q(1, 10 ** 45), 'endpoint: root bracket')
    need((lo_a * 10 ** 24).__floor__() == (hi_a * 10 ** 24).__floor__() == C * 10 ** 24, 'endpoint: C is not the 24-digit floor')
    # conservative endpoint with the 32 m^2 n / 1e16 surcharge (an extra rank-1 entry scaled by 1e-16)
    Cc = Q(spec['expected']['conservative_complex_lower'])
    n_children = sum(prof.values())

    def cons(a):
        lo, hi = moment(prof, a)
        lo2, hi2 = moment({1: 32 * M * M * n_children}, a)
        return lo + lo2 / 10 ** 16, hi + hi2 / 10 ** 16
    cons_C = cons(Cc)
    need(accepts(cons_C), 'endpoint: conservative endpoint not accepted')
    need(rejects(cons(Cc + Q(1, 10 ** 24))), 'endpoint: conservative endpoint + 1e-24 not rejected')
    # ledger native moments (2^-527 rationals) bracket the enclosure at b
    nm = [Q(x['rational']) for x in led['native_moment']]
    native_bracket = len(nm) == 2 and all(x.denominator == 1 << 527 for x in nm) and nm[0] <= enc['b'][0] and nm[1] >= enc['b'][1]
    need(native_bracket, 'endpoint: native moments do not bracket the enclosure')
    # outer: kappa = C - 1/F - B (DIG = 24 instance of the parametric grid maximum)
    kappa = Q(claim['kappa'])
    row = led['rows']['struct_boundary_radix_union']
    eps, q, F, B = Q(row['epsilon']['rational']), Q(row['q']['rational']), 10 ** 70, Q(1, 10 ** 46)
    need(kappa == C - Q(1, F) - B, 'outer: kappa formula')
    need(b == C - r0 == C - Q(row['r0']['rational']) and q == C - 2 * r0 and (1 - eps) / r0 == Q(1025, 1024),
         'outer: b, q, delta')
    need(Q(row['kappa']['rational']) == kappa, 'outer: ledger row kappa != CLAIM kappa')
    grid = outer_grid(C, eps, q, F, B, kappa)
    res = dict(C=dec(C, 24), kappa=dec(kappa, 70), rank_mass=mass, deficit=M * W - mass, children=n_children,
               root_bracket=[dec(lo_a, 50), dec(hi_a, 50)], root_minus_C_e25=dec((lo_a - C) * 10 ** 25, 3),
               moment_minus_1=dict((k, '%.6e' % float(v[1] - 1)) for k, v in sorted(enc.items())),
               conservative=dict(C=dec(Cc, 24), moment_minus_1='%.6e' % float(cons_C[1] - 1)),
               native_moment_bracket=native_bracket,
               outer=dict(F='1e%d' % (len(str(F)) - 1), B='1e-%d' % (len(str(B.denominator)) - 1),
                          r0='1e-%d' % (len(str(r0.denominator)) - 1), delta_over_r0=str((1 - eps) / r0), grid=grid),
               spec_outer_refinement=spec['outer_refinement'])
    return res, prof, C, Cc, cons, enc, (eps, q, F, B, kappa)


def outer_grid(C, eps, q, F, B, kappa):
    """The DIG = 24 instance of PR2462's grid-maximum rule (rule outer.grid): C*F is an integer, 0 < C - eps*q
    (interval lower end), C - eps*q < 1/F (interval upper end) and floor(F eps q)/F - B = kappa (floor equality).
    Returns the computed quantities."""
    gap = C - eps * q
    fl = (F * eps * q).__floor__()
    need((C * F).denominator == 1, 'outer.grid: C*F is not an integer')
    need(0 < gap, 'outer.grid: interval lower end, C - eps*q = %s <= 0' % gap)
    need(gap < Q(1, F), 'outer.grid: interval upper end, C - eps*q >= 1/F')
    need(Q(fl, F) - B == kappa, 'outer.grid: floor equality, floor(F eps q)/F - B != kappa')
    return dict(C_minus_eps_q=dec(gap, 130), C_minus_eps_q_sci='%.12e' % float(gap), one_over_F='1e-%d' % (len(str(F)) - 1),
                floor_F_eps_q=str(fl), C_times_F=str(C * F), floor_equals_C_times_F_minus_1=fl == C * F - 1)


def validate_moment_checker(inp):
    """Positive control on PR2462's outer/B.json profile at its certified 3000-digit endpoint C2462 = b + 1e-3080
    (accepted by PR2462, with C2462 + 1e-3000 rejected, so the root lies within 1e-3000 above it and, as
    0 < M' <= M ln 73 < 4.3 there, 1 - 1e-2999 < M(C2462) <= 1): the enclosure must have lo <= 1 (sound lower
    end) and hi >= 1 - 1e-2990 (sound upper end, tested far below the 2^-640 working precision), and
    C2462 - 1e-150 must be accepted."""
    bj = inp.json('outer_b2462')
    prof = dict((int(k), v) for k, v in bj['profile'].items())
    C2 = Q(bj['b']) + Q(1, 10 ** 3080)
    lo, hi = moment(prof, C2)
    need(lo <= 1 and hi >= 1 - Q(1, 10 ** 2990), 'validation: PR2462 endpoint not enclosed (lo <= 1 <= hi + 1e-2990)')
    need(accepts(moment(prof, C2 - Q(1, 10 ** 150))), 'validation: PR2462 endpoint - 1e-150 not accepted')
    need(rejects(moment(prof, C2 + Q(1, 10 ** 150))), 'validation: PR2462 endpoint + 1e-150 not rejected')
    positive('moment_enclosure_C2462')
    return dict(C2462_60_digits=dec(C2, 60), moment_minus_1=['%.3e' % float(lo - 1), '%.3e' % float(hi - 1)],
                enclosure_straddles_1=lo <= 1 <= hi), prof, C2


def latest_gain(k30, k74, claimed):
    """The gain kappa(PR2530) - kappa(PR2474), computed from the two kappas, must equal CLAIM's latest_claim_gain
    exactly (rule pr2474.gain)."""
    gain = k30 - k74
    need(gain == Q(claimed), 'pr2474.gain: own %s != CLAIM %s' % (dec(gain, 45), claimed[:50]))
    return gain


def compare_2474(inp):
    need(inp.raw('claim2474') == inp.raw('claim2474_copy2530'), 'PR2474: evidence copy != file at PR2474 commit')
    o, c = inp.json('claim2474'), inp.json('claim2530')
    k74, k30 = Q(o['kappa_rational']), Q(c['kappa'])
    need(Q(o['kappa']) == k74, 'PR2474: decimal and rational kappa differ')
    need(c['latest_comparison_pr'] == 2474, 'PR2474: CLAIM latest_comparison_pr')
    gain = latest_gain(k30, k74, c['latest_claim_gain'])
    pct = 100 * gain / k74
    s = c['latest_claim_percent_gain']
    digits = len(s.split('.')[1])
    need(Q(s) <= pct < Q(s) + Q(1, 10 ** digits), 'PR2474: percent string is not a truncation')
    return dict(kappa_2474=dec(k74, 30), gain=dec(gain, 40), percent=dec(pct, 30), percent_digits=digits), (k30, k74, c)


# ---------------------------------------------------------------------------------------------- run ---
def _comment_out(raw, startswith, skip_lines, after=0):
    """raw (bytes) with the first line (1-based number > after and not in skip_lines) whose stripped text starts
    with `startswith` commented out in place (same line count); returns (bytes, line number)."""
    lines = raw.split(b'\n')
    k = next(k for k, ln in enumerate(lines) if k + 1 > after and k + 1 not in skip_lines
             and ln.strip().startswith(startswith))
    body = lines[k].lstrip()
    lines[k] = lines[k][:len(lines[k]) - len(body)] + b'# ' + body
    return b'\n'.join(lines), k + 1


def run(inp, log, words):
    res, ctl, ctl_grid, ctl_ov, ctl_prov = {}, [], [], [], []
    res['overrides'], ic, py_files = overrides(inp, words)
    log('accounting: OVERRIDES old hashes = PR2462 files, new = PR2530 files; independent_core changes only lines %s '
        '(pins = words), rebind only line %d (+ zero buffers); old pins in no other of %d .py files'
        % (list(IC_PIN_LINES), REBIND_LINE, res['overrides']['py_files_scanned_for_old_pins']))
    res['source_reconstruction'], (archive, overlay, tree2435, tree2462, word_blobs) = source_reconstruction(inp)
    log('accounting: source-pr2435.tar.gz (%d members) = PR2435 tree (%d files); + overlay (%d) = %d files = PR2462 tree '
        '(%d files)' % (res['source_reconstruction']['archive_files'], res['source_reconstruction']['pr2435_files'],
                        res['source_reconstruction']['overlay_files'], res['source_reconstruction']['reconstructed_files'],
                        res['source_reconstruction']['pr2462_files']))
    res['stock_precision'] = stock_and_precision(inp, words)
    log('accounting: physical rule reproduces 66814 / 66822 / 66826; prefix %d = receipt <= %d; row %d = receipt for '
        'every stock 66736..66830' % (res['stock_precision']['global_prefix_bits'], res['stock_precision']['payload_bits'],
                                      res['stock_precision']['receipt_independent_global']['physical_row_coefficient']))
    res['endpoint'], prof, C, Cc, cons, enc, (eps, q, F, B, kappa) = endpoint(inp)
    res['validation_pr2462'], prof2, C2 = validate_moment_checker(inp)
    res['pr2474'], (k30, k74, c30) = compare_2474(inp)
    log('accounting: C = %s accepted, C+1e-24 rejected, root in [%s..., %s...]; kappa = C - 1e-70 - 1e-46 (grid: C - eps*q '
        '= %s, floor(F eps q) = C*F - 1); PR2462 endpoint reproduced; PR2474 gain and %s%% exact'
        % (res['endpoint']['C'], res['endpoint']['root_bracket'][0][:30], res['endpoint']['root_bracket'][1][:30],
           res['endpoint']['outer']['grid']['C_minus_eps_q_sci'], res['pr2474']['percent'][:10]))

    def control(out, name, rule, fn, condition=None):
        """Negative control: fn() must raise an AuditFail whose 'rule:' prefix is `rule` and, if `condition` is
        given, whose message starts with it (which of the rule's conditions rejected)."""
        attempt(name)
        try:
            fn()
        except AuditFail as e:
            got, msg = str(e).split(':', 1)[0], str(e)
            need(got == rule and (condition is None or msg.startswith(condition)),
                 'control %s: rejected by %s (%s), expected %s%s' % (name, got, msg[:100], rule,
                                                                    '' if condition is None else ' (%s)' % condition))
            rec = dict(control=name, mutant=name, expected=rule, rejected_by=got, rejected=msg[:120])
            if condition is not None:
                rec['expected_condition'] = condition
            out.append(rec)
            return
        raise AuditFail('negative control ACCEPTED: ' + name)
    # the acceptance predicate (upper end < 1) must fail above the root; at PR2462's C2462 the enclosure straddles 1
    # (lo < 1 < hi), so accepting C2462 + 1e-3000 or rejecting C2462 would expose a predicate on the wrong end
    control(ctl, 'acceptance check at C + 1e-24', 'endpoint.accept',
            lambda: need(accepts(enc['C_plus_1e24']), 'endpoint.accept: C + 1e-24 not accepted'))
    control(ctl, 'conservative acceptance check at C\' + 1e-24', 'endpoint.conservative_accept',
            lambda: need(accepts(cons(Cc + Q(1, 10 ** 24))), 'endpoint.conservative_accept: C\' + 1e-24 not accepted'))
    control(ctl, 'PR2462 acceptance check at C2462 + 1e-150', 'validation.accept',
            lambda: need(accepts(moment(prof2, C2 + Q(1, 10 ** 150))), 'validation.accept: C2462 + 1e-150 not accepted'))
    control(ctl, 'PR2462 acceptance check at C2462 + 1e-3000 (enclosure straddles 1)', 'validation.accept',
            lambda: need(accepts(moment(prof2, C2 + Q(1, 10 ** 3000))), 'validation.accept: C2462 + 1e-3000 not accepted'))
    control(ctl, 'PR2462 rejection check at C2462 (enclosure straddles 1)', 'validation.reject',
            lambda: need(rejects(moment(prof2, C2)), 'validation.reject: C2462 not rejected'))
    bad_pins = [ic[0][2].replace('{23,29,32', '{23,28,32'), ic[1][2]]
    control(ctl, 'target pin 29 -> 28 in independent_core.py', 'overrides',
            lambda: pins_match_words(bad_pins, [c[1] for c in ic], words), 'overrides: pr2530 target pin')
    short = dict((k, v) for k, v in overlay.items() if k != OVERLAY_WORDS[0][1])
    control(ctl, 'reconstruction keeping PR2435\'s base word (overlay word omitted)', 'recon.pr2462_tree',
            lambda: reconstruct(archive, short, tree2435, tree2462, word_blobs))
    R, Z = words['base']['pr2530']['helpers'], words['base']['pr2530']['buffers']
    control(ctl, 'stock rule without the zero-buffer term (the pre-PR2530 rebind formula)', 'stock',
            lambda: stock_rule_matches('pr2530 without zero buffers', R, 0, inp.json('spec2530')['expected']['physical']))

    # outer grid (the kappa composition): each of its three conditions must be able to reject
    control(ctl_grid, 'claimed kappa + 1e-70', 'outer.grid', lambda: outer_grid(C, eps, q, F, B, kappa + Q(1, F)),
            'outer.grid: floor equality')
    control(ctl_grid, 'q - 2e-70 (C - eps*q grows past 1/F)', 'outer.grid',
            lambda: outer_grid(C, eps, q - Q(2, F), F, B, kappa), 'outer.grid: interval upper end')
    control(ctl_grid, 'q = C/eps (C - eps*q = 0)', 'outer.grid', lambda: outer_grid(C, eps, C / eps, F, B, kappa),
            'outer.grid: interval lower end')

    # overrides: in-memory edits of the changed verifier files (one more line, before and after the allowed ones)
    # and of the scanned PR2462 package
    for after in (0, IC_PIN_LINES[-1]):
        ic_bad, ic_line = _comment_out(inp.raw('ic2530'), b'require(', IC_PIN_LINES, after)
        control(ctl_ov, 'independent_core.py with line %d (a require) also commented out' % ic_line, 'overrides',
                lambda: independent_core_change(inp.raw('ic2462'), ic_bad), 'overrides: independent_core changed lines')
    for after in (0, REBIND_LINE):
        rb_bad, rb_line = _comment_out(inp.raw('rebind2530'), b'assert ', (REBIND_LINE,), after)
        control(ctl_ov, 'rebind.py with line %d (an assert) also commented out' % rb_line, 'overrides',
                lambda: rebind_change(inp.raw('rebind2462'), rb_bad), 'overrides: rebind change')
    py_bad = dict(py_files)
    py_bad['extra_pin_check.py'] = b'assert set(levels) == {23, 34, 50, 108}\n'
    control(ctl_ov, 'an extra .py file carrying the old target pin', 'overrides', lambda: old_pin_files(py_bad, sorted(py_bad)),
            'overrides: old pins also in')
    control(ctl_ov, 'old-pin scan restricted to independent_core.py', 'overrides',
            lambda: old_pin_files({'independent_core.py': py_files['independent_core.py']}, sorted(py_files)),
            'overrides: old-pin scan covers')

    # provenance: archive/overlay member maps with one extra and one missing file, for both tree comparisons
    extra_name = 'zz-extra-member.txt'
    archive_extra = dict(archive)
    archive_extra[extra_name] = git_blob_id(b'extra\n')
    control(ctl_prov, 'source archive with one extra member', 'recon.pr2435_tree',
            lambda: reconstruct(archive_extra, overlay, tree2435, tree2462, word_blobs),
            "recon.pr2435_tree: source-pr2435.tar.gz vs PR2435 tree: missing [] extra ['%s']" % extra_name)
    gone = sorted(k for k in archive if k not in overlay)[0]
    archive_missing = dict((k, v) for k, v in archive.items() if k != gone)
    control(ctl_prov, 'source archive missing one member (%s)' % gone, 'recon.pr2435_tree',
            lambda: reconstruct(archive_missing, overlay, tree2435, tree2462, word_blobs),
            "recon.pr2435_tree: source-pr2435.tar.gz vs PR2435 tree: missing ['%s'] extra []" % gone)
    overlay_extra = dict(overlay)
    overlay_extra[extra_name] = git_blob_id(b'extra\n')
    control(ctl_prov, 'overlay with one extra member', 'recon.pr2462_tree',
            lambda: reconstruct(archive, overlay_extra, tree2435, tree2462, word_blobs),
            "recon.pr2462_tree: archive + pr2462-overlay vs PR2462 tree: missing [] extra ['%s']" % extra_name)
    added = sorted(k for k in overlay if k not in archive)[0]
    overlay_missing = dict((k, v) for k, v in overlay.items() if k != added)
    control(ctl_prov, 'overlay missing one of the files it adds (%s)' % added, 'recon.pr2462_tree',
            lambda: reconstruct(archive, overlay_missing, tree2435, tree2462, word_blobs),
            "recon.pr2462_tree: archive + pr2462-overlay vs PR2462 tree: missing ['%s'] extra []" % added)
    # provenance: the PR2474 gain and the global prefix arithmetic
    control(ctl_prov, 'CLAIM latest_claim_gain + 1e-40', 'pr2474.gain',
            lambda: latest_gain(k30, k74, str(Q(c30['latest_claim_gain']) + Q(1, 10 ** 40))))
    big = max(res['stock_precision']['prefix_l1']['pr2530'], key=Q)
    bits_up = prefix_bits_of(str(2 * Q(big)))
    control(ctl_prov, 'global prefix from the largest receipt prefix_l1 doubled (%d local bits)' % bits_up,
            'precision.global_prefix',
            lambda: global_prefix(bits_up, CALLS, inp.json('iglobal2530')))
    return res, dict(accounting=ctl, outer_grid=ctl_grid, overrides_diff=ctl_ov, provenance_accounting=ctl_prov)
