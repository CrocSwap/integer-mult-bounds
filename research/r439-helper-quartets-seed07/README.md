# A four-helper fusion below the R439 disjoint-pair floor

One four-helper change reduces the frozen PR941 circuit from **11,949 to
11,946 complete ADDs**, including preparation and restoration. It crosses
the **11,948-ADD disjoint-pair floor** certified by PR941, whose integer dual
certificate is replayed here. The new helper graph is a connected four-node
path, outside that class. No new kappa is claimed.

This is a small construction and an exact bounded search result. It is not
the cheapest known R439 word: Ross Richardson's PR965 reports 11,840 ADDs
with coupled triples, and PR967 reports 11,783 with restored stars. Their
savings are not combined here. The final overlap refresh also found @woklerx's
PR1040, which retunes one target step after PR967 and reports 11,780 ADDs.
That changes the target basis; this package freezes it. PR1040 head:
`9d885867f28c1f391ab395af2d0b1f2a63681bfd`. The additional evidence here is a fully priced
GL(4,2) search around a fixed, precision-admitted matching, with an exact
minimum for each of 64 prescribed quartets.

| Quantity | Frozen PR941 | Four-helper word |
|---|---:|---:|
| Complete ADDs | 11,949 | 11,946 |
| D ADDs | 5,729 | 5,726 |
| Native records | 14,878 | 14,875 |
| Helper preparation ADDs | 199 | 200 |
| D injection ADDs | 4,719 | 4,714 |
| Forward positive maximum F | 70,083 | 70,355 |
| Reverse positive maximum B | 10,548,832 | 10,548,832 |
| Local payload bits | 101 | 101 |
| Nine-stage prefix bits | 192 | 192 |

All 439 helper registers, nine COPY/ERASE pairs, per-register frame paths,
paid rank histogram and rank mass 5,129 are unchanged. The selected PR942
conditional kappa remains `1661960547713947/1000000000000000000`.

## Reproduce

Run from the repository root with Python 3.11 or later. The finite replay
uses the standard library and source-pinned repository checkers.

```sh
rtk proxy python3.11 -I -B research/r439-helper-quartets-seed07/verify.py
```

The output is JSON with `status = PASS_R439_HELPER_QUARTETS`,
`combinations = 1290240`, `columns = 661`, `native_ADDs = 11946`,
`saved_ADDs = 3` and `no_new_kappa = true`. Eleven negative controls must
be rejected, and an endpoint-neutral pair must be accepted and charged
two ADDs. Optimized isolated Python produces the same receipt.

To print the complete deterministic census separately:

```sh
rtk proxy python3.11 -I -B research/r439-helper-quartets-seed07/search.py
```

It must reproduce `CERTIFICATE.json` as parsed JSON, including census hash
`34cd212d94a5caeea01fbf774b62155a99778bb9b9dfacce738d48d2d8e06cfc`.

The optional native replay requires a C++17 compiler and Boost headers.
Use a fresh output directory; all generated files stay there.

```sh
rtk proxy env BOOST_INCLUDE=/path/to/boost CXX=c++ python3.11 -I -B \
  research/r439-helper-quartets-seed07/native.py /tmp/r439-quartets-native
```

Expected output:

```text
PASS_R439_HELPER_QUARTETS_NATIVE ADDs=11949->11946 columns=883/1327/1549 controls=96/96 no_new_kappa
```

`NATIVE-RECEIPT.json` records the completed Apple clang 21 / Boost 1.85.0
replay and all 186 non-system compiler dependency hashes. The runner saves
the exact commands, generated candidate, reports and logs in its output
directory. Toolchain versions and dependency hashes describe this run;
other supported environments should reproduce the mathematical fields,
not the environment strings. Linux CI success is not asserted.

## The exact change and its cost

Use local helper labels `a=269`, `b=88`, `c=288`, `d=153`, with zero-based
indices among the 439 helpers. They are pairs 114 and 126 of the frozen
PR941 `selected_pairs`. Originally the two preparations are `a ^= b` and
`c ^= d`. The replacement is the chronological word

```text
a ^= b
c ^= d
b ^= c
```

Its matrix has rows `[3,14,12,8]` in the ordered basis `[a,b,c,d]`.
The second operation changes `c` before the third reads it. Restore with
the literal reverse word after the D injection and target restoration.
The other 197 helper pairs and the 306 target shears stay fixed.

Let K be the original D coefficient matrix, E the frozen PR915 target
basis and H the complete helper basis. Prepare H on arbitrary helper data
and E on arbitrary targets, inject `M = E K H^-1`, then restore E and H.
The endpoint is exactly

```text
(x,y,s) -> (x,y + K s,s)
```

over F2, including arbitrary initial helper dirt and target values. Indeed,
the prepared target is `E y`; injection gives `E y + M H s`, and restoring
E gives `y + E^-1 M H s = y + K s`. Helper restoration returns s. Sources
are never destinations. This is an F2 endpoint identity, not equality of
the corresponding integer transfer matrices.

Write A,B,C,D for the four columns of E K. The old injection uses
`[A, A+B, C, C+D]`. The replacement uses `[A, A+B, A+B+C, C+D]`.
Their column weights are `[9,11,13,15]` and `[9,11,8,15]`, respectively.
The injection saves five ADDs; the extra preparation and restoration cost
two. The complete invoice is

```text
200 + 306 + 4714 + 306 + 200 = 5726 D ADDs
5726 + 6220 = 11946 complete ADDs
```

The forward positive maximum increases, so a local norm-domination
argument would be false. Whole-word chronological replay, including
COPY/ERASE and both orientations, gives F=70,355 and B=10,548,832. The
strict inherited checks are

```text
64 F^3 B^2 = 2480125329327922327549632512000 < 2^104
2^18 F^5 B^4 = 5595414477252957880107217850693663956755891575010099200000 < 2^192
```

The second expression occupies about 89.14% of its cap. This checks the
existing nine-stage prefix expression only; it is not a new global invoice.

## Completed search and exact boundary

The OS assignment draw was 7. The local claim was recorded within the first
eight minutes of the cycle. From all `choose(199,2)=19,701` pair unions,
take the first 64 under ascending SHA256 of the ASCII string `7:i:j`.
No random restarts, additional nominees or combinations of winners follow.

For each quartet, enumerate all **20,160** invertible four-by-four matrices
over F2. Breadth-first search over the 12 lexicographically ordered XOR
generators supplies one shortest helper word per matrix. Complete prices
include both helper passes, the fixed target passes, the changed injection
and all 6,220 outside-D ADDs. Ties use the matrix tuple. Each quartet's
cheapest representative receives a complete positive-bound replay.

The 1,290,240 prices yield 62 unchanged minima, one 11,948-ADD minimum and
one 11,946-ADD minimum. All 64 representatives pass the precision checks.
The chosen quartet is therefore optimal in this declared union of 64
single-quartet classes, including arbitrary-length XOR preparation words
on those four helpers. It is also optimal for its own quartet. It is not
an optimum over all 19,701 quartets, different frozen matchings, several
simultaneous fusions, added registers, changed target bases or full circuits.

The independent check enumerates the group directly by Gaussian elimination,
replays every realizing word and checks every generator edge inequality for
its proposed distance. An identity distance of zero and the inequalities
prove the lower distance bound along every path; realizing words prove the
upper bound. Set-valued column operations and independently inverted matrices
then reproduce every price and the census hash. This is an exact finite
certificate, not a failed search interpreted as an impossibility theorem.

The predecessor's separate 96,141-edge integer vertex/odd-set dual is also
replayed. Its complete all-disjoint-pair floor is 11,948. The connected
four-helper word lies outside its hypothesis, so the new 11,946 count is
consistent with that result.

## Verification and remaining obligations

The Python replay checks the full 661-input D boundary in both directions,
the complete word's source/frame checker, all outside-D fields and exact
literal costs. Controls omit each quartet operation in each pass, reorder
dependent preparations, change a frame, alter an outside-D operation,
undercharge the invoice and test an endpoint-valid precision overflow.
The native replay checks 883, 1,327 and 1,549 formal columns at 5, 9 and 11
stages for each of the two words, rejecting all 96 omitted-bridge controls.
It independently agrees on cost, bounds, paid ranks and copy lifetimes.

Like PR915/926/941, this word intentionally fails the original syntactic
`H2_D_frame0_targets_from_helpers` and literal `K_equals_D` predicates.
Those checks are not weakened. The semantic endpoint above and its exact
column replay replace that premise for this finite result; H1/H3/H4/H5 and
the other owning-checker conclusions still pass.

Publication checks also rejected four external package corruptions: a false
complete cost, an altered quartet operation, a duplicate JSON field and a
changed source digest. The 25 existing selected-record tests and nine finite
bit-contract tests pass. No new test framework or repository-wide artifacts
were added.

Supplier adoption still requires acceptance of the semantic D interface,
changed whole-hosted emission and audit, complete finite/precision invoices
and outer assembly against the selected complex supplier. All-size/compiler,
common-label/mutable-source realization, whole-call hosting, tape and analytic
assumptions remain. No complete multiplication theorem, formal proof-assistant
check, supplier cold replay, repository-wide test run or human peer review is
claimed. The selected frontier and `upstream/` are unchanged.

## Sources and credit

Exact research base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`.
`SOURCES.json` binds 43 repository files plus the predecessor's checked
manifest closure. It records the selected context separately; replay does
not consume the moving selected pointer.

Credit Gareth Davidson / @bitplane for PR915's target basis, PR926's
two-sided helper construction and PR941's matching and exact pair bound.
PR941 head: `8af78333709a2eafd84463a7dc91467be5618b49`. Its native and
owning-checker routines are reused with attribution. Scott Woolsey Biggart's
PR733 is the two-sided mechanism predecessor. Ross Richardson's PR965
`6292e3774abd82f2d5202190b498f35cc1628c39` supplies the GL(3,2) search
pattern adapted here to two-pair GL(4,2) fusion. PR967's independently
selected stars and PR978's historical R420 sharing are adjacent work.

The selected R439 word is eumemic's PR555 on PR543, with DreamingOfClouds'
PR545 punctured unit and PR589 tuning. Preserve their earlier E8, frame,
hosting and source attributions in the checked dependency manifests. The
selected T37 construction and review are read for context and are not changed.

Prepared by **Sagar Thakrar / @thakrarsagar**, with substantial **OpenAI Codex
assistance** in mathematics, search, implementation, verification and writing.
All new files are under the repository's **Apache-2.0** license. This is an
independent computation using reused source checkers, not independent human
peer review. No priority or best-known-circuit claim is made.
