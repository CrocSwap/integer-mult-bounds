# Paired E-free BIT caller at the existing ordinary saving 0.00385248

This is a conditional premise reduction, **not a new kappa or a new raw paid-profile advantage**.
The old chain-root BIT construction of DreamingOfClouds in #6834 already has
the raw crossing `(0.0038525393934, 0.0038525393935)` and ordinary saving
`0.00385248`. An initial independent reconstruction here rediscovered that
invoice. Its slightly tighter ordinary margin is not presented as a research
advance. The contribution below removes all its empty-body root credits by
pairing actual BIT native calls and specializing CubeJerry's #6980 caller.

## 1. Sources and exact statement

Exported source inputs are listed with byte hashes in `INPUT-PINS.json`;
`SOURCES.json` keeps only base-main Git provenance:

* #6834, `79603d1f7d243f1d034613df84991673a94ad5ae`: existing chain-root BIT invoice.
* #6726, `435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`: actual unchanged BIT native,
  integral-transfer method, independent source checker, finite compiler,
  independent interval arithmetic, ordinary/route/ownership allowances.
* #6980, `617903497387a98f7ca929ad0b6928dd32abffec`: QUERY-only replacement of the
  two separated QSELF sites in DreamingOfClouds' E-free two-chain caller.
* Main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`: selected ordinary BIT backend
  `17/5000`, not the empty-credit supplier, is the bootstrap starting point.

The new 38-input caller uses only ADD, SWAP, QUERY, LOCAL and IDLE_ONE. It has
798 events: 362 ADD, 364 SWAP, 36 LOCAL, 32 IDLE_ONE and 4 QUERY. Its diagonal
has 38 entries, each `q` times a **nonempty** monomial in the independent body
operators `D1,...,D18`. Every coefficient is checked in
`F2[q,D1,...,D18]/(q²-1)`, retaining repeated powers of D. No inverse,
idempotence or numerical specialization of D is used.

The direct row engine and the retained independent reverse-functional engine
each verify all 1,444 coefficients. Their agreement establishes the stated
finite formal identity; it does not prove the inherited physical all-width
native/QUERY/erasure contracts.

## 2. Integral specialization, without dividing by two in F2

The #6980 source is a mixed A/B caller. Each joint event has a block-diagonal
action: a two-shear HOST2 block on the 38 A roles and a separate hosted block
on the B roles. All other events remain within their type. Retain only A.
This selection is checked from every event's literal role indices, not inferred
from counts.

First impose `q²=1` over characteristic zero. The source normalization

`lambda_s = ((1+s*i)+(1-s*i)*q²)/2`

is exactly 1 in this quotient. Delete those normalization operations there.
Every remaining A ADD coefficient is an integer, every SCALE is ±1, and
the HOST2 second shear has coefficient -1. The result is an integer identity:
the relevant quotient of `Z[q,D1,...,D18]` is free as a Z-module on the
standard monomials. Only now reduce coefficients modulo two. Odd ADDs become
XOR, even ADDs disappear, SCALE ±1 disappears, and `q^-1=q`.

The resulting identity is also replayed directly in the characteristic-two
ring, so it does not rest solely on the source complex proof. In particular,
the test replacing QUERY by ADD passes after the unfaithful specialization
`q=1`, but fails in the actual quotient. A mutated scalar 1/2 is rejected;
there is no map that treats the source 1/2 as a characteristic-two scalar.

## 3. Why two real native copies are necessary in this fixed interface

For a fixed scalar caller with only ADD, SWAP, QUERY, LOCAL and IDLE_ONE,
specialize every D to 1. Every allowed event has determinant 1 over
`R=F2[q]/(q²-1)`: ADD and QUERY are transvections, SWAP has determinant
`-1=1`, LOCAL is the same transvection, and IDLE_ONE becomes identity.

A single E-free chain has 19 q-bearing outputs. For the native's 111 ports,
the desired determinant would be `q^(19*111)=q`, whereas `q != 1` in R
(equivalently write `q=1+epsilon`, `epsilon²=0`, `epsilon != 0`). Therefore
that exact odd-port target contract cannot be obtained by those gates on
those root roles. Evaluating q=1 would erase this obstruction. This is a
fixed-interface argument, not a universal no-go result for BIT algorithms;
additional targets, QSELF, new owned interfaces or different target contracts
are outside it.

Two copies give 222 chains and even q degree. Pair the corresponding port
from the two native copies, producing 111 independent 38-role groups. The
#6980 replacement couples only the two chains within each group. At each
of the 18 stage cuts, the first actual native supplies the first shear of
all 111 groups and the second supplies the other shear. These are **36
actual native invocations**, with disjoint fresh public helpers and owned
lifetimes. They use the same seven body axes within one stage, on disjoint
arrays; different stages use disjoint body axes. The ambient remains
`1+7*18=127`. `native_instances` in the receipt lists all 36 occurrences,
root role maps, helper namespaces and body axes.

The native file SHA256 is
`51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78`.
Its unchanged source checker replays all 659 public scalar inputs, all
owned lifetimes and native MOVE ranks, and checks the 111 rational
head/body charts. The all-width transform theorem is inherited, not reproved.

## 4. Complete recursive invoice

Write `H_r=r^(1-kappa)`. The unchanged native contributes, per actual call,

`P0={1:1386,2:1253,3:62,4:47,5:9,6:104,7:10}` and
`T0={2:1,4:25,6:1,8:410}`.

The new complete profiles are

`Pnew = 36 P0 + 444 H1 + 444 sum(j=1..8) H_(7j)` and

`Tnew = 36 T0 + 222 H127 + 444 sum(j=1..9) H_(1+7j)`.

This counts both native copies, every one-field whole idle, every thin query,
every fresh native helper and every independent root target exactly once.
The totals are 19,950 productive fields, 107,352 paid jobs and rank surplus
1,506. There is no productive rank-1 credit, and every root target has a
nonempty body mask.

Relative to the complete #6834 invoice,

`Tnew = 2 Told - 222 H1`, `Pnew = 2 Pold - 222 H1`.

These are exact all-rank histogram equalities, checked against the pinned
#6834 receipt. Hence every complete signed moment is doubled and the raw
crossing is unchanged. This is not a numeric improvement disguised as a
change of root size.

## 5. Finite loss, compiler, ordinary work and bootstrap

At tested saving `0.00385253`, two separate rational interval engines bound
the signed margin and all three finite-tail ratios. With chronological
product power 768, paid cutoff 15, productive floor 16 and both tail offsets
1/5, the normalized paid-plus-discarded-target bound is strictly below one.
All discarded complete productive outputs become owned zero inputs and are
charged in `D=19950^768-W`. Their productive mass is not retained.

The uniform compiler uses gap `10^-10`, theta `42/43`, logarithm power 610,
and integer threshold `H=293160000000000`. The integer inequality is checked
at the displayed threshold, and the preceding grid point fails. Cover loss
is separately debited by another `10^-10`, leaving covered saving
`0.0038525298`. The receipt supplies the product, reset, owned and ordinary
compiler constants rather than omitting these enormous finite costs.

The full changed ordinary recount is:

| Quantity | Bound |
| --- | ---: |
| Visible native/caller work | 363,507,600 |
| Routed whole-job work | 740,743,004,160 |
| Combined ordinary work | 741,106,511,760 < 10^12 |
| Owned bank | 6,878,988 < 10^7 |

The same fixed `10^12` allowance funds the two native copies; it is not
doubled for free. The source tariff is inherited. Neither the emitted
enormous product nor a physical fixed-tape implementation is materialized.

Crucially, the ordinary bootstrap does **not** use #6726 or #6834 as its
starting backend, since that would re-import their empty-credit dependency.
It starts from the selected `17/5000=0.0034`, authenticated by the selected
record and `frontier6030/CLAIM.json`. For atom `a=1/250`, each step checks
the full envelope `(1-a)*covered + a*previous`, strict improvement and both
stock inequalities. The steps are

`0.0034 -> 0.0038507 -> 0.00385248`.

The first envelope is `0.0038507196808`; the second is
`0.0038525224808`. One step cannot justify the retained final saving.
The selected backend is a source-bound inherited contract, not rerun here.

## 6. Validation and limits

Run `python3 -I -B check.py` with Python 3.11+ and the standard library.
It authenticates retained sources, recomputes the caller and receipt, compares
all proof-relevant fields against the frozen artifacts without writing, and
checks exact identities and the full displayed budget. Artifact generation is
available only through explicit `--write`. Negative controls
remove a LOCAL, the second native in a pair, QUERY, IDLE_ONE, ADD or SWAP;
replace QUERY with ADD; erase a target's q factor; and introduce a 1/2
coefficient. Each relevant formal or integrality gate rejects it. The
determinant fixtures retain q distinct from 1 and show why QSELF would fall
outside the obstruction.

The five framework assumptions remain: native_all_columns, owned_erasure,
compiler, precision_tape and analytic_recovery. The inherited one-field idle,
whole-job adapter, scalar and routing tariffs still require their usual
source-contract review. No new opcode is introduced; no empty-body root
input is assumed acceptable. The paired composition is a concrete formal
caller and complete conditional invoice, not an unconditional multiplication
theorem or a maintainer-admitted frontier update.

## Open next questions

1. Independently review the 36 native-call embeddings and the reuse of the
   common head/body interface on two disjoint arrays per port. The finite
   caller equality does not establish every physical all-width contract.
2. Can two actual BIT copies share productive helper infrastructure while
   retaining the E-free caller? First require a complete F2 endpoint and
   frame invoice; simple identification of helper registers can leak old
   inputs and must not be credited from the complex construction.
3. Can a different fixed target contract avoid doubling an odd 111-port layer?
   The determinant proof says exactly which current assumptions must change.

Credit: DreamingOfClouds for the chain-root BIT and E-free roots; @CubeJerry
for #6912 caller blocks and #6980's separated QUERY-only replacement; zxv
and the retained authors for #6726's integral transfer and full admission
framework; Ali Romman and Cinna Davis for the root/native lineage. Source
notices remain unchanged. This specialization, parity analysis and complete
recount were prepared with substantial OpenAI Codex assistance. Apache-2.0.
