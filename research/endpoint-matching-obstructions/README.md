# Complete exclusion of the fixed PR705 register-word corpus

This package excludes the **eight literal words left open by PR800**, for
every invertible complex choice of their four scalar 3 by 3 blocks. Together
with PR705's 64 exclusions and PR800's `evolved-27`, all **73 words in the
unchanged corpus** are now excluded. The general m=3, W=3, s=8 question remains
open. **No new kappa or positive eight-call primitive is claimed.**

The additional condition is simple: augmentation of the formal group-algebra
word is the product of its invertible scalar blocks. Its nonzero endpoint
entries must admit a perfect matching made from active permitted paths.
This closes five words using Boolean certificates alone. Laurent exclusions
close a sixth when combined with matching; two further words need 67 exact
polynomial identities. See [PROOF.md](PROOF.md) for the argument and scope.

## Reproduce

Python 3.11 or later, standard library only, offline:

```sh
python3 -I -B research/endpoint-matching-obstructions/verify.py
python3 -I -B research/endpoint-matching-obstructions/validate.py
```

Expected markers: `PASS_ENDPOINT_MATCHING_OBSTRUCTIONS` and
`PASS_ENDPOINT_MATCHING_PACKAGE`. Assertions must be enabled; `-O` is
explicitly rejected because the retained model uses them.

The verifier is standalone: no SAT solver, SciPy, sibling research package,
network access or generated file is required. It rebuilds the necessary
Boolean formula from exact dense paths, replays resolution and polynomial
identities, and compares a deterministic mathematical receipt. The supplied
certificate does not require reproducing its discovery search.

It checks all 2,187 full paths in the nine heterogeneous words, 490
frame-specific Laurent certificates, 67 polynomial identities and 5,342
resolution clauses. Three valid nine-call endpoints exercise the new
matching condition, including nontrivial scalar matrices and zero entries.
Controls reject corrupted identities, resolutions, gauge premises, missing
case coverage and missing terminal refutations. Package controls cover
relocation, gzip recompression, corrupted source/payload and optimized mode.

Discovery used bounded, single-worker native Python searches and a locally
checked clause-learning prototype. Boolean models and resource limits were
never accepted as constructions. The proof payload contains mathematical
evidence only, without performance measurements or local workspace data.
This is not a proof-assistant formalization or an independent human review.

## Sources and overlap

Jeremy Diviney's [PR800](https://github.com/CrocSwap/integer-mult-bounds/pull/800)
supplies the freely chosen Laurent path weights and exact `valuation.py`.
Its source and attribution are preserved in [ORIGINS.json](ORIGINS.json) and
[PR800-NOTICE.md](PR800-NOTICE.md). The unchanged word corpus and homogeneous
screen come from littleBro's PR705; `model.py` and `dense.py` originate in
littleBro's PR680. The model and open problem retain eumemic's PR288 and the
Swapnil Jain/upstream lineage. See [NOTICE.md](NOTICE.md).

PR836 excludes scalar-unitary mixing by a different potential argument;
PR720 concerns an abelian bit model. Neither is used to close these words.
The selected frontier and `upstream/` are unchanged. Validation scope and the
pinned selected record are documented in [VALIDATION.json](VALIDATION.json).
