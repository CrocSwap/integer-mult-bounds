# Exclude fixed-word singleton P104 helper splits

**NO VERIFIED GAIN. Conditional κ change 0%.** The complete comparable
benchmark remains κ = 0.003645669928698 on #7277. The current selected
record, retained callers, and paid profile are unchanged.

The literal source is #7277 at ed090b57ed88f8859e5ff4643645099e6ba856ea.
Its complete signed caller is #7113 at 07a76c5e2738882c0cb322278e56f6cae3c9885d.
A productive split changes the target histogram T. The fixed-packing relaxation
retained by #7277 fixes T, all 17 native paid words and the rank mass of the
remainder with ambient cap 145. Its upper crossing does not cover this change.

## Price gate

Write H(r)=r^(1−κ). Any one two-way split with ranks a,b>0 and a+b=r≤9 has
gross gain H(a)+H(b)−H(r) ≤ H(r)(2^κ−1) by concavity. Since log 2<1 and
e^x ≤ 1/(1−x) for 0≤x<1, all 17 copies together gain at most
153κ/(1−κ) ≤ 153/199 < 1 for 0≤κ≤1/200. This includes the incumbent
crossing and fixed moonshot probe. One additional positive integral-rank
child in the complete invoice costs at least 1. Hence a one-split change
with a new paid child and no paid removals cannot improve the signed moment.
This grants every new ordinary operation, access, routing and restoration
for free in the optimistic upper. Credit #5702 and #7299 for related
refinement-fee and balanced-split bounds.

## Exact support condition

Fix a helper h and a clock with strict chart inclusions U < F < V.
Let P be the literal scalar prefix and S its literal suffix. A singleton
split with only endpoint rescalings needs nonzero λ such that

    e_h^T P = λ e_h^T,         S e_h = λ^(-1) e_h.

The left identity is on independent public inputs. The right identity
covers every public output and retained owned scalar endpoint. The old
complete operator already fixes the helper input column and output row.
Start h with λ^(-1) x_h, retire it with x_h at F, and replace every
suffix reference to h with a fresh arbitrary independent public input z
starting at F. The suffix changes by S e_h (z−x_h). A final λ scaling
of its successor returns z. Other outputs are unchanged. Thus an admitted
case replaces a U→V target by two independent U→F and F→V targets while
keeping every literal MOVE. Both scale factors need the inherited finite
alphabet and compiler checks. This is the singleton case of the general
cocharted basis identity of #5599. #7121 and #7130 provide exact successor
constructors on the #7113 lineage; #5718 permits different input and output
basis corrections and is wider than the present scope.

The scalar proof does not establish signed physical action, all-width
phase, dirty ownership and restoration, or the complete new caller and
compiler invoice. These would be mandatory before a κ claim. Merely
dividing one rank into two numbers supplies no new independent field.

## Finite screen

For each h, inspect the clock after every literal contact of h for which
its chart is strictly intermediate. Between these representatives the
chart and prefix row do not change. When a skipped event touches only
other roles, it acts identically on the input vector e_h to the suffix,
so the suffix column does not change either. Before the first contact the
chart equals U and cannot be a strict intermediate. A MOVE changes the
physical chart and is retained as a contact. INIT and CLEAR have their
literal owned scalar meaning.

The screen uses deterministic vectors x and y over the prime field
q=2305843009213693951, seed 7277. The exact identities imply that the
modular values from public all-ones and x satisfy P_h(x)=x_h P_h(1),
and that P_h(1) (S^T y)_h = y_h. Every literal coefficient has
denominator invertible modulo q. Thus an unequal residue is a definitive
rejection of the exact identity. Equal residues can collide and are
confirmed over the rationals. This use of projections has no probabilistic
assumption in any exclusion. Allowing arbitrary endpoint rational λ makes
the negative result at least as strong as restricting to admissible units.

The first 128-triple cap left 1,268 triples unvisited. The bounded
continuation below exhausted the entire declared scope. Basis changes,
retiming, changed charts, endpoint corrections using other roles, and
simultaneous splits are outside this scope.

## Exhausted continuation and independent verification

A separate one-second bounded continuation exhausted all 1,396 triples
and 11,489 representative cuts in 0.13 s wall. The 74 prefix projection
matches all failed the suffix projection. No signature, exact case, or
site remains inside the singleton scope.

A separate verifier reconstructs the same support geometry by binary
echelon, uses a different prime and probe, and then checks both scalar
conditions over the rationals for every one of its 74 projection
survivors. Each has a valid scalar prefix row and fails the exact suffix
identity. The independent proof needs only one mismatched projection
to reject the other cuts. The toy controls include a reciprocal
rescale and two contaminated cuts. One contaminated cut retains an
identity whole-word scalar operator, demonstrating that a pure prefix
alone cannot prove an independent split.

## Reproduction

From a clean checkout using CPython 3.12 with assertions enabled:

    python3.12 -B scripts/research_package.py --package research/p104-singleton-helper-split-bound
    python3.12 -B scripts/check_research_commit.py --package research/p104-singleton-helper-split-bound --check-modes --check-source-history

The package is self-contained. Its Git-free replay command from the
export root is:

    python3.12 -I -B research/p104-singleton-helper-split-bound/replay.py

The exact original word is bundled byte for byte. PROVENANCE.json
records the public source path, exact #7277 commit, SHA-256 and Git
blob. The wrapper compares the complete deterministic continuation
and rational verifier with frozen receipts, checks the exact tariff
bound and rejects duplicate JSON keys and a mutated source word.
No Git process, temporary pointer, network or machine-specific root
is required. The replay does not build a new physical supplier.

## Open next questions

The next larger scope allows a cocharted middle basis or a distinct
boundary correction. Its exact prefix and suffix support should be
checked jointly before materializing a candidate. The scalar exclusion
and price lemma support a pivot. Neither changes the conditional κ.
Material AI assistance by OpenAI Codex.

#7110/#7112 provide earlier zero-new-MOVE cocharted constructions.
#7175 bounds free refinement on older #7000, and #7299 supplies
generic rank-dependent fees. #7142 moves an input boundary and
increases productive rank mass while charging a new H1. Its changed
rank mass is outside the price lemma here.
