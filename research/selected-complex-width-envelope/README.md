# A two-sided complex row-depth coefficient for the #4470 nested compiler

**Scoped written bound with author-checked exact arithmetic; no new κ.**
The selected conditional exponent remains `60403/20000000`. This answers the
open coefficient-bracket question of James Reed's [PR4972](https://github.com/CrocSwap/integer-mult-bounds/pull/4972).
It does not compute an astronomical word or change the compiler.

Put `H = 64215200000000`, `N = 2^H`, and

```
K = ceil(log2 B_N) / H.
```

For the actual #4470 product/completion/splitting rule and **#4436's nested
divisible-width realization**, the written argument below proves

```
(2943/1000) N < K < (3639/1000) N.
```

The endpoint ratio is below `5/4`. The older lower bound used only
`S_n >= 2`, while the upper bound counted paid rank mass as paid calls and
used `G(N) <= H`. Counting actual root sources, charging every split and
completion, and using the productive floor give the sharper bounds.
These are bounds on the same permitted realization, not a search for
smaller batching widths. #4470 does not specify a unique minimal `B_N`.

In the **same conservative outer-accounting formula** as #4972, retaining
its `c_row = 1`, support-width tariff `Cw = 232960`, BIT share, nesting and
sum allowances, `K < 4N` gives:

| Quantity | PR4972 | This bound |
| --- | ---: | ---: |
| Complex-share `log2` upper bound | 64,215,200,000,022 | 64,215,200,000,008 |
| `log2 C` upper bound | 64,215,200,000,024 | 64,215,200,000,010 |
| Displayed sufficient-fit `log2 p` | 64,473,100,659,050 | 64,473,100,659,036 |

The factor-`5/4` bracket is for **K**, not for an optimal `C`. The outer
figures retain the predecessor's deliberately loose tariffs and do not
admit them independently. The numerical threshold comparison is a
consequence of the new source-count bound, not a second cutoff search.

## Source-bound rule and realization

At base `bee95ce88f9f19802f0613f92838895cd0e14a1f`,
`joint-helper-lattice/RESULT.json` and `PROOF.md` §§4–6 give:

```
raw productive count W0 = 10928; raw paid count Q0 = 64620;
raw paid rank mass R0 = 239134; raw ambient rank m0 = 145;
v = 1024; productive floor b = 21; paid cutoff c = 20.
```

The product has `W = W0^v` productive fields. Complete each target of rank
below `L = b^v` to rank L on disjoint coordinates of that same field, then
split every paid job at `J = c^v`. Its ambient rank is `M = m0^v` and its
minimum productive rank is L. Completion and splitting retain all paid
charges and do not add productive fields. Native correctness, whole-job
adapters and physical tariffs remain the source hypotheses.

Exactly 7792 raw productive fields have rank at most 21. The ordered
product choices using only those fields give at least

```
A = 7792^1024
```

distinct final targets of rank **exactly L**: their original product rank
is at most L, and paid completion raises it to L when necessary. This is
a lower bound on one target multiplicity, not credit for all W targets.

Use the default-height flow of `direct-mixed-flow/README.md` §§2–3:

```
G(n) = max {g >= 0 : M L^g <= n},    n >= M;
B_n = 1 below M;
a_n = B_(n-1),  B_n = a_n S_n;
B_N = product_(n=M..N) S_n.
```

`S_n` counts all distinct top sources at rank n. The nested widths make
every complement/exit batch integral. #4507's least chronological widths
and #4483's changed-height compiler are different choices and are not used.

## Proof of the two bounds

**1. Fully charged paid-count upper bound.** Let Q be the final number of
paid calls. For any positive rank R, splitting at J produces
`ceil(R/J) <= 1 + R/J` calls. Original product calls have count `Q0^v` and
total rank mass `R0^v`. Every completion has rank below L, and there are
at most W completions. Hence the integer bound

```
Q <= Qbar = Q0^v + ceil(R0^v/J) + W ceil(L/J)
```

charges original calls, every original rounding surcharge and every
completion. A completion of rank zero contributes no actual call; the
bound may still overcount it. Write `C0 = W + Qbar + 1`.

**2. A root-source injection.** In the source flow, the root multi-index
having G copies of the minimum target type is eligible because
`M L^G <= n`. It has at least `A^G` unit instances. Each has W distinct
productive target slots; all these root slots are top sources, at rank
at most n. Therefore

```
S_n >= W A^G(n).
```

These slots are distinct source arrays in the integer flow, not copied
values or extra productive credit. The source's full-layer count also gives

```
S_n <= W (W+Q+1)^(G(n)+1) <= W C0^(G(n)+1).
```

**3. Height bounds without logarithmic approximations.** For a positive
integer x, `bit_length(x)-1 <= log2(x) < bit_length(x)`. Thus

```
hlo = floor((H - bit_length(M)) / bit_length(L))
    = 14276389504;
hhi = floor((H - (bit_length(M)-1)) / (bit_length(L)-1))
    = 14279564152;
hlo <= G(N) <= hhi.
```

The lower estimate certifies `M L^hlo <= N`. For every integer
`n >= M L^(hlo-1)`, `G(n) >= hlo-1`. This interval contains at least
`N(1-1/L)` indices because `M L^(hlo-1) <= N/L`. Since `hlo >= 1`,
the interval lies in the nonbase range. All other factors `S_n` are positive
integers, so their logarithms cannot decrease the lower bound.

Define the following small, exactly computable integers:

```
Xlo = (bit_length(W)-1) + (hlo-1)(bit_length(A)-1)
    = 188990844254451;
Xhi = bit_length(W) + (hhi+1)bit_length(C0)
    = 233670787813430.
```

Summing the source logarithms proves

```
N(1-1/L) Xlo <= log2 B_N <= N Xhi.
```

The upper endpoint `N Xhi` is an integer, so it also bounds
`ceil(log2 B_N)`. Exact integer comparisons now give

```
1000 (L-1) Xlo > 2943 L H;
1000 Xhi < 3639 H;
4 Xhi L < 5 (L-1) Xlo.
```

Divide by NH to obtain the stated coefficient bracket and its ratio.
No integer of size N, no full target inventory and no uniform word is
constructed in these checks. All integer powers computed here have only
tens of thousands of bits.

**4. Conditional outer substitution.** `batched-complex-rows.tex` and
#4972 identify the row-depth coefficient as K under their stated contract.
The previous formula multiplies K by an upward width factor `2^5` and
a nesting factor 2. Since `Xhi < 4H`, `K < 4N`, so its complex share is
below `2^(H+8)`. The unchanged BIT bound is `2^51973930319885`; the
unchanged old-stock allowance is `2^74`. The predecessor's factor-four
sum allowance gives `log2 C <= H+10`.

For its displayed sufficient condition
`(log2 C+10+3 ulog2(Lp))/(1-1/250) <= (69999991/70000000) Lp`,
the verifier partitions positive integers Lp by bit length and solves
each resulting rational linear inequality. This gives the least integer
for that particular upward-rounded formula without assuming its stepwise
predicate is monotone. It is not an exact physical input threshold.

## Reproduction and verification scope

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -I -W error -B research/selected-complex-width-envelope/verify.py
python3.12 -I -O -W error -B research/selected-complex-width-envelope/verify.py
python3.12 -B scripts/research_package.py --package research/selected-complex-width-envelope
```

The read-only verifier authenticates every live input by SHA-256 and Git
blob identity before and after replay. It loads only the authenticated
#4436 flow bytes, compares merged and literal chronological flows on small
instances, checks source/nested-width bounds and twelve exact product/
completion/splitting cases, and requires five mathematical rejection
controls. `RESULT.json` binds the deterministic arithmetic and finite scope.
Direct commands support a Git-free export; metadata/provenance checks
separately require Git. `--emit` prints the receipt to stdout.

Author validation used Linux x86_64 and Python 3.12.15. Both registered
normal/optimized modes pass: 366 small source flows, 12 literal comparisons,
332 nested lower checks, 16 height checks, 12 product/pad/split cases and
six reduced-power (`v=1`) calibrations of the actual #4470 raw invoice at
rank/height boundaries. Five mathematical controls reject. Allow a minute
for the bounded replay. Committed-byte and Git-free export checks are
separate publication evidence; the optional full-history ancestry preflight
is not claimed in this shallow checkout.

Finite checks corroborate the written inequalities; they are not a proof
by enumeration of every rank or native operator. All evidence from this
session is **author-checked**, including the separately implemented
arithmetic. No independent reviewer or proof kernel is claimed.

Not checked: exact `B_N`, least/alternative batching widths, a physical
compiled word, all-column/native correctness, owned-bank and route bodies,
precision or fixed tapes, BIT/outer supplier admission, analytic/prime/
recovery hypotheses, or the full selected cold replay. The `c_row`, `Cw`
and unchanged BIT/old-stock tariffs are explicit inherited premises in the
outer substitution. No selected record, predecessor or frozen source is edited.

## Open next questions

1. **Sharpen the root/source census rather than change batching.** The
   coefficient bracket is below 5/4 but not exact. Derive a uniform bound
   on all eligible root multi-indices and nonroot source classes for this
   same fixed rule. First compare those counts on the literal small flows;
   stop if the additional estimate only renames the existing bounds.
   The missing ingredient is a quantified truncated-source estimate, not
   another numerical outer-root calculation.
2. **Bind the inherited physical stock interface.** This count result
   supplies B_N for one permitted finite realization. A full implementation
   still needs the actual fixed-program stock, routing, owned-storage and
   precision/tape contracts. Begin with one named source-bound invocation
   and its complete ownership ledger; the enormous uniform word is not
   materialized here.

## Attribution and task

Card `selected-stock-envelope`, adversarial-audit, priority revision 7,
refined to PR4972's open next question. Seed
`12681598eca9c3a85296c48193125739`; exact sources and card are in
`SOURCES.json` and `TASK.json`.

Credit James Reed / jwr404 (#4972 coefficient and handoff, #4970 old leaf);
Mark / Matarener (#4612 and `lockstep-live-role-audit`); zxv (#4436 nested
widths, higher-moment strictification and retained native/stock sources);
Cinna Davis / 1337isnot1337 and zxv (#4440/#4470); Jacob Alan Sussman
(Theorem 1G multinomial lockstep flow); Ryanson Jonathan (#4476 separate
width checks); and mihir-s-05 / #4507 and its #4519 recount for the distinct
chronological batching boundary. All retained source notices remain intact.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance, solo.
New material is Apache-2.0. The claim and subsequent handoff are linked in
the contribution PR; no scientific acceptance is inferred from publication.
