# A ceiling-free parent-stock bound for the selected BIT producer

Under the same packet and completed-leaf hypotheses as [PR2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084), the selected ordinary BIT producer admits

```
log_q S(n,w) <= 6748*w*log2(max(1,n))
            <= 6748*w*(1+log2 e),     0 <= n <= e, e,w integers >= 1.
```

This reduces PR2084's sufficient parent-stock coefficient from 8194 to 6748, a ratio of exactly 14/17. It also reduces `ceil(log2(8*sigma))` from 17 to 16. The existing native first-stage cutoff passes the sufficient fit guard with this coefficient.

This is a conditional stock-bound refinement and independent audit, not a new supplier, changed cutoff, physical reserve implementation or new kappa. The production row coefficient remains 18,355. No selected record or predecessor evidence changes.

## Scope and overlap

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. The one-time selection is retained in [SELECTION.json](SELECTION.json). The assigned card is `selected-stock-envelope`, refined to the native first-stage ordinary BIT producer and a tighter depth implication.

The nearest predecessor is Adam Gall's PR2084, read at head `8001a23b003bec5dff5e61edec907b652c475932`. Its packet/restoration proof and coefficient 8194 are credited, not claimed as new. Sricharan Vagvala's concurrent [PR2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105), head `0aca64e29d43533743bb912ac8b77b434e04b84a`, audits floor-depth thresholds for the **different complex m=73/rank-48 producer**. Its exact-depth method informed the independent inverse-threshold cross-check here. No predecessor verifier is imported or executed, and no pending package is copied into this one.

The new implication uses the BIT terminal threshold to remove a rounded-depth additive term before bounding stock. It does not reproduce the fourteen known headrooms or solve the retained implementation hypotheses. The ordinary producer is BIT `m=64`, not the complex `m=73` supplier that constrains the shared exponent.

Coordination: [Discussion 2114](https://github.com/CrocSwap/integer-mult-bounds/discussions/2114). The entry refresh covered 376 open PRs and 769 discussion records with complete pagination and no warnings. Metadata searches do not cover every diff or unpublished result.

## Source binding

The selected record binds `research/community-frontier1094-audit/ASSEMBLY.json`. Its BIT citation binds the exact tuned PR589 receipt by Git blob. The retained PR1087 assembler is authenticated as an immutable archive, then its `code/assemble.py` member is authenticated separately and read without execution. Its `BIT_L,BIT_T=9,32` and `BIT_M=1+7*BIT_L` identify dimension 64.

The cited receipt has maximum child rank 42, 28,416 live roles and 28,425 physical roles. All nine work roles remain in the packet. Its row bill is `2*(64^2+1)+9909+252=18355`; this package changes none of those charged production terms.

The source `three-stage-cover-bit.tex` supplies the local-ring full-cover formula and floor-child contract in sections "Finite covers, batching, and the strict moment" and "One weighted child on a generic residue class". Its displayed dimension 67 is historical. Instantiating that contract on the selected BIT recipe remains an explicit realization assumption. The reviewed PR185 proof retained by PR387 supplies the internally completed ordinary-leaf interface in "Nested row restoration and fixed tapes". Source hashes, Git blobs and the archive-member hash are in [SOURCES.json](SOURCES.json).

## Conditional all-width lemma

Retain these hypotheses.

- Fix an eligible odd prime `q>2^80`, avoiding the recipe's fixed denominator and rank exclusions, before choosing widths.
- The selected full-cover implementation exposes one complete packet per active coarse level, with divisor
  `W_q(w)=28425*|GL_64(F_q)|*q^(4096*(w-1))`.
- Atom width `w` stays fixed along a coarse call. Every child has atom count at most `r*floor(n/64)`, with `r<=42`. Bad-class fallback children have the stronger bound `floor(n/64)`. Below 64 atoms, and for peeled remainders and other ordinary operations, use completed ordinary calls.
- A child uses only its unused row quotient, fixes exposed ancestor fields as complete spectators and restores its supplied row before sequential reuse. The complete node restores its exposed role field. Completed ordinary leaves borrow internally and need no additional external row factor.

These are inherited interfaces, not conclusions of the finite checks below.

### Depth without a ceiling

Let `D(n)` be the maximum-rank depth envelope: zero for `n<64`, and otherwise

```
D(n) = 1 + D(42*floor(n/64)).
```

Monotonicity makes this an upper bound for every permitted child path, including fallback. It is not a claim that every such path is realized by the physical compiler.

Set `rho=42/64`. The exact integer certificate

```
2^17 * 42^28 < 64^28
```

proves `rho < 2^(-17/28)`. If a path has `d>=1` active nodes, its last active atom count is at least 64 and at most `rho^(d-1)*n`. Thus

```
log2 n >= 6 + (d-1)*log2(64/42)
        >= 6 + (d-1)*17/28
        >= d*17/28.
```

The last step uses the terminal slack `6>=17/28`. Consequently, for every integer `n>=0`,

```
D(n) <= (28/17)*log2(max(1,n)).
```

This has no ceiling or unnamed additive constant. Removing the terminal threshold invalidates this proof step. Replacing the floor by a ceiling can even prevent termination, since `42*ceil(84/64)=84`. Neither countermodel describes a defect in the selected floor contract. The allowance 28/17 is not claimed optimal.

### Divisible stock and its complete packet charge

Reduction modulo q gives exactly `q^(4096*(w-1))` lifts of each invertible low matrix. Therefore

```
|GL_64(Z/q^w Z)| < q^(4096*w),
log_q W_q(w) < 4096*w+1 <= 4097*w,
```

since `28425<q`. High-matrix fibers do not cancel from stock, and the nine additional physical roles stay charged.

Use the actual integer divisor `S(n,w)=W_q(w)^D(n)`. At a node, divide its complete row into one packet and a quotient. That quotient is divisible by each child's required reserve; surplus factors are complete spectators. Each completed child restores it, so siblings and the two outer-wrapper calls reuse it instead of multiplying it. At an ordinary leaf the external factor is one, under the retained completed interface. Its internal borrowing, tapes and time remain part of that interface.

Combining the packet and depth bounds gives

```
log_q S(n,w) <= 4097*w*(28/17)*log2(max(1,n))
             = 6748*w*log2(max(1,n)).
```

For positive depth the packet inequality is strict; for zero depth both sides are zero. For borrowing, choose `S(e,w)=W_q(w)^D(e)` from the original width e, before choosing k or the body width. Monotonicity ensures this reserve also supplies every body with `n<=e`. There is no circular choice of stock from a body width that depends on k.

This gives PR1965's H3 form with `sigma=6748`. The high-part exchange, remainders, leaf implementation and uniform time estimate are not proved or repriced here.

### Native first-stage comparison

The selected receipt defines `s=min(bit_lower,(1-10^-24)*complex_lower)-10^-27`, `a0=384599/10^10` and `a1=(1-s)*s+s*a0`. Its first recorded gap and cutoff are independently reconstructed with rational arithmetic. For `ell=ceil(log2(8*6748))=16` and `L=4785575287428`, the checker establishes

```
0 < delta <= 1-s,
L >= 3,
L*delta^2 >= 36,
L*delta >= 2*(4+16).
```

The sufficient fit lemma of Josie Elliston's PR1965 then gives `ceil(log_q S(e,w))<e/2` for all integer `e>=2^L`, with `w=ceil(e^s)`, subject to the retained interfaces. This comparison does not assert that an actual selected implementation meets them, nor that this cutoff is necessary. The known headroom arithmetic is not claimed as new.

## Replay and controls

Standard-library Python 3.12, from the repository root:

```
python3.12 -I -B research/selected-bit-ceiling-free-stock/verify.py
python3.12 -I -O -B research/selected-bit-ceiling-free-stock/test_verify.py
python3.12 scripts/research_package.py --package research/selected-bit-ceiling-free-stock
```

Expected output includes `PASS_SELECTED_BIT_CEILING_FREE_STOCK sigma=6748 predecessor=8194 ratio=14/17 widths=100001 ell=16 no_new_kappa`, ten passing test groups and `PASS_REGISTERED_RESEARCH_PACKAGE`.

The verifier checks every external byte pin before semantic use, authenticates the archive member, and requires the committed [RESULT.json](RESULT.json). It neither regenerates a missing result nor changes a mismatched one. The exact checks cover every width 0..100,000 using separate forward and all-child dynamic programs, 196 inverse-threshold boundary probes, and 15 power-boundary probes up to 4097-bit atom counts. Literal depth fixtures constrain their shared conventions.

Tests reject a false contraction, rank-43 substitution, missing terminal slack, capacity excess, wrong producer, omitted largest child, corrupted/nonregular archive member, insufficient cutoff and wrong coefficient. Optimized public-CLI controls mutate every declared live input in isolated copies and test corrupted and missing required results. No frozen file is modified. Python assertions are not acceptance gates. The universal implication rests on the written argument, not the finite fixtures.

## Verification limits and implementation bounds

No full selected cold replay, native compiler execution, Lean proof, hosted CI pass or independent human review is claimed. Only the native first-stage comparison is checked. Other stages need their preceding completed ordinary contract. The selected exponent and production row charge are unchanged.

The new checker has no recursion. The width sweep is bounded at 100,001, rank inventories at 64, source lists at 16, archive scanning at 1024 members, consumed member size at 65,536 bytes and forward paths at 8194 edges. Source files are capped at 8 MiB and authenticated before archive decoding. The selected two-level halving guard bounds paths for the admitted 4097-bit atom counts.

Power-of-Ten deviations are confined to Python's managed allocation and standard testing machinery. Rules 3 and 9 cannot provide allocation-free arithmetic or static unittest dispatch in this runtime. The fixed input/sweep/bit capacities bound live collections and integer sizes; test subprocesses have 120-second timeouts and temporary copies have scoped cleanup. The single `runpy` target is this package's own fixed verifier path. Follow-up is to reassess these capacities if the sweep or width domain expands, not to generalize this checker into an unbounded search. Syntax compilation, warnings-as-errors and normal/optimized replays are the available diagnostics; no repository-wide analyzer configuration changes are made.

## Open next questions

1. Can the selected GL64 packet and completed-row interfaces be realized with a source-bound all-size field-dependency certificate? Begin with one emitted parent/child split and verify that routes fix ancestor spectators and unused descendant stock. Finite scalar and depth checks do not discharge this implementation obligation. PR2097's fresh-fiber theorem is complementary.
2. Can an actual selected ordinary leaf be bound to the internally completed, zero-extra-external-stock interface at every admitted width? Trace its borrowing and restored endpoints while retaining complete outer spectators. The reviewed contract is inherited here; its physical realization, uniform time coefficients and tape obligations still block unconditional adoption.

## Credit

Adam Gall supplied PR2084's conditional BIT packet/stock implication. Sricharan Vagvala supplied the concurrent PR2105 complex depth audit. Josie Elliston supplied PR1956/PR1965's cutoff audit and time/space separation; ToikY supplied PR1990's independent stock-fit audit. DreamingOfClouds supplied the selected PR589 BIT word on eumemic's base and its credited compiler/hosting lineage. Rohan Arun supplied the reviewed PR185/PR387 contracts and selected PR1094 assembly on Jeremy Kothe's PR1087 predecessor. Their constructions, interface arguments and existing numerical receipts are not claimed as new.

Nick Petalas retains authorship and responsibility for this conditional refinement and checker. Apache-2.0, following the repository license. No predecessor files are vendored or modified.
