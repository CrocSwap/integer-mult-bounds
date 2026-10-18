# Source, credit, and scope

New construction code, proofs, and documentation were prepared for Ali Romman
(@aliromman) with substantial OpenAI Codex assistance using GPT-6 Astra.
The new material is under the repository's Apache-2.0 license. No independent
human review or priority claim is made.

The base is `8bddbee377e2f3ce1f1247196c4b290d55767d20`. SOURCES.json records
the source hashes and Git blobs. The only executable source copied from the
base is `vendor/clifford_exact.py`. It is retained byte for byte. It comes from
icekylinx's PR531 complex provider lineage, through PR552, PR558, and PR626. Credit
remains with those contributors and the earlier Clifford and physical compiler
work recorded in that lineage. The package uses the same exact canonical-frame
and Gaussian-dyadic phase convention.

The mathematical and construction dependencies are:

- [PR717](https://github.com/CrocSwap/integer-mult-bounds/pull/717),
  DreamingOfClouds: the complex B14 decoder model and cost-63 P111 examples.
- [PR968](https://github.com/CrocSwap/integer-mult-bounds/pull/968), head
  `6a99e7240b961ac5e115ae6aa0301ec7c4a45d77`, themilkman216, retained as
  `research/complex-frame-pair-decoders`: the root-pair explanation and exact
  eight-term puncture floor. Its proof leaves physical asymmetric-centre
  construction open. The cost-63 number and its optimality are not new here.
- [PR620](https://github.com/CrocSwap/integer-mult-bounds/pull/620),
  Joel Pulikkan / GamingPuzzled: the E8 decoder floor and coordinate decoder.
  The related binary depth-one P111 value 63 is also prior work in
  [PR757](https://github.com/CrocSwap/integer-mult-bounds/pull/757) and
  [PR761](https://github.com/CrocSwap/integer-mult-bounds/pull/761).
- `notes/general-clifford-frames.tex`, credited there to icekylinx with OpenAI
  assistance: exact frames for arbitrary binary subspaces, nested transitions,
  and dirty tail conventions.
- `notes/copied-centers-lemma.tex` and its retained Paureel copy interface:
  complete-stream copy, transform, read, and discard; one sequential temporary
  stream; a paid recursive transform on the copy.
- The selected PR942/T37 construction and its recorded predecessors supply the
  comparison exponent. No selected coefficient, profile, or supplier is changed.

## Distinct scope at review

[PR998](https://github.com/CrocSwap/integer-mult-bounds/pull/998), head
`66b777bf2b0160ed926572ff8714ac7b7bba0859`, extends the P112 single-lift floor
to complex coefficients. Its contract keeps eight coordinate readers and adds
one total. This package uses P111 and replaces one reader within eight terms.
It does not assert a counterexample to that floor.

[PR1008](https://github.com/CrocSwap/integer-mult-bounds/pull/1008), head
`5d90de8d5b7077f4078e42c08ba4872682662e5b`, checks binary P111 tensor elementary
shears. It credits the earlier depth-one value and excludes a physical supplier
or delivery program. This package concerns an executed complex depth-one word.

[PR1020](https://github.com/CrocSwap/integer-mult-bounds/pull/1020), head
`bf4ee95df4ee6e3101a88f5d015c8aa85b688b6d`, proves a cost-six root-pair
threshold at 26 punctures. It excludes a native supplier. This package keeps
the nine-line puncture and does not change that structural threshold.

PR781 concerns a coded packet kernel; PR892 concerns complete fixed packing
for a helper endpoint change; PR920 concerns a restricted frame class for parity
kernels. Those scopes do not supply this complex changed-reader word. This is a
targeted overlap check, not a claim that all possible concurrent work was read.

The first local candidate used eight nonzero COPY endpoints on P104. Their
common-target order was not resolved. That candidate was stopped. The retained
P111 construction has one nonzero endpoint and puts it last. No P104 physical
realization is claimed.
