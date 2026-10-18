# Ordered, noncommuting R420 decoder sharing

**Finite bit-circuit research; no new kappa.** Starting from Sagar Thakrar's
PR708 disjoint-pair recipe on eumemic's historical PR543 R420 word, seven
additional, fully charged helper shears reduce the nine-total decoder from
**264 to 250 XORs**. Relative to the original 321-XOR decoder, literal reverse
cleanup doubles the saving: **26,916 to 26,774 native ADDs (142 saved)**.
Only this research package is added; no selected construction is changed.

Unlike disjoint pairs or PR753's disjoint stars, this recipe contains **six
noncommuting shear pairs**. The order of both covector substitution and
restoration is essential. Two explicit order-corruption controls distinguish
this result from a repackaged commuting-star construction.

## Reproduce

From the repository root, Python 3.10+ and its standard library suffice:

```sh
python3 -B research/r420-decoder-chain/verify.py
```

Expected:

```text
PASS_R420_DECODER_CHAIN decoder=321->250 ADDs=26916->26774 columns=660 controls=8 noncommuting=6 no_new_kappa
```

The command regenerates the bounded search, compares every certificate field,
checks SHA-256 input pins, runs the unchanged original E8/frame/H1-H5 checker,
and reuses PR708's separate set-valued full-word interpreter. It checks all
660 arbitrary source, target and helper-dirt columns, not just clean inputs.
Eight negative controls are required to reject. Optimized Python is refused
because the inherited checker contains assertions.

For native nine-stage verification, with a C++17 compiler and Boost headers,
choose two fresh output directories (neither may exist):

```sh
python3 -B research/r420-decoder-chain/verify.py --output /var/tmp/decoder-chain-words
python3 -B research/r420-decoder-chain/native.py \
  /var/tmp/decoder-chain-words /var/tmp/decoder-chain-native
```

`CXX` and `BOOST_INCLUDE` may override the compiler and Boost include root.
The native wrapper is adapted from PR708, preserving its exact exporter,
COPY/ERASE/source-owner legality checks, 1,380 formal columns per word,
all nine stages and 18 omitted-bridge controls per word. It compares the
paid profile and charges the recomputed positive prefixes against the strict
104-bit budget; it does not inherit the original precision invoice.
The generated native receipt contains environment details and exact bounds.

The completed Linux replay is retained in [NATIVE.json](NATIVE.json), with
the exact command and prerequisite recovery in [VALIDATION.json](VALIDATION.json):

```text
PASS_R420_DECODER_CHAIN_NATIVE words=2 stages=9 columns=1380 controls=18/18 payload_bits=100/103
```

The candidate forward/reverse positive-prefix bounds are 219,001 and
2,932,970. Its exact local payload upper bound is
`64 * 219001^3 * 2932970^2 = 5782737910556506080751636537600`,
requiring 103 bits, strictly below 104. Both words pass the same full native
checks; the candidate does not receive a weakened precision allowance.

## Ordered construction and proof

Let the nine decoder source rows be binary covectors `r_t` on the 80
non-retained helper operands. Each elementary shear `E_i` performs
`h[a_i] <- h[a_i] XOR h[b_i]`, for distinct helpers. The preparation executes
`E_1,...,E_k` chronologically, hence its column-state matrix is
`P = E_k ... E_1`. Because each shear is an involution,
`P^-1 = E_1 ... E_k` even when the shears do not commute.

Replace each decoder row by `r_t P^-1`. To compute it, visit the shear list
**in chronological order** and toggle coefficient `b_i` whenever coefficient
`a_i` is present. Its value on the prepared state is
`r_t P^-1 P h = r_t h`. Decoder destinations are retained totals and are
excluded from all temporary operands; arbitrary incoming total dirt is
therefore also unchanged. Then restore the helpers with the shears in
**reverse chronological order**, leaving every helper exactly as received.
This proves equality of the complete A operator on arbitrary inputs.

D compensation, scatter, B, every register and frame are unchanged. C is
rebuilt as the literal reverse of the complete new A/B helper-source word,
as required by H4. Every preparation/read/restoration is at FULL. Equality
of all 660 ordered register-frame paths is independently checked, not
inferred just from endpoint equality. There are no new helper, COPY, ERASE,
source-access, frame-transition or recursive-child charges.

For one further shear `(a,b)`, the decoder read saving is the number of rows
containing both `a,b` minus the number containing `a` but not `b`. Subtract
**two** for preparation plus restoration. All seven selected shears have
net saving two. Their operands and the full 34-shear recipe are in
[CERTIFICATE.json](CERTIFICATE.json).

A concrete ordering witness is the old shear `[377,366]`, followed by the
new `[309,377]`: the second operation reads the value changed by the first.
Commuting them changes the preparation map. The other five noncommuting
pairs and both wrong-order rejection tests are recorded in the certificate.

| Complete charged scalar expense | Original | PR708 matching | Ordered chain |
|---|---:|---:|---:|
| Decoder reads | 321 | 210 | 182 |
| Preparation + restoration | 0 | 54 | 68 |
| Decoder suffix | 321 | 264 | 250 |
| Complete word, including cleanup | 26,916 | 26,802 | 26,774 |

The paid histogram remains `{1:1320, 2:1440, 4:60, 5:120, 8:9}` and rank mass
5,112. Thus the improvement is scalar circuit length, not the paid recursive
moment or a multiplication exponent. Positive scalar-word maximum row sum
increases from 144,651 to 219,001 and column sum from 40,742 to 57,518; these
bounds are recomputed and are **not** a hosted-parent invoice.

## Search, scope and controls

The OS draw was 2,323,817,007, giving assignment seed **07** and the bit-supplier
track. [CLAIM.json](CLAIM.json) records three candidate tasks and the local
claim. GitHub had no pinned issue or open issue matching `sprint`.

The search starts with PR708's unchanged 27 pairs. At each of exactly seven
accepted steps, it scores all **6,320 directed pairs** on the same 80 helpers,
allowing helpers already used in preparation. Maximum positive fully charged
saving wins; `random.Random(7)` provides deterministic tie keys in sorted
pair order. Coverage is **44,240 pair scores**, with no restarts. The cap of
seven is the stopping rule, **not** a local optimum or exhaustion theorem.
The certificate retains each census and the complete reproducible recipe.

Controls remove restoration, restore in the wrong order, omit decoder
substitution, apply substitution in the wrong order, retain scalar-valid but
nonliteral old cleanup, move preparation to frame zero, use a retained total
as temporary storage, and delete dirt compensation. The first four are also
rejected by the independent set-valued interpreter. Stale cleanup is explicitly
classified as endpoint-valid but outside H4, not as a false scalar identity.

The exact base is `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`. Its selected
conditional result is PR1042, kappa `0.001672188119205421`, with **PR589 on
PR555** as its bit supplier, not historical R420. The selected source manifest,
actual tuned-bit construction and batch1047 maintainer review were followed.
This package does not replace that supplier or claim its hosted admission.
[SOURCES.json](SOURCES.json) pins the exact replay files and predecessor heads.

### Prior and concurrent work

- **PR543**, eumemic: R420 word, original exact checker, D4 skeleton and
  interleaved mutable-source interface.
- **PR708**, Sagar Thakrar (@thakrarsagar), head
  `2ec522a466ec448f148d4355dc43b51c0ef1e0b5`: disjoint matching, source recipe,
  separate interpreter and native replay design. Those modules are reused,
  not claimed as independent new implementations here.
- **PR753**, Sagar Thakrar, head
  `2b30b63789f6d9948233fc67d9d79bca6b185c5b`: disjoint restored stars,
  decoder cost 257 and complete word 26,788. This ordered-chain result costs
  seven fewer decoder XORs but has a different order-sensitive preparation;
  no composition with PR753 is claimed.
- **PR748**, Chinmay Khaladkar: source-coset modification with larger overall
  savings but changed helper-dirt map and recomputed D. Here the complete A
  operator and D remain unchanged; no overall record is claimed.
- Dylan Crow, DreamingOfClouds, Zhihao Chen and the realization, geometry,
  hosting and assembly predecessors retain the credit recorded in
  `research/e8-bit-r420/NOTICE.md` and the selected maintainer review.

- **PR848**, head `510441077c17ad775003b22fca03a519f5330453`:
  selected R439 decoder totals have pairwise-disjoint source sets, so this
  restored-total mechanism is vacuous there. This negative result is respected:
  the changed search class here is ordered helper reuse on **historical R420**,
  not a reopened claim that sharing improves the selected copy path.

The full hosted-parent invoice, selected cold replay, outer assembly,
repository-wide suite, Lean and remote CI are outside this isolated research
addition. All-size/compiler, common-label/mutable-basis realization,
whole-call hosting, residual, precision/tape and analytic assumptions remain.
Finite symbolic/native replay is not a formal multiplication proof or an
observed integer-multiplication runtime speedup.

Prepared by **Adam Gall (@adamgall)** with substantial **OpenAI Codex
assistance** in research, implementation, proof, verification and packaging.
No independent human review is claimed. New work is Apache-2.0; all predecessor
licenses and notices are preserved.
