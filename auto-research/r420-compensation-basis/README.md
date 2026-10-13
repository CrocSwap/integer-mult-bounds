# R420 compensation through 201 restored helper-basis pairs

**Finite bit-circuit improvement; no new κ.** The frame-zero dirt
compensation in eumemic's accepted #543 R420 word uses 19,922 binary XOR
additions. A simultaneous disjoint helper-basis change reduces this to
**12,988**, including all 201 preparation and 201 restoration additions.
The complete native word falls from **26,916 to 19,982 ADDs**: 6,934 fewer,
about 25.8%. No helper, COPY, frame transition or recursive rank is removed.

The signed-prefix allowance rises from 100 to **102 bits**, within the
original strict 104-bit cap. This tradeoff is part of the result; a lower
ADD count alone would not establish admissibility. A hosted-parent invoice
and integration of the semantic prefix contract remain separate work.

## Reproduce

Python 3.11 or later, standard library only:

```sh
python3 -B research/r420-compensation-basis/verify.py
```

Expected:

```text
PASS_R420_COMPENSATION_BASIS D=19922->12988 native_ADDs=26916->19982 saved=6934 rank_mass=5112 payload_bits=102<104
```

This regenerates the seeded matching, rebuilds the word, checks all pinned
sources, compares the complete certificate, runs the original E8/frame and
all-column audits, checks the semantic prefix contract independently, and
replays both exported scalar orientations and their positive-prefix bills.
It takes about two seconds on the contributor's macOS machine. Checks stay
active under `-I -O`; no admission predicate relies on Python assertions.
The unchanged exporter is launched in a separate isolated interpreter with
assertions enabled.

For the unchanged C++ legality and five/nine/eleven-stage column checkers:

```sh
python3 -B research/r420-compensation-basis/verify.py --native
```

This additionally requires a C++17 compiler and Boost headers. Use
`--cxx /path/to/compiler --boost-include /path/to/include` when needed.
`--output /path/to/new-directory` writes the reconstructed `word.json.gz`,
the matched `certificate.json`, and, with `--native`, `native.json`.
An existing output directory is rejected. Linux CI runs the native command
on Python 3.11 and 3.14; its result is reported separately from local tests.

## Sources and concurrent work

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The reviewed #543 source head is `2065fe4f72a914d907f1046603f5a36f17018535`.
[SOURCES.json](SOURCES.json) pins the exact word, checker, emitter, C++
sources and supporting files. The word's full decompressed payload is
pinned, so changing only gzip headers does not invalidate its mathematics.

The first reference word has semantic SHA-256
`e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2`;
the reconstructed candidate has
`02a652417125bef15a2c01946a642d45dae8bba11a09a1ac13f3b7d2057be3dc`.
All fields except `D` are identical, including literal `A`, `B`, `C`,
the scatter, labels, source/target boundaries and retained totals.

**Concurrent #686 is directly related and credited.** Mikhail R. Gadelha's
[single-pair contribution](https://github.com/CrocSwap/integer-mult-bounds/pull/686),
at `23dcb610c2b156b76b9d599ea296c3cbde224b2d`, appeared while this experiment
was underway. It publishes the same restored frame-zero mechanism for
helpers 552 and 521, saving 108 ADDs, and states the same semantic H2
replacement. This matching contains that pair. No priority for that
mechanism or contract is claimed here. The additional result is a literal
**201-pair simultaneous construction**, its complete 6,934-ADD reduction,
and the measured increase in prefix bounds. No #686 code is imported.

The earlier #670/#674 proposals change separate phase-B blocks; #688
composes and hosts those block changes. This word does not import those
changes. #661 fixes D and the scalar gate stream. The historical
response-kernel/entrance lineage, including #259, changes recursive
interfaces; this prefix restores its entire helper basis before A.

## Circuit and sufficient prefix contract

Let `s` be the 420 arbitrary helper inputs, `y` the 120 arbitrary targets,
and `K` the binary 120-by-420 compensation matrix read from the original D.
The source inputs `x` are untouched by D. The required prefix is

```text
(x, s, y) -> (x, s, y + K s),       over F2.
```

Choose disjoint ordered helper pairs `(a,b)`. Each preparation operation is
`s_a <- s_a XOR s_b`. Let their product be `P`. Every elementary operation
is an involution; disjointness makes them commute, and the implementation
also records a literal reverse-order undo. Replace the original reads by
the matrix `K' = K P^-1`:

```text
s' = P s
y' = y + K' s' = y + K s
s  = P^-1 s'.
```

For one pair this keeps column `K_a` and changes column `K_b` to
`K_b XOR K_a`. The operations are ordinary binary XORs, at frame zero,
on existing helpers. Every helper is restored before the first A gate.
There are no initialized scratch, fresh-zero helper, source-access or
free-restoration assumptions. Arbitrarily correlated helper inputs are
covered by the full linear operator identity.

All starts of the touched helper and target registers are frame zero.
Consequently preparation, recoded reads and restoration introduce no
MOVE or recursive child. Their scalar work is charged explicitly. The
unchanged remainder sees exactly the original `(x,s,y+Ks)` state and the
original frames. Under the inherited common-label realization, this
pointwise frame-zero identity supplies the same prefix on every address.
It does not prove that inherited all-size realization interface anew.

### Why the old syntactic H2 still rejects this representation

The original `xcheck.py` requires every D destination to be a target.
It also extracts K by reading each D gate as a direct helper-to-target
addition. Those two predicates cannot represent a temporary helper basis.
They continue to reject this candidate; no predecessor checker is patched
or its rejection hidden.

The sufficient replacement is stronger than a comparison on clean inputs:
every D gate is legal at frame zero, uses only existing helpers as donors,
does not write a source, and its **complete operator on all 660 input
columns equals the original D**. All 420 helper columns are restored.
Every field outside D must equal the pinned word. The verifier checks this
with independent set-valued symbolic rows before relying on the original
interleaved-prefix proof. It separately runs the original checker on the
actual changed word: labels, frames, full arbitrary-dirt endpoint and all
other interface predicates pass. The canonical source word still passes
every original H1–H5 and conclusion predicate.

This is a finite semantic-prefix substitution with a written composition
argument, not a claim that the changed syntax is accepted by every existing
supplier pipeline. In particular, no signed integer endpoint equality is
asserted: the circuit identity is over F2, and the signed lift's actual
nonnegative coefficient bounds are recomputed below.

## Search and complete bill

The operating-system assignment seed was **12**, selecting the bit track.
It seeds only the tie order in a deterministic greedy matching. Three
candidate tasks and the local scope claim are recorded in
[CLAIM.json](CLAIM.json); no pinned coordination issue existed.

For columns `K_a,K_b`, the net saving from `s_a ^= s_b` is

```text
weight(K_b) - weight(K_b XOR K_a) - 2.
```

The final `2` pays preparation and restoration. Both orientations of all
87,990 unordered helper pairs are scored. For each pair retain its better
positive orientation (lower-index destination breaks orientation ties),
then sort by descending gain and seed-12 64-bit tie keys. Take a pair only
when neither helper has already been used. The selected gains are additive
because the supports are disjoint. There are 27,653 positive candidates
and 201 selected pairs, touching 402 existing helpers.

The stopping rule is exactly one complete pair-score enumeration and one
greedy matching. No maximum-weight matching, optimal circuit, or exhaustive
multi-operation search is claimed. [RECIPE.json](RECIPE.json) freezes the
literal pairs and gains; the verifier re-nominates them and also recounts
the complete emitted program, so a search score is not an admission receipt.

| Item | Original | Changed |
|---|---:|---:|
| Basis preparation ADDs | 0 | 201 |
| Compensation target ADDs | 19,922 | 12,586 |
| Basis restoration ADDs | 0 | 201 |
| Complete D ADDs | 19,922 | 12,988 |
| Complete native ADDs | 26,916 | 19,982 |
| Exported records | 29,874 | 22,940 |
| Helpers / COPYs | 420 / 9 | 420 / 9 |
| Rank mass | 5,112 | 5,112 |
| Forward positive-prefix bound | 144,651 | 202,699 |
| Reverse positive-prefix bound | 2,270,064 | 2,446,788 |
| `64 * forward^3 * reverse^2`, in bits | 100 | 102 |

Binary ADDs are the primitive count. The higher-level grouped D gate count
actually rises from 120 to 522, because each of the 120 target rows was
already represented as one multi-source gate. The unchanged recursive
profile is `{1:1320, 2:1440, 4:60, 5:120, 8:9}`. Every register's complete
frame path, not just that histogram, is compared exactly. The normalizer
counts all ADDs, source accesses, COPY and ERASE operations in the literal
record stream; no work is inferred from a reduced matrix rank.

## Evidence and limitations

[CERTIFICATE.json](CERTIFICATE.json) retains exact input/output hashes,
all-column results, chronological frame-path hash, emitted-record hashes,
primitive counts and integer prefix bounds. Its seven rejection controls
cover missing preparation, missing restoration, a missing recoded read,
cancelled preparation, nonzero prefix frames, a neutral target-fed-helper
pair outside the stated contract, and an unrelated A change. A positive
control inserts a cancelling helper pair: it has the correct endpoint and
must still be charged two ADDs.

[VALIDATION.json](VALIDATION.json) records local normal/optimized execution,
a relocated minimal checkout with a recompressed input, and rejection of
corrupt source data, a changed recipe and an underpriced prefix certificate.
The separate selected-record inventory/proof binding check passed as well.

The `--native` path compiles the original C++ sources and checks 900,
1,380 and 1,620 formal columns at five, nine and eleven stages. It retains
all 6/18/24 omitted-bridge controls and requires the independently computed
prefix bounds and profiles to agree. Removing a helper restoration must
also fail the actual C++ endpoint check at each stage count. The original
legality check prices the emitted ADDs, frame moves and COPY lifecycles.

This is a useful finite circuit reduction, not an exponent improvement.
Full hosted-parent reconstruction, whole-owner/finite invoices, integration
of the semantic D-prefix contract and a changed-word outer assembly remain
necessary before treating it as an admitted supplier replacement. The
all-size compiler, common-label/mutable-basis realization, whole-call
hosting, precision/tape and analytic-transfer assumptions remain inherited.
No practical multiplication speedup, full Lean proof or selected-frontier
change is claimed. See [NOTICE.md](NOTICE.md) for attribution.
