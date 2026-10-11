# #493's R489 bit supplier with #495's retimed complex word on hybrid cross-copy hosting

PR #494 composed eumemic's #493 bit word (c = 1.565442·10⁻³) with higherbeing's #448 cross-copy hosting of icekylinx's
#433 complex word (b = 1.437532·10⁻³), so κ was complex-bound with about 9 % headroom on the bit side. This package
keeps the bit side unchanged and replaces the complex word with Ali Romman's PR #495 retimed R560 word. That word
combines DreamingOfClouds' PR #449 shared-donor kernel with chafreaky's PR #458 paid two-sided residual adapters.
It is hosted in the same nine-stage template, every residual on idle data coordinates:

    b = 1455062642351477/10¹⁸ = 1.455063·10⁻³,  κ = 726474255625747/(5·10¹⁷) = 0.001452948511251494 (complex-bound),

which is 1.22 % above PR #494's κ = 0.001435468764627892.

## Construction

1. **Word.** `code/build_word.py` copies PR #495's frozen `FULL-WORD.json.gz` and runs PR #495's own word-level
   scripts, vendored byte for byte (`SOURCE.json` lists every file with its PR #495 path and hash):
   - `scalar.py`: exact arbitrary-input scalar maps and nested frames;
   - `programs.py`: both local programs (forward and backward orientation);
   - `phases.py`: exact Clifford phase recipes for every used transition;
   - `adapters.py`: the paid two-sided residual adapters of the 79 entering helpers;
   - `local_audit.py`: the independent local read-back, status `PASS_INDEPENDENT_COMPLEX_KERNEL_LOCAL_REALIZATION`,
     with 158 residual-adapter events per call, all 800 columns read back, helpers restored and private centres cleared.

   The word has v = 120 ports, h = 9 and R = 560 helpers. Of these, 79 enter with a frame of rank 1 (residual width 8)
   and 481 enter with the full frame (residual width 9). Its local paid profile per call is
   {1: 2317, 2: 260, 3: 524, 4: 56, 5: 224, 6: 168, 8: 24}.

2. **Template.** `code/complex_retimed9.py` starts from PR #433's nine-stage compressed template (m = 73, K = 4 pairs,
   eight replicas, 72 calls), as rebuilt by PR #442's complete verifier inside PR #494's run. This is the template
   PR #494 prices. The data side is unchanged: schedule, bridges, data owners, cover sweeps and the exact data-phase
   recipes (`DATA-PHASES.json`, bound to the template by its hash). Only the following change:
   - the helper owners of each call;
   - the two local programs;
   - the idle-child remainders;
   - the bank padding, which becomes empty;
   - the final cover correction, which now covers all 7680 live families.

3. **Hosting.** Every residual of every call is hosted on the pending idle axes of a copy (one data family of one side
   of an idle pair). The copy must lie inside its child's window: strictly after the pair's last write, strictly
   before its idle cover sweep, and off the active pair. These are PR #442's windows. The frozen selection
   `data/SELECTION.json` (made once by `--discover`, a small MILP; not needed to verify) uses two kinds of copies:
   - **pattern copies** (237 per replica) host whole residuals of pairwise distinct stages. All 711 entering residuals
     per replica go here, with PR #495's owner record `[4, child, offset, 8, entrance frame, axes]`. The chart maps
     the child's orthogonal pending axes [offset, offset+8) in PR #495's exact idle basis U_q, then spectator axes.
   - **tape copies** host the 4329 width-nine residuals per replica under PR #448's rules, exactly as PR #494 does:
     whole (`[3, child, offset]`, PR #442), or split into two pieces on two adjacent copies of the same child
     (`[5, child, o1, w1, family2, o2, w2]`, PR #448). There are 12,024 split residuals in all.

   With nothing left for banks, the live stock is the 7680 data families. The physical stock is
   7680 + 560 + 16 private centres + 2 = 8258. The global profile has rank mass 558,144 = 73·7680 − 2496 and largest
   child 48, so the degree-two halving inequality 73² > 2·48² holds.

4. **Price.** `code/invoice_retimed9.py` computes a fresh finite invoice for this word and template. It follows the
   form of PR #433's `complex_integrate.py`, with these charges added:
   - paid entrance monomials at entry and exit for the entering helpers, as in PR #484's `integrate_gk.py`;
   - PR #495's wrapper charge of two wrappers of eight monomial compiler groups per helper;
   - a second route charge per helper, for the second piece of a split residual;
   - the hosted live and physical stock.

   It is asserted to exceed the parent's per-vertex invoice and to satisfy every PR #442 inequality: the logical,
   router, literal and C₀ bounds, and the row coefficient 15,443 < 20,161.

5. **Assembly.** `code/assemble_complex.py` is PR #494's `assemble_489.py` with the complex word directory and
   deficit as arguments. It does the following:
   - recomputes #493's bit root and asserts it equal to #493's receipt (c is unchanged);
   - computes b from the new hosted profile with PR #494's two rational moment engines;
   - prices it with the new invoice;
   - runs PR #434's outer assembly on s = min(c, (1−β)b) − 10⁻²⁴: six bootstrap levels, the 47 strict inequalities,
     and the next-grid, zero-η, zero-β and unit-β controls rejected.

## Why the pieces are compatible

No gain is added to another. One word is priced in one template by one invoice, and κ is read off
min(c, (1−β)b) by the unchanged outer assembly. The argument is that each hosted object is used exactly under the
rule its source proves it for:

1. **Same ports, same data phases.** The word's 120 ports equal PR #433's. `complex_retimed9.py` asserts they equal
   the ports of PR #442's `DATA-PHASES.json`. Every data-side call and phase recipe is therefore PR #433's, and the
   audit checks that every unchanged template field is equal.
2. **Local exactness is PR #495's.** Every call runs one of the two programs read back by PR #495's local audit,
   unchanged. Owners are substituted only where PR #495's own `emit.py` substitutes them. Each program's digest is
   recorded in its call, and the audit recomputes the digest of all 1,724,328 emitted events.
3. **Width-nine residuals are PR #433-type residuals.** They enter with the full frame, like all 560 residuals of
   PR #433's word. Hosting them by owner records 3 and 5 is therefore exactly the PR #442/#448 hosting PR #494
   audits, and it uses only tape copies.
4. **Entering residuals are hosted as PR #495 hosts them:**
   - whole, by PR #495's chart;
   - wrapped by PR #458's paid pre/post adapters, conjugated by the route;
   - alone on their physical family in their invocation. This is PR #495's "at most one helper per physical family
     per invocation", which its adapter argument uses.

   Here this holds because pattern copies carry pairwise distinct stages and are never tape copies. The emitter
   asserts it per call, and the audit re-checks it.
5. **Separation.** Every copy is either a pattern copy or a tape copy. The hosted cells of a copy are disjoint across
   all its residuals. Entering residuals never touch the tape. So PR #448's cross-copy argument is used only for
   width-nine residuals on tape copies, as in PR #494. PR #458/#495's adapter argument is used only for entering
   residuals on pattern copies, as in PR #495. Data families of a call never host a helper of that call.

## Independent audit

`code/audit_retimed9.py` shares no code with the emitter. It re-derives the windows from the schedule and then checks
every one of the following:
- every slot and owner record;
- each route chart, against U_q;
- each call's program profile, against the local audit;
- the 158 residual-adapter events per call;
- the emitted digest;
- the remainders, the live and physical stock and the deficit;
- the halving bound and the cover correction.

It rejects 20 mutations:
- a residual outside its window, wrong split widths, split pieces on non-adjacent copies;
- an entering residual moved onto the tape, overlapping cells, two helpers of one invocation on one pattern family;
- an understated remainder, a dropped live family, an understated physical reserve;
- a duplicated or missing hosted residual, an omitted local event, an omitted residual pre-adapter;
- a wrong route axis, a helper owner on the active pair, a changed data owner, a cross-replica helper family;
- an omitted or undercharged cover correction, a wrong local orientation.

## Scope and remaining assumptions

Conditional, like its parents. The following remain assumptions:
- **Everything PR #494 assumes:**
  - PR #448's cross-copy slot (disputed in the discussions on PR #451 and PR #485; PR #448 §7 gives the exact
    two-family check). It is used here only where PR #494 uses it.
  - #493's review points (mutable-source bit word, carrier structure, relaxed checker).
  - The inherited all-size compiler, correlated dirty-helper, compressed-window, restored-work, tape/common-grid,
    precision and analytic interfaces.
- **What PR #495 assumes for its word:**
  - PR #449's expanded scalar interface for the shared-donor kernel;
  - PR #458's paid two-sided residual adapters;
  - PR #495's pending E8 mutable-target, idle-hosting and Gaussian-adapter interfaces.
- **One new composition point:** PR #495's whole entering-residual hosting is used in PR #433's nine-stage m = 73
  template instead of PR #451's eleven-stage m = 89 template, next to PR #448 tape copies of other families. The
  semantics of each record are its source's. The template, the route chart's ambient dimension and the family
  separation are checked exactly here, but no source has reviewed this combination.

A finite certificate is not a formal proof of the asymptotic multiplication theorem. No Lean proof is claimed, and κ
is an exponent saving, not a measured runtime speedup.
