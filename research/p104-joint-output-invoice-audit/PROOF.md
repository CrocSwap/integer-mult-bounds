# Independent finite invoice audit for frozen PR6353

## Proposition and explicit premises

This result derives a finite **formal job invoice** for the frozen PR6349
source word and PR6353 output word. It uses the rank tariff declared in
`sources/tariff-source.py` and the fixed caller interface and diagonal in
`sources/CONTROLLER.json`. The invoice is a multiset of paid and productive
job ranks. It is not native-operator or physical-caller admission.

The source/output word bytes are authenticated before counting. The output
is PR6353 head `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`; its PR6349 input
word is retained at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The fixed PR6348 caller and the
declared tariff are separately frozen in `SOURCE-PINS.json`. The predecessor
result is used only for a final comparison, after independent derivation.

The declared interface allocates a fresh helper-target copy to each distinct
`LOCAL` stage. It charges each thin `QUERY` at rank one per main port, and
each field in a paired `IDLE` at rank eight times its number of stages.
For the declared caller diagonal, a main field with nonzero central exponent
and `s` distinct stage coordinates has productive rank `1+8s` per port.
These are the explicit tariff/interface premises of this finite audit.
Proving their native realization, physical ownership and phase, or proving
that the emitted caller realizes that diagonal, remains separate.

## Local ledger and the nine target debits

Write `H_r` for a formal rank-`r` job price. Every literal `MOVE` contributes
one paid job of rank equal to the absolute difference of its source and
destination frame dimensions. The temporal inventory tracks owned labels,
including all their downward moves. An owned move is counted even though
an owned field earns no productive target.

The public main roles are the 104 live roles and their partners at offset
112, for 208 main roles. The other 562 public roles are the helper targets.
Their productive rank is the positive difference of final and initial frame
dimensions. Owned labels are outside that target inventory. Counting frame
dimensions and literal moves establishes a formal ledger; it does not prove
the corresponding native all-column maps or erasure permissions.

Let `P_0,T_0` be the source local paid and helper-target profiles and
`P_1,T_1` the changed profiles. Independent recount gives the exact formal
identities

```
P_1-P_0 = 14 H_1 - 4 H_2 - 3 H_3 + 4 H_4 - 5 H_5,
T_1-T_0 = H_5 + 8 H_8 - 9 H_9.
```

Exactly nine helper productive ranks change. Role 703 loses four productive
rank units, from nine to five. Roles
`393,707,484,297,485,226,361,451` each lose one, from nine to eight.
Their input declarations are unchanged. Thus the helper count stays 562,
and all nine debits are present rather than crediting the old rank-nine
targets after reducing their outputs.

The paid-job count increases by `14-4-3+4-5=6`. Its rank mass changes by
`14-8-9+16-25=-12`. Productive rank mass changes by `5+64-81=-12`.
Both sides of this signed invoice are necessary; a paid-rank decrease alone
does not establish an improved moment.

## Binding all nineteen copies to the fixed caller

The frozen event list has exactly nineteen `LOCAL` stages, each used once.
Formal helper jobs are indexed by `(stage, public helper role)`, so the nine
changed targets give exactly `19*9=171` distinct debit records. This is a
formal distinct-copy allocation under the stated interface, not a proof of
physical fresh-stage ownership.

The caller has three binary trees with 4, 7 and 8 leaves. A forest with
nineteen leaves and three roots has sixteen internal nodes. Their subtree
size multiplicities are

```
c_2=9, c_3=1, c_4=4, c_7=1, c_8=1.
```

There are sixteen thin queries and sixteen paired idles. The 104-port query
invoice is `16*104 H_1`. Each internal node contributes two main fields,
each with 104 copies, hence 208 jobs of paid idle rank `8s` and productive
rank `1+8s`. The two exterior main fields each use all nineteen stages and
give 208 productive jobs of rank `1+8*19=153`.

Consequently, for either local profile pair `(P_i,T_i)`, the complete
declared caller invoice is

```
P_i^call = 19 P_i + 1664 H_1
           + 208 (9 H_16 + H_24 + 4 H_32 + H_56 + H_64),
T_i^call = 19 T_i + 208 H_153
           + 208 (9 H_17 + H_25 + 4 H_33 + H_57 + H_65).
```

The emitted event/diagonal recount and this tree formula must agree as full
integer rank profiles. Their equality is an invoice identity under the
declared diagonal; it does not replace a Laurent endpoint proof of the
caller. The fixed query, idle and main-target parts cancel in the
source/output difference, leaving nineteen times each local signed change.

The productive-job count is `19*562 + 34*104 = 14214` for both words. The
changed paid-job count is `19*3456 + 1664 + 208*16 = 70656`; the old count
is 70542. The changed paid and productive rank masses are 200938 and
201746; their difference is 808. Both masses fall by 228 from the old
invoice, so the rank-mass surplus alone does not explain the fixed-saving
strict inequality.

## Rigorous moment at one fixed saving

An independently written oracle recounts the local and complete profiles
without importing the primary checker or predecessor code. It then checks
only the fixed rational parameter

```
k = 315057/100000000,       H_r = r^(1-k),
D = sum_r (target_count_r - paid_count_r) H_r.
```

All ranks are positive integers and the largest included rank is 153.
Every productive price is positive, so `D>0` is equivalent to a formal
paid/productive moment below one.

For each rank, set `e=floor(log2(r))` and
`z=(r-2^e)/(r+2^e)`. Then `0<=z<1/3` and

```
log(r) = e*log(2) + 2*atanh(z).
```

The 48-term positive series for `2*atanh(z)` is a lower bound. Its omitted
tail is bounded above by

```
2*z^97 / (97*(1-z^2)).
```

Indeed the next exponent is 97, every later denominator is at least 97,
and the remaining powers sum to a geometric series. The same construction
at `z=1/3` bounds `log(2)`. Nonnegative integer multiplication by `e` and
addition preserve these bounds. The oracle rounds the lower logarithm
down and the upper logarithm up to the grid `10^-40`.

For all included ranks, the resulting `x=k*log(r)` bounds lie in `[0,1]`.
The alternating series for `exp(-x)` has decreasing term magnitudes there.
Its degree-17 partial sum is a lower bound and its degree-16 partial sum an
upper bound. Since `exp(-x)` decreases, evaluating the odd sum at `x_upper`
and the even sum at `x_lower` encloses the exact value. Multiplication by
`r` gives `r^(1-k)`; final rounding is outward to `10^-30`.

The signed sum uses the lower power bound for a nonnegative coefficient
and the upper bound for a negative coefficient when forming its lower
endpoint, with the choices reversed for its upper endpoint. All arithmetic
in these enclosures is rational. The exact certificates include

```
changed D >= 3060557499610309553830947421 / 10^30 > 0,
source D  <= -192875573170364277720987693967 / 10^30 < 0.
```

Thus the changed formal invoice passes this one moment gate, while the
source invoice with the same fixed caller fails it. No crossing search,
uniqueness result, new admitted saving or frontier update is inferred.
Nor is uniform improvement for arbitrary tariffs claimed: at the constant
price `H_r=1`, the changed paid-minus-productive bill is worse by 114 jobs.

## Contained scalar-work tally

The local literal ordinary tally follows the frozen coefficient convention,
without importing its implementation. `INIT` and `CLEAR` cost two units
each. For reduced nonzero dyadic `q=m/2^d`, an `ADD` or `COPY` costs
`2*(3+floor(log2(abs(m)))+popcount(abs(m))+d)`. A dyadic-unit `SCALE`
costs `2*(abs(log2(abs(q))) + indicator(q<0))`.

This counts the declared local allowance, including every owned initialization
and clear: 127088 units for the source and 128694 for the changed word.
It does not establish complete nonrecursive funding: native
lowering, routes, caller scalar work, compiler costs and the original
ordinary-work proof are outside this finite tally.

## Semantic controls and evidence boundary

The primary receipt supplies six explicitly counterfactual invoice vectors.
Each differs in a concrete rank coefficient from the complete derived bill:

| Incorrect ledger | Rank | Correct coefficient | Incorrect coefficient |
|---|---:|---:|---:|
| Omit one actual owned transport in all nineteen calls | 4 | 1976 | 1957 |
| Omit one complete local paid bill | 1 | 44053 | 41822 |
| Retain one old rank-nine target instead of its rank-eight debit in every call | 8 | 570 | 551 |
| Give one owned label productive credit in every call | 1 | 266 | 285 |
| Leave one thin query unpaid | 1 | 44053 | 43949 |
| Leave one member of one paired idle unpaid | 32 | 832 | 728 |

These are counterfactual accounting checks, not six executed mutations of
valid source programs. The owned-transport witness is the actual rank-four
move at event 8314, role 798, frame 267 to frame 1091. The oracle additionally
changes role 703's declared final frame back to the full frame; the literal
word's final-frame inventory rejects that inconsistent omitted contraction.
The unchanged same-caller source's strictly negative moment is a separate
meaningful comparison control at the same fixed saving.

Complete profiles, all nine named target changes with nineteen copies each,
the exact power intervals and control witnesses are retained in `RESULT.json`
and `ORACLE.json`. Their replay checks authenticate immutable inputs and
compare retained receipts with type-preserving canonical JSON.

## Remaining obligations and predecessor credit

The rational basis/public-boundary gate is the separate PR6355 result.
This invoice result does not re-prove that gate, native phases or all
operator columns, physical erasure, the emitted Laurent endpoint, physical
caller contact/ownership correctness, full ordinary or outer admission,
uniform compilation, precision tape, analytic recovery, a new selected
`kappa`, or a multiplication theorem. The five framework assumptions
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and
`analytic_recovery` remain.
The selected frontier is unchanged.

Ali Romman, with substantial OpenAI Codex assistance, supplied PR6353's
construction and author invoice, PR6349's input-lift source and PR6348's
fixed caller. PR6350 supplies the released composition comparison and is
not imported as a new contribution. Retain Cinna Davis's productive caller,
thin-query interface and factorization; DreamingOfClouds's PR6314 source
with Claude Opus 5.5 assistance; David Arias's word, Gareth Davidson's
composition and the full frozen `sources/NOTICE` lineage. The elementary
profile arithmetic and inherited rank tariff are not claimed as new
general mathematics. New source-bound recount, fixed-saving interval check,
controls and proof review are prepared for ToikY with substantial OpenAI
Codex assistance, including separately assigned checker, oracle and
mathematical-review agents. Same-session agent review is part of the
author process, not independent human or formal acceptance.
