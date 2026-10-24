# Independent complete-word audit of the five-label sharp cap

**No correctness gap found in the stated PR4992 argument.** A separate exact
checker corroborates the sharp excess cap **11** and the exclusion of universal
`(8,4)` splits for simple restored length-twelve singleton walks on `F2^5`.
The result belongs to Ali Romman's [PR #4992](https://github.com/CrocSwap/integer-mult-bounds/pull/4992).
This contribution answers its independent-review handoff with a proof review
and a different complete-domain enumeration; it claims no new bound or kappa.

Reviewed author head: `12a0105150f5f44a19a2199db8506d1aa44b009a`. The reviewed
README is Git blob `1b80ac21964baf508859127126baac595dc9cdba`, identical at that
head and this package's canonical-main base
`f259dabc7d70e0db8d6d36bfda888f008bbfecc1`. [SOURCES.json](SOURCES.json) pins its
SHA256, the selected record and revision-7 task catalogue as provenance.
No predecessor program is imported by the new checker. The source documents
are not runtime inputs; direct replay is self-contained and needs no Git.

This is a fresh solo agent/code check of the successor. The submitting account
also authored predecessor #4907; that relationship is disclosed rather than
claiming an independent human review. Prepared by Mihir Srivastava with
substantial OpenAI Codex assistance. No proof-kernel or maintainer acceptance
is asserted; the central review ledger is unchanged.

## Exact question and definitions

For labels `w_i` in `{0,1,2,3,4}`, put `q_0=0` and
`q_(i+1)=q_i XOR (1 << w_i)`. The twelve nonclosing states form `S`.
Restoration means `q_12=0`; simplicity means those twelve states are distinct;
universality means `{x XOR y: x,y in S}=F2^5`.
For a nonzero functional mask `f`, split `S` into its two parity classes `A,B`.
Writing `D(C)` for the distinct pair sums of unequal points in `C`, the quantity is

```text
X_f = choose(|A|,2) + choose(|B|,2) - |D(A)| - |D(B)|.
```

Overlapping supports must be subtracted separately. For weight four or five,
the claim is `X_f <= 11`; weight four additionally excludes split `(8,4)`.
This audit checks that exact domain, not partial prefixes or a production prune.

## Review of the written proof

The following checks address the logical implications, separately from running
the author's verifier. Symbols below agree with PR4992's README.

1. **The matching equality is sufficient to force the block cycle.** If `f`
   has weight four, its omitted coordinate `v` is the only preserving edge.
   Those edges form a matching. From `s-t=a-b`, `2a<=s`, and `2b<=t`, an `(8,4)`
   split forces `a=4,b=0,c=8`. Thus every majority vertex has exactly one
   preserving edge and one crossing edge. The four distinct majority pairs
   occur as `B-A-A-B` blocks. Each block flips the `v` level once, so the four
   minority vertices have alternating levels, two at each level. This uses
   simplicity and a complete cycle, including the closing edge.

2. **The complement really is one translation.** Project the majority to the
   four-dimensional cube and translate it into the even subspace `E` of size
   eight. A four-point projection `T` has three or six nonzero differences.
   The three-difference case supplies only `1+2*3=7` lifted differences;
   four minority vertices supply at most six, so it cannot cover the fifteen
   required kernel differences. In the six-difference case, translate one
   point to zero. The other three form a basis of `E`. Their sum `z` is the
   unique missing nonzero difference. Therefore `T` and `T+z` partition `E`.

3. **Universality forces the repeated projection used in the contradiction.**
   Both missing majority differences `(z,0)` and `(z,1)` must occur in `D(B)`.
   The first uses both minority vertices at one level, with projections `u`
   and `w=u+z`. Every cross-level pair uses one of those two vertices. To
   obtain difference `(z,1)`, the other level must therefore contain a second
   lift of `u` or `w`. Renaming gives the alternating order
   `u_0,u_1,w_0,y_1`, up to rotation/reversal. The four distinct block labels
   force at least three neighbors of `u` in `T` and at least two of `w`.
   The case `y=w` remains covered; no distinctness of all four projections
   was assumed. Translation by `z` sends `N(u)` to `N(w)` and `T` to its
   complement in `E`. Hence the two neighbor counts sum to exactly four,
   contradicting the required five. This closes the nonplanar case too.

4. **The support classification does not omit a six-point type.** Five to
   seven points in affine dimension three occupy more than half their
   eight-point affine space, so all seven nonzero differences occur.
   In dimension four, an affine basis is `{0,e1,e2,e3,e4}`. An added point
   of weight two or three yields twelve differences; one of weight four
   yields fifteen. For the weight-three case, translate by `e1`: use basis
   `{e1,e1+e2,e1+e3,e1+e4}`. The extra point `e2+e3` is the sum of the middle
   two basis vectors, so this is indeed the weight-two normal form.
   Thus the stated `C6={0,1,2,3,4,8}` case and the fifteen-difference case
   exhaust the possibilities. Each possible seventh point in the displayed
   table adds a difference outside `1,...,12`, establishing at least thirteen.

5. **Both final class splits have the claimed bound.** For `(6,6)`, both
   supports cannot have size seven because their union must have size fifteen;
   one therefore has size at least twelve. The bound is `30-7-12=11`.
   For `(7,5)`, if the seven-point class had affine dimension three with
   direction `H`, the other class would have to supply all eight differences
   outside `H`. Five points split into the two `H` cosets have only
   `k(5-k)<=6` cross-coset pairs. Thus its seven-point partner has dimension
   four and support at least thirteen, giving `31-13-7=11`. The explicit
   witnesses attain eleven. Coordinate permutations cover every weight-four
   mask, and weight five is the alternating `(6,6)` case.

No larger-dimensional, other-length, partial-prefix or arbitrary-point-set
claim is inferred from these steps.

## Different complete-domain oracle

The new `verify.py` does not traverse a pruned cube-path tree. Restoration
forces every label multiplicity to be even; universality forces all five
labels to appear. With twelve positions, the multiplicities are necessarily
`(4,2,2,2,2)`. Normalize the unique four-occurrence label to zero.

Choose its four positions in `choose(12,4)=495` ways. Partition the remaining
eight positions into unordered pairs: there are `8!/(2^4*4!)=105` perfect
matchings. Give the four pairs labels one through four in order of their
smallest positions. This has exactly one representative per coordinate-label
permutation orbit. All six high-weight masks are checked, so the normalization
does not discard a functional. Neither rotations nor reversals are quotiented.
Every required word is represented; absent-label words cannot be universal.

All **51,975** candidates are generated before any geometric filtering. Only
literal simplicity and the full 32-element pair-sum test select the universal
domain. No excess threshold, class split, support bound, matching balance,
Hamiltonian search or quotient argument prunes candidate generation.
The split and cap are checked as conclusions on every admitted word.

| Stage | Exact count |
|---|---:|
| Coordinate-normalized multiplicity words | 51,975 |
| Nonsimple words | 48,594 |
| Simple words | 3,381 |
| Simple but nonuniversal words | 2,553 |
| Universal words | 828 |
| Universal word / high-weight functional pairs | 4,968 |
| Weight-four cases attaining eleven | 444 |
| Weight-five cases attaining eleven | 36 |
| Universal `(8,4)` cases | 0 |

The complete histograms agree with #4907's previously measured census. Those
counts and the bound are prior results, not new discoveries. The additional
evidence is an implementation using positions/perfect matchings, its domain
completeness argument, and the explicit review above. [RESULT.json](RESULT.json)
retains the histogram and SHA256 digests of both sorted candidate lists
(ASCII words separated by LF, including the final LF).

Controls check both literal sharp witnesses, 64 translated starts, 48 rotated
or reversed witnesses, and reject cap ten, invalid lengths/labels, a nonrestored
word, a nonsimple word and a low-weight mask. The simple restored word
`012013024034` has an `(8,4)` split at mask 30 but is not universal: it is
retained as a discriminating boundary case. Merging the two class supports
would give fifteen rather than eleven on the weight-five witness.
`mutations.py` rejects eight actual code changes, under `-O` and with stored
receipt comparison disabled; it also runs an unmodified positive control.

## Reproduction and evidence

From the repository root, with CPython 3.12 and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/f7-five-label-independent-audit
python3.12 -I -O -W error -B research/f7-five-label-independent-audit/verify.py
```

The registered replay checks normal and optimized modes plus all eight mutations.
Direct `--emit-receipt` prints the recomputed result for inspection; ordinary
replay compares it exactly with `RESULT.json` and writes no package files.
The complete registered replay is expected to take under ten seconds locally.

On Windows 11 / CPython 3.12.0, the predecessor's own registered normal/optimized
replay also passed: 23,816 support sets, 127,400 invariant-majority set pairs
and 13,664 universal graphs. This is additional replay evidence, distinct from
the new algorithm. Source equality was checked against both canonical main
and the exact public author head. The optional full-history preflight is not
claimed in this shallow partial clone. The package pins only its main ancestor;
the author's separate fetched commit is not a runtime or provenance dependency.

## Coordination, limits and credit

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/4903#discussioncomment-19140259)
takes the independent-review part of the
[handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138920).
Entry overlap covered 323 open PRs and 4,134 Discussion records with complete
remote pagination at 2026-10-23 07:04 UTC. Initial local coverage was 7 of
6,710 note records, followed by direct reads/materialization of the relevant
f7 predecessors and successor. Omitted notes, arbitrary diffs and unpublished
work remain limits. [TASK.json](TASK.json) records the changed card scope.

Submission refresh at 07:16 UTC retained the same main and guidance and covered
329 open PRs and 4,150 Discussion records. It found a concurrent
[six-plus-six path-join audit](https://github.com/CrocSwap/integer-mult-bounds/discussions/4903#discussioncomment-19140301)
under the same account. This package retains the already completed, different
position/perfect-matching method. The concurrent audit is acknowledged, not
treated as absent; neither claims the predecessor's cap or census as new.
The local refresh searched 47 records with 6,665 tracked notes omitted.

No maintained engine, seven-label census, supplier admission, selected cold
replay or complete multiplication theorem was checked. The selected exponent
remains `60403/20000000`. This audit does not promote an archive into a selected
result or modify its recorded scientific acceptance status.

Credit Ali Romman for #4992's sharp proof; Mihir Srivastava for
[#4907](https://github.com/CrocSwap/integer-mult-bounds/pull/4907)'s cap-15 proof,
measured sharp cap and handoff; Nick Petalas for
[#4894](https://github.com/CrocSwap/integer-mult-bounds/pull/4894)'s matching
balance; unpaidmoon for [#4148](https://github.com/CrocSwap/integer-mult-bounds/pull/4148);
Nicholas Stone for [#2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973);
James Reed for [#3096](https://github.com/CrocSwap/integer-mult-bounds/pull/3096);
and Ross Richardson for [#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943).
New code and review are Apache-2.0; predecessor files and notices are unchanged.

## Open next questions

The complete-walk proof does not supply a partial-prefix runtime improvement.
Ali Romman's #5001 supplies a separate completion condition, and JoyboyBrian
has already [claimed its maintained-engine integration](https://github.com/CrocSwap/integer-mult-bounds/discussions/4903#discussioncomment-19139518).
The next useful check is exact equality of the implementation's prune-off/on
leaf multisets, followed by measured runtime. Follow that existing claim;
this audit neither duplicates nor reserves it. An independent human or formal
proof-kernel review of the written sharp-cap argument also remains welcome.
