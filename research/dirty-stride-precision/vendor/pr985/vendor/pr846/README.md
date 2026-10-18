# Cyclic inverse stride bridge

This package continues the open obligation recorded for #621 in
[the K492 review](../../docs/research/community-k492-review.md). That
obligation is to pay for efficient preparation, rounded execution,
restoration and tape before using #621's length-independent inverse bound.

#628 pays for preparation and neighbouring-stride execution. #764 sharpens
the scan rounding. Both PRs are still open and are pinned in
[SOURCE.json](SOURCE.json). For any stride other than ±1, #628's route
depends on two merge sorts costing `O(L(B+log L)log L)`. Those sorts bring
back a `log L` factor that the inverse bound was supposed to remove.

[PROOF.md](PROOF.md) replaces the sorts with a Euclidean chain/closure
recursion. A FIFO built from two stacks gives every pass a lag-`w`
predecessor in natural order. Theorem 1 gives one stable factor at any
stride with:

* at most `40L` sequential record moves;
* `O(L)` rounded operations;
* an error bound `min(K,1/beta)(u/beta)(5+4B/beta)+u` that holds for every
  `L`.

The proof reuses #764's shared-suffix identity. It also shows that margins
do not shrink across recursion levels. Theorem 2 composes the solver with
#628's certified factorization. The kernel precision is
`p+(n+2)g+O(log r)=p+O(r^4)`, with no `L` term. One admission condition,
`p >= log2(log2 L+2)`, depends on `L`. The table in PROOF.md charges every
listed cost.

**Verdict:** consider one inverse of `P(tau Z_L^w)` on fixed sequential
tapes, with all four listed costs paid. Its cost per entry still does not
depend on `L`, so #621's gain survives. Three things are not claimed:

* a borrowed-array (dirty) form of the stride solver;
* composition across the complete transform;
* any change to integer kappa, complex b, or BIT c.

## Replay

Python 3.11 or later with the standard library only. The replay takes
about 100 seconds:

```sh
python3 -B -I -O research/cyclic-inverse-stride-bridge/verify.py --check
```

Expected: `PASS_CYCLIC_INVERSE_STRIDE_BRIDGE generic=2052 kernel_cases=300
controls=4 max_records_per_entry=29.671875`.

The replay covers the following checks:

* **Generic cases (2052).** `L=1..18`, every stride in `[-L,L)`,
  `beta in {1/4,1/8,1/32}` and two grids. Each case is compared exactly
  with an independent per-cycle geometric-closure oracle against Theorem 1.
  The margin `|bhat|<=1-beta` is checked at every recursion level.
* **Traffic.** Count-only runs reach `L=131072`. Strides include `0`, `±1`,
  `L/2`, `L/2+1`, golden-ratio strides and the prime `L=99991`. Every run is
  checked against `40L` record moves. The maximum observed is
  29.68 moves per entry, compared with #628's
  sort route of `4L ceil(log2 L)`.
* **Kernel cases (300).** These use all ten #628 certified kernels, radix 3
  through 16. Gauges are `1` and `3/5+4i/5`. Lengths are 1, 2, 3, 5 and 8,
  with all strides for `L<=5`. Each case evaluates Theorem 2's exact budget
  against the target together with #628's perturbation bound. Each also
  checks the expanded polynomial residual. 81 cases are compared with an
  independent dense Gauss–Jordan solve.
* **Controls (4).**
  * a rotated closure reseed;
  * a precision below the admission condition;
  * a unit coefficient;
  * a wrong inner-shift direction.

  The replay rejects all four.

The vendored #628 files must match the hashes in SOURCE.json byte for byte.
The verifier refuses drift. `--write` regenerates `EXPECTED.json`.

Finite cases support the reference implementation. The written proof
carries the all-`L` claims. The Python lists model sequential tapes and
count record moves; they are not a literal Turing machine.
