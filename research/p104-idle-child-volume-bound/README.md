# One-child volume bound for a signed Type-B idle pair

The fixed Type-B idle events 1339 and 2324 of #7113 have signed ranks
9 and 64 on each of their eight corresponding ports. A canonical
rank-73 child with arbitrary linear setup and extraction needs volume
at least `266287972320/206158430209` times one field under the relaxed
parity-scalar erased-child contract. The complete #7277 invoice can
afford at most approximately 1.001365082990607 times one field at the
incumbent crossing upper. The directed raw margin upper is
approximately −166.904940310003. **NO VERIFIED GAIN.** Conditional κ
change is 0%.

## Scope and evidence

The proof computes exact signed phase multiplicities and bounds the
displacement rank when the child is erased. It treats both an independent
translation on each field and the larger class that also allows two
arbitrary parity scalars per field. The closed multiplicity formula
applies at every positive integer tensor width of the repeated phase
cores. A supplementary invariant-subspace argument rules out a twofold
carrier at width one under reversible setup, identity erased action and
full-state restoration in both runs.

The exact volume price grants free incremental setup, routing, ordinary
work, precision, tape and restoration. The rest of the complete signed
caller remains charged. The scope is one fixed caller pair, repeated on
eight corresponding ports. All eight signed layouts and three directed
price probes are covered. [Written proof](PROOF.md) [Exact receipt](AUDIT.json)

## Replay

From a clean checkout with CPython 3.12 and assertions enabled:

```sh
python3.12 -B scripts/research_package.py --package research/p104-idle-child-volume-bound
```

The standalone replay also works without Git or network from a verified
package export:

```sh
python3.12 -I -B research/p104-idle-child-volume-bound/verify.py
```

It authenticates the bundled literal caller, frozen complete invoice and
two inherited physical binding files by their Git blob IDs and
uncompressed SHA-256 hashes. It reconstructs the pair windows, checks the
bundled eight-port projection, verifies all eight layouts, tests five
tensor widths per signed rank, checks 126 small signed patterns, and
reprices the complete histogram with directed rational bounds. The
width-uniform conclusion uses the written phase identity. The full
predecessor physical and compiler replays are separate.

To regenerate and authenticate the port projection directly against
the exact public native word, run this from the checkout or export root:

```sh
(
set -e
word=$(mktemp)
trap 'rm -f "$word"' EXIT
curl -fsSL https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/ed090b57ed88f8859e5ff4643645099e6ba856ea/research/p104-terminal-cut-rechart/WORD.json.gz -o "$word"
python3.12 -I -B research/p104-idle-child-volume-bound/verify.py --word "$word"
)
```

The same receipt is expected. Both forms check immutable inputs, and
the optional command additionally reproduces the projection from the
whole original word. [Source manifest](PROVENANCE.json)

## Open next questions

Can a field-mixing erased-child map reduce the displacement for these two
signed fields? First find or exclude one exact candidate under the same
affordable carrier and signed phase contract. A survivor needs arbitrary-input
forward and adjoint verification, restored ownership, precision, tape and a
fully charged invoice. Another canonical pair or a different rank or volume
tariff has a separate price test.

## Credit

#7113 supplies the literal caller and signed physical binding. #7277 and
#7274/#7244 supply the complete comparable invoice and retained native
construction. #7166 supplies the related rectangular-adapter argument,
#7163 the no-child rank method for BIT reflections, and #1920/#1924 the
related reciprocal and clean-invariant Clifford encoding contracts.
#7144 proves the related fixed-caller gauge obstruction and #7295 bounds
the complete fixed-contact rank-additive stock. This proof adds a volume
lower bound for one exact complex pair and compares it with the signed
incumbent price. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
[#7166](https://github.com/CrocSwap/integer-mult-bounds/pull/7166)
[#7163](https://github.com/CrocSwap/integer-mult-bounds/pull/7163)
[#1920](https://github.com/CrocSwap/integer-mult-bounds/pull/1920)
[#1924](https://github.com/CrocSwap/integer-mult-bounds/pull/1924)
[#7144](https://github.com/CrocSwap/integer-mult-bounds/pull/7144)
[#7295](https://github.com/CrocSwap/integer-mult-bounds/pull/7295)

OpenAI Codex and subagents materially assisted the proof, implementation,
independent audit and packaging. Apache-2.0. [Notice](NOTICE)
