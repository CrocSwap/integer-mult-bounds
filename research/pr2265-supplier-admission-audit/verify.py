#!/usr/bin/env python3
"""Independent supplier-admission audit of the PR2265 substitution, traced into PR2260.

Reads pinned Git blobs of PR2260 (head fde6b107) and PR2265 (head 49ce38fe) plus
three files of the base checkout, checks their SHA-256 pins, and re-derives the
supplier-admission premises with independent stdlib code.  It imports and executes no
code from either PR.  All acceptance arithmetic is exact (int / Fraction) except the
moment signs, which use correctly rounded `decimal` ln/exp at 320 digits with an
explicit error bound (see `moment`).  Negative controls must be rejected by the same
check functions.

Prerequisite (once):  git fetch origin pull/2260/head pull/2265/head
(if a PR head has moved, fetch the pinned SHAs instead: git fetch origin <C2260> <C2265>)
Run from the repository root:  python3 -B research/pr2265-supplier-admission-audit/verify.py

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic,
Claude Opus 5.5).  Apache-2.0.
"""
import collections
import copy
import decimal
import gzip
import hashlib
import json
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.set_int_max_str_digits(0)
PKG = Path(__file__).resolve().parent
ROOT = PKG.parent.parent
C2260 = 'fde6b107e26a14da5bac5b66913c914708ea6901'
C2265 = '49ce38fee91f33edb54645724e7be9530f5631f6'
PREFIX = {C2260: 'research/selective-borrowing-kappa/', C2265: 'research/selective-borrowing-outer-retune/'}
PINS = {
    (C2260, 'local/data/forward.json'): 'a9d513bc1d85eb11184d73242a4016119f3968bb2a1ff9b365e78109778c17ee',
    (C2260, 'local/data/backward.json'): 'fc965c4a041f26960268b78ba526b9cca13cd01d713a843f31fe4a82c4e08334',
    (C2260, 'local/data/postludes.json'): 'e14aed87c976b66c17735c6c198a33024c590e7f183ddcea8725aa6514974235',
    (C2260, 'local/inputs/WITNESS.json'): '0a696e6243ba611eec064d0a3bb28fa94ca263d97eec22830f83fabf2e96616b',
    (C2260, 'owners/OWNERS.json.gz'): '892b49f97d4caa7e92918262ea3a8cfa8cbf273c92d574ae53bb89a61ee5e847',
    (C2260, 'owners/inputs/HOSTED-PARENT.json.gz'): 'f713f8e66aaeaebb8202fe72bf36c7d23497152497342c27892e0fda3092f95b',
    (C2260, 'owners/EXPECTED.json'): 'c4ad5debab3f3bd5cba68b91e28a6a8fa64febcbeb892b1fd1d27e3977a76cb1',
    (C2260, 'local/data/finite-invoice.json'): '6c7d14c364bd5d98395826ea7bc208fe1ebf2e46c62621bd9f393c4c9b0eaf1e',
    (C2260, 'arithmetic/vendor/BIT-EXPECTED.json'): 'b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4',
    (C2260, 'PROOF.md'): '5b166115490a71e9ec406497a4177e4b681e96185d0fcee9ceda69020301b23b',
    (C2260, 'PROOF-LOCAL.md'): 'eb8a083f2ef5348a24e9f8873092eecdc2f5a95b5e86f09d6fb10e2dcf398960',
    (C2260, 'PROOF-OWNERS.md'): '268292c6cd87e7c1be15390506412c65fee363b92ea47f6ce7bb51eff9f084d7',
    (C2265, 'SPEC.json'): 'c60d04a8d971d0e984aeeeda87ae613d712537b2623e57a2f315983245e8a280',
    (C2265, 'ENDPOINT.json'): 'aefecb3ba73c417e6942fb440fb9f964e74a635dd4d73074ecc54e31768df5be',
    (C2265, 'outer/LEDGER.json'): 'df357ddc0265bbad6edc8b9c44e882fc0f8c783030dc68619ff9c0be188a2167',
    (C2265, 'README.md'): '82cff31a66becda1ea8e6f051308293148b8057a29af467aed6ae40f59c7dc43',
    (C2265, 'vendor/pr1673/capped-phase-fusion/frontier_fusion/INDEPENDENT-SUBSTITUTION-REVIEW.md'):
        'b48d3e14083829db81336b639a6cfc698ac0dccc76fa2606d11b4be7a968ddeb',
    (C2265, 'vendor/pr1673/capped-phase-fusion/phase_fusion_note.tex'):
        'b5957f38c98a68f2584a42cedf91d753180dab438129fdf749b441074f00d4e1',
}
LOCAL_PINS = {
    'research/e8-bit-p111-tuned/tune/EXPECTED.json': 'b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4',
    'research/direct-delivery504-global/evidence/audit/PREFIX-AND-INVOICE.json':
        'ce1bfa49be88ae67a404f606a11db2232b7e1f2610d4418058e39749d86d8478',
    'scripts/verify_frontier1094.py': 'c7e20f59968ed5736fb859735de4de207de3418083e37012310ebcded946b949',
}


class Reject(Exception):
    pass


def need(cond, label):
    if not cond:
        raise Reject(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ensure_commits():
    """Fetch the two pinned PR heads once if they are absent (read-only network access)."""
    def present():
        return all(subprocess.run(['git', '-C', str(ROOT), 'cat-file', '-e', c + '^{commit}'],
                                  capture_output=True).returncode == 0 for c in (C2260, C2265))
    if not present():
        subprocess.run(['git', '-C', str(ROOT), 'fetch', '--no-tags', '--quiet', 'origin',
                        'refs/pull/2260/head', 'refs/pull/2265/head'], capture_output=True)
    if not present():
        # Fallback if a PR head has moved: GitHub serves PR-network commits by SHA.
        subprocess.run(['git', '-C', str(ROOT), 'fetch', '--no-tags', '--quiet', 'origin', C2260, C2265],
                       capture_output=True)
    if not present():
        raise SystemExit('pinned PR heads unavailable; run `git fetch origin pull/2260/head pull/2265/head`')


def blob(commit, path):
    spec = f'{commit}:{PREFIX[commit]}{path}'
    try:
        data = subprocess.run(['git', '-C', str(ROOT), 'cat-file', 'blob', spec],
                              check=True, capture_output=True).stdout
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f'missing pinned blob {spec}; run '
                         '`git fetch origin pull/2260/head pull/2265/head` first') from exc
    if sha(data) != PINS[commit, path]:
        raise SystemExit(f'pin mismatch for {spec}')
    return data


def local_file(path, raw=False):
    data = (ROOT / path).read_bytes()
    if sha(data) != LOCAL_PINS[path]:
        raise SystemExit(f'pin mismatch for {path}')
    return data.decode() if raw else json.loads(data)


def text_pin(text, phrase):
    """Return the 1-indexed line where the whitespace-normalised phrase starts."""
    flat = ' '.join(text.split())
    pos = flat.find(' '.join(phrase.split()))
    need(pos >= 0, f'phrase not found: {phrase!r}')
    word_index = flat[:pos].count(' ')
    seen = 0
    for number, line in enumerate(text.splitlines(), 1):
        seen += len(line.split())
        if seen > word_index:
            return number
    return None


# ---------------------------------------------------------------- (A) call closure of the local word
REG_OPERANDS = {'scale': (1,), 'add': (1, 2), 'transport': (1,), 'copy': (1, 2), 'clear': (1,),
                'handoff': (1,), 'swap': (1, 2), 'zero_buffer': (1, 3), 'logical_monomial': (1,),
                'dual_monomial': (1,), 'dual_handoff': (1,), 'zero_reframe': (1,)}


def check_alias_closure(trace, witness, postlude):
    """Borrowed aliases come from helper inputs of the same local call; no event leaves the call."""
    n0 = trace['original_register_count']
    active = set(trace['active_registers'])
    helpers = set(map(int, trace['helper_widths']))
    zero = set(map(int, trace['zero_buffers'].values()))
    partners = set(map(int, trace['zero_buffers']))
    copy_reg = trace['copy_register']
    warps = trace['warps']
    removed = [w['removed'] for w in warps]
    borrowed = [w['borrow_from'] for w in warps]
    need(len(warps) == 44 and len(set(removed)) == 44, 'exactly 44 distinct removed aliases')
    need(all(0 <= r < n0 for r in removed), 'removed aliases lie in the original call namespace')
    need(active == set(range(n0)) - set(removed), 'active registers = original namespace minus removed aliases')
    need(len(active) == 660 and helpers <= active and len(helpers) == 436, '660 public = 224 data + 436 helpers')
    need(active - helpers == set(range(224)), 'data arrays are 0..223')
    need(all(b in active for b in borrowed), 'every borrowed source is a live public input array of the same call')
    from_data = sorted(b for b in borrowed if b not in helpers)
    need(not (zero | {copy_reg}) & set(range(n0)), 'owned private arrays are outside the public namespace')
    need(partners <= active, 'zero-buffer partners are public registers of the call')
    pairs = witness['pairs']
    need(len(pairs) == 44, 'witness has 44 pairs')
    need(sorted((p['register'], p['borrow_from'], tuple(p['handoff_basis'])) for p in pairs)
         == sorted((w['removed'], w['borrow_from'], tuple(w['to_basis'])) for w in warps),
         'warps equal WITNESS pairs (removed alias, borrowed source, handoff basis; emission order differs)')
    need(all(p['handoff_paid_rank'] == 0 for p in pairs) and all(w['physical_handoff_rank'] == 0 for w in warps),
         'every handoff has paid rank zero')
    allowed = active | zero | {copy_reg}
    hand = collections.Counter()
    for event in trace['events']:
        kind = event[0]
        need(kind in REG_OPERANDS, f'unknown event kind {kind}')
        for i in REG_OPERANDS[kind]:
            need(event[i] in allowed, f'event {kind} touches register {event[i]} outside the call')
        if kind in ('handoff', 'dual_handoff'):
            hand[event[1]] += 1
    need(hand == collections.Counter(borrowed), 'handoffs occur exactly on the borrowed helper sources')
    need(set(map(int, trace['endpoints'])) == active, 'endpoint ABI covers exactly the 660 public arrays')
    need({e[1] for e in postlude} == zero | {copy_reg} and len(postlude) == len(zero) + 1
         and all(e[0] == 'clear' for e in postlude), 'postlude clears exactly the 76 owned private arrays')
    return dict(distinct_borrowed_sources=len(set(borrowed)), borrowed_from_helper_inputs=len(borrowed) - len(from_data),
                borrowed_from_data_inputs=from_data, events=len(trace['events']),
                handoffs=sum(hand.values()), owned_private_arrays=len(zero) + 1)


# ---------------------------------------------------------------- (A) restoration replay
def rref(vectors):
    """Canonical reduced basis of the GF(2) span of integer bit-vectors (frame identity)."""
    basis = {}
    for v in vectors:
        for top in sorted(basis, reverse=True):
            if v >> top & 1:
                v ^= basis[top]
        if v:
            top = v.bit_length() - 1
            for t in list(basis):
                if basis[t] >> top & 1:
                    basis[t] ^= v
            basis[top] = v
    return tuple(sorted(basis.items()))


def replay_restoration(trace):
    """Exact replay over a free group of reference-change symbols with rational coefficients.

    Each register holds {(input_label, reduced_word): Fraction}.  Every public array starts
    as its own independent label (arbitrary dirty content); owned private arrays start absent.
    The endpoint must be the normalized shear (forward Y_i += X_i, backward X_i -= Y_i,
    i < 112 the X side) with every other public array -- including every borrowed source --
    returned exactly to its own label, and every owned private array returned to zero.
    """
    active = trace['active_registers']
    public = set(active)
    val = {r: {(r, ()): Q(1)} for r in active}
    frame = {r: rref(trace['endpoints'][str(r)]['initial']) for r in active}
    private = set()
    paid = collections.Counter()

    def warp(r, symbol):
        out = collections.defaultdict(Q)
        for (label, word), c in val[r].items():
            word = word[1:] if word and word[0] == -symbol else (symbol,) + word
            out[label, word] += c
        val[r] = {k: c for k, c in out.items() if c}

    for i, e in enumerate(trace['events']):
        kind = e[0]
        if kind == 'transport':
            _, r, old, new, gap = e
            need(frame[r] == rref(old), ('transport source frame', i))
            grow, shrink = rref(old + new) == rref(new), rref(old + new) == rref(old)
            need((grow and len(new) > len(old)) or (r in private and shrink and len(new) < len(old)),
                 ('nested transport', i))
            need(gap == abs(len(new) - len(old)), ('transport rank', i))
            frame[r] = rref(new)
            paid[gap] += 1
        elif kind == 'add':
            _, d, src, q, common = e
            need(d != src and frame[d] == frame[src] == rref(common), ('ADD common frame', i))
            q = Q(q)
            for k, c in list(val[src].items()):
                v = val[d].get(k, 0) + q * c
                if v:
                    val[d][k] = v
                else:
                    val[d].pop(k, None)
        elif kind == 'scale':
            _, r, q, common = e
            need(frame[r] == rref(common) and Q(q) != 0, ('SCALE', i))
            val[r] = {k: Q(q) * c for k, c in val[r].items()}
        elif kind == 'swap':
            _, a, b, common = e
            need(frame[a] == frame[b] == rref(common), ('SWAP', i))
            val[a], val[b] = val[b], val[a]
        elif kind in ('logical_monomial', 'dual_monomial'):
            _, r, symbol, common = e
            need(frame[r] == rref(common), ('monomial frame', i))
            warp(r, symbol)
        elif kind in ('handoff', 'dual_handoff'):
            _, r, old, new, symbol = e
            need(frame[r] == rref(old) and len(old) == len(new), ('handoff frame', i))
            warp(r, symbol)
            frame[r] = rref(new)
        elif kind == 'copy':
            _, r, src, common = e
            need(not val.get(r) and frame[src] == rref(common), ('COPY guard', i))
            val[r], frame[r] = dict(val[src]), rref(common)
            private.add(r)
        elif kind == 'clear':
            _, r, common = e
            need(r in private and frame[r] == rref(common), ('CLEAR guard', i))
            val[r] = {}
        elif kind == 'zero_buffer':
            _, r, common, role = e
            need(r not in val and role in public, ('fresh zero buffer for a public role', i))
            val[r], frame[r] = {}, rref(common)
            private.add(r)
        elif kind == 'zero_reframe':
            _, r, common = e
            need(r in private and not val[r], ('zero reframe', i))
            frame[r] = rref(common)
        else:
            raise Reject(('unknown event', kind))
    backward = trace.get('orientation') == 'backward'
    for r in active:
        want = {(r, ()): Q(1)}
        if backward and r < 112:
            want[r + 112, ()] = Q(-1)
        if not backward and 112 <= r < 224:
            want[r - 112, ()] = Q(1)
        need(val[r] == want, ('endpoint column not restored/sheared', r))
        need(frame[r] == rref(trace['endpoints'][str(r)]['final']), ('endpoint frame', r))
    need(private and all(not val[r] for r in private), 'owned private arrays return to zero')
    need({str(k): v for k, v in paid.items()} == trace['local_profile'], 'paid transport profile')
    borrowed = sorted({w['borrow_from'] for w in trace['warps']})
    identity = [b for b in borrowed if val[b] == {(b, ()): Q(1)}]
    sheared = [b for b in borrowed if b not in identity]   # already checked equal to the declared shear column
    return dict(borrowed_sources_returned_to_input=len(identity), borrowed_sources_ending_as_shear_column=sheared,
                private_arrays_zero=len(private), public_columns=len(active))


# ---------------------------------------------------------------- (A) whole-call owner hosting
def check_owner_hosting(owners, parent, helper_widths, local_profile):
    widths = {int(k): v for k, v in helper_widths.items()}
    calls = collections.defaultdict(list)
    for row in owners:
        calls[row['stage'], row['replica']].append(row)
    need(set(calls) == {(s, r) for s in range(9) for r in range(8)}, '72 actual (stage, replica) calls')
    pair_of = {(int(c['stage']), int(c['replica'])): int(c['pair']) for c in parent['calls']}
    need(set(pair_of) == set(calls), 'parent call list matches owner calls')
    for (stage, replica), rows in calls.items():
        need(len(rows) == 436 and {r['helper'] for r in rows} == set(widths), 'one row per (call, helper)')
        need(len({r['family'] for r in rows}) == 436, 'at most one helper per physical family per call')
        pair = pair_of[stage, replica]
        data = {replica * 896 + (2 * pair + side) * 112 + port for side in (0, 1) for port in range(112)}
        need(not data & {r['family'] for r in rows}, 'helper family is not an active data family of its call')
    for r in owners:
        need(r['width'] == widths[r['helper']], 'owner width equals the helper residual width')
        need(r['copy'] == r['owner_replica'] * 112 + r['port'], 'copy ABI')
        need(r['family'] // 896 == r['owner_replica'] and r['family'] % 112 == r['port'], 'family ABI')
    # Original pending children = old pooled blocks + old idle residuals of the hosted parent.
    pooled = collections.Counter()
    for r in parent['hosting']['pooled_slots']:
        pooled[r['family'], r['child']] += r['width']
    original = collections.Counter(pooled)
    for x in parent['idle_children']:
        need(x['hosted'] == pooled.get((x['family'], x['child']), 0) == x['pending_offset'],
             'idle offset = pooled prefix')
        original[x['family'], x['child']] += x['rank']
    blocks = collections.defaultdict(list)
    for r in owners:
        blocks[r['family'], r['child']].append((r['offset'], r['offset'] + r['width']))
    for key, iv in blocks.items():
        need(key in original, 'owner row targets an inherited pending child')
        iv.sort()
        pos = 0
        for lo, hi in iv:
            need(lo == pos, 'assigned blocks are disjoint and form an exact prefix')
            pos = hi
        need(pos <= original[key], 'assigned prefix fits inside the inherited child rank')
    residual = collections.Counter()
    for key, rank in original.items():
        rest = rank - sum(hi - lo for lo, hi in blocks.get(key, []))
        if rest:
            residual[rest] += 1
    hosted = sum(r['width'] for r in owners)
    total = sum(original.values())
    profile = collections.Counter()
    for r, n in local_profile.items():
        profile[int(r)] += 72 * n
    profile.update(residual)
    return dict(calls=len(calls), roles=len(owners), original_children=len(original),
                original_rank_mass=total, hosted=hosted, residual_mass=total - hosted,
                residual={str(k): v for k, v in sorted(residual.items())},
                profile={str(k): v for k, v in sorted(profile.items())})


# ---------------------------------------------------------------- (B) finite constants
def orthogonal_count(n):
    """Brute-force |O(n,2)| = #{A in GF(2)^(n x n): A A^T = I} by orthonormal row extension."""
    vecs = [v for v in range(1 << n) if bin(v).count('1') % 2 == 1]

    def extend(rows):
        if len(rows) == n:
            return 1
        return sum(extend(rows + [v]) for v in vecs
                   if v not in rows and all(bin(v & w).count('1') % 2 == 0 for w in rows))
    return extend([])


def group_order(m):
    k = m // 2
    g = 2 ** (k * k)
    for j in range(1, k + 1):
        g *= 2 ** (2 * j) - 1
    return g


def row_guard(stock_bits, payload_bits):
    row = 2 * stock_bits + 9909 + 252 + 2 * payload_bits
    need(row < 20161, 'row guard 2*stock_bits + 9909 + 252 + 2*payload < 20161')
    return row


def check_constants(invoice, trace, old, lineage1094, payload=512):
    need(orthogonal_count(3) == group_order(3) == 6 and orthogonal_count(5) == group_order(5) == 720,
         '|O(n,2)| formula on brute-forced small cases')
    m = 73
    live, reserve, cleanup, centres, work = 896 * 8, 492, len(trace['zero_buffers']), 8, 2
    physical = live + reserve + cleanup + centres + work
    need(physical == invoice['physical_families'] == 7745, 'physical family identity 7168+492+75+8+2')
    group = group_order(m)
    stock = group * physical
    row = 2 * stock.bit_length() + 9909 + 252 + 2 * payload
    total_mass = group * m * live + 2 ** 100000
    c0_bits = (32 * m * total_mass * total_mass).bit_length()
    literal = 2 * 2 ** 30000 * stock ** 2 + 8 * group * m * live + 4 * stock + 4 + 32 * m
    fin = invoice['finite']
    need((group.bit_length(), stock.bit_length(), row, c0_bits, literal.bit_length())
         == (fin['group_bits'], fin['physical_stock_bits'], fin['physical_row_coefficient'],
             fin['required_C0_bits'], fin['literal_bits']), 'recomputed finite fields equal the invoice')
    need(fin['retained_row_coefficient'] == 20161, 'retained row allowance')
    row_guard(stock.bit_length(), payload)
    need(c0_bits < 210000 and 2 * total_mass + 18 < 2 ** 210000, 'C0 guards')
    # Equal finite fields in the direct-delivery504 invoice are explained by equal stock bit length.
    ofin = old['finite']
    need((group * old['physical']).bit_length() == stock.bit_length()
         and (ofin['physical_stock_bits'], ofin['physical_row_coefficient'], ofin['required_C0_bits'])
         == (fin['physical_stock_bits'], fin['physical_row_coefficient'], fin['required_C0_bits']),
         'identical finite fields are explained by equal stock bit length')
    guard = invoice['exact_magnitude_guard']
    ideal = max(invoice['local'][o]['precision']['P_binary_upper'] for o in ('forward', 'backward'))
    blocks = guard['completed_blocks']
    conv = (m + 1) // 2
    need((ideal, blocks, conv) == (guard['ideal_local_bits'], 144, guard['initial_sup_to_hilbert_per_lambda']),
         'guard ingredients 63, 144, 37')
    coeff = ideal + blocks + conv
    need(coeff == invoice['global_precision_guard_coefficient'] == 244 and coeff < payload,
         'per-lambda guard 244 < payload')
    # (ideal+blocks) + conv*lam <= coeff*lam  <=>  (ideal+blocks)*(lam-1) >= 0, i.e. lam >= 1; tight at lam = 1.
    need(ideal + blocks + conv == coeff, 'guard identity at lambda = 1')
    retained_fixed = ideal + conv + 72 + 72 + 4   # direct-delivery504 code/invoice_final.py fixed-bit prefix rule
    need(retained_fixed < payload, 'retained fixed-bit prefix rule also holds at lambda = 1')
    # Unit question (lineage-wide, not a PR2260 gap).  Both self-consistent readings pass at the
    # supplier: fixed rule 248 < 512, per-lambda rule 244*lambda < 512*lambda.  The thresholds below
    # only matter for mixed readings, and they bind the selected #1094 equally or more tightly.
    lam_max = max(k for k in range(1, 64) if not rejected(lambda: row_guard(stock.bit_length(), payload * k)))
    lam_fixed = max(k for k in range(1, 64) if coeff * k < payload)                    # relaxed bound 244*lambda
    lam_literal = max(k for k in range(1, 64) if ideal + blocks + conv * k < payload)  # literal 207 + 37*lambda
    need((lam_max, lam_fixed, lam_literal) == (4, 2, 8), 'PR2260 mixed-reading lambda thresholds 4, 2, 8')
    # Selected #1094 (scripts/verify_frontier1094.py:94-96): prefix 397 (fixed 37 conversion), charged 512, row 16469.
    for phrase in ("final['prefix_bits'] == 397", "final['charged_prefix_bits'] == 512",
                   "final['physical_row_coefficient'] == 16469"):
        need(phrase in lineage1094, ('#1094 constant', phrase))
    lam_1094_row = max(k for k in range(1, 64) if 16469 - 2 * payload + 2 * payload * k < 20161)
    lam_1094_prefix = max(k for k in range(1, 64) if 397 - conv + conv * k < payload)
    need((lam_1094_row, lam_1094_prefix) == (4, 4), '#1094 mixed-reading lambda thresholds 4, 4')
    return dict(guard_lambda_max_if_payload_fixed_bits=lam_fixed,physical=physical, group_bits=group.bit_length(), stock_bits=stock.bit_length(), row=row,
                required_C0_bits=c0_bits, literal_bits=literal.bit_length(), guard_coefficient=coeff,
                retained_fixed_bit_prefix=retained_fixed, row_lambda_max_if_payload_scaled=lam_max,
                guard_lambda_max_literal_prefix_fixed_bits=lam_literal,
                selected1094_row_lambda_max_if_payload_scaled=lam_1094_row,
                selected1094_prefix_lambda_max_if_conversion_scaled=lam_1094_prefix)


# ---------------------------------------------------------------- moments (decimal, bounded error)
PREC = 320
TOL = decimal.Decimal(10) ** -300


def moment(profile, m, W, b, surcharge):
    """sum_r r H_r/(m W) (m/r)^b  [+ 32 m sum(H)/(10^16 W) m^b]  minus one.

    Each term uses <= 7 correctly rounded decimal operations (CPython's decimal ln and exp
    are correctly rounded), each with relative error <= 5e-320; there are <= 13 terms of
    size <= 2, so the absolute error is < 1e-316.  Callers accept a sign only when
    |result| > TOL = 1e-300.
    """
    with decimal.localcontext() as ctx:
        ctx.prec = PREC
        D = decimal.Decimal
        bb = D(b.numerator) / D(b.denominator)
        terms = [(Q(r * n, m * W), Q(m, r)) for r, n in profile.items()]
        if surcharge:
            terms.append((Q(32 * m * sum(profile.values()), 10 ** 16 * W), Q(m)))
        total = D(0)
        for w, ratio in terms:
            weight = D(w.numerator) / D(w.denominator)
            total += weight * (bb * (D(ratio.numerator) / D(ratio.denominator)).ln()).exp()
        return total - 1


def sign_of(x):
    need(abs(x) > TOL, 'moment within the decimal error tolerance')
    return 1 if x > 0 else -1


def check_endpoint(spec, endpoint, ledger, profile):
    m, W = 73, 7168
    prof = {int(k): v for k, v in profile.items()}
    need({int(k): v for k, v in spec['expected']['global_profile'].items()} == prof
         == {int(k): v for k, v in endpoint['profile'].items()}, 'SPEC = ENDPOINT = recounted profile')
    mass = sum(r * n for r, n in prof.items())
    need((spec['expected']['live'], endpoint['W'], spec['geometry']['dimension']) == (W, W, m), 'm and W')
    need(mass == spec['expected']['rank_mass'] == 520704 and m * W - mass == spec['expected']['deficit'] == 2560,
         'rank mass and deficit')
    need(m * m > 2 * max(prof) ** 2, 'halving guard m^2 > 2 rmax^2')
    need(spec['geometry']['calls'] * spec['geometry']['helpers_per_call'] == 72 * 436, '72 x 436 owner rows')
    need(Q(endpoint['surcharge_weight']) == Q(32 * m * sum(prof.values()), 10 ** 16 * W), 'surcharge weight')
    C = Q(endpoint['complex_lower'])
    need((C * 10 ** 200).denominator == 1, 'C on the 10^-200 grid')
    need(Q(ledger['complex_lower_pinned']['rational']) == C, 'ledger uses the certified endpoint')
    native = moment(prof, m, W, C, False)
    cons = moment(prof, m, W, C, True)
    nxt = moment(prof, m, W, C + Q(1, 10 ** 200), True)
    need(sign_of(native) < 0 and sign_of(cons) < 0, 'moments below one at C')
    need(sign_of(nxt) > 0, 'conservative moment above one at C + 10^-200')
    row = ledger['rows']['struct_boundary_radix_union']
    q, a, kappa = (Q(row[k]['rational']) for k in ('q', 'a', 'kappa'))
    c = Q(spec['supplier']['bit_lower'])
    need(0 < q < a < C < c, 'rate ordering q < a_eff < b < c')
    need(kappa == C - Q(1, 10 ** 246) - Q(1, 10 ** 222), 'kappa = C - 1e-246 - 1e-222')
    return dict(C_decimal_40=f'{decimal.Decimal(C.numerator) / decimal.Decimal(C.denominator):.40f}',
                native_moment_minus_one=f'{native:.6e}', conservative_minus_one=f'{cons:.6e}',
                next_grid_conservative_minus_one=f'{nxt:.6e}', a_minus_q=f'{float(a - q):.6e}',
                b_minus_a=f'{float(C - a):.6e}', c_minus_b=f'{float(c - C):.6e}')


# ---------------------------------------------------------------- (C) retained bit supplier
def check_bit(spec, bit_pr2260, bit_main, bit_override=None):
    need(bit_pr2260 == bit_main, 'PR2260 BIT-EXPECTED equals the base-tree e8-bit-p111-tuned EXPECTED')
    nine = bit_pr2260['nine']
    need(Q(spec['supplier']['bit_lower']) == Q(nine['bit_lower']), 'SPEC bit_lower is the retained bit endpoint')
    c = Q(nine['bit_lower']) if bit_override is None else bit_override
    H = {int(k): v for k, v in nine['profile'].items()}
    BW = nine['bit']['live']
    word = bit_pr2260['word']
    need(64 * BW - sum(r * n for r, n in H.items()) == 32 * (8 * word['v'] - 9 * sum(word['copy_ranks'])),
         'bit deficit identity')
    need(64 * 64 > 2 * max(H) ** 2, 'bit halving guard')
    mom = moment(H, 64, BW, c, True)
    need(sign_of(mom) < 0, 'conservative bit moment below one at c')
    return dict(bit_conservative_minus_one=f'{mom:.6e}', bit_live=BW, bit_maxchild=max(H))


# ---------------------------------------------------------------- inherited-statement trace
REVIEW = 'vendor/pr1673/capped-phase-fusion/frontier_fusion/INDEPENDENT-SUBSTITUTION-REVIEW.md'
TRACE = [
    ('A-restoration', C2260, 'PROOF.md', 'restore arbitrary dirty helpers, and return all owned private fields to zero'),
    ('A-restoration', C2260, 'PROOF-LOCAL.md', 'Thus arbitrary dirty inputs and operator order, rather than only the all-zero helper assignment, are checked.'),
    ('A-serialize', C2260, 'PROOF.md', 'Invocations serialize; each whole-helper operator restores all spectator coordinates.'),
    ('A-serialize', C2260, 'PROOF-OWNERS.md', 'Each invocation completes before the next one begins.'),
    ('A-completed-call', C2265, 'README.md', "PR2260's dirty borrowing is internal to the T8 parent call and is restored at its boundary"),
    ('A-pr1673-use', C2265, REVIEW, 'acts as identity on arbitrary dirty helper/coarse/spectator coordinates at completed-call boundaries'),
    ('B-guard', C2260, 'PROOF-LOCAL.md', '63 + 144 + 37*lambda <= 244*lambda < 512*lambda.'),
    ('B-guard', C2260, 'PROOF.md', 'the new row coefficient 16467<20161'),
    ('B-pr1673-generic', C2265, REVIEW, 'It does not require the former numeric prefix constant to remain512 or1024.'),
    ('C-interchange', C2265, REVIEW, 'The retained bit supplier supplies the same arbitrary-width equal-chunk interchange interface'),
    ('C-interchange', C2260, 'PROOF.md', 'Its circuit/realization assumptions remain inherited.'),
    ('C-theorem', C2265, 'vendor/pr1673/capped-phase-fusion/phase_fusion_note.tex', 'Assume the paid equal-chunk interchange primitive used by the retained support router.'),
]


def check_trace(texts):
    return [dict(item=item, commit=commit[:8], file=path, line=text_pin(texts[commit, path], phrase))
            for item, commit, path, phrase in TRACE]


# ---------------------------------------------------------------- driver
def rejected(fn):
    try:
        fn()
    except Reject as exc:
        return str(exc)
    return False


def main():
    ensure_commits()
    inp = {key: blob(*key) for key in PINS}

    def J(commit, path):
        data = inp[commit, path]
        return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)
    fwd, bwd = J(C2260, 'local/data/forward.json'), J(C2260, 'local/data/backward.json')
    post = J(C2260, 'local/data/postludes.json')
    witness = J(C2260, 'local/inputs/WITNESS.json')
    owners, parent = J(C2260, 'owners/OWNERS.json.gz'), J(C2260, 'owners/inputs/HOSTED-PARENT.json.gz')
    owners_expected, invoice = J(C2260, 'owners/EXPECTED.json'), J(C2260, 'local/data/finite-invoice.json')
    bit2260 = J(C2260, 'arithmetic/vendor/BIT-EXPECTED.json')
    spec, endpoint, ledger = J(C2265, 'SPEC.json'), J(C2265, 'ENDPOINT.json'), J(C2265, 'outer/LEDGER.json')
    bit_main = local_file('research/e8-bit-p111-tuned/tune/EXPECTED.json')
    old = local_file('research/direct-delivery504-global/evidence/audit/PREFIX-AND-INVOICE.json')
    lineage1094 = local_file('scripts/verify_frontier1094.py', raw=True)
    texts = {k: v.decode() for k, v in inp.items() if k[1].endswith(('.md', '.tex'))}

    out = dict(status=None, pr2260=C2260, pr2265=C2265)
    out['A_alias_closure'] = {o: check_alias_closure(t, witness, post[o])
                              for o, t in (('forward', fwd), ('backward', bwd))}
    need(fwd['helper_widths'] == bwd['helper_widths'] and fwd['local_profile'] == bwd['local_profile'],
         'orientations agree')
    out['A_restoration_replay'] = {o: replay_restoration(t) for o, t in (('forward', fwd), ('backward', bwd))}
    need(all(v['borrowed_sources_returned_to_input'] + len(v['borrowed_sources_ending_as_shear_column']) == 44
             for v in out['A_restoration_replay'].values()), 'all 44 borrowed sources end at their endpoint column')
    hosting = check_owner_hosting(owners, parent, fwd['helper_widths'], fwd['local_profile'])
    need(hosting['residual'] == owners_expected['idle'] and hosting['profile'] == owners_expected['profile'],
         'independent residual recount equals PR2260 owners EXPECTED')
    need((hosting['original_rank_mass'], hosting['hosted'], hosting['residual_mass']) == (387072, 254088, 132984),
         'factor partition 387072 = 254088 hosted + 132984 residual (PR2260 PROOF.md)')
    out['A_owner_hosting'] = hosting
    out['B_constants'] = check_constants(invoice, fwd, old, lineage1094)
    out['C_bit'] = check_bit(spec, bit2260, bit_main)
    out['D_endpoint'] = check_endpoint(spec, endpoint, ledger, hosting['profile'])
    out['trace'] = check_trace(texts)
    inventory = json.loads((PKG / 'INVENTORY.json').read_text())
    classes = collections.Counter(item['class'] for item in inventory['premises'])
    need(all(inventory['summary'][k] == classes.get(k, 0) for k in inventory['classes']),
         'INVENTORY summary matches its premise classes')
    out['inventory_classes'] = dict(sorted(classes.items()))

    # ------------------------------------------------------------ negative controls
    removed = [w['removed'] for w in fwd['warps']]

    def alias_source_is_removed_alias():
        t = copy.deepcopy(fwd)
        t['warps'][0]['borrow_from'] = removed[1]
        w = copy.deepcopy(witness)
        w['pairs'][0]['borrow_from'] = removed[1]
        check_alias_closure(t, w, post['forward'])

    def alias_source_outside_call():
        t = copy.deepcopy(fwd)
        t['warps'][0]['borrow_from'] = 2000
        w = copy.deepcopy(witness)
        w['pairs'][0]['borrow_from'] = 2000
        check_alias_closure(t, w, post['forward'])

    def event_reads_removed_alias():
        t = copy.deepcopy(fwd)
        i = next(i for i, e in enumerate(t['events']) if e[0] == 'add')
        t['events'][i][2] = removed[0]
        check_alias_closure(t, witness, post['forward'])

    def owner_block_overlap():
        o = copy.deepcopy(owners)
        r = next(r for r in o if r['offset'] > 0)
        r['offset'] -= 1
        check_owner_hosting(o, parent, fwd['helper_widths'], fwd['local_profile'])

    def owner_on_active_data_family():
        o = copy.deepcopy(owners)
        r = o[0]
        call = next(c for c in parent['calls'] if (int(c['stage']), int(c['replica'])) == (r['stage'], r['replica']))
        r['owner_replica'] = r['replica']
        r['family'] = r['replica'] * 896 + 2 * int(call['pair']) * 112 + r['port']
        r['copy'] = r['owner_replica'] * 112 + r['port']
        check_owner_hosting(o, parent, fwd['helper_widths'], fwd['local_profile'])

    def halving_child_rank_52():
        p = dict(hosting['profile'])   # mass-preserving: 48 + 4 -> 52
        p['48'] -= 1
        p['4'] -= 1
        p['52'] = 1
        s = copy.deepcopy(spec)
        e = copy.deepcopy(endpoint)
        s['expected']['global_profile'] = p
        e['profile'] = p
        check_endpoint(s, e, ledger, p)

    def invoice_guard_coefficient_245():
        inv = copy.deepcopy(invoice)
        inv['global_precision_guard_coefficient'] = 245
        check_constants(inv, fwd, old, lineage1094)

    def invoice_row_coefficient_16466():
        inv = copy.deepcopy(invoice)
        inv['finite']['physical_row_coefficient'] = 16466
        check_constants(inv, fwd, old, lineage1094)

    def endpoint_plus_one_grid_step():
        e = copy.deepcopy(endpoint)
        e['complex_lower'] = str(Q(e['complex_lower']) + Q(1, 10 ** 200))
        led = copy.deepcopy(ledger)
        led['complex_lower_pinned']['rational'] = e['complex_lower']
        check_endpoint(spec, e, led, hosting['profile'])

    def kappa_plus_1e_240():
        led = copy.deepcopy(ledger)
        k = led['rows']['struct_boundary_radix_union']['kappa']
        k['rational'] = str(Q(k['rational']) + Q(1, 10 ** 240))
        check_endpoint(spec, endpoint, led, hosting['profile'])

    def bit_endpoint_equal_to_b():
        s = copy.deepcopy(spec)
        s['supplier']['bit_lower'] = endpoint['complex_lower']
        check_endpoint(s, endpoint, ledger, hosting['profile'])

    def bit_endpoint_plus_1e_18():
        check_bit(spec, bit2260, bit_main, bit_override=Q(bit2260['nine']['bit_lower']) + Q(1, 10 ** 18))

    def replay_drops_one_monomial_warp():
        t = copy.deepcopy(fwd)
        i = next(i for i, e in enumerate(t['events']) if e[0] == 'logical_monomial')
        del t['events'][i]
        replay_restoration(t)

    def backward_replay_inverts_one_dual_monomial_symbol():
        t = copy.deepcopy(bwd)
        i = next(i for i, e in enumerate(t['events']) if e[0] == 'dual_monomial')
        t['events'][i][2] = -t['events'][i][2]
        replay_restoration(t)

    def replay_doubles_one_add_coefficient():
        t = copy.deepcopy(fwd)
        i = next(i for i, e in enumerate(t['events']) if e[0] == 'add' and str(e[1]) in t['helper_widths'])
        t['events'][i][3] = str(2 * Q(t['events'][i][3]))
        replay_restoration(t)

    controls = {}
    for fn in (replay_drops_one_monomial_warp, replay_doubles_one_add_coefficient,
               backward_replay_inverts_one_dual_monomial_symbol, alias_source_is_removed_alias,
               alias_source_outside_call, event_reads_removed_alias,
               owner_block_overlap, owner_on_active_data_family, halving_child_rank_52,
               invoice_guard_coefficient_245, invoice_row_coefficient_16466, endpoint_plus_one_grid_step, kappa_plus_1e_240,
               bit_endpoint_equal_to_b, bit_endpoint_plus_1e_18):
        controls[fn.__name__] = rejected(fn)
    out['negative_controls'] = controls
    need(all(isinstance(v, str) for v in controls.values()), ('control accepted', [k for k, v in controls.items() if not v]))
    out['status'] = 'PASS_PR2265_SUPPLIER_ADMISSION_AUDIT'
    rendered = json.dumps(out, indent=1, sort_keys=True) + '\n'
    expected_path = PKG / 'EXPECTED.json'
    if '--write' in sys.argv[1:]:
        expected_path.write_text(rendered)
    else:
        need(json.loads(expected_path.read_text()) == json.loads(rendered), 'receipt differs from EXPECTED.json')
    print(out['status'], 'controls_rejected', sum(isinstance(v, str) for v in controls.values()), 'of', len(controls))


if __name__ == '__main__':
    try:
        main()
    except Reject as exc:
        raise SystemExit(f'FAIL: {exc}')
