# P112 matched support frames of COPY rank at most four cost at least 84

**Scoped obstruction. No new decoder, supplier, kappa or selected-frontier change.**

For the fixed P112 binary label model, consider any finite masked decoder
`sum_k d_k t_k^T = 2G` on the constrained even entries. Coefficients may be
arbitrary complex numbers; transpose is ordinary, not conjugate transpose.
For each **paid** term, require that its actual nonzero source and target
supports span the **same F2 label subspace**, and that its pairing-rank COPY
charge is at most four. Supports need not be identical, local to a tetrad,
root-linear, disjoint, or restricted to eight terms. Arbitrary cost-zero
corrections and cancellations are allowed.

Then, writing `n_r` for the number of paid rank-r terms,

```
n_1 + 2 n_2 + 4 n_3 + 5 n_4 >= 112,
COPY = n_1 + 2 n_2 + 3 n_3 + 4 n_4 >= 84.
```

The integer **rank relaxation**, not the decoder problem, attains 84 uniquely
at 28 rank-three terms. The incumbent uses eight rank-eight copies, total 64.
For every exponent `q=1-a` with `0 <= a < 1`, the candidate COPY moment is at
least `21/16` times the incumbent's, under the same width, multiplicity and
role normalization. Thus this candidate alphabet cannot deliver a COPY saving,
even before any extra preparation, frames, precision, restoration or hosting.

## Why this question is distinct and useful

A masked decoder can trade a few broad copies for many cheaper support-rank
copies. Equality of the two support **spans** is a natural algebraic relaxation
of matched reader/source frames; it is not an assertion of physical frame
legality. The result closes COPY ranks one through four in that alphabet,
without imposing the eight-term/all-pairs restriction. A competitive matched
span design must use at least one paid term of rank five or greater, or change
the copy accounting. Unmatched span designs are not excluded.

PR1909's COPY112 theorem instead requires one actual support to lie within a
single canonical tetrad, with an arbitrary opposite support. This proof uses
no locality restriction and does not extend that theorem merely by enlarging
a tetrad. PR1923 examines a bounded Householder orbit of one symmetric
witness; PR1633 gives all-pairs outside-root-code budgets. Neither establishes
the present characteristic-lift rank inequality, and none is a proof input.

## Proof

### 1. The binary mask turns masked exactness into an identity matrix

Let the live roots have norm two, `G_ij=<r_i,r_j>`, and let

```
B_ij = (G_ij + 1) mod 2.
```

The symmetric binary label pairing is `B`. Its diagonal and orthogonal-root
entries are one; odd-inner-product entries are zero. On P112, the required
masked target therefore satisfies

```
B Hadamard (2G) = 4 I_112.
```

For a term with actual supports `S,T`, its COPY charge is
`beta = rank_F2 B[S,T]`. The masked term over C is
`diag(d|S) B[S,T] diag(t|T)`, embedded in the full matrix. The two diagonal
scalings are invertible because these are **actual nonzero supports**. Its
complex rank equals the rational rank of the zero-one matrix `B[S,T]`.
No coefficient is reduced modulo two. A beta-zero term has `B[S,T]=0`, so its
masked contribution is zero, whatever its coefficients or opposite spans.

### 2. Common spans give a nonalternating quotient

Suppose the two label spans equal `W`. Because S and T both span W, beta is
exactly the rank of the symmetric pairing restricted to W. Divide W by the
radical of that restricted form. The quotient V has dimension beta and a
nondegenerate symmetric form b.

Every live label u has `b(u,u)=1`. This remains true in the quotient: radical
vectors pair to zero with every vector in W, including themselves. Consequently
V is nonalternating, and every actual row or column type belongs to

```
O = {v in V : b(v,v)=1}.
```

In characteristic two, `v -> b(v,v)` is a nonzero linear functional, so
`|O|=2^(beta-1)`. The support matrix is a submatrix of the zero-one Gram matrix
`H_O=(b(u,v))_(u,v in O)`, possibly with repeated row or column types. Taking
submatrices and repeating rows/columns cannot raise its characteristic-zero
rank. This argument does not require S=T. A nonempty matched-span term cannot
have beta zero, since W would contain a label with self-pairing one.

### 3. The even-rank complement improvement

Nondegeneracy gives a unique characteristic vector c satisfying
`b(v,c)=b(v,v)` for all v. It is nonzero, and `b(c,c)=dim(V) mod 2`.
For completeness, split off a norm-one vector and its orthogonal complement
repeatedly until the remaining form is alternating. The alternating remainder
has even dimension. In the resulting orthogonal decomposition c is the sum of
the norm-one basis vectors, so its norm is their number modulo two, equal to
the dimension modulo two. This argument does not assume positive definiteness.

When beta is even, c has norm zero. Translation `u -> u+c` pairs the elements
of O without fixed points, stays in O, and for every v in O gives

```
b(u+c,v) = b(u,v)+1  over F2.
```

As **integer zero-one rows**, the paired rows sum to the all-ones row. Thus
`rank_Q H_O <= 1 + |O|/2 = 1 + 2^(beta-2)`. For odd beta, the cardinality bound
`rank_Q H_O <= 2^(beta-1)` suffices. In particular:

| COPY rank beta | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| Maximum lifted rank used in the proof | 1 | 2 | 4 | 5 |

All four capacities are attained by explicit P112 support matrices in the
certificate. For rank four, eight distinct quotient row types have rational
rank **five**, not eight. The complete finite census also checks all 452
nonalternating nonsingular symmetric binary forms of dimensions one through
four, not just one convenient coordinate form. The proof is quantified linear
algebra; the census checks its exact premises and implementation.

### 4. Rank demand, COPY bill and moment

Sum all masked terms. Their sum is `4I_112`, of complex rank 112. Rank
subadditivity and the capacities give the displayed inequality. Since each
capacity is at most `4r/3`, the COPY bill is at least 84. Equality in this
relaxation requires only rank-three terms, hence exactly 28 of them. This
neither supplies coefficients nor proves that a COPY84 decoder exists.

For `q=1-a`, `0 <= a < 1`, and r at most four,

```
sum n_r r^(1-a) >= 4^(-a) sum n_r r >= 84 * 4^(-a).
```

The incumbent COPY moment before common normalization is
`8 * 8^(1-a) = 64 * 8^(-a)`. Their ratio is at least
`(21/16) * 2^a >= 21/16`. Extra charges cannot repair that comparison when all
other work and the interface are retained. Changes elsewhere, shared copies,
role counts, or the coverage law are outside this comparison.

## Fully charged optimistic fixed-template screen

The card's required first working example was run on CPython 3.12:

```
uv run --python 3.12 --no-project python -I -B research/complex-local-word-ceiling/verify.py
PASS_COMPLEX_LOCAL_WORD_CEILING a_ceiling 0.00169005410908900006 kappa<= 0.0016872026453254019
```

For the stronger fixed-template rejection, retain the selected non-COPY work,
width 73, 896 families, nine stages, idle-rank cap 51 and its coverage law.
Grant every *additional* implementation charge zero, only as a favorable
relaxation. For `0 <= a <= 1/5`, the smallest COPY cost per unit of rank demand
is rank three, so every admissible profile pays at least `28*(3/73)^(1-a)`.
For rank four, the needed comparison follows already at `1-a=4/5` from the
integer inequality `4^9 > 3^4 * 5^5`; ranks one and two are immediate. The
comparison persists as `1-a` increases to one.

Accordingly replace eight rank-eight children by 28 rank-three children, and
raise the centre charge from 64 to **84 at the same time**:

```
optimistic local profile = {1:2412, 2:418, 3:460, 4:142, 5:82}
local paid mass = 5606; total paid mass = 7252; idle mass = 1646.
```

The changed local COPY mass and changed centre charge cancel in the idle
remainder. Keeping centre=64 would incorrectly spend 20 units of idle mass
instead of paying the extra copies; a control makes that error visible.
The pinned exact-rational interval engine gives:

| Quantity | Certified interval or value |
|---|---|
| Selected fixed-word a ceiling | `[0.001690054109088, 0.001690054109089]` |
| Optimistic alphabet a ceiling | `[0.000736244670745, 0.000736244670746]` |
| Original five-percent gate | `0.00177455681454345` |

This is a rejection even with favorable physical charges, not a new admitted
profile. The original positive construction gate is **not met** and is not
silently lowered. No selected cold replay or new kappa calculation is needed
or claimed for this scoped rejection.

## Exact evidence and reproduction

The verifier reconstructs the 120 Euclidean root lines independently, binds
all 112 live roots and all 12,544 label/coordinate entries to the pinned
geometry, and checks the masked target `4I`. Fraction elimination and a
separate odd-prime column algorithm corroborate the finite ranks. The four
capacity witnesses, a nonidentical-support common-span witness, and all
quotient-form census counts are committed in `CERTIFICATE.json`.

Controls include the incumbent eight-copy identity; a valid COPY112 diagonal
decoder; an arbitrary cost-zero odd correction; omitted/wrong diagonal terms;
a wrong mask; and the centre-undercharge error. Two explicit **hypothesis
counterexamples**, not decoder constructions, show the boundary is real:

- unmatched supports can have COPY rank two but lifted rank three;
- a matched-span rank-five P112 support has lifted rank ten, violating the
  low-rank inequality `lift_rank <= 4*COPY/3`.

The sharp per-term witnesses were proposed by a bounded deterministic
support-span search (20,011 sampled closures, proposal RNG seed 7). Discovery
is not exhaustive or needed by replay: every saved witness is rechecked
exactly, and the proof covers arbitrary supports under the stated hypotheses.
The chooser was run independently **once**, with OS seed
`5cee555544503585ad60b2631e790c0c`, track `complex-mechanisms`; its entire output
is in `SELECTION.json`. The proposal seed does not establish novelty.

From the repository root, standard library only:

```sh
uv run --python 3.12 --no-project python -I -O -B research/p112-matched-frame-copy-floor/verify.py
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/p112-matched-frame-copy-floor
```

The expected final marker is
`PASS_P112_MATCHED_FRAME_COPY_FLOOR forms=452 entries=12544 capacities=1,2,4,5 COPY>=84 moment_ratio>=21/16 controls=7 no_new_kappa`.

Local verification on **CPython 3.12.12**, Darwin arm64, 2026-10-14: normal
`-I -B --write` certificate generation, isolated optimized `-I -O -B` replay,
and the registered Python 3.12 replay all passed. The wrapper additionally
printed `PASS_REGISTERED_RESEARCH_PACKAGE research/p112-matched-frame-copy-floor outcome=negative-result`.
An initial metadata-only failure used an unsupported outcome spelling; it
was corrected to `negative-result`, after which the registered replay passed.
No native, hosted-CI, selected cold-replay or proof-assistant result is claimed.

`verify.py --write` regenerates the deterministic certificate. The verifier
uses explicit exceptions rather than removable assertions. Neither a proof
assistant nor independent human verification of the quantified proof is
claimed; the two finite rank methods belong to this same assisted contribution.

## Open next questions

- **Can unmatched spans achieve a useful full decoder?** The rank-two
  counterexample identifies where the proof fails. First formulate the exact
  coefficient equations for a collection of such rectangles, on every masked
  entry. A rectangle with a high lifted rank is not itself a decoder; coefficient
  compatibility and all physical charges block admission.
- **Can rank-five matched terms help?** The supplied ten-line rank-five fixture
  escapes the low-rank ratio. A first step is an exact covering/linear-algebra
  screen using those supports and every diagonal/orthogonality constraint.
  No coefficient solution, complete moment bill, source-access contract,
  restoration schedule or hosting assignment is supplied.
- Arbitrary unmatched spans, COPY rank at least five, shared/nonseparate COPY
  pricing, other punctures and changed coverage/role interfaces remain open.
  Existing eight-term and locality theorems retain their own distinct scopes.

## Sources, overlap, credit and disclosure

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Exact live inputs and
historical catalogue/selected-record pins are in `SOURCES.json`; all inputs,
selected results and predecessor packages are unchanged. The geometry is
Mihir Srivastava's AI-assisted independent implementation of DreamingOfClouds'
PR717 P112 model. Credit DreamingOfClouds for the masked decoder and separate
COPY-rank convention, themilkman216 for the frame-pair decoder floor,
Douglas Colkitt for the selected-word ceiling engine and its Claude-assisted
implementation, and the selected supplier's credited predecessor chain.
PR1909, PR1923 and PR1633 are acknowledged as adjacent work, not dependencies.

The shared cached overlap snapshot covered 579 open PRs including drafts
and 547 discussion records, complete pagination, fetched on 2026-10-14 at
14:10:13Z and 14:11:43Z. Targeted terms included matched/support frames,
characteristic lifts, tetrad locality, rank shape, binary rank and symmetric
factors. This does not search every code diff or establish literature priority.
The final cached search covered 584 PRs (14:27:47Z) and 565 discussion records
(14:29:09Z), including this claim. Targeted live reads confirmed that PR1909,
PR1923 and PR1633 remained open at the exact heads in TASK.json.
The local `complex-parity-frames-seed35` and `parity-edge-compatibility-seed46`
notes were also read: their characteristic-vector/common-span obstructions
concern legal separating frames and nested DAG edges, not the P112 masked
COPY invoice. PR1558's form census verifies Z4 Gauss-kernel normalization,
not characteristic-zero rank of the odd-vector pairing mask. The underlying
characteristic-vector linear algebra is standard and is not claimed as new.
No matched-span COPY obstruction appeared in these bounded searches; that
absence is not a novelty certificate.
Coordination:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1929#discussioncomment-18925923.

Prepared for Adam Gall with substantial OpenAI Codex (GPT-6 Astra) assistance
in research, proof, implementation, experiments and writing. Apache-2.0.
