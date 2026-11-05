# Review: from the literal certificate to a minimal ordered-coin controller

**Verdict: no material gap found on the actual generated graph/certificate path.** Nick Petalas’s PR #6124 checks are sufficient for the claimed behavioral quotient and for interpreting its finite partition as a minimum of reachable pending residual states in the stated model. This review independently explains the implication of those checks. The quotient, numerical partition, 22,482 internal states, 84,578-byte payload and finite control outcomes remain the source author’s results, without a fresh numerical replay.

The exact source head is `9ae1d82f4e248dd830e32c4d2a0330b62cddc1dd`. Its proof, dispatcher and validator blobs are respectively `346ae141ac82ea807b3a0863932766ba4d23280a`, `2e00e0bfd034e1e3804be1735932c884a1fbae72` and `e78ac558f4c8f932da14ab2a4890ad7dfaf75f32`. They match canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. See the exact inert copies and [SOURCE-PINS.json](SOURCE-PINS.json).

## 1. Actual domain and the proposition being checked

`pair_graph(a,b)` requires genuine integers in `1..12` and reconstructs the predecessor’s ordered graph. Its increasing leaf list is the first-negative subtraction rule of zxv’s PR #6072: each binary digit allocates one ordered output, then the surviving child rank is reduced by the length of that list. The source’s 312-state per-pair specification and sampling law are inherited; this review does not recount or reprove the numeric catalogue.

`disjoint_bank` constructs the 144 configurations in lexicographic order, with disjoint pending states, shared ordered outputs `00,01,10,11`, and a complete entry tuple. Four absorbing output rows complete the proof graph. The implementation’s `validate_graph` checks genuine integer in-range binary targets and those terminal rows. `minimize` checks pending roots and starts from exactly five observations: pending, then the four distinct outputs.

The claim concerns the same deterministic function of every ordered future coin tape, including its **first stopping depth**. A parameter selects an entry; after entry, every behavior-relevant residual datum must be counted as state. Retained parameters, clocks, histories, cursors, entropy and tape-position information cannot silently act as free selectors. This is stronger than equality of probability laws and narrower than a general physical-memory theorem.

## 2. Why the actual refinement is monotone without an own-color field

For a finite graph with observation `o` and transitions `δ(s,b)`, let `R_h` identify states whose observations agree after every word of length at most `h`. The source initializes `R_0` by observation. Its next signature is precisely

```text
(o(s), color_h(δ(s,0)), color_h(δ(s,1))).
```

Induction on `h` shows that equal signatures characterize `R_(h+1)`: the immediate observation handles the empty word, and the two successor classes handle every nonempty word. Therefore `R_(h+1)` refines `R_h`, even though the previous own-color is absent from the signature. This conclusion depends on the observation start and the complete history; it is false for arbitrary initial colors.

On the same finite state domain, a proper refinement strictly increases the number of nonempty classes. Equal consecutive **actual class counts** therefore imply equal relations. Numeric color IDs may change without changing that relation. Since the refinement operator depends only on the relation, this is a genuine fixed point; all later refinements agree. Conversely, states separated by any recorded round already have a finite distinguishing continuation.

`refine` appends exactly one integer color per original state and interns each distinct signature once. Pending states are enumerated first. Their observation zero cannot equal a terminal signature; the four terminal observations are distinct and enumerated last. Consequently each new coloring assigns consecutive pending codes followed by the four terminal codes in the original order. This justifies the actual final-four convention used by quotient construction and packing.

The implementation’s 16-round cap is an explicit error boundary for this bounded constructor. It is not a theorem that arbitrary graphs stabilize within 16 rounds. The source’s depth-nine/confirmation-ten history remains inherited finite evidence here.

## 3. The separately sorted validator needs its global gate

`partition_certificate` starts by checking the exact empty-observation coloring. For each round it recomputes every state’s signature, sorts all original state indices by signature, and checks adjacent pairs for the biconditional

```text
equal signatures  iff  equal proposed new colors.
```

Within an equal-signature block, adjacent equality forces the proposed color to be constant. Between adjacent distinct blocks, colors must differ. That local test alone would still allow nonadjacent reuse: three distinct blocks `A < B < C` colored `0,1,0` pass adjacent inequality.

The actual separate check `len(set(after)) == len(set(signatures))` closes the gap. The constant block-colors define a surjection from signature blocks onto the colors actually used. Equal finite cardinalities make it a bijection. Thus **every** pair of states has the same new color exactly when it has the same signature. This proves each history row is the actual Moore step, rather than merely a locally plausible split. Final-row equality with `mapping` and equal final consecutive class counts bind the certified fixed relation to the installed map.

The count must refer to actual used colors on the complete state domain. A declared count or `max(ID)+1` would not suffice when IDs are unused. Likewise, the proof needs exactly one color per original state in every history row. The actual `refine` producer guarantees those lengths and genuine integer values; this low-level validator does not independently admit all possible hostile Python history packets. The audit covers the internally generated path, without claiming a new arbitrary-packet parser.

## 4. The complete homomorphism proves first stopping and nontermination

`minimize` installs the translated target row for every source state and requires all members of a class to propose the same quotient row. Every color occurs; no quotient row remains unfilled. `quotient_certificate` then checks all of the following against the actual generated objects:

- a map on every original state, with range exactly all quotient identifiers;
- each ordered terminal label mapped to its corresponding quotient terminal;
- every pending state mapped to a pending state;
- all configured entries equal the images of their original roots;
- both edges of every original state commute with the map, including artificial terminal loops.

Induction on word length gives `map(δ*(s,w)) = δ̄*(map(s),w)`. Terminal and pending observations therefore agree at **every prefix** of every finite word. If one execution first stops with output `i` after `h` bits, both are pending at every shorter prefix and both first return `i` at `h`. If a finite tape ends first, both remain unresolved with the same consumed length.

For each infinite tape, either some finite prefix first stops, identically on both sides, or every finite prefix remains pending on both sides. Thus the same set of infinite tapes is nonterminating pointwise, including possible measure-zero paths. No probabilistic argument or finite sample of tapes is used for this conclusion.

The source `run` follows exactly this first-terminal convention and uses finite bit tuples in its controls. Its initial-terminal branch implements the empty-word observation; valid entries are pending. It trusts its source-built table and binary input. The absorbing output loops extend observations for proofs; the stopped sampler does not consume further bits or store those rows in its pending transition payload.

## 5. Reachability makes the lower bound apply to actual executions

`reachable` performs complete finite discovery from the entry tuple: every new state is inserted once, the frontier has at most the graph size, and the final cardinality requires every graph state to be reached. The source checks both original and quotient graphs. An original pending state cannot be reached after passing through an absorbing output, so each counted pending residual class has a configuration and a prefix **before first stop** witnessing it.

Two different stable classes have a finite distinguishing continuation. If witness prefixes for two different pending classes reached the same complete counted state in a deterministic dispatcher realizing the same fixed functions, their behavior on every future continuation would agree, a contradiction. Hence one counted pending state is required for each reachable pending residual behavior. The source quotient realizes those behaviors and attains this lower bound, conditional on its finite partition values.

The four terminal classes are excluded from the reported internal-state minimum. A controller may emit an output and halt without retaining four mutable terminal states. A free external register storing the full residual identifier could trivialize a count of nominal control labels; it changes the counted-state premise rather than refuting the theorem. No minimum ROM bytes or physical state bits with omitted registers follows.

## 6. Packing, witnesses and finite controls have separate roles

The actual writer checks genuine integer codes and width, allocates zeroed bytes, and writes each code to its distinct little-endian fixed-width field. The reader extracts those fields. That proves generated code roundtrips; unused high padding bits remain zero under the writer. The reader does not reject arbitrary nonzero padding, so generated roundtrip equality is not arbitrary-bit corruption detection or canonical hostile-binary admission.

Given the source’s 22,482 pending states and fixed 15-bit encoding, the quoted payload calculation is `ceil(2*22482*15/8)=84308` transition bytes plus `144*15/8=270` entry bytes, totaling 84,578. This arithmetic interprets the existing source count; it is not a new partition run or byte minimum. Interpreter and header costs remain omitted on both sides.

The depth-nine witness extractor follows differing successor classes down the already certified history and checks the resulting finite tape. The named states, literal witness, complete history, packed hashes, 36,864 eight-coin comparisons and five source corruption outcomes were **not executed or recomputed** here. The complete certificate implications, rather than those finite controls, justify the all-depth statement.

## 7. Written controls, exposure and remaining obligations

Both retained first drafts provide nine written weakening controls each; they overlap and are not counted as 18 independent experiments. All are **UNEXECUTED**. Decisive examples include nonadjacent color reuse, splitting equal-signature blocks while preserving cardinality, equal-count partitions that are not refinements, wrong roots or terminal labels despite internal edge agreement, one omitted edge, unreachable padding states, finite-prefix agreement followed by later divergence, irrelevant post-stop distinctions, and uncounted residual storage. These are hand deductions about weakened checks or changed premises, not observed defects in the source.

The abstract role sealed its target-known derivation before reading current source proof/code or the code-role draft. The source-aware code role sealed separately before reading that derivation. The latter’s earlier scout and PR #6747 participation are disclosed; historical exposure is not excluded for either role. Root read the scout and source PR body before the claim, then actual source after claiming. Cross-review and the assembled exact-version check follow the seals. This is substantial OpenAI Codex assistance, without blind, human or formal-kernel acceptance.

Nick Petalas owns PR #6124’s shared quotient, certificate, packing and counts. zxv owns PR #6072’s graphs, sampling law, expected-bit optimum and sharing question, with its disclosed assistance. Moore refinement and residual distinguishability are classical. JoyboyBrian #6096/#6102 and Nick Petalas #6127 retain their distinct caller/reversal/cleanup credit. In particular, forward merging does not prove predecessor uniqueness or transfer a reversible cleanup tariff. All original source notices, license and prior native/compiler lineage remain.

The original formal/kernel gate is unmet. Complete physical selection, lookup, tape movement/freshness, owned stopping records, restoration/cleanup, invoice/error, native all-columns, owned erasure, compiler, precision/tape, analytic recovery, outer assembly and full supplier remain open obligations. No scientific source program or new mathematical checker was run; no κ/frontier/adoption or merge change is proposed.
