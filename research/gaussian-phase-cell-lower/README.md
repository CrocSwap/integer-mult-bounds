# Broad Gaussian edge conditioning has sharp theta order

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped analytic proof with exact finite corroboration. No new kappa.

For the broad Gaussian matrix

```text
K[k,i] = alpha^-1 exp(-pi/alpha^2 (i-k/rho-c)^2),
rho=1+theta, c=1/(2rho), 0<=k,i<N, theta(N-1)<=1,
```

the new result is

```text
||K^-1||_2 >= alpha m exp(-pi theta (2m-1)^2/(alpha^2 rho))
for every integer m>=1 with 2m<=N.
```

Consequently, for 0<theta<=1/16 and
N>=2 floor(1/(2 sqrt(theta))),

```text
||K^-1||_2 >= (alpha/4) exp(-pi/alpha^2) theta^(-1/2).
```

Together with the cited upper theorem of JoyboyBrian's
[PR5103](https://github.com/CrocSwap/integer-mult-bounds/pull/5103), this proves
the sharp order Theta_alpha(theta^(-1/2)) for these boundary sections at
fixed alpha. This answers its open matching-lower-estimate question. The
sharp leading coefficient in Ryanson Jonathan's
[PR4435](https://github.com/CrocSwap/integer-mult-bounds/pull/4435) remains open.

[PROOF.md](PROOF.md) gives the universal argument. A checkerboard sign change
makes every inverse entry positive. One positive term of the cited finite
q-LDU inverse survives the exact diagonal gauges. An m by m rectangle at
the cell edge then gives an explicit alternating unit test vector and the
norm lower bound. No floating inverse, SVD or asymptotic boundary condition
is used in this proof.

## Evidence and reproduction

The verifier independently eliminates 36 rational Gaussian matrices of sizes
two through five, checks 416 inverse entries and 50 rectangle/test-vector
estimates. These fixtures use the larger algebraic family with independent
positive Gaussian exponent and normalization. They do not purport to sample
the transcendental source kernel exactly. Another 520 exact rational
exponent checks include the source fixture theta=1/400. There are 1,009
floor-inequality checks and nine boundary/sign/overstatement controls.

At the actual alpha=3, theta=1/400, N=400 fixture, m=10 gives a new
certified lower estimate exceeding 109/5. The rational polynomial
certificate is 8753084362189/400075200000 > 109/5. This is a lower bound
on the inverse norm, not its exact value or the sharp asymptotic constant.
The source fixture is used for this new estimate only; no predecessor
operator replay or numerical table is repeated as a contribution.

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-phase-cell-lower/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/gaussian-phase-cell-lower/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-phase-cell-lower
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-phase-cell-lower --check-source-history
```

Any CPython 3.12 installation can replace the displayed interpreter path.
The direct checks report PASS_GAUSSIAN_PHASE_CELL_LOWER; the registered
runner reports PASS_REGISTERED_RESEARCH_PACKAGE. Default execution writes
nothing. Optional --receipt NEW_EXTERNAL_PATH exclusively creates a generated
JSON receipt binding all six package files by SHA256. No receipt is handwritten.

## Sources and limits

The scientific base is canonical main
a5df48c55ea806d7952b65acc9c76d878ff09b13, priority revision 7.
[SOURCES.json](SOURCES.json) pins predecessor texts as provenance. No
predecessor code is imported and no external scientific input is read at replay.
The originating uniform-transfer-audit card is changed to this original
conditioning side result. The purpose is to settle the necessity of the edge
conditioning loss before refining its sharp constant or pricing a caller.

Credit JoyboyBrian #5103 for the rigorous upper theorem and the open lower
question; Ryanson Jonathan #4408/#4435 for the scaling observation and formal
leading-coefficient prediction; Jose Manuel/jmbarrancoml #4193 for the finite
Toeplitz inverse estimate; Vlado Vojdanovski and the retained #1673 Gaussian
and q-LDU lineage; and Cinna Davis's later Gaussian caller. Classical finite
q-binomial identities retain their earlier mathematical credit. Their results,
credit lines and frozen evidence are unchanged. The positive lower rectangle
and the resulting matching-order theorem are the new contribution.

This theorem fixes beta_0=-1/2 and requires a section containing a sufficiently
long boundary window. It gives no theta-dependent lower bound for arbitrary
tiny sections or sections separated from both edges. The alpha-dependent
constant is deliberately coarse. The universal claim rests on the written
proof, with finite exact checks as corroboration. Independent human and
formal proof-kernel review are unclaimed.

Coefficient preparation, rounded inverse application, all circuit-prefix
norms, physical source access, restoration, storage/tape, native implementation,
compiler and outer integer recovery remain unpriced. No Lean, Docker, selected
operator replay or complete multiplication theorem is claimed.

Live open PRs, recent account PRs, handoffs, active discussions, distinctive
main-tree and merged searches were checked before claiming and submission.
The initial cache covers 305 open PRs and 4,166 Discussion records. Sparse
local-note coverage is incomplete; no exhaustive novelty claim follows.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144272)
records the scope.

## Open next questions

- Recover #4435's sharp leading coefficient, with a uniform boundary remainder
  and a growing-alpha regime. Start by retaining more positive inverse terms
  and optimizing boundary test vectors; a comparably sharp upper estimate is
  still needed. The present lower constant does not establish that coefficient.
- Bind a complete rounded Gaussian caller before changing numerical guards.
  Start with one pinned caller and retain its coefficient, prefix, restoration,
  movement and storage costs. Endpoint conditioning alone supplies no physical
  invoice. Structured questions are in [TASK.json](TASK.json).
