# Exact consecutive batches for mixed-precision cancellation

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration.
There is no new kappa or selected-frontier change.

For every rational affine scalar increment, the consecutive inputs on which
coarse and fine rounded increments agree have an exact run-length law.
The law gives a sharp maximum batch length, an explicit attaining start,
and the exact frequency of every proposed batch length without enumerating
the source period. This adds ordered batching information to woklerx's
[PR1853](https://github.com/CrocSwap/integer-mult-bounds/pull/1853), whose
bounded-interval counting theorem is a cited predecessor, not an audit target.

In coarse-grid units put

```text
t_k = c + (a/d) k,   gcd(a,d)=1,   d>1
R(t) = floor(t+1/2),   F_g(t) = floor(g t+1/2)/g,   g=2^s, s>=1
m = floor(d c),   theta = d c-m
L = ceil(-d/(2g)-theta),   U = ceil(d/(2g)-theta)-1,   B = U-L+1
v = a-d*floor(a/d+1/2),   u = abs(v),   B = q*u+r,   0<=r<u
```

Per period d there are r maximal safe runs of length q+1 and u-r of
length q, omitting zero counts and zero lengths. The sharp longest batch
has length `ceil(B/u)`. Exactly `max(0,B-(ell-1)*u)` starts per period
admit a safe batch of any positive length ell. If B is nonzero, a longest
run starts at `(j-m)*a^(-1) mod d`, where j=L for positive v and j=U for
negative v. Integral coefficients are handled separately as a constant
all-safe or all-unsafe sequence, depending on the offset.

[PROOF.md](PROOF.md) gives the quantified statement, the half-open tie
boundary and the proof. Its key step unwraps every adjacent safe pair into
the same signed integer step. Safe runs become finite residue chains in
one integer interval. The universal claim rests on that written proof.

For coefficient 1/1000, zero offset and two extra bits, the longest batch
is exactly 250, starting at 875 modulo 1000. No 251 consecutive inputs are
safe. For coefficient 3/8 and one extra bit, there are two length-one runs
and one length-two run. At coefficient `1/(2^100+1)` and three extra bits,
the sharp maximum is `2^97+1`; no large period is enumerated.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/cancellation-safe-batches/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/cancellation-safe-batches/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cancellation-safe-batches
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cancellation-safe-batches --check-source-history
```

Another host may replace the interpreter path with its CPython 3.12.
In a sparse checkout, materialize `research/bounded-grid-rounding-count`
first. The direct verifier authenticates its pinned README, imports no
predecessor code, prints `PASS_CANCELLATION_SAFE_BATCHES` in a generated
JSON receipt, and writes nothing. The receipt binds all six package files
and the one declared predecessor text. The registered runner additionally
validates Git blobs and historical provenance.

The independent oracle literally rounds every point of each small period,
finds every maximal cyclic run and tests every start for each batch length
one through d+1. Its domain is all reduced signed coefficients a/d with
2<=d<=24 and -d<=a<=d; offsets 0, 1/3, -3/8, 1/(2d), 1/(4d); and gaps
one through four. It also covers integer coefficients -3..3 with offsets
c/8 for c=-8..8 and the same gaps. Separate literal signed dirty-target
updates check rescaling at three source/coarse grid pairs. Four large
fixtures check their exact attaining endpoints and neighboring failures;
they do not enumerate their periods. Counts are incremented by the checker
and emitted in the generated receipt. The final finite domain has 7,636
cases, 117,036 literal source points, 17,948 maximal runs, 124,672
all-start batch-count comparisons and 6,812 attaining runs. The separate
grid check executes 891 dirty updates. All 15 boundary/input controls pass.

Boundary controls cover asymmetric ties, an empty safe orbit, two positive
run lengths and a step near an integer. Invalid float inputs, booleans,
nonpositive or excessive gaps, excessive rational sizes, and invalid batch
lengths reject explicitly under normal and optimized Python.

## Limits and implementation

The executable caps rational numerators/denominators at 4096 bits, the gap
at 256, and the requested batch length at 2^4096. The written theorem has
no such caps. The literal oracle permits periods at most 32. Every loop
has a fixed finite domain or an input bound. There is no recursion,
network, subprocess or runtime import of predecessor code. Functions fit
within 60 physical lines. Warning-strict normal/optimized replay and AST
inspection supply the available diagnostics; no proof kernel is used.

Power of Ten rule 3 has a managed-runtime deviation. Python integers,
Fractions and collections allocate during the computation. Six package
files are capped at 128 KiB each, the source text at 64 KiB, and only one
small period of at most 32 booleans is live in an oracle call. The small
census retains counters rather than all cases. Exact integer bit lengths
are bounded by the input caps and fixed arithmetic expression depth;
allocator overhead is not measured. The two local rejection callbacks
have fixed validator targets and no external dispatch. This is a bounded
reference computation, not a fixed-allocation physical runtime.

Restoration assumes the source is unchanged and both signed target updates
are exact. It does not cover internally rounded nonlinear leaves, aliasing,
overflow, saturation, target rounding or adaptive precision. Complete-period
frequency does not imply a distribution of reachable source inputs.
No actual native caller, physical scheduler, precision/storage/movement
invoice, compiler or outer admission is supplied. All five selected
framework assumptions remain. Selected cold replay, Lean and Docker were
unrun. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Can one actual rounded-linear caller use an attaining consecutive batch?
Start with a pinned inverse pair, its exact affine source parameterization
and a proved consecutive-index domain, then charge batch routing and the
complete precision/storage bill. Source reachability and a physical caller
remain the blockers. No follow-on scope is reserved.

## Sources and coordination

Base main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The uniform-transfer-audit card is explicitly changed to
this precision-interface side result; it discharges no selected assumption.
[SOURCES.json](SOURCES.json) pins the source text and historical provenance.
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375381)
follows live open/account PR, active Discussion, main/merged general-form
and formula searches and local reservation checks. Arbitrary diffs, sparse
historical notes and unpublished work remain overlap limits.

Credit woklerx for PR1853/1848, Adam Gall for PR1908, Gareth Davidson,
Chafik Boukhalfa, Ali Romman and the retained dirty-leaf lineage. Nick
Petalas's older PR4881 universal affine-box test and PR4878 period-density
bound are related context; the ordered run census is the new step here.
Interval rotations and Euclidean division are classical. No global
literature-priority claim is made. Predecessor files and credit are unchanged.
