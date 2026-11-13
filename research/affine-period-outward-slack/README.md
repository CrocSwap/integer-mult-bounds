# Exact outward slack from affine periods and sum fibers

**Result.** For a rational orthogonal map with a full-rank affine period, the
supremum of the outward norm increment equals the largest period-coset error.
Applying the same ray argument within each fixed-sum fiber proves, for every
legal bounded center rule in the #6509 pair family, that the global outward
slack is exactly `sup_s |c(s)|`. The least value among these center rules is
one, attained by #6509's source rule.

This is an exact norm-slack classification for a scoped family. It gives no
physical tariff, selected `kappa`, or unrestricted optimality claim. The
#6509 sign-based center does not have a full-rank global affine period; its
proof uses integral ray shifts inside fixed-sum fibers.

## Files and reproduction

- [PROOF.md](PROOF.md) gives the period theorem, the complete legal-center
  family proof, the ray inequalities, and the source-bound corollaries.
- [SOURCES.json](SOURCES.json) pins the canonical base, retained kernel, and
  predecessor proofs by commit, Git blob, and SHA-256.
- [kernel.py](kernel.py) is a byte-identical copy of #6509's tiny kernel.
- [SOURCE-NOTICE.md](SOURCE-NOTICE.md) preserves its upstream notice;
  [NOTICE.md](NOTICE.md) records this package's added work and credit.
- [VERIFY.json](VERIFY.json) records the exact replay command.

Run from this directory with Python 3.10+ and the standard library:

```sh
python3 -B reproduce.py
```

The default run prints the full receipt to stdout and leaves `RESULT.json`
untouched; the explicit checks also pass under `python3 -O -B reproduce.py`.
Use `python3 -B reproduce.py --write-result` to refresh the receipt file.

The verifier authenticates the copied kernel bytes, runs the exact `c(1)=1`
ray and literal inverse on integer-grid witnesses, checks the dyadic
unit-ball crossing with `Fraction`, and requires both an illegal-center
mutation and a specific unsupported equal-coordinate global-period candidate
to fail. The finite run
corroborates the retained kernel on those witnesses; it does not prove the
all-center theorem, which follows from the written algebra.

## Predecessors and limits

Ali Romman's #6509 supplies the legal-center condition, exact inverse, and the
unchanged pair kernel. #6534 and #6536 do not state the radial outward-slack
equality proved here. Ali Romman's #6534 two-axis map already has sharp
uniform error `sqrt(2)h`; the period theorem converts that inherited error
result into exact outward slack `sqrt(2)h`. The #6536 matched three-axis map
has sharp uniform error `2h`, giving exact outward slack `2h`. These are
corollaries of pinned source claims; their tables and matchings are not
reverified here.

Nick Petalas's #6438 five-seed rotation has an affine period, a per-seed error
bound `sqrt(4/5)`, and an attained maximum across the construction, so its
worst outward slack across the seeds is exactly `sqrt(4/5)`. CubeJerry's #6758 native map similarly has inherited sharp
forward and inverse error `sqrt(8)` and a full-rank period, so both outward
slacks are `sqrt(8)`. This package does not recheck either certificate.

The prior finite-set argument #2589, cited by #6619, concerns exact norm
preservation on finite spheres; it is not the unbounded lattice ray proof
used here. #6619's unrestricted outward-slack optimization remains open in
this package.

## Open next questions

- **Question:** Is there a sharp outward-slack bound for injective
  integer-output maps without an affine-period or fixed-fiber decomposition?
  **Why it matters:** Such a result would connect this exact periodic/fiber
  classification to the unrestricted problem left open by #6619.
  **First step:** Prove a bound or construct a counterexample while checking
  injectivity over complete integer spheres, not only a finite sample.
  **Blocked by:** No period quotient or other finite classification is known
  here for the unrestricted map class.

## Assistance

The new proof and reproduction package were prepared with substantial OpenAI
Codex assistance. No code from #6534, #6536, #6438, or #6758 is copied.
