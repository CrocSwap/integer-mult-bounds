# Complete the six-source one-TRIO census domain

This resolves the profile omission identified in the maintainer review of
[PR2134](https://github.com/CrocSwap/integer-mult-bounds/pull/2134), head
388a63c83cf24c3355be9798bde5a381188dadb3. The full legal domain contains five
singleton-count profiles and 5,675,670 canonical words, rather than the two
profiles and 2,342,340 words accepted by its filter. Two enumeration methods
agree on every per-profile histogram. The claimed maximum survives: 61 of 63
nonzero masks, attained by 88 canonical words. The best completed unit-call
bill remains 144, versus the credited 142-call singleton incumbent.

This repairs the existing finite result's completeness. It does not claim its
witness, cost formula or maximum as a new construction, or extend the search
to more calls or another alphabet.

## Exact domain and complete profile proof

Retain six read-only sources, one arbitrary dirty connector, arbitrary dirty
output targets, thirteen singleton source calls, and one atomic TRIO toggling
three distinct sources. Readouts observe the connector at call boundaries;
their targets are unread until completion. Each complete call restores private
scratch and preserves other rows. The schedule must work for arbitrary
compatible linear maps and inputs over F2. The combined TRIO remains a changed
alphabet assumption; its native realization and extra costs are not free.

Let c_j be singleton multiplicities. Every source must have even total count
at least two. Hence every c_j>=1 (zero cannot become two with one TRIO), their
sum is 13, and exactly three are odd. The unique restoring TRIO acts on those
odd labels. Conversely these conditions suffice: odd positive counts become
even and at least two; already-even counts are at least two.

The total sorted profiles are (2,2,2,2,4,4) and (2,2,2,2,2,6). Subtract one from
*any three distinct positions*, rather than one selected choice in each profile:

| Sorted singleton counts | Canonical words | Maximum nonzero coverage | Old filter |
| --- | ---: | ---: | --- |
| 1,1,1,2,2,6 | 180180 | 45 | omitted |
| 1,1,1,2,4,4 | 450450 | 50 | omitted |
| 1,1,2,2,2,5 | 540540 | 54 | retained |
| 1,1,2,2,3,4 | 2702700 | 58 | omitted |
| 1,2,2,2,3,3 | 1801800 | 61 | retained |

Independently enumerate positive nondecreasing six-tuples summing 13 and keep
exactly three odd entries. This yields the same five profiles exhaustively,
since each entry lies between 1 and 8. The review's omitted example with counts
(1,1,1,2,2,6) passes the complete predicate and fails the pinned predecessor's
actual `analyze_word`. That source remains unchanged and receives credit for
its valid subdomain.

## Why the TRIO can be last

The valid invariance is **cyclic rotation of the closed path**, not arbitrary
commutation of adjacent calls. Let the 14 edge masks have XOR sum 0, with prefix
vertices q_0=0,...,q_14=q_0. Rotate the edge sequence to start just after its
unique TRIO. Every new boundary vertex is an old q_i XOR the new starting
vertex, so all pair differences are unchanged. The TRIO is now last. The
duplicate closing vertex adds no new difference, making q_0 through q_13
the complete boundary set. Repeated vertices are allowed.

Source-label permutations preserve coverage too. Thus the census covers every
TRIO placement. Controls check all 14 rotations of the witness and exhibit an
adjacent commuting swap that changes its coverage set; the stronger arbitrary-
commutation assertion is unnecessary and is not used.

## Two complete enumerations

The Python primary fixes each sorted multiplicity profile, labels coordinates
by their total counts, and orders equal-count labels by first occurrence. It
enumerates multiset permutations under only that equal-count symmetry. Every
source-relabeling orbit has exactly one representative. For profile c its
independent combinatorial count is

    13! / (product_j c_j! * product_v multiplicity(v)!).

The program checks this count for each profile. It stores occupied prefixes
in a 64-bit mask; adding vertex q contributes that set translated by XOR q,
implemented by exact bit-block swaps. This differs from the predecessor's
list-based incremental calculation and the native direct-pair calculation.

The C++ cross-check enumerates all 9,321,312 restricted-growth words on six
labels. It admits a leaf solely when exactly three counts are odd, recomputes
all pair differences from its 14 prefixes, and records a separate histogram
per profile. Every histogram matches Python. Neither acceptance predicate uses
the old two-profile list. Summing the new rows belonging to that old list
reproduces every bin of its recorded histogram, including maximum 61 and 88
maximizers. The finite exclusion depends on these completed exhaustive runs;
it is not inferred from a sampled subset or receipt alone.

## Completed bill and limits

An arbitrary dirty connector requires an even number of readouts for each
active output. Paired readouts realize precisely prefix differences. At most 61
of 63 masks are paired, so at least two outputs need four or more readouts:
the total is at least 61*2+2*4=130. The credited witness repairs its missing
masks 11 and 40 with four readouts each, attaining 130. Adding 14 source calls
gives 144. The retained full-cover singleton word uses 126 readouts and 142 calls.

The attaining witness has the incumbent's source-map multiplicity multiset.
With common dispatch/frame price f, readout price g, and all incremental TRIO
expenses rho, its difference is -2f+4g+rho, or 2+rho at unit prices. No native
TRIO implementation, free workspace, favorable nonuniform tariff, hosted
invoice, selected supplier or new kappa follows. Additional TRIO calls,
different readouts and different restoration rules are outside this theorem.

The two algorithms share model-assisted development. Their different symmetry
quotients and coverage calculations are computational cross-checks, not
independent human authorship or formal-kernel verification.

## Reproduce

Python 3.12+, standard library only (about 17 seconds locally):

```sh
python3 -I -O -B research/six-trio-complete-profile-audit/verify.py
python3 scripts/research_package.py --package research/six-trio-complete-profile-audit
```

Separate C++17 full census:

```sh
g++ -O3 -std=c++17 research/six-trio-complete-profile-audit/independent.cpp -o trio-independent
./trio-independent
```

Its JSON `profiles` must equal RESULT.json's `profiles`. Registered replay
recomputes the complete Python census; it does not compile C++. Default replay
is read-only and compares the complete typed receipt. --write creates a new
file exclusively. Actual runs are in VALIDATION.md.

## Provenance and stopping decision

Start b5ea56e0, priority 5; picker 1f7ab218c17758bb2e23f41aac1faadd drew
bit-mechanisms. Baseline and R439 helper-star orientation passed first.
The changed scope repairs a current review blocker instead of extending the
closed scalar/helper censuses. TASK.json links the canonical claim. Current
model sources and unchanged predecessor bytes have exact Git/SHA256 pins.
No original author's branch, frozen source or selected frontier is changed.

Family decision: finish this completeness repair and stop. Boundary and call
bill are explicit; native TRIO, scratch, hosting, precision/tape and whole-
supplier costs remain unknown. This changes whether the existing finite claim
has evidence for its stated domain, without justifying a construction campaign.

Credit 1337isnot1337 for PR2134's witness and subdomain census, the maintainer
review for the omission finding, Ross Richardson's connector boundary and the
retained six-source authors. The C++ cross-check follows the predecessor's
RGS/direct-difference approach; Python's multiplicity-first enumerator is
separately written here. Prepared by ywz65 with substantial OpenAI Codex
assistance in proof, code, validation and writing. Apache-2.0; notices retained.

## Open next questions

Can the original PR incorporate this complete domain and replace its arbitrary-
commutation sentence with the closed-path rotation proof? Compare all five
histograms and the old subdomain before updating its claim. This closes the
stated finite blocker; no additional larger census is proposed here.
