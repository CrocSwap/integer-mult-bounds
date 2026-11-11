# Causal helper split at frame 595 with a retained scalar-width contract

Prepared for dillona with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. This is another source-bound instance of Ali Romman's causal-history
owned-buffer identity. CubeJerry's retiming and exact verification methods,
Matarener's kernels, Rohan Arun's endpoint construction/caller and all retained
authors remain credited. No mechanism-invention claim is made.

## Exact source and timed coefficient certificate

INPUTS.json retains the complete 33-file #7145 package at
`db8f31c4a1d9e191976e2c92951e6d2dea886a27`, native
`8f5c08866c50070c8579d0dc230bc2941ec3669d643ba373ac4b1d59b423446d`.
PEER-INPUTS.json retains all 31 files of #7143 at
`9ff298bd6547299dc5b263873bf8a400909e5501` as the implementation reference.
Both archives include their full nested closures and notices. Six retained
implementations are byte-identical; construct.py is retained under the explicit
name temporal_construct.py. The new construct.py adds only the charged scalar
normalization described below. Every registered command authenticates this reuse.

Let P(t,r) be the complete normalized source row before event t and S(t,r) the
complete final response to injecting one unit into role r there. All public
inputs, main outputs, COPY and owned initialization/erasure are included.
The exact certificate is

```
c = 2 P(38883,1207) - 3 P(68,1479) + 2 P(38882,450)
    + P(35972,581) + P(35972,582) - 2 P(31897,451)
d = -2 S(41969,757)/3 + S(40248,1207)/3
    -2 S(41967,1255)/3 - S(40250,1479)/3.
```

WITNESS.json lists every coefficient of c (42 coordinates) and d (353).
The checker reconstructs both vectors exactly, proves they lie wholly in the
helper group 3→127, and proves c d=1. The last gather is 38883 and first injection
is 40248, so retirement at 38883 is causal. This dense certificate is not inferred
from a simultaneous cut or from a selected sample of coordinates.

## Paths and boundary identity

F=595 has basis [52], dimension 1. Pivot 451 is actually in F at retirement.
Nine source-bound neutral paths bring the gathering/delivery roles to F at their
stated times, preserving every MOVE and paid rank. All role events and source
reads in each interval are checked. Role 757's one changed path spans
[32841,41969], original MOVE 41968 from zero 3 to 603. Replace it by 3→595 at 32841
and 595→603 at 41969, ranks 1+1 instead of 2. Its injection occurs before departure.

The retained basis constructor produces G with row451=c and Gd=e451.
Apply G inverse at zero 3. Initialize owned A in F before the first gather
and accumulate the six listed prefix observations. Their combined row after
G inverse is e451, so A=x451, the original independent input. The fresh public input is n=1495,
with arbitrary value z at F. At retirement let pivot451 hold v. Initialize B=0
and execute the credited seven ADDs:

```
B += n; B -= A;
n += p; n -= A; n -= B;
p += A; p -= n.
```

The result is B=z-x451, n=v, p=x451. Clear A; retire p at F. Continue the old
p program on n and inject the four listed multiples of B. Their final response
is d(z-x451). Clear B after the last injection, then apply G at 127 using n as
successor. Thus n returns z, p retains x451, and every other output/main
operator is unchanged. Both owned buffers are explicitly initialized, charged
and cleared. Every old owned label shifts by one. The full forward/adjoint and
cleared-owned rows are checked independently.

## Four exact scalar refinements

The initial emitted word had four ADD coefficients whose reduced numerators
had 25 bits. The retained fixed-tape substitution requires at most 24; its
assertion is kept unchanged. For each such distinct-role ADD(r,s,q), write
q=a+b using numerator floor-halving at the same denominator. Emit ADD(r,s,a)
and ADD(r,s,b), consecutively in the same chart. Since r!=s, the source is
unchanged and the exact sum equals the original operation. Each summand has
at most 24 numerator bits and a denominator dividing the original denominator.
All four extra ADDs are charged. Grids, rounded envelopes, ordinary and tape
costs are recomputed for this normalized word.

NORMALIZATION.json retains the original native hash and the exact count.
The original native replay was interrupted before completion after this
compiler-premise issue was found; it is not a passing receipt. The final
normalized native hash is
`ecb1f56ba06dbaae424d0f94ad41c6d08f39f5f1f2fec348f2d0c9c9873c657f`.
The source archives and retained constructor bytes are unchanged.

## Full accounting and limits

Native ΔP={1:+2,2:−1}, ΔT={1:+1,8:+1,9:−1}; both rank masses remain unchanged.
The normalized word has 76,150 events, 1,496 public fields, 1,096 helpers, 57 owned labels,
60 lifetimes, peak 45 and rise mass 56. Relative #7145 it adds 815 ADDs, 4 SCALEs,
one MOVE, 2 INITs and 2 CLEARs. All long-lived buffer stock is included.

Both directed preliminary prices give κ=.003643716168305, a gain of
.000000277661886 over #7145. The literal 17-stage caller, all maps, ordinary,
precision, physical and compiler gates are separate obligations; their actual
status is in APPLICATION.md and VALIDATION.md. No earlier receipt substitutes
for replaying this normalized word. The search stopped at its first positive
after 4,250 of 7,660 one-path candidates. No optimality or global barrier follows.
Chris R/Clear1nsight's two-paid-path investigation on #7143 is a distinct scope.

## Open next questions

Independently replay the dense timed vectors, long owned lifetimes and four
scalar refinements, then the full changed invoice. Start with VERIFY.json,
WITNESS.json, PATHS.json and NORMALIZATION.json. A future optimization requires
a fresh upstream/overlap checkpoint and its own complete costs.

Five inherited assumptions remain: native_all_columns, owned_erasure, compiler,
precision_tape and analytic_recovery. Human/formal acceptance, maintainer
admission and compiled top-level execution remain open. Credit Ali Romman,
CubeJerry, Matarener, Rohan Arun, ToikY, Cinna Davis/1337isnot1337, Dugongue,
DreamingOfClouds, Douglas Colkitt/#7000 reviewers and every retained author.
