# Twelve restored R439 helper shears save 94 ADDs

This finite bit-circuit construction extends woklerx's retained PR1047 word
from **11,769 to 11,675 complete local ADDs**. Twelve additional helper shears
and their matching middle-column corrections save 94 ADDs after paying for
all 24 preparation/restoration gates. The complete forward and reverse
positive bounds remain 72,847 and 10,394,084. The paid rank profile is unchanged.
No improved exponent, best-known circuit or unrestricted minimum is claimed.

The source is PR1047 at `a01bd602969e4086e55f0d1f392855b91cfe0507`, built on
Sricharan Vagvala's PR967 at `c6caa79e6655d83780a3b70a1d658313126fb0b3`.
Both are retained in base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The accepted result at this base is PR1094 with the PR589 bit supplier,
conditional κ = `836330098538459/500000000000000000`. This package does not
alter that selection, its construction, or any frozen predecessor.

## Reproduce

From the repository root, Python 3.10+ and its standard library suffice:

```sh
python3 -I -O -B research/r439-helper-descent-seed15/verify.py
```

The final line is:

```text
PASS_R439_HELPER_DESCENT ADDs=11769->11675 rounds=12 columns=661 no_new_kappa
```

The command regenerates the entire bounded search and candidate in memory,
compares every field of [CERTIFICATE.json](CERTIFICATE.json), and checks nine
SHA256/Git-blob source pins in [SOURCES.json](SOURCES.json). The certificate
contains the complete additional gate sequence, every round's score histogram
and all priced nominees. Its candidate hash covers the entire canonical JSON
word. `--show` emits the regenerated certificate. No output files are written.
The default command also works when invoked by absolute path from another
working directory. [VALIDATION.md](VALIDATION.md) records executed checks.

## Exact circuit and complete cost

Use local helper indices 0 through 438; physical register indices add 222.
Immediately before PR1047's 111 middle target rows, append these helper ADDs:

```text
240 <- 127       146 <- 258       251 <- 255       260 <- 31
 17 <-  95       146 <-  75        18 <-   1        17 <- 82
254 <- 245       254 <- 211       360 <- 149       232 <- 113
```

For each `d <- s`, replace middle column `s` by column `s XOR d`. Apply the
helper gates in reverse order after the middle rows. The target basis and the
rest of D remain fixed; A, scatter, B, C, helper inventory and all frame data
are byte-for-byte equal as decoded fields.

For a formal identity, write `E_j = I + e_d e_s^T` over F2 for the jth gate.
Let h be the arbitrary helper state after the predecessor's fixed preparation,
and M the middle response matrix. Chronological preparation gives
`h' = E_k ... E_1 h`, while the column updates give `M' = M E_1 ... E_k`.
Since every `E_j^2 = I`, `M'h' = Mh`. Reverse restoration recovers h. Targets
may also start dirty, so this preserves the entire D operator. The argument
allows noncommuting gates. The twelve selected gates happen to commute;
this package claims no noncommutative advantage or new basis-change identity.

| Complete local resource | PR1047 parent | Candidate |
|---|---:|---:|
| Helper preparation ADDs | 222 | 234 |
| Target preparation ADDs | 306 | 306 |
| Middle target ADDs | 4,493 | 4,375 |
| Target restoration ADDs | 306 | 306 |
| Helper restoration ADDs | 222 | 234 |
| Complete D ADDs | 5,549 | 5,455 |
| Other local ADDs | 6,220 | 6,220 |
| Total local ADDs | 11,769 | 11,675 |
| Paid rank mass | 5,129 | 5,129 |
| Retained rank-seven COPYs | 9 | 9 |

All additional gates run at frame zero. No helper, source-access operation,
frame change, COPY or recursive child is added. Preparation and restoration
are both included in the net score
`weight(column_s) - weight(column_s XOR column_d) - 2`.
The inherited strict precision checks remain
`64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192`; both exact integers are in
the certificate. The verifier checks the retained bridge formula and 192-bit
allocation against their pinned sources. These are inherited sufficient
prefix bounds, not a newly established physical precision contract.

## Completed domain and failure boundary

The fresh OS assignment seed is 15. [CLAIM.md](CLAIM.md) records the three
candidate tasks, overlap check and fixed stopping rule. This extends PR1047's
explicitly excluded multi-shear domain. It does not rerun that package with a
different seed or treat its single-edge optimum as a global optimum.

At each round, score every ordered distinct helper pair on the updated matrix.
Rank positive net scores by descending saving, then SHA256 of the ASCII string
`15:round:destination:source`, then indices. Fully price exactly the first
`min(32, positive_count)` nominees, even after finding an admitted one. Accept
the first admitted nominee. Stop after at most 15 accepted steps or when that
prefix contains none. The round number starts at zero.

The run completed **2,499,666 pair scores across 13 rounds**, with **416 complete
trial invoices**. It accepted twelve steps. At the thirteenth round, 836 pairs
have positive ADD scores, but all first 32 violate precision admission. This is
a bounded stopping result. It does not rule out a later nominee, another tie
order, neutral setup, changed target basis or a different search algorithm.

Packed columns and explicit sets agree on every support score. A separately
written literal row constructor agrees on every trial word. The predecessor's
set-valued interpreter checks all 661 formal dirty-input columns, COPY/ERASE
lifetimes, and complete forward/reverse endpoints and prices for all 416
trials. The unchanged owning checker verifies the final geometry. Every
register's ordered frame path and the complete paid rank histogram agree with
the parent and retained selected inventory.

Ten rejection controls cover missing preparation/restoration/correction,
wrong direction, noncommuting restoration order, an unpaid restoration,
source omission, Boolean receipt substitution, strict precision equality,
and an actual positive-saving nominee outside precision. Forward-order
restoration is a positive control for the commuting selected gates. A fully
paid neutral pair preserves the endpoint and adds exactly two ADDs.

## Scope and predecessor credit

The syntactic H2 and literal `K_equals_D` predicates remain false, as in
PR1047/967. H1/H3/H4/H5 and the other owning interface conclusions pass; a
separate exact semantic D check passes. This is finite circuit evidence. It
does not admit the changed word as a physical supplier or prove the full
multiplication theorem. All-size/compiler, common-label/mutable-source,
whole-call hosting, precision/tape and analytic assumptions remain.

PR1122's composed A/B/star word and PR1188/1208's local rewrites report cheaper
words in other classes. Their counts are not combined here. The added evidence
is the precisely pinned 94-ADD composition on PR1047, its full trial invoices
and the recorded precision stop. PR1040 changes the target basis; this one
freezes it. The retained helper-quartet seed07 and frame281 seed15 packages
solve different finite problems.

Credit **woklerx, PR1047**, for the source word, one-shear formula, score/pricing
code and set-valued interpreter used here; **Sricharan Vagvala / theon199,
PR967**, for the helper-star construction; **Gareth Davidson / bitplane,
PR915/926**, for the fixed target basis and paired construction; **Ross
Richardson, PR965**, for related GL(3,2) work; and **Sagar Thakrar, PR753**, for
earlier restored helper stars. **DreamingOfClouds, PR589**, tunes **eumemic's
PR555/543** supplier and supplies the retained geometry/precision evidence.
The earlier two-sided and semantic-D work of Scott Woolsey Biggart, Greer
Guthrie, Mikhail R. Gadelha and commdata2338 remains credited in the predecessor
notices. Their source files, notices, licenses and AI disclosures are unchanged.

Prepared for **Sagar Thakrar** with substantial **OpenAI Codex assistance** in
research, mathematics, implementation, verification and writing. Apache-2.0.
One agent performed this work. Separate implementations are computational
cross-checks, not independent human review or formal verification.

## Open next questions

Can a lower-positive-bound preparation admit one of the final rejected
nominees? This matters because the current path stopped on precision while
positive ADD scores remain. Start with the first rejected pair in the final
round, identify the prefix attaining its larger F or B, and seek a different
literal preparation of that same map. More enumeration alone would not
resolve that mechanism question. The complete precision budget is the blocker.

Can this exact extension survive whole-hosted semantic-D admission? First
compare its emitted hosted records and full invoices with PR1047's provider
boundary, retaining all restoration and source operations. Acceptance of the
semantic substitution, native compiler replay, hosted invoices and outer
assembly are still required. The unchanged paid profile gives no reason to
expect an exponent improvement from these ADD savings alone.
