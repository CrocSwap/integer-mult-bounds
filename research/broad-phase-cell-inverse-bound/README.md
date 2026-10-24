# A rigorous broad Gaussian phase-cell inverse bound

For the actual broad phase-cell matrix

```text
K[k,i] = alpha^-1 exp(-pi/alpha² (i-k/rho-c)²),
rho = 1+theta,  beta_k = theta*k-rho*c in [-1/2,1/2],
gamma = pi/(alpha²*rho),  P_m = product_(r=1)^m (1-exp(-2gamma*r)),
A_N = alpha exp(pi/(4alpha²rho²)) / P_(N-1)^3,
```

[PROOF.md](PROOF.md) establishes, for every finite contiguous N-coordinate
cell and alpha,theta>0,

```text
|K^-1[i,j]| <= A_N exp(-gamma*theta*(i-j)²),
||K^-1||_2 <= A_N min(N, 1+sqrt(pi/(gamma*theta))).
```

The exact diagonal gauges are kept together with PR4193's finite Toeplitz
inverse entry estimate. Their coupled exponent gives Gaussian off-diagonal
decay. Bounding the two gauge norms separately loses this decay. This supplies
a rigorous theta^(-1/2) upper dependence for fixed alpha, while retaining an
explicit alpha-dependent constant. It does not prove PR4435's sharp leading
coefficient, an asymptotic equality, a new kappa or a physical multiplier.

The first source fixture is alpha=3, theta=1/400, N=400, starting at beta=-1/2.
The new certified norm bound is below **8080.184**; the earlier displayed
theta^-2 ceiling is above **713520770.18**. The latter number is a rigorous
lower bound on the old ceiling, not a lower bound on the actual inverse norm.

## Evidence and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/broad-phase-cell-inverse-bound
```

Both direct normal and optimized verifiers take about0.2 seconds and use
only the standard library. The official Git-free export can run
`python3.12 -O -B research/broad-phase-cell-inverse-bound/verify.py`.
The certificate checks2395 exact source-expression/gauge pairs, all160000
phase inequalities in the actual first cell,36 directed finite inverse-entry
enclosures, and12 independently eliminated rational Toeplitz matrices.
Controls include both closed phase endpoints, both index orders, translated
origins, an inadmissible phase, wrong inverse gauge sign, missing alpha
normalization and an omitted inverse pivot.

The source check executes the retained exponent AST with exact rational
scalars after factoring out pi. It does not execute the predecessor's
floating-point SVD program. The original matrix is not band-truncated.
The universal theorem is the written argument; finite cases are supporting
evidence. Decimal correctly-rounded exp/sqrt with explicit outward widening
is an arithmetic dependency, checked against rational controls.

## Attribution and limits

Credit Ryanson Jonathan's PR4408/PR4435 for the observed scaling and formal
turning-point derivation; Jose Manuel/jmbarrancoml's PR4193 for the finite
Toeplitz inverse entry theorem; Vlado Vojdanovski and the retained PR1673
Gaussian/q-LDU lineage for exact gauges and factorization; Cinna Davis's
later caller and all source notices. Classical finite q-binomial and Gaussian
integral identities remain credited predecessor mathematics.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Source
archives and selected frontier are unchanged. This is a scoped written
analytic theorem, not independent human or proof-kernel acceptance.
No fast inverse-application, coefficient-generation, rounded-caller, tape,
native or outer cost is discharged by this estimate.

## Open next questions

- Prove a matching lower estimate and recover the sharp formal leading constant.
- Bind an actual complete Gaussian caller and parameter family before changing
  its numerical guard; retain every preparation and physical cost.
