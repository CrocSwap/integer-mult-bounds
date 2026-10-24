# Join and enclosure argument

## 1. Charging model (taken from #4440 PROOF.md sections 1-2, not re-derived)

Complex controller with p = 16 pairs and prefix a = 7, so there are 2p+1 = 33 local stages.
The thick stages are S = {0, 2p} ∪ {1, 3, ..., 2p-1}, which gives |S| = 18. The model has
112 ports and fresh block rank d = 8. Events are charged as follows:

- `LOCAL(stage, pair, backward)`: one full native call. It charges one fresh copy of the local
  helper targets and one copy of the local paid unit for that orientation.
- `QUERY_SHEAR(stage, ...)`: 112 paid rank-one jobs, one per port. No productive credit.
- `IDLE(pair, stages)`: both lines of the pair on every port. This is 2·112 paid jobs of rank
  d·|stages|.
- `ADD`, `SIGNED_SWAP`: scalar bridges with no rank charge. They sit under the nonrecursive allowance
  of #4470, which is not checked here.
- Diagonal output `(c, e_0, ..., e_32)`: c is ±1, the central Gaussian (rank 1). The term gives
  112 productive targets of rank 1 + d·|{s : e_s = 1}|.

The verifier checks the structural conditions that make this model applicable to the
committed word:

- one full call per thick stage;
- one query per thin stage;
- idle stages are distinct and thick;
- outputs have 0/1 exponents, support inside S, and c = ±1.

The verifier does not prove that the word realizes the advertised operator. That is the
Laurent factorization of `research/pr4470-controller-replay`, and both packages pin the same
`CONTROLLER.json` bytes.

## 2. Join and cross-bindings

T is the sum of the main targets plus 18 helper copies. P is the sum of:

- the idle charges;
- 112·15 rank-one queries;
- the forward unit, once per forward call;
- the backward unit, once per backward call.

The units are read from #4504's committed `RESULT.json`, `profiles.new`. Both orientations are
required to carry the same paid unit with eight rank-8 center jobs.

The #4440 closed form gives a second derivation that does not use the event word:

- 2·112 targets of rank 1 + d(p+2);
- for j in 1..a and in 1..p-1-a: 2·112 targets of rank 1 + d(j+1) and 2·112 paid jobs of rank d(j+1);
- (p+2) units;
- 112(p-1) queries.

The event-word join and the closed form agree exactly. Their common value equals:

- `RESULT.json` targets/paid;
- `NATIVE.json.gz` helpers/paid, times the call counts;
- `CONTROLLER.json`'s embedded invoice after replacing 18 THREE-base units by 18 new units;
- #4478's literals `T` and `P`.

## 3. Enclosure

For integer k ≥ 1 and rational t ≥ 0, k^t = exp(t ln k). Decimal `ln` and `exp` are documented
as correctly rounded at the working precision (60 digits). Each returned value v is widened to
[v - |v|·10⁻²⁰, v + |v|·10⁻²⁰]. Rationals are converted to [floor, ceiling] decimal quotients.
Products of nonnegative intervals, sums and quotients are rounded outward with `ROUND_FLOOR` /
`ROUND_CEILING` contexts. exp is increasing, so exp evaluated at the interval endpoints encloses
the image.

Then M_H(t) = Σ n_k k^t is enclosed for each histogram H. The surplus lower bound is
M_T,lo − M_P,hi, and the upper bound is M_T,hi − M_P,lo. The tails are enclosed from above by
using upper bounds in numerators and lower bounds in denominators:

- α = M_P(t)/M_T(t);
- γ = M_P(t+1/5)/(20^{1/5} M_T(t));
- δ = 21·|T|/(20^{C} M_T(t)), where t = 1 − C and C = 0.003020155.

The exact rational facts (97/100)^128 < 1/16 and 1/(1 + 1024·10⁻⁹) + 4/2³² < 1 are checked in
`Fraction`.

## 4. Sharpness

The rank-one moment is 1^t = 1 for every t. The certified upper bounds of the raw surplus at
κ and at the tested saving are below 1. Adding any single rank-one paid job therefore makes
both surpluses negative, and the verifier asserts this bound.
