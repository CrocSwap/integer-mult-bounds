# Width contraction pays for a complete generated-weight vector

This is a scoped resource theorem for Jose Manuel's PR2310 interpreter at
`a5258f548bfb6da71c3b72733fbbd2fb4995c929`. It strengthens its preparation
estimate under the same implementation hypotheses. It does not change a
child, a supplier invoice, the selected exponent or the physical dispatcher.
The four unmodified predecessor files and their hashes are in `SOURCES.json`.

## 1. Exact model and statement

Let `n_0=e` be a positive integer. A valid chronological descriptor chain has
`h` steps and positive extents `n_0,...,n_h`. With `f=floor(n_(i-1)/64)`, its
steps are precisely the following operations in `Program.extents` and
`evaluate`:

| Step | Child extent `n_i` | Recursive parent requests `b_i` | Table reads per value request | Ring operations |
|---|---:|---:|---:|---:|
| Good of rank `r`, `1<=r<=42` | `r*f` | 1 | 1 | 1 |
| Pair | `f` | 0, 1 or 2 | 1 | 3 |
| Unit reset | `f` | 0 | 0 | 0 |
| Half-unit reset | `floor(f/2)` | 0 | 0 | 0 |

For Pair, the two potential parent rows are `field` and
`permutation[field]`; a row below 64 requests its parent weight and a row
at least 64 returns a constant. Thus `b_i` does not depend on the coordinate
being evaluated. A reset discards expression ancestry, but retains all global
frozen-field positions. Both physical orientations have the same work count.
No memoization, cancellation of equal requests, or recursive vector building
is assumed.

Evaluate every coordinate `0<=j<n_h` once using the unchanged iterative
interpreter. Reuse its read-only frozen tape, whose page length is `L` bits,
and start each evaluation at head zero. Count:

- `R`: processed `value` requests, including root and reset requests;
- `T`: complete frozen-table reads;
- `M`: the source's modular-operation counter (Good costs 1, Pair costs 3);
- `E`: all popped interpreter events, including constants and continuations;
- `H`: frozen-tape head movements, in bits, including reads and return to zero.

Then, uniformly over all valid extents, chains, allowed tables and coefficients,

| Quantity | Upper bound | Attaining depth with every step Good(42) |
|---|---:|---:|
| `R` | `(21/16)e` | 1 |
| `T` | `(441/512)e` | 2 |
| `M` | `(441/512)e` | 2 |
| `E` | `(2205/1024)e` | 2 |
| `H/L` | `(972405/262144)e` | 4 |

All five constants are sharp for this interpreter and grammar. These are
resource counts, not bit-cost timings of Python. A ring inversion counts as
one of Pair's three ring operations here; its actual bit cost is addressed
only by the conditional corollary below. The same upper bounds hold for at
most `n_h` valid evaluations, including repetitions, because the count for
one evaluation is coordinate independent. They do not cover `e` evaluations
at every smaller descendant.

## 2. A common product bound

Set `alpha=42/64=21/32`, and `rho_i=n_i/n_(i-1)`. Every step satisfies

    rho_i <= alpha,       rho_i*b_i <= alpha.

For Good these inequalities are immediate. Pair has `rho_i<=1/64` and
`b_i<=2`, hence `rho_i*b_i<=1/32`; a reset has `b_i=0`.
The floors only strengthen the inequalities.

For one final-coordinate evaluation let `k_i` be the number of `value`
requests processed at global level `i`. Then

    k_h=1,                 k_i = product_(j=i+1)^h b_j.

This is an exact multiplicity identity. A zero from a reset or an all-constant
Pair removes precisely its older requests. Consequently, for every `0<=i<=h`,

    n_h*k_i
      = e * product_(j=1)^i rho_j
          * product_(j=i+1)^h (rho_j*b_j)
      <= e*alpha^h.                                      (1)

The width loss and branching must occur in the same product. Bounding
`n_h<=e` and the tree by `2^h` separately discards this information.

Summing (1) gives `R <= e*(h+1)*alpha^h`. A table can be read only at an
internal level, so `T <= e*h*alpha^h`.

For ring work, write `c_i=1,3,0,0` for the four rows of the table. In addition
to the two preceding inequalities, `rho_i*c_i<=alpha`: for Pair this is
`3/64<=21/32`. Apply the same product argument to each charged level to get
`M <= e*h*alpha^h`. This step accounts for Pair's three operations; it does
not identify a Pair with a one-operation Good step.

## 3. Events, physical ages and stack

At an internal value request, the total number of local events, excluding
recursive parent value events, is

    d_i = 2                 for Good,
          4-b_i             for Pair,
          1                 for either reset.

Good has its value and multiply events. Pair has its value, quotient
continuation and `2-b_i` constant events. A root has one value event.
Every step satisfies `rho_i*d_i<=2*alpha`. The root term and `h` internal
terms therefore give `E <= e*(2h+1)*alpha^h`.

A table at global level `i` occupies slot `i-1`. Starting at head zero,
`FrozenTape.read` moves `(i-1)L` bits, reads `L` bits, then returns `iL` bits.
The exact charge is `2iL`. It is still `2iL` after a reset; physical field
slots are not renumbered. Applying (1) at each table-reading level gives

    H/L <= 2e*alpha^h * sum_(i=1)^h i
         = e*h*(h+1)*alpha^h.                            (2)

Bit reads themselves equal `L*T`. Table location is thus charged explicitly,
not treated as a random-access operation. This theorem concerns the compact
frozen-table band. An unrelated spectator prefix traversed on every request
would introduce a different charge and is excluded, as it is in PR2310.

The source's pending-events plus values stack has at most `2h+1` items in a
single coordinate evaluation. A Good descent increases that sum by one; a
Pair descent by two. A terminal value/constant keeps it unchanged, and a
continuation reduces it. The active depth is at most `h`. Each evaluation
leaves exactly one returned value, no pending continuation and head zero.

## 4. Sharp uniform constants

The ratios of successive positive terms of the depth envelopes are

    (h+1)alpha^h:       alpha*(h+2)/(h+1),
    h*alpha^h:         alpha*(h+1)/h,
    (2h+1)alpha^h:     alpha*(2h+3)/(2h+1),
    h(h+1)alpha^h:     alpha*(h+2)/h.

Each ratio decreases with `h`. Exact comparison with one puts their maxima
at depths 1, 2, 2 and 4, respectively. Substitution gives the five fractions
in Section 1. This ratio argument covers every depth; the finite envelope
table in the executable evidence is only a cross-check.

For sharpness choose `e=64^h` and only rank-42 Good steps. Then
`n_i=42^i*64^(h-i)`, so no floor loses anything and every inequality used
for the relevant quantity is an equality. At depths 1, 2 and 4 this gives
the stated attaining instances. The depth-four witness has 3,111,696 output
coordinates. The checker executes one coordinate there and uses the proved
coordinate-independent multiplicity formula; it does not claim to execute
that entire vector. Depths 1 and 2 are executed completely.

Sharpness is for the accepted grammar, not a claim that the selected physical
producer realizes every rank-42 ancestry or that its tables attain a worst
bit-operation cost.

## 5. Conditional preparation consequence: exponent 592

Retain PR2310's fixed `q`, fixed 64/128 dimensions, schoolbook modular
arithmetic, compact control bands, sequential complete-vector discipline,
and root coupling

    w = ceil(e^(17/10000)).

Also retain its hypotheses that one fixed-size full-ring table/plan can be
prepared in `O_q(w^3)` bit operations, an individual continuation/local
index operation fits that allowance, and no recursive request constructs
an entire parent vector. Those arithmetic and physical hypotheses are not
newly proved by the finite interpreter experiment.

There are `O(e)` requests, table preparations, ring operations and events
for one complete vector. Sequential table-head travel is `O(eL)` with
`L=O_q(w)`. Constructing or scanning the extent/descriptor list separately
for each output adds `O(n_h*h)` bounded-size operations, and

    n_h*h <= e*h*alpha^h <= (441/512)e.

Initial metadata and stack storage have the predecessor's polynomial bound;
the same per-step work allowance covers them. Output writing and local scratch
erasure are included. Thus this discipline has the sufficient preparation
envelope

    E_vector(e,w) <= A_q * e * w^3.                      (3)

Here `A_q` may absorb fixed call-site multiplicities. The vector theorem is
applied separately to each site; it is not a claim that all passes or all
recursive payloads together cost (3). A site making more than a fixed
multiple of `n_h` weight requests needs a separate count. Arbitrary extra
coefficient work is not licensed by this bound.

For `w>=2`, `e^17<=w^10000` gives the entirely integral comparison

    (e*w^3)^17 <= w^(10000+51) <= w^(592*17),

so `E_vector <= A_q*w^592`. When `w=1`, root coupling forces `e=1`; the
empty ancestry has bounded preparation and the predecessor's identity-header
bypass applies. Exponent 592 is a sufficient envelope, not a lower bound on
the optimal preparation algorithm.

PR2310's existing factorial absorption argument applies with `A=592`:

    w^592 / q^(w-1) <= 2^592 * 592!     (q>=2, w>=1).

Indeed `w^A/A! <= binomial(w+A-1,A) <= 2^(w+A-1)`. Thus the same complete
body/header fibre accounting retains a root-independent constant. The explicit
factor has 5,196 bits instead of the predecessor's 18,675-bit factor for
`A=1800` (the checker recomputes both exact integers). This does not compare
the unknown constants `A_q` or establish a practical runtime improvement.

The predecessor already claims `C_q V(n+w)` under its physical premises.
This result tightens one sufficient preparation estimate within that claim.
It does not close completed payload dispatch, actual matrix production,
spectator/counter lowering, physical parking, selected GL64 hosting, precision,
the recurrence's physical premises or supplier admission. No new kappa follows.

## 6. Evidence and attribution

`audit.py` computes level multiplicities independently of the source's stack
execution order. It compares them with the unchanged source's meters and
counts actual popped events with Python line tracing. The abstract finite
census, actual full-vector corpus, deep binary fixture, sharpness instances
and adversarial controls are separately labelled in `RESULT.json`. Source
and receipt authentication remain part of replay.

The grammar, interpreter, global-age reset contract and factorial absorption
are predecessor work: Jose Manuel/PR2310 and PR2234, commdata2338/PR2188,
Ross Richardson/PR2159 and their retained lineage. PR2332's actual-table
binding is complementary and is not replayed here. The new result is the
coupled width/request proof, sharp constants and its conditional preparation
consequence. Prepared for commdata2338 (@commdata2338), with substantial
OpenAI Codex assistance. Author-checked only; no independent human or formal
review is claimed.
