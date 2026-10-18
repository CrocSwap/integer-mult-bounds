# Constant-coefficient dirty stride precision

This package removes the length-dependent precision admission from
PR985's dirty arbitrary-stride solver and replaces its conservative
kernel precision by a cubic sufficient bound. The rounded word and all
two-tape movement remain unchanged. No new kappa is claimed.

For a certified prime-power kernel of radix `r`, initial array norm at
most `2^m`, target error `2^-p`, and incoming grid precision `w_input`,
the sufficient fractional precision is

    W <= max(p,w_input) + m + 18r^3.

A signed integer reserve of at most `m+15r^3` bits per component covers
both forward and inverse intermediate values. Immutable coefficient and
gauge descriptor lengths are additional word-size inputs. The kernel
keeps `ceil(log2(r-1))` arbitrary dirty arrays. Every source and borrowed
array restores exactly. Negative calls execute the full inverse word.

At radix 64, target 128 bits, and magnitude bound `2^20`, the explicit
fractional budget is `1,420,902` bits. PR985's full-word bound with the
same margin needs `517,236,859` bits before a larger depth admission.
Both have `4,000` leaf calls and six borrowed arrays. These are sufficient
precision bounds, not runtime measurements or minimum widths.

## Reproduce

Use standard-library Python 3.11 or later:

```sh
python3 -I -O -B research/dirty-stride-precision/verify.py
python3 -I -O -B research/dirty-stride-precision/test_package.py
```

The main check covers exact exponent budgets, coefficient extinction,
return-time bounds, the dirty zero-subtree identity and its internal
magnitudes, signed leaf errors, and actual kernel executions with odd
lowest working bits. The kernel checks use a dense polynomial oracle,
exact prepared-coefficient bounds, complete tape counters, integer
guards, and both orders of inverse cancellation. `EXPECTED.json` is
the exact mathematical receipt. `VALIDATION.json` records the local
checks and omitted checks; hosted CI is separate.

The `L=5741`, `w=2378`, `beta=1/2`, `W=12` case executes the full word
beyond the old admission. Its structural depth is 10 and its effective
error depth is 5. No runtime recursion is skipped.

## Files and mathematical boundary

- `PROOF.md` gives the all-length proof, the common-operator transfer,
  inverse-preimage guards, explicit cubic inequalities, and complete cost.
- `dirty_stride.py` derives from PR985. It changes admission and caches
  the two validation reads so each literal access has its meter charge.
- `budget.py` supplies exact finite and uniform precision budgets.
- `verify.py` checks the mathematical and execution contracts.
- `vendor/pr985/` retains the original complete package unchanged.
  The other vendor folders retain the relevant credited proofs.
- `SOURCES.json` pins every retained dependency. `NOTICE.md` gives credit
  and discloses substantial OpenAI Codex assistance.

The actual increment can depend on its target and scratch data. The proof
bounds each negative leaf at its positive preimage and does not assume
target-independent rounded increments. It proves the zero-subtree
identity for the dirty word itself; PR977's clean-scratch theorem is not
imported by assertion.

The supplied prime-power preparation, analytic inverse, and fast scalar
arithmetic hypotheses remain. The rational reference does not implement
an all-size factorizer or a fast bit compiler. Variable site phases,
common-label/Clifford realization, full transform composition, physical
supplier hosting, and the multiplication reduction remain open. The
selected certificate and `upstream/` are unchanged.
