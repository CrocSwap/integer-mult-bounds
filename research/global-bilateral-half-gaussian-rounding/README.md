# A global Gaussian lattice bijection with optimal bilateral radial slack 1/2

This package proves an all-input rounding theorem. For the normalized four-dimensional Hadamard map `U=H4/2`, an explicit bijection `F:Z^4 -> Z^4` has Euclidean error at most one and

\[
\left|\|F(x)\|_2-\|x\|_2\right|<\tfrac12
\quad\text{for every }x\in\mathbb Z^4.
\]

The supremum is exactly `1/2`. Every total integer-output map with error at most one has bilateral radial supremum at least `1/2`, without an injectivity, parity, periodicity, conserved-sum or equivariance premise. Therefore the construction attains the optimal **bilateral** constant among bijections. Its forward and inverse outward suprema both equal `1/2`.

The signed-permutation transfer gives the same result for the ideal Gaussian pair `C+` used in [CrocSwap/integer-mult-bounds#6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509). The actual negative provider is the explicit inverse. It is **not** obtained by conjugating the positive rounded map.

## What is new

The [complete proof](proof/PROOF.md) supplies an explicit global matching, its inverse, a uniform radial inequality, and an unrestricted lower-bound sequence. This answers the bilateral optimization problem and improves the constructive forward outward upper bound to `1/2`. It does not settle the forward-only optimum: the separately certified finite Hall lower bound `sqrt(78)-sqrt(73)` remains below `1/2`.

The distinction matters. [#6619](https://github.com/CrocSwap/integer-mult-bounds/pull/6619) proves a zero-slack norm obstruction and asks about the least positive outward slack. The [affine-period package](https://github.com/CubeJerry/integer-mult-bounds/tree/26ea0e01b09b12759a17f006c9066d9e5fcd84e0/research/affine-period-outward-slack) proves results for globally affine-periodic maps and the conserved-center family. Its lower bound `1` for that family does not exclude the new matching. The [finite Hall package](https://github.com/CubeJerry/integer-mult-bounds/tree/58a8facd7fbae9212774925349fbb617f114f040/research/sharp-finite-gaussian-outward-slack) supplies finite/global-necessary lower bounds; it does not construct this infinite bijection.

## Construction and computational contract

Write `J=diag(1,1,1,-1)`, `E=JU`, `R=UJU`. The even-sum integer coset uses `Ux` exactly. On the odd-sum coset, `R` maps to one color of the half-integer grid. A staggered coordinate pairing `M` toggles the coordinate of least partner-invariant score. This is an involution between the two colors. The odd branch is `E M R`; its inverse is `R M E^T`.

Two coordinates use magnitude pairs `(1/2,3/2), (5/2,7/2), ...`; the other two use a central pair `(-1/2,1/2)` and pairs `(3/2,5/2), ...`. For a selected noncentral lower magnitude `a`, the lower endpoint radius satisfies `r^2 >= (2a+1)^2+1`. The one-coordinate toggle changes squared radius by `2a+1`, proving the strict half-unit bound. All signs, ties and cosets are covered by the written proof.

`kernel.py` exports `hadamard_forward`, `hadamard_inverse`, `gaussian_forward` and `gaussian_inverse`. Each takes exactly four Python integers, excluding Booleans. Its arithmetic is extracted byte-for-byte from the independently written checker, with input-validation wrappers; `KERNEL-ORIGIN.json` records the boundary and hashes. It uses a fixed number of integer additions, exact divisions, residue tests, absolute values and comparisons. No search, floating-point square root or finite-ball lookup is used by the kernel.

This is an unbounded-integer arithmetic contract. It is not a fixed-word implementation or a fixed-tape tariff. On grid spacing `h`, homogeneity transfers error `1` and radial slack `1/2` to error `h` and slack `h/2`.

## Reproduction and independent checks

From the repository root, using Python 3.12 and its standard library:

```sh
python3 -I -B -W error research/global-bilateral-half-gaussian-rounding/verify.py
python3 -I -B -W error research/global-bilateral-half-gaussian-rounding/proof/check_identities.py
python3 -I -B -W error research/global-bilateral-half-gaussian-rounding/review/independent/mechanism_check.py
python3 -I -B -W error research/global-bilateral-half-gaussian-rounding/review/root/check_global_candidate.py
python3 -B scripts/research_package.py --package research/global-bilateral-half-gaussian-rounding --check-only
python3 -B scripts/research_package.py --package research/global-bilateral-half-gaussian-rounding
```

The first command prints `PASS_GLOBAL_HALF_KERNEL`. The proof-role checker prints `PASS_STAGGERED_BIJECTION_PROOF_IDENTITIES`. The remaining checks report their exact counts and scopes in JSON. All commands are read-only. `VERIFY.json` is an explicit opt-in to the repository replay hook, with bounded command arrays and no external runtime inputs. Source provenance is pinned at canonical main `e54523517d0f03e58352e647c403a5af3e525a57`.

The proof role derived the all-size argument separately from the implementation role. The implementation and root checkers use separate arithmetic implementations, but all roles knew the proposed mathematical formulas; this is not a blind or human review. Finite cases corroborate the proof and test failure modes. They do not establish universality by exhaustion. See [ROOT-REVIEW.md](ROOT-REVIEW.md), [the independent proof challenge](review/independent/PROOF-CHALLENGE.md) and their retained results.

## Limitations and kappa status

The public verifier records exact failures of complex-sum preservation, global `i` covariance, inverse-by-conjugation and fourth-power identity for this construction. These are limitations of this particular rounder, not impossibility theorems for other rounders. The Gaussian negative operation must use `gaussian_inverse`.

No tensor-stage commutation, arbitrary native-word admission, dirty-port wrapper, fixed-width overflow envelope, all-column precision propagation, recursive physical tariff or complete multiplication argument is supplied. All five selected framework assumptions remain. **No new kappa**: the pinned selected value remains `363005817/100000000000`, and the full bound remains conditional.

## Open next questions

The structured questions in [TASK.json](TASK.json) identify three remaining obligations: close the forward-only gap; meet one actual caller's additional algebraic identities; and implement a complete physical precision/storage budget. Each gives a first step, its relevance and its blocker. The present package completes the stated rounding subproblem, not those interfaces.

## Credit and assistance

Prepared for **@CubeJerry**, with substantial OpenAI ChatGPT/Codex assistance. The root supplied the staggered-matching construction; a separate proof role established and challenged the all-size proof and unrestricted lower bound; a separate implementation role checked the mechanism; the root independently checked the implementation and Gaussian interface. Exact role boundaries and source hashes are retained.

Credit Ali Romman for [#6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509), Nick Petalas for [#6619](https://github.com/CrocSwap/integer-mult-bounds/pull/6619), and ywz65 for [#2589](https://github.com/CrocSwap/integer-mult-bounds/pull/2589). Credit the earlier finite Hall and affine-period packages for the distinct lower-bound and scope questions. No priority claim is inferred from the bounded overlap search. Apache-2.0; retained notices remain effective.
