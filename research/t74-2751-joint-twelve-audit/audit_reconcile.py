# SPDX-License-Identifier: Apache-2.0
"""Scope C: reconciliation of PR #2751 with PR #2720 (petalas, head 813fae62, research/t74-inherited-centre-floor).

PR2720 shows, on PR2696's words (its inputs/eight-alias-*.json.gz are byte copies of PR2696's), that under its three
hypotheses (README lines 23-36, quoted verbatim by check_quotes from the pinned README) the four partner sources
P = (33,55,74,85) need an A-boundary correction Q on target rows (23,34,50,108) with det Q = -1/16
(q_i = K_(47+i) x_(P_i)), and that with its extra cut-bill premises (README lines 111-116: the four targets' line-30
cut frames, the pinned cut incidences, a zero-frame reader per centre, rank-eight producers, the descending
private-copy model, no target chart changes or nonmonotone target frame paths) the cut costs 4H7 + 4H1 + 4H8.
PR2751's cut costs 8H8.  analyse() derives, with the own tracker over pinned data, for one word: the P prelude
blocks; the P operator-word columns on every target row at the prelude boundary (A[prelude_events]) and at the cut;
the omitted-correction error E_P = F_P - I_P (F_P: PR2720's output response with the partner correction omitted; the
word replayed through restore with the P-block target adds deleted, minus the desired response Y_t + X_t); the
target-to-target continuation T from the prelude boundary (fresh target symbols, every non-target zero; a target read
into a non-target is recorded, as are zero target scales and target ADDs with equal endpoints); and the cut facts in
the descending private-copy model (forced centres, invoice, zero readers) from the declared target levels, which
scope A proves equal to the frame recount's levels for the published words.  analyse() never raises on a semantic
defect; the checks below do.  PR2720's identity F_P + T Q_P = I_P is checked as E_P + T Q_P = 0.

reconcile_checks() then checks, in this order (rule ids reconcile.*):
  on PR2696 against PR2720's RESULT.json: Q_support (rows carrying P terms at the prelude boundary are exactly
  23,34,50,108), Q_det (det Q = published determinant), Q_matrix (Q = published matrix), Q_cut (the same projection
  at the cut), zero_readers (each published witness is the least zero-frame reader of its centre), cut_floor
  (forced centres and invoice = published; cut rank mass 64), residual (E_P = published omitted-residual table and
  only P operator-word errors), T_rank (rank T = 112), ETQ (E_P + T Q_P = 0 on every target row and P column);
  on PR2751: pr2751_zero_on_2720_rows (no P term at all on rows 23,34,50,108 at either boundary), pr2751_support
  (= 21,37,47,110 at both boundaries), pr2751_rank (4), pr2751_det (1/2), pr2751_not_cut_written (no cut gate
  writes a support row), T_identical (T of PR2696 = T of PR2733 = T of PR2751), pr2751_ETQ;
  echo (each P correction equals the echo of the helper it replaces: PR2751's blocks = the deleted echo reads of
  696/697/698/700 in PR2733; PR2733's (= PR2696's) blocks = the echo reads of 640/641/642/644 re-instated in PR2751);
  hypotheses (computed booleans of PR2720's hypotheses for PR2733 and PR2751 against PR2696, see hypotheses():
  PR2733 must satisfy all of them; PR2751 must have exactly EXPECTED_PATTERN_2751; a mismatch raises PatternFail
  carrying the word and the exact list of differing booleans).
"""
import copy
from collections import Counter

import audit_diff as AD
import audit_lib as AL
import words_check as WC
from audit_common import AuditFail, need

V = AL.V
P_SRC = (33, 55, 74, 85)
P_TARGETS = (23, 34, 50, 108)          # PR2720's target order
NEW_SUPPORT = [21, 37, 47, 110]
NEW_DET = AL.Fraction(1, 2)
EXPECTED_PATTERN_2751 = dict(
    h1_P_helper_paths_inherited=False, h1a_P_charts=False, h1b_P_prelude_lines=False, h1c_P_aliases=False,
    h2a_compensation_P_terms_inherited=False, h2b_continuation_fixed=True,
    h2c_target_scales_nonzero_add_endpoints_distinct=True, h3_P_response_retained=False,
    cut_incidences_kept=True, zero_reader_per_centre=True, rank8_producers=True, line30_cut_frames_kept=False)
E_IDENTITY = "E_P + T Q_P = 0 (i.e. PR2720's F_P + T Q_P = I_P, with E_P = F_P - I_P)"

# PR2720 README.md at 813fae62 (pinned input readme2720): verbatim quotes, whitespace-normalised (lines joined by one
# space).  check_quotes extracts each line range from the pinned bytes and requires exactly this text.
PR2720_QUOTES = (
    ('h1', 23, 27, "1. Keep the original recovery operations and inherited P-source helper paths. At each new handoff "
                   "the lender is exactly its original R input. Replacing a helper changes its incoming independent "
                   "dirty value to a chart of that input. Deleted early echo reads contain only that helper's incoming "
                   "dirty value. Consequently these substitutions have zero P-source projection."),
    ('h2', 28, 32, "2. Apply the resulting additive target compensation at the beginning of A. Its additional "
                   "source-dependent terms use only original R inputs. The target-to-target linear continuation from "
                   "that boundary is unchanged. No continuation operation reads a target into a non-target. All target "
                   "scales are nonzero and target ADDs have distinct endpoints."),
    ('h3', 33, 36, "3. The original P-source response in the uncompensated continuation is retained. Hypothesis 1 "
                   "gives this by linearity and induction through the helper updates. It is also an explicit boundary "
                   "condition, not an assumption that arbitrary changed source programs preserve that response."),
    ('family', 38, 42, "This family includes reassignments of the eight pure recovered inputs with unchanged inherited "
                       "partner corrections. It does not include changing the four partner aliases, mixing a partner "
                       "input into a new lender, moving compensation past its boundary, or changing the target "
                       "continuation. Physical feasibility of an arbitrary assignment is not claimed."),
    ('identity', 81, 88, "Let T be the target-to-target continuation and F_P its output response when the partner "
                         "correction is omitted. T is invertible: its target block is a product of elementary ADDs and "
                         "nonzero scales, with no target feedback into other rows. For the checked word, \\[ "
                         "F_P+TQ_P=I_P. \\]"),
    ('cut_bill', 111, 116, "The support result above does not alone prove a private-copy cost bound. For that bound "
                           "additionally retain the four targets' **exact line-30 cut frames**, the pinned "
                           "centre-to-target cut incidences, and at least one zero-frame reader per centre. Retain "
                           "rank-eight producers and the descending private-copy model used by PR2696. No target chart "
                           "changes or nonmonotone target frame paths are allowed. These are material restrictions."),
)
# (boolean, quote id, the clause it evaluates (a substring of that quote), how it is computed here)
HYPOTHESIS_CLAUSES = (
    ('h1_P_helper_paths_inherited', 'h1', 'Keep the original recovery operations and inherited P-source helper paths.',
     'h1a and h1b and h1c'),
    ('h1a_P_charts', 'h1', 'inherited P-source helper paths',
     'the P sources\' B warp records (G, U, E) equal PR2696\'s'),
    ('h1b_P_prelude_lines', 'h1', 'inherited P-source helper paths',
     'the P prelude blocks use PR2696\'s operator, port and line'),
    ('h1c_P_aliases', 'h1', 'inherited P-source helper paths',
     'each P source aliases the same removed helper as in PR2696 (alias = the unique removed helper whose echo, '
     'from scope B, equals its P correction)'),
    ('h2a_compensation_P_terms_inherited', 'h2', 'Apply the resulting additive target compensation at the beginning '
     'of A. Its additional source-dependent terms use only original R inputs.',
     'the P-source operator-word terms of the A-boundary compensation (every target row at A[prelude_events]) equal '
     'PR2696\'s: only rows 23,34,50,108, with PR2696\'s Q'),
    ('h2b_continuation_fixed', 'h2', 'The target-to-target linear continuation from that boundary is unchanged. No '
     'continuation operation reads a target into a non-target.',
     'T equals PR2696\'s, no target is read into a non-target after the boundary, and T is invertible (rank 112)'),
    ('h2c_target_scales_nonzero_add_endpoints_distinct', 'h2', 'All target scales are nonzero and target ADDs have '
     'distinct endpoints.',
     'no target scale with factor 0 and no target ADD with equal endpoints after the boundary (an ADD with equal '
     'endpoints is also rejected by the tracker, rule tracker.item)'),
    ('h3_P_response_retained', 'h3', 'The original P-source response in the uncompensated continuation is retained.',
     'E_P (= F_P - I_P) equals PR2696\'s'),
    ('cut_incidences_kept', 'cut_bill', 'the pinned centre-to-target cut incidences',
     'the cut gate list equals PR2696\'s'),
    ('zero_reader_per_centre', 'cut_bill', 'at least one zero-frame reader per centre',
     'every centre writes at least one target whose declared level is 0'),
    ('rank8_producers', 'cut_bill', 'Retain rank-eight producers', 'every centre frame has dimension 8'),
    ('line30_cut_frames_kept', 'cut_bill', 'retain the four targets\' **exact line-30 cut frames**',
     'targets 23, 34, 50, 108 are declared at [30]'),
)
PREMISES_NOT_EVALUATED = (
    ('cut_bill', 'the descending private-copy model used by PR2696',
     'assumed by construction: cut_facts derives forced centres, invoice and zero readers in this model'),
    ('cut_bill', 'No target chart changes or nonmonotone target frame paths are allowed.',
     'not evaluated (PR2751 changes the lifted-target set: diff.target_levels, removed 23,34,50,108 at [30], added '
     '21,37,47,110 at [45])'),
)


class PatternFail(AuditFail):
    """reconcile.hypotheses: a word's computed booleans differ from the expected pattern (who, flipped keys)."""


# ---------------------------------------------------------------------------------------------- quotes ---
def norm(text):
    return ' '.join(text.split())


def check_quotes(readme, clauses=HYPOTHESIS_CLAUSES, premises=PREMISES_NOT_EVALUATED, quotes=PR2720_QUOTES):
    """Each PR2720_QUOTES line range of the pinned README equals its quote and starts and ends on a non-blank line
    (so the cited range is exact, not padded), and each HYPOTHESIS_CLAUSES / PREMISES_NOT_EVALUATED clause is a
    substring of its quote (rule reconcile.quotes)."""
    lines = readme.split('\n')
    out = {}
    for qid, a, b, text in quotes:
        need(1 <= a <= b <= len(lines) and lines[a - 1].strip() and lines[b - 1].strip(),
             'reconcile.quotes: README lines %d-%d of quote %s start or end on a blank line' % (a, b, qid))
        got = norm(' '.join(lines[a - 1:b]))
        need(got == text, 'reconcile.quotes: README lines %d-%d != quote %s (%r)' % (a, b, qid, got[:80]))
        out[qid] = dict(lines='%d-%d' % (a, b), text=got)
    for key, qid, clause, _ in clauses:
        need(clause in out[qid]['text'], 'reconcile.quotes: clause of %s not in quote %s' % (key, qid))
    for qid, clause, _ in premises:
        need(clause in out[qid]['text'], 'reconcile.quotes: premise %r not in quote %s' % (clause[:40], qid))
    AL.ran('reconcile.quotes')
    return out


# ------------------------------------------------------------------------------------------- analysis ---
def p_blocks(w):
    """{source: dict(op, U, E, start, end, adds {target: Fraction})} for the P blocks in A[:prelude_events] (the
    last block of a source wins)."""
    A, pe = w['A'], w['prelude_events']
    out, i = {}, 0
    while i < pe:
        g = A[i]
        if g[0] == 'warp' and g[2] > 0:
            j = i + 1
            adds = {}
            while A[j][0] != 'warp':
                h = A[j]
                need(h[0] == 'add' and h[2] == g[1] and V <= h[1] < 2 * V,
                     'reconcile.blocks: prelude block body at A[%d]' % j)
                adds[h[1] - V] = adds.get(h[1] - V, 0) + AL.Fraction(h[3], h[4])
                j += 1
            need(A[j][1] == g[1] and A[j][2] == -g[2], 'reconcile.blocks: prelude block close at A[%d]' % j)
            if g[1] in P_SRC:
                out[g[1]] = dict(op=g[2], U=g[3], E=g[4], start=i, end=j, adds=adds)
            i = j + 1
        else:
            i += 1
    need(sorted(out) == sorted(P_SRC), 'reconcile.blocks: P blocks for %r' % sorted(out))
    return out


def is_pk(key):
    var, word = key
    return var in P_SRC and len(word) > 0


def pk_on_targets(rows):
    out = {}
    for t in range(V):
        terms = dict((k, v) for k, v in rows[V + t].items() if is_pk(k))
        if terms:
            out[t] = terms
    return out


def p_plain_on_rows(rows, targets):
    """Plain (no operator word) P-source terms on the given target rows."""
    return sorted(t for t in targets if any(var in P_SRC and not wd for (var, wd) in rows[V + t]))


def matrix(pk, targets, cols):
    return [[pk.get(t, {}).get(c, AL.Fraction(0)) for c in cols] for t in targets]


def omitted_error(w, blocks):
    """E_P = F_P - I_P: target errors (row - (Y_t + X_t)) after restore when the P-block target adds are deleted.
    Returns (E restricted to P operator-word terms, targets whose error has any other term); check_residual
    requires the latter to be empty."""
    drop = set(k for b in blocks.values() for k in range(b['start'] + 1, b['end']))
    w2 = dict(w)
    w2['A'] = [g for k, g in enumerate(w['A']) if k not in drop]
    rows = AL.run(w2, AL.events(w2))
    E, other = {}, []
    for t in range(V):
        row = dict(rows[V + t])
        for k, v in AL.target_final(t).items():
            nv = row.get(k, 0) - v
            if nv:
                row[k] = nv
            else:
                row.pop(k, None)
        if any(not is_pk(k) for k in row):
            other.append(t)
        pk = dict((k, v) for k, v in row.items() if is_pk(k))
        if pk:
            E[t] = pk
    return E, other


def continuation(w):
    """T from A[prelude_events] through restore: targets start as fresh symbols ('T', t), non-targets zero.  Returns
    (T {(t, s): coefficient}, number of target-into-non-target reads plus target-row terms that are not plain target
    symbols, number of zero target scales plus target ADDs with equal endpoints); check_T requires the second to be
    0."""
    pe = w['prelude_events']
    evs = AL.events(w)
    j0 = next(j for j, (sec, i, g) in enumerate(evs) if sec == 'A' and i == pe)
    tail = evs[j0:]
    leaks = sum(1 for sec, i, g in tail if g[0] == 'add' and not (V <= g[1] < 2 * V) and V <= g[2] < 2 * V)
    degenerate = sum(1 for sec, i, g in tail if V <= g[1] < 2 * V and (
        (g[0] == 'scale' and g[2] == 0) or (g[0] == 'add' and g[1] == g[2])))
    rows = dict((r, {}) for r in AL.init_rows(w))
    for t in range(V):
        rows[V + t] = {(('T', t), ()): AL.ONE}
    rows = AL.run(w, tail, rows=rows)
    T, nonlinear = {}, 0
    for t in range(V):
        for (var, word), val in rows[V + t].items():
            if isinstance(var, tuple) and word == ():
                T[(t, var[1])] = val
            else:
                nonlinear += 1
    return T, leaks + nonlinear, degenerate


def cut_facts(w):
    """Cut facts in the descending private-copy model from the declared target levels (scope A proves them equal to
    the frame recount's levels for the published words): per centre the served levels of the targets it writes form
    a descending chain from the centre's rank; each strict descent is one COPY child."""
    lev = dict((int(k), len(WC.span(F))) for k, F in w['target_levels'].items())
    dims = dict((q, len(WC.span(F))) for q, F in zip(w['centers'], w['center_frames']))
    by_centre = dict((q, []) for q in w['centers'])
    for g in w['cut']:
        by_centre[g[2]].append((g[1] - V, lev.get(g[1] - V, 0)))
    paths = {}
    for q, lst in by_centre.items():
        prev, path = dims[q], []
        for d in sorted(set(d for _, d in lst), reverse=True):
            if d != prev:
                path.append(prev - d)
            prev = d
        paths[q] = path
    lifted_read = sorted(set((t, q) for q, lst in by_centre.items() for t, d in lst if d))
    zero = dict((q, sorted(set(t for t, d in lst if d == 0))) for q, lst in by_centre.items())
    return dict(lifted_targets_written=lifted_read, forced_centres=sorted(set(q for _, q in lifted_read)),
                invoice=dict(sorted(Counter(d for p in paths.values() for d in p).items())), copy_paths=paths,
                zero_readers=zero, min_zero_reader=dict((q, z[0] if z else None) for q, z in zero.items()),
                centre_dims=dims, cut_written=sorted(set(t for lst in by_centre.values() for t, _ in lst)))


def analyse(w):
    """All derived objects of one word used by the checks (see the module docstring)."""
    blocks = p_blocks(w)
    cols = [(x, (blocks[x]['op'],)) for x in P_SRC]
    pe = w['prelude_events']
    rows_pre = AL.run(w, AL.events(w), stop=lambda s, i, g: s == 'A' and i == pe)
    rows_cut = AL.run(w, AL.events(w), stop=lambda s, i, g: s == 'cut')
    E, E_other = omitted_error(w, blocks)
    T, leaks, degenerate = continuation(w)
    return dict(w=w, blocks=blocks, cols=cols, pk_pre=pk_on_targets(rows_pre), pk_cut=pk_on_targets(rows_cut),
                plain_on_2720_rows=p_plain_on_rows(rows_pre, P_TARGETS) + p_plain_on_rows(rows_cut, P_TARGETS),
                E=E, E_other=E_other, T=T, leaks=leaks, degenerate=degenerate, cut=cut_facts(w),
                P_warps=dict((rec[1], rec[2:]) for rec in w['warps'] if rec[1] in P_SRC))


def T_matrix(T):
    return [[T.get((i, j), AL.Fraction(0)) for j in range(V)] for i in range(V)]


def etq(a, q_from=None):
    """The (target, P column) pairs where E_P + T Q_P != 0, with Q from q_from (default: the same word)."""
    q = (q_from or a)['pk_pre']
    bad = []
    for t in range(V):
        for c in a['cols']:
            lhs = sum((a['T'].get((t, s), 0) * q.get(s, {}).get(c, 0) for s in q), AL.Fraction(0))
            lhs += a['E'].get(t, {}).get(c, 0)
            if lhs != 0:
                bad.append([t, list(c)])
    return bad


def published_residual(pub):
    return dict((int(t), dict(((x, tuple(word)), AL.Fraction(c)) for x, word, c in lst))
                for t, lst in pub['omitted_residual'].items())


# ----------------------------------------------------------------------------------------- hypotheses ---
def aliases(a, echo_pool):
    """For each P source, the helpers h (removed in this word, with an echo in the pool) whose echo equals the
    source's P-block correction; the alias is that helper if it is unique, else None."""
    removed = set(a['w']['removed'])
    out = {}
    for x in P_SRC:
        hits = [h for h, m in sorted(echo_pool.items()) if h in removed and m == a['blocks'][x]['adds']]
        out[x] = hits[0] if len(hits) == 1 else None
    return out


def hypotheses(a, ref, echo_pool):
    """Computed booleans of PR2720's hypotheses for word a against PR2720's input word ref (PR2696); see
    HYPOTHESIS_CLAUSES for the quoted clause each one evaluates.  Returns (booleans, aliases)."""
    h1a = all(a['P_warps'][x] == ref['P_warps'][x] for x in P_SRC)
    h1b = all((a['blocks'][x]['op'], a['blocks'][x]['U'], a['blocks'][x]['E']) ==
              (ref['blocks'][x]['op'], ref['blocks'][x]['U'], ref['blocks'][x]['E']) for x in P_SRC)
    al, al_ref = aliases(a, echo_pool), aliases(ref, echo_pool)
    h1c = al == al_ref and None not in al.values()
    h2a = a['pk_pre'] == ref['pk_pre']
    h2b = a['T'] == ref['T'] and a['leaks'] == 0 and AL.rank(T_matrix(a['T'])) == V
    h2c = a['degenerate'] == 0
    h3 = a['E'] == ref['E']
    w, c = a['w'], a['cut']
    return dict(h1_P_helper_paths_inherited=h1a and h1b and h1c, h1a_P_charts=h1a, h1b_P_prelude_lines=h1b,
                h1c_P_aliases=h1c, h2a_compensation_P_terms_inherited=h2a, h2b_continuation_fixed=h2b,
                h2c_target_scales_nonzero_add_endpoints_distinct=h2c, h3_P_response_retained=h3,
                cut_incidences_kept=w['cut'] == ref['w']['cut'],
                zero_reader_per_centre=all(len(z) > 0 for z in c['zero_readers'].values()),
                rank8_producers=all(d == 8 for d in c['centre_dims'].values()),
                line30_cut_frames_kept=all(w['target_levels'].get(str(t)) == [30] for t in P_TARGETS)), \
        dict((str(x), h) for x, h in al.items())


def check_pattern(got, want, who):
    bad = sorted(k for k in want if got.get(k) != want[k])
    if bad or sorted(got) != sorted(want):
        e = PatternFail('reconcile.hypotheses: %s differs in %r' % (who, bad))
        e.who, e.flipped = who, bad
        raise e


def reconciliation_record(quotes, recon, moved=None):
    """The RESULT section on PR2720's hypotheses (recon: reconcile_checks' record per provider): the booleans must be
    equal in both providers (reconcile.providers); each computed boolean with its verbatim clause and line range, the
    premises that are not evaluated, the E_P identity, PR2751's changed and kept booleans, and (moved, from scope B's
    checked edit script) where the recovery operations of hypothesis 1 sit in PR2733 and PR2751."""
    need(sorted(recon) == ['base', 'extra'] and all(recon['base'][k]['hypotheses'] == recon['extra'][k]['hypotheses']
                                                    for k in ('pr2733', 'pr2751')),
         'reconcile.providers: the hypothesis booleans differ between the providers')
    h33, h51 = recon['base']['pr2733']['hypotheses'], recon['base']['pr2751']['hypotheses']
    hyp = [dict(boolean=key, short=key.split('_')[0], quote=qid, quote_lines=quotes[qid]['lines'], clause=clause,
                computed_as=how, pr2733=h33[key], pr2751=h51[key]) for key, qid, clause, how in HYPOTHESIS_CLAUSES]
    need(sorted(h['boolean'] for h in hyp) == sorted(EXPECTED_PATTERN_2751),
         'reconcile.providers: hypothesis clauses do not cover the computed booleans')
    changed, kept = [h['short'] for h in hyp if not h['pr2751']], [h['short'] for h in hyp if h['pr2751']]
    need(sorted(changed + kept) == sorted(k.split('_')[0] for k in EXPECTED_PATTERN_2751) and not set(changed) & set(kept),
         'reconcile.providers: changed %r and kept %r do not partition the booleans' % (changed, kept))
    AL.ran('reconcile.providers')
    return dict(pr2720_readme_quotes=quotes, hypotheses=hyp,
                premises_not_evaluated=[dict(quote=qid, quote_lines=quotes[qid]['lines'], clause=clause, status=st)
                                        for qid, clause, st in PREMISES_NOT_EVALUATED],
                E_identity=E_IDENTITY,
                h1_recovery_operations=dict(moved or {}, note='the pair recoveries x += y/2; y -= x are moved with '
                                            'identical gates and frames (scope B, rule diff.B); h1 is evaluated on the '
                                            'P charts, P prelude lines and aliases, not on the recovery positions'),
                pr2751_changed=changed, pr2751_kept=kept,
                pr2733_all_kept=all(h['pr2733'] for h in hyp))


# --------------------------------------------------------------------------------------------- checks ---
def check_inputs(raw2720, raw2696):
    b1, b2 = AL.AC.git_blob_id(raw2720), AL.AC.git_blob_id(raw2696)
    need(raw2720 == raw2696 and b1 == b2, 'reconcile.pr2720_inputs: PR2720 input %s != PR2696 word %s' % (b1, b2))
    return b1


def check_Q(a96, pub):
    """Q_support, Q_det, Q_matrix, Q_cut on PR2696 against PR2720's RESULT.json."""
    sup = sorted(a96['pk_pre'])
    need(sup == list(P_TARGETS), 'reconcile.Q_support: rows with P terms at the boundary %r' % sup)
    Q = matrix(a96['pk_pre'], P_TARGETS, a96['cols'])
    dQ = AL.det(Q)
    need(dQ == AL.Fraction(pub['determinant']), 'reconcile.Q_det: det %s != published %s' % (dQ, pub['determinant']))
    need(AL.strs(Q) == pub['matrix'], 'reconcile.Q_matrix: %r != published %r' % (AL.strs(Q), pub['matrix']))
    need(a96['pk_cut'] == a96['pk_pre'], 'reconcile.Q_cut: the P projection changes between the boundary and the cut')
    return sup, Q, dQ


def check_cut(a96, pub):
    """zero_readers and cut_floor on PR2696 against PR2720's RESULT.json."""
    c96 = a96['cut']
    wit = dict((int(q), t) for q, t in pub['zero_reader_witnesses'].items())
    need(sorted(wit) == sorted(c96['min_zero_reader']) and all(c96['min_zero_reader'][q] == t for q, t in wit.items()),
         'reconcile.zero_readers: published witnesses %r != least zero-frame readers %r' % (wit, c96['min_zero_reader']))
    inv = dict((str(k), v) for k, v in c96['invoice'].items())
    need(c96['forced_centres'] == pub['forced_centres'] and inv == pub['invoice'] and
         sum(k * v for k, v in c96['invoice'].items()) == 64,
         'reconcile.cut_floor: forced %r invoice %r != published %r %r' % (c96['forced_centres'], inv,
                                                                          pub['forced_centres'], pub['invoice']))
    return inv


def check_residual(a96, pub):
    need(not a96['E_other'] and a96['E'] == published_residual(pub),
         'reconcile.residual: E_P != published omitted-residual table (non-P errors on targets %r)' % a96['E_other'][:5])


def check_T(a):
    rT = AL.rank(T_matrix(a['T']))
    need(rT == V and a['leaks'] == 0, 'reconcile.T_rank: rank T = %d, target-into-non-target reads or non-linear '
         'terms %d' % (rT, a['leaks']))
    return rT


def check_etq(a, rule, q_from=None):
    bad = etq(a, q_from)
    need(not bad, '%s: E_P + T Q_P != 0 at %r' % (rule, bad[:4]))


def check_2751(a51):
    """pr2751_zero_on_2720_rows, pr2751_support, pr2751_rank, pr2751_det, pr2751_not_cut_written."""
    M0 = matrix(a51['pk_cut'], P_TARGETS, a51['cols'])
    need(all(x == 0 for r in M0 for x in r) and all(t not in a51['pk_pre'] and t not in a51['pk_cut'] for t in P_TARGETS)
         and not a51['plain_on_2720_rows'], 'reconcile.pr2751_zero_on_2720_rows: P terms on rows 23,34,50,108')
    sup = sorted(a51['pk_pre'])
    need(sup == NEW_SUPPORT and sorted(a51['pk_cut']) == NEW_SUPPORT,
         'reconcile.pr2751_support: %r / %r' % (sup, sorted(a51['pk_cut'])))
    Q = matrix(a51['pk_pre'], sup, a51['cols'])
    r = AL.rank(Q)
    need(r == 4, 'reconcile.pr2751_rank: rank %d' % r)
    d = AL.det(Q)
    need(d == NEW_DET, 'reconcile.pr2751_det: det %s' % d)
    hit = sorted(set(sup) & set(a51['cut']['cut_written']))
    need(not hit, 'reconcile.pr2751_not_cut_written: cut gates write support rows %r' % hit)
    return M0, sup, Q, r, d


def check_T_identical(a96, a33, a51):
    need(a96['T'] == a33['T'] and a96['T'] == a51['T'], 'reconcile.T_identical: target continuation differs '
         '(PR2696 vs PR2733: %s, vs PR2751: %s)' % (a96['T'] == a33['T'], a96['T'] == a51['T']))


def check_hypotheses(a96, a33, a51, echo):
    pool = dict(echo['old_alias'])
    pool.update(echo['new_alias'])
    h33, al33 = hypotheses(a33, a96, pool)
    h51, al51 = hypotheses(a51, a96, pool)
    check_pattern(h33, dict((k, True) for k in EXPECTED_PATTERN_2751), 'PR2733')
    check_pattern(h51, EXPECTED_PATTERN_2751, 'PR2751')
    return h33, al33, h51, al51


def error_text(E):
    return dict((str(t), dict(('%d.K%s' % (k[0], '.'.join(map(str, k[1]))), str(v)) for k, v in sorted(e.items())))
                for t, e in sorted(E.items()))


def reconcile_checks(a96, a33, a51, pub, echo):
    """The checks of the module docstring, in that order.  pub: PR2720 RESULT.json providers[provider]; echo: scope
    B's echo maps.  Returns the computed record."""
    sup, Q, dQ = check_Q(a96, pub)
    inv = check_cut(a96, pub)
    check_residual(a96, pub)
    rT = check_T(a96)
    check_etq(a96, 'reconcile.ETQ')
    M0, sup51, Q51, r51, d51 = check_2751(a51)
    check_T_identical(a96, a33, a51)
    check_etq(a51, 'reconcile.pr2751_ETQ')
    check_echo(a96, a33, a51, echo)
    h33, al33, h51, al51 = check_hypotheses(a96, a33, a51, echo)
    c96 = a96['cut']
    return dict(
        E_identity=E_IDENTITY,
        pr2696=dict(support=sup, Q=AL.strs(Q), det=str(dQ), Q_equals_published=AL.strs(Q) == pub['matrix'],
                    det_equals_published=dQ == AL.Fraction(pub['determinant']),
                    Q_cut_equals_prelude=a96['pk_cut'] == a96['pk_pre'], forced_centres=c96['forced_centres'], invoice=inv,
                    cut_rank_mass=sum(k * v for k, v in c96['invoice'].items()),
                    lifted_targets_written=c96['lifted_targets_written'],
                    min_zero_reader=dict((str(q), t) for q, t in sorted(c96['min_zero_reader'].items())),
                    E_P=error_text(a96['E']), E_P_equals_published_omitted_residual=a96['E'] == published_residual(pub),
                    T_rank=rT,
                    T_nonidentity_entries=sum(1 for (i, j), v in a96['T'].items() if (i == j and v != 1) or
                                              (i != j and v != 0)),
                    T_sha256=AL.sha(sorted([i, j, v] for (i, j), v in a96['T'].items() if v)),
                    target_into_nontarget_reads=a96['leaks'], E_plus_TQ_zero=not etq(a96)),
        pr2733=dict(P_projection_equals_pr2696=a33['pk_pre'] == a96['pk_pre'], E_P_equals_pr2696=a33['E'] == a96['E'],
                    invoice=dict((str(k), v) for k, v in a33['cut']['invoice'].items()),
                    forced_centres=a33['cut']['forced_centres'], hypotheses=h33, aliases=al33),
        pr2751=dict(matrix_on_2720_rows=AL.strs(M0), matrix_on_2720_rows_zero=all(x == 0 for r in M0 for x in r),
                    support=sup51,
                    Q=AL.strs(Q51), rank=r51, det=str(d51),
                    cut_written_support_rows=sorted(set(sup51) & set(a51['cut']['cut_written'])),
                    E_P=error_text(a51['E']), E_plus_TQ_zero=not etq(a51),
                    invoice=dict((str(k), v) for k, v in a51['cut']['invoice'].items()),
                    forced_centres=a51['cut']['forced_centres'], hypotheses=h51, aliases=al51),
        T_identical_2696_2733_2751=a96['T'] == a33['T'] == a51['T'],
        partner_charts=dict((str(x), dict(op=a51['blocks'][x]['op'], port=a51['blocks'][x]['U'],
                                          line_pr2696=a96['blocks'][x]['E'], line_pr2751=a51['blocks'][x]['E']))
                            for x in P_SRC))


def check_echo(a96, a33, a51, echo):
    """PR2751's P block of x = echo of NEW_ALIAS[x] deleted from PR2733; PR2733's (= PR2696's) P block of x = echo of
    OLD_ALIAS[x] re-instated in PR2751 (scope B's alias maps)."""
    bad = []
    for x in P_SRC:
        if a51['blocks'][x]['adds'] != echo['new_alias'][AD.NEW_ALIAS[x]]:
            bad.append(['PR2751', x, AD.NEW_ALIAS[x]])
        if a33['blocks'][x]['adds'] != echo['old_alias'][AD.OLD_ALIAS[x]]:
            bad.append(['PR2733', x, AD.OLD_ALIAS[x]])
        if a96['blocks'][x]['adds'] != a33['blocks'][x]['adds']:
            bad.append(['PR2696', x, AD.OLD_ALIAS[x]])
    need(not bad, 'reconcile.echo: P correction != echo of the replaced helper %r' % bad)


def mutate_block(w, x, fn):
    """Copy of w whose P block of x has its target adds rewritten by fn(list of add items) -> list of add items."""
    m = copy.deepcopy(w)
    b = p_blocks(m)[x]
    body = fn([list(g) for g in m['A'][b['start'] + 1:b['end']]])
    m['A'][b['start'] + 1:b['end']] = body
    m['prelude_events'] += len(body) - (b['end'] - b['start'] - 1)
    return m


def k_block(w, x, target, num, den):
    """Items [K_op x, target += (num/den) x, K_op^-1 x] with the operator, port and line of x's P block in w."""
    b = p_blocks(w)[x]
    return [['warp', x, b['op'], list(b['U']), list(b['E'])], ['add', V + target, x, num, den, list(b['E'])],
            ['warp', x, -b['op'], list(b['E']), list(b['U'])]]
