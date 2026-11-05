# External review of the common-image subspace law

This is a written external audit of SHIN09-git's [PR6710](https://github.com/CrocSwap/integer-mult-bounds/pull/6710), exact head `465a0060fbd236a5e202619de4a45a694d44970a`. The reviewed claim is its complete-uniform-header joint law for arbitrary normalized common-image row families, including repeated or dependent rows and lists longer than the ambient dimension. The original author already supplies this theorem and stronger sign results. This package adds independent written verification; it does not claim a new all-field law or count.

The domain is every finite field, `m>=2`, nonzero `u`, and a nonempty row list `V` satisfying `Vu=t=(1,...,1)`, with rank `r<=m` and fixed coordinate image `S=im(V)`. Each event requires every proper leading principal minor of `G(I-u*v_i)G^-1` to be nonzero, under complete uniform `GL_m` headers. The image vector is fixed before taking the header orbit; this is not a projective-line count.

## Evidence and reproduction

Read [REVIEW.md](REVIEW.md), the separately authored [review notes](reviews/), and the inert [source proof](inputs/PROOF.md). Coverage is its orbit/denominator, safe-prefix span-contained count and subspace-inversion law. Later pencil signs, full flats, small-field classification, independent-triple inequalities, fixed-determinant transfer and all source implementation/censuses are outside this review, even though the complete source text is retained.

[SOURCE-PINS.json](SOURCE-PINS.json) records four exact source objects. [SOURCE-TREE-CUSTODY.json](SOURCE-TREE-CUSTODY.json) binds their original head/path/modes through the remote commit/tree chain; [SOURCES.json](SOURCES.json) records eight canonical-main guidance pins. Pending-source copies are not falsely claimed as canonical ancestry. No scientific program or source checker was executed, and there is no scientific VERIFY hook. [VALIDATION.md](VALIDATION.md) distinguishes the written argument, source exposure, metadata/byte/export checks and any later hosted helper outcome.

The proposed all-field extension was rejected during overlap because PR6710 already covers it. A coordinator independent-row sketch was sealed before reading the source proof/code, after related prior work and the source PR body; it honestly records exploratory reasoning before the public claim. One proof role receives the proposition but not the source proof before sealing; another is source-aware. This is not blind, human or proof-kernel acceptance. [TASK.json](TASK.json) records changed formal-interface scope and its unmet original kernel gate.

## Open next questions

- Can the exact tuple orbit, safe-state transfer and interval inversion be certified by a proof kernel? This would add a different kind of evidence. Begin with the fixed-vector fiber and then separate contained-span counting from inversion. No kernel environment or proof development is supplied here.
- Which complete physical header domain and invoice does an actual caller provide? A complete uniform GL probability need not transfer to restricted headers or runtime. Start with the literal producer, sampling/selection, owner/restoration and complete costs; those interfaces are not supplied by this count-law review.

## Credit and limits

SHIN09-git/PR6710 supplies the arbitrary-dependency law and sign classification, with substantial disclosed Codex assistance. This account's prior PR6701 binary family and PR6703 all-field pair sign are predecessors, not recounted results. Nick Petalas4227/4807 supplies marginal/pair laws and6694 the related continuation; unpaidmoon6515 and the retained Ryanson Jonathan4607/4599/5146, Cinna Davis/source527/commdata2338/Jose Manuel/normalizer/compiler lineage retain their attribution. Rank-one determinants, orbit-stabilizer and subspace-lattice Möbius inversion are classical methods.

ToikY prepared this review with substantial source-aware OpenAI Codex assistance and separate proof/adversarial/metadata roles. Original [source NOTICE](inputs/NOTICE), [license](inputs/source/LICENSE), headers and [review attribution](NOTICE.md) are retained. All native, ownership/erasure, compiler, precision/tape, analytic/outer and selected framework obligations remain. No supplier, physical speedup, multiplication theorem, κ/frontier/adoption change or merge is established.
