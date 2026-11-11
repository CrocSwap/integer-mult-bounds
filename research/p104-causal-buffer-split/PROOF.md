# A timed two-buffer helper split on the exact composed word

This is a source-bound conditional construction and finite certificate. It is
not a proof of the complete multiplication theorem. Ali Romman's causal-history
owned-buffer mechanism is the predecessor; this package supplies a newly priced
instance on the current word. CubeJerry's contact-free retiming and temporal
coefficient methods, Matarener's kernel methods, and all retained source authors
remain credited.

## Source and typed observations

The complete 37-file artifact at
`666fd749ec465de7238633a0c2fd5ee3081477e0`,
`research/p104-output-rechart-composition`, is retained in `INPUTS.json`.
Its reconstructed native SHA256 is
`9557c4682056ab7cc7cda89aa73865bef0e3948cc10b3c3061b0a944af05b96a`.
Rohan Arun's PR #7131 represents the identical canonical native construction.
The selected frontier is not changed here.

A cut t means immediately before original event t. Work in normalized chart
coordinates, in which a correctly implemented MOVE preserves scalar values.
Let P(t,r) be the complete source row at that cut and S(t,r) the complete final
response to adding one unit to role r there. Both include every public input or
output coordinate, with owned INIT/CLEAR and COPY treated explicitly.

Take F=237 with basis [30,75,138,266], dimension four; U=3 is the zero space and
V=127 the full nine-dimensional space. The certificate gives

| Cut | Role | Gather coefficient |
|---:|---:|---:|
|27366|323|−1|
|27429|320|−2|
|27476|321|1|
|27482|330|2|
|27540|23|2|
|40052|49|1|
|40066|333|−2|

The exact sum of these rows is

`c = −e411 − e320/2 − e331/2 − e335/2`.

The sole later injection is role 22 at cut 45280 with coefficient −2. Its
complete response is `d = −2 e331`. Thus `c d = 1`. Every support coordinate
belongs to the helper boundary group (3,127); all main and other helper
coefficients cancel exactly. `certificate.py` reconstructs these equations
from the frozen source, without importing the search.

Seven original MOVE paths are retimed within their adjacent scalar contacts,
as listed in `PATHS.json`. No target write or source read lies inside those
intervals. Their ordered paths and paid ranks are retained. The additional
path is role 49, interval [40052,47650], original event 47648: frame 734 to 127,
rank six. Frame 734 has basis [30,138,266]. Replace it by 734→237 at cut 40052
and 237→127 at cut 47650, ranks one and five. All observations are performed
after entry to F and before departure. The constructor checks the literal
source intervals, all original scalar frames and the retiring pivot's actual
residency. Original MOVE indices are removed only after those checks.

## Boundary identity and chronology

Let p=333. The credited helper-basis algorithm emits G with row p equal to c
and `G d = e_p`. Its eight elementary instructions and their inverses use the
existing 2,3,5-smooth alphabet. Apply G inverse to the old helper inputs at U.
Then the timed gather functional c has value x_p, the original independent
input assigned to p. All main inputs and other boundary groups are untouched.

Introduce a fresh independent public input z at F, role n=1492. It is an
arbitrary input, not an initialized scratch field. Explicitly initialize owned
A at F before the first gather and add the seven observations to it. Because
gathers only read the old program before retirement, A=x_p at cut 40066.

At that cut p actually resides at F. Let its current value be v. Initialize
owned B=0 at F and emit:

```
B += n
B -= A
n += p
n -= A
n -= B
p += A
p -= n
```

Now B=z−x_p, n=v and p=x_p. Clear A explicitly under the inherited owned-erasure
assumption. Retire p at F; all remaining occurrences of old p use n instead.
Every old owned label is shifted by one to make room for the new public role.

At cut 45280 emit `role22 += −2 B` in F. The response identity shows that this
changes the old final outputs by `d(z−x_p)`. Clear B after this injection. The
old circuit otherwise continues unchanged in normalized coordinates.
Finish with G at V, using n as the successor of p. Since the source acts as the
identity on the helper group and `G d=e_p`, all continuing outputs have their
original values except the successor p slot, which is z. The retired public p
already equals x_p. Every independent public input is therefore restored to
its specified output, and all main actions are preserved.

This argument uses two explicit owned accumulators and their erasure contract.
It does not assume that the local replacement on public cut coordinates is
invertible or that a simultaneous middle pairing equals one. It does not add
an opcode or grant a free cross-frame exchange. The whole emitted operator is
also checked separately by exact forward and transposed reverse execution.

## Complete change and obligations

The productive helper ranks change by `{4:+1,5:+1,9:−1}`; paid MOVE ranks by
`{1:+1,5:+1,6:−1}`. Rank masses are unchanged. The native has 1,493 public
fields, 1,093 helpers, 53 owned labels, 56 owned lifetimes and exact owned peak
44. The previous counts were 1,492/1,092/51/54/43. Owned rise mass remains 56.
There are 74,627 events, a delta of 27 ADD, four SCALE, one MOVE, two INIT and
two CLEAR instructions. Both newly owned lifetimes and every scalar instruction
are included in ordinary, precision and finite-tape accounting.

The 17-stage caller repeats the native changes 17 times: 110,417 paid positions,
22,325 productive fields, rank surplus 1,424 and zero empty credit. The two
directed price engines give claim κ=.003642959019031. Full application evidence
and verification status belong to `APPLICATION.md` and `VALIDATION.md`; this
algebraic argument alone does not discharge their obligations.

The independently derived grid remains 1125/F25. Precision adapters replace
the old exact lifecycle census (54,43,51) by the checked new census (56,44,53),
with counted source substitutions in temporary code only. The lifecycle check
is retained, and an extra uncharged lifetime is rejected. Frozen predecessor
bytes are not edited.

The five framework assumptions remain `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. Finite complete checks,
independent human/formal acceptance, maintainer admission and execution of a
compiled top-level multiplier are distinct obligations.

## Open next questions

1. Independently replay the timed coefficient certificate and complete
   application, especially the two owned lifetimes and their compiler costs.
2. On a freshly pinned successor, can a different causal history repay its
   complete path and storage bill? The search stopped at its first positive;
   it does not prove a temporal ceiling or exhaust the remaining paths.

Prepared for dillona with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. All nested source notices are retained.
