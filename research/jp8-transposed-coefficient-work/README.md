# Inverse-transpose JP8 coefficient work

**Finite historical #626 circuit construction: 32,810 fewer backward
real-component primitives; no new kappa.**

Transposing the cleared private-work circuits from
[#811](https://github.com/CrocSwap/integer-mult-bounds/pull/811) supplies their
backward companions, including varying magnitudes and numerator-changing
source reads. The complete backward count falls **257,280 -> 224,470**.
This is **13,122 beyond #751's equal-coefficient reverse-Horner saving**.
Every read, accumulation, shift and both boundary clears is charged.

| Historical #626 scalar program | Forward | Backward |
|---|---:|---:|
| Original | 257,232 | 257,280 |
| #811 forward construction alone | 224,422 | 257,280 |
| #811 plus this companion | **224,422** | **224,470** |

The backward comparator counts are independently reconstructed: 237,592
for 999 equal-magnitude blocks, 227,254 for 1,015 power-only blocks, and
224,470 for this 1,091-block class. These are arithmetic operation counts,
not timing claims. No new work register, helper, frame change, restoration
operation or recursive child is omitted from the count.

The current accepted construction at this base is **#741/#589**, with
conditional kappa **0.001661202643272239**. This deliberately scoped result
uses the historical #626 JP8 word. It neither changes the selected frontier
nor asserts transport to #741.

## Reproduce

Python 3.11+ and the standard library suffice, offline, from the repository
root:

```sh
python3 -I -B research/jp8-transposed-coefficient-work/verify.py
```

Expected final line:

```text
PASS_JP8_TRANSPOSED_WORK backward_saved=32810 blocks=1091 columns=725 controls=10
```

The command verifies source/dependency pins, reconstructs the literal
companion circuits, checks all block boundaries on arbitrary inputs, and
executes every scalar primitive in both complete candidate programs. It
checks both shear endpoints on **716 native plus nine arbitrary private
columns**, all 492 dirty helpers, private-work erasure, costs and unchanged
paid profiles. Ten controls catch missing clears, an incorrect inverse
sign, wrong order/scaling, omitted writes, frame crossing and excessive
endpoint-neutral growth. Ordinary verification is read-only.

The independent integer implementation imports neither the constructor nor
the main verifier:

```sh
python3 -I -B research/jp8-transposed-coefficient-work/independent.py
```

Expected: `PASS_INDEPENDENT_TRANSPOSED_WORK blocks=1091 columns=6776
saved=32810 controls=4`. It executes every committed backward block matrix
on an exact integer grid, checking **6,776 arbitrary block input columns**,
then replays the complete backward positive prefix recurrence with a separate
integer/dyadic representation. It also checks literal counts and four
endpoint/clearing/prefix mutations.

The unchanged original macro frame/wrapper contract has its own scratch
replay:

```sh
python3 -I -B research/jp8-transposed-coefficient-work/native_replay.py --output NEW_DIRECTORY
python3 -I -B research/jp8-transposed-coefficient-work/test_package.py
```

The first prints `PASS_UNCHANGED_JP8_NATIVE_CONTRACT columns=716 controls=25`.
It checks the pinned original macro word, not an unimplemented production
primitive-contract change. The five packaging tests check optimized Python,
relocated minimal sources, equivalent recompression, read-only execution,
source/vendor corruption, a wrong companion sign and an undercharged receipt.

`verify.py --write NEW_DIRECTORY` explicitly generates CERTIFICATE.json and
EXPECTED.json. `independent.py --write NEW_FILE` generates its receipt.
Existing outputs are not overwritten.

## Prefix caveat and full cost

Transposition does **not** preserve every isolated prefix bound. Of the
1,091 blocks, **377 have larger isolated positive prefixes**. Block
`[24875,24886)` grows from `9/2` to `20`, a factor **40/9**. A four-source
quarter-coefficient example grows from 2 to 4. These are concrete finite
counterexamples to a blanket nonincrease claim, not failures of the final
program. [PROOF.md](PROOF.md) explains the distinction.

Both complete candidate programs retain the exact inherited prefixes:
**64 bits forward and 101 bits backward**, within the existing 192-bit
allowance. The independent dyadic replay confirms the complete backward
value. This finite check is necessary; the endpoint-transposition identity
alone would not establish the prefix contract.

Keeping all **437,040 adapter allowances**, the **25,934,336 compiler charge**,
all original macros and the complete paid recursive profile, the optimistic
paired local invoice changes **11,334,342,462,720 -> 11,334,342,429,910**.
The backward-only substitution changes that invoice by just **48**, since
the original forward count then binds. These are explicit unintegrated
budget calculations. They do not constitute revised global admission or
an exponent improvement. The paid rank profile and all source geometry are
unchanged.

## Scope, sources and credit

Exact base: `c290b7b919790300e14004a75d8d24b55ca3c5b5`.
OS-random assignment seed **25** chose the complex track and, by `25 % 3`,
this mechanism among three candidates in [CLAIM.md](CLAIM.md). This is a
deterministic transformation of all 1,091 blocks from a pinned construction,
not a new coefficient search or a claim of general circuit optimality.
Its stopping rule is complete block and full-program replay.

The pending #811 dependency is pinned at
`b5c244c916dd0b30957332edad7ae7ae22b0eb9d`. Its constructor is retained
verbatim in [vendor/construct_seed31.py](vendor/construct_seed31.py), with
its SHA-256 in [SOURCES.json](SOURCES.json). No GitHub fetch or sibling PR
checkout is required. The full forward route search was completed in #811;
this package checks the new backward companion and its composition with
that forward construction.

Direct predecessors:

- Ryan Haines's #811 positive one-read forward circuits; Jeffrey Cox
  (@namredips)'s #739 power-of-two reuse; @ellipsi2's #722 equal-magnitude
  forward reuse.
- Sagar Thakrar (@thakrarsagar)'s
  [#751](https://github.com/CrocSwap/integer-mult-bounds/pull/751), pinned at
  `7a1a3a319da359ec8b6e83230a7fcf7733fac8e5`, supplies the equal-coefficient
  backward reverse-Horner predecessor. The new contribution covers varying
  magnitudes, one-read transitions and their exact complete prefix audit.
- Jeremy Kothe's #622/#623 providers and Chafik Boukhalfa's #626 owner
  allocation, retained emitter/auditor and PR514/PR433 lineage, icekylinx,
  DreamingOfClouds, Rohan Arun, eumemic and other credited predecessors.

#793's compensation permutation, #807's restored CK helper bases and
#816's CK target forests change different mechanisms. Their savings are not
combined here. The current #741 construction/review was read before choosing
the historical object. No pending code besides the explicitly pinned #811
constructor is imported.

The coefficient-work clearing interface changes from one macro to one
block. Production-emitter integration, revised typed contracts, global
invoices/admission and inherited all-size/compiler, common-label/mutable-
basis, whole-call hosting, precision/tape/recovery and analytic assumptions
remain separate. Finite exact replay is not a formal proof of the full
integer-multiplication theorem.

Contributor: **Ryan Haines (@Ryan-Haines)**, with substantial **OpenAI Codex**
assistance in research, implementation, verification and writing. No
independent human review is claimed. New and vendored material retain the
repository's **Apache-2.0** license. See [VALIDATION.md](VALIDATION.md) for
completed checks and explicit limits.
