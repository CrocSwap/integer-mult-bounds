# Support-dependent projector prices collapse under free scalar mixing

This contribution is produced by Nick Petalas. Apache-2.0.

## Result and scope

**Scoped proof, with finite executable corroboration.** This closes the literal
free-mixing version of Open next question 2 in ywz65's
[PR #2544](https://github.com/CrocSwap/integer-mult-bounds/pull/2544).
Allow the price of each paid label to depend arbitrarily on its displayed
rank-one projector. If every scalar change of basis is free between calls,
only the cheapest price for each label affects the exact optimum.

For `R >= t >= 0` binary roles, write `c_a(N), c_b(N) >= 0` for these prices,
where N runs over every rank-one idempotent of `M_R(F2)`. For `R >= 1`, set

```text
A = min_N c_a(N),   B = min_N c_b(N).
minimum price of t coordinate SWAP targets = t (A + B + min(A,B)).
```

Every spectator starts arbitrarily and is restored individually. The minimum
for `R=t=0` is zero, without defining an empty projector minimum. Prices may
depend on R; take the two minima separately at that R. The fixed-price SWAP
theorem and its lower bound are inherited from #2544. The new step is the
exact compilation that eliminates dependence on projector support.

This formal price result gives no native implementation, recursive invoice,
supplier admission, new kappa or complete multiplication theorem. Free changes
of basis are a hypothesis, not an assertion about physical costs.

## Model

Use precisely #2544's address group `G=GL_2(F2)` and paid labels

```text
a = [[1,1],[0,1]],  b = [[1,0],[1,1]],  z = aba = bab.
D_N(g) = I_R + ([g]+[e]) N  in M_R(F2[G]).
```

The endpoint is `diag([z] I_t, I_(R-t))`, coefficientwise in the full group
algebra. Scalar `GL_R(F2)` matrices may be interleaved for free and must be
included in that endpoint equality. The price `c_g(N)` is attached to the
projector displayed at the paid instruction. It is independent of the data,
earlier instructions, current gauge and eventual output. There are no free
address maps, erasures, clean allocations or state-dependent rebates.

## Proof of price collapse

The following compilation lemma applies more generally. Let H be any group of
free invertible scalar maps acting by conjugation on an allowed projector set
that is closed under H, with every orbit finite. For each projector orbit O
and paid label g, replace its prices by `m_g(O)=min_{P in O} c_g(P)`.
For every exact endpoint, the infimum over finite words is unchanged.

For one direction, keep every word and reduce each of its paid prices to its
orbit minimum. Its new price cannot increase. For the reverse direction, take
any word at orbit-minimum prices. For each occurrence of `D_N(g)`, choose a
cheapest P in N's orbit and C in H with `N=C P C^(-1)`. Scalar entries commute
with address coefficients, so full coefficient equality gives

```text
D_N(g) = C D_P(g) C^(-1).
```

Replace that occurrence by the three displayed factors. The two scalar maps
are free and the paid factor has price exactly `m_g(O)`. This preserves each
factor as a complete operator. Thus it preserves the entire endpoint, all dirty
inputs and every spectator, at exactly the orbit-minimum price. The two
inequalities give equality of infima. If one problem attains its infimum, the
same construction proves attainment for the other. This argument does not
assume that projectors in different calls commute, nor that gauges can be
discarded after normalization.

For full `H=GL_R(F2)`, all rank-one idempotents lie in one orbit. This is standard
linear algebra: write `P=u v^T` with `v^T u=1`, and take a basis whose first
vector is u and remaining vectors form a basis of `ker(v^T)`. In that basis P
is `E_11`. Given bases `B_P,B_N` of this form, `C=B_N B_P^(-1)` maps P to N.
The verifier constructs these bases and checks the full formal replacement.

Consequently the exact target cost equals the fixed-label-price optimum at
A and B. The cited #2544 theorem gives `t(A+B+min(A,B))`. Its coordinate `aba`
or `bab` attaining words can be compiled one factor at a time through cheapest
projectors. This proves the displayed all-role formula. No predecessor census
or proof is independently reverified here.

## Why the free-mixing hypothesis matters

Consider two roles and `P=[[1,0],[1,0]]`, with both labels free only at P and
priced one at every other projector. Let `N=E_11`. With free mixing, the target
`D_N(z)` has price zero by the compiler. If no scalar mixing is allowed, every
zero-price word belongs to the six-element subgroup `{D_P(g):g in G}`. Indeed
`D_P(g)D_P(h)=D_P(gh)` because `P^2=P`. This subgroup omits `D_N(z)` since its
nonidentity group coefficient is P rather than N. The verifier enumerates all
six states and checks closure and the omitted target. This does not claim the
exact positive optimum in the restricted-gauge model.

Support tariffs can therefore matter with charged or restricted scalar maps.
Searching additional projector supports with unrestricted free scalar mixing
cannot change the optimum beyond the two minima above.

## Reproduction and evidence

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/projector-price-orbit-collapse/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/projector-price-orbit-collapse
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/projector-price-orbit-collapse --check-source-history
```

The direct script checks every ordered projector pair at R=1,2,3 for each paid
label, and additional constructed pairs at R=4 through 8. It constructs full
group-algebra attaining endpoints for every t=0 through R at R=1,2,3 under four
price tables, including zero and nonconstant tariffs. It also checks the
restricted-gauge example and detects a missing inverse gauge. The printed
receipt is generated from those checks and binds its code, proof and source
manifest by SHA256. Default replay writes no files. The universal conclusion
rests on the written compilation proof and the cited fixed-price theorem,
rather than extrapolation from the finite checks.

No Lean, Docker, predecessor replay or selected cold replay is required or run.
Independent human and formal proof-kernel review are unclaimed.

## Sources and overlap

The base is canonical main `624de9dc66858af0945e5f8a0942488d62280d43`, priority
revision 7. [SOURCES.json](SOURCES.json) pins the inherited #2544 theorem at its
retained main bytes. Credit ywz65 for the asymmetric SWAP tariff and explicit
support-price question; Ross Richardson #1989/#2415 for its inherited total-call
cut theorem; Aaron Wang's asymmetric-price handoff and their credited
register-model predecessors. Projector conjugacy itself is classical.

The original `bit-new-register-model` card changes to a formal pricing side
question. This closes a stated loophole in the nonabelian model; it does not
provide a changed productive mechanism. Before claiming, live title/body and
Discussion searches, distinctive main README searches and merged PR searches
found no same-question result within their coverage. The overlap cache held
348 open PRs and 3,782 Discussion records. Sparse local notes, arbitrary code
diffs and unpublished work were not fully searched. The local question lock
was reserved before the public claim. These searches are not a novelty proof.
The pre-submission refresh at 21:17 UTC covered 352 open PRs and 3,793 Discussion
records, with complete remote pagination. Canonical main and the scoped source
remained unchanged. The refreshed terms matched this package, its own claim
and the explicit #2544 predecessor; broader group-algebra work is related
rather than checked.

## Engineering bounds

The verifier uses fixed dimensions at most eight, finite group size six and
bounded loops. The largest exhaustive projector-pair domain is 28 squared.
Functions fit within 60 lines, have direct call paths and use explicit checks
that remain active under optimized Python. It authenticates the sole inherited
input before computing. Managed Python allocation is a deviation from Power
of Ten rule 3: tuples, integer objects and convolution temporaries allocate at
runtime. Their dimensions and enumeration bounds are fixed above; no input can
expand them. Follow-up for a larger census would require an explicit capacity
limit before extending these constants. No compiler or static type checker is
required by this standard-library repository hook; direct development-mode
replay with warnings as errors provides its interpreted-code diagnostic check.

## Open next questions

1. Charge scalar mixing by an explicit native ADD or routing price. Does a
   nonconstant support tariff then beat the best coordinate protocol after both
   gauges are charged? First solve the two-role P/N example above with its
   actual gauge costs. A physical gauge price and complete endpoint contract
   are missing; the free-mixing theorem supplies neither.
2. Restrict free maps to a named subgroup H, such as coordinate permutations.
   Which projector orbits determine the exact SWAP cost? First classify the
   two-role orbits and solve one nonconstant orbit-price instance. The lemma
   reduces each orbit internally but leaves interactions between orbits open.
