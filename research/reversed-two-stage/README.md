# Reversed two-stage boundary basis

This focused increment is based on [PR33](https://github.com/CrocSwap/integer-mult-bounds/pull/33)
at its scientific commit e0399d0e1a222bebf72e44ad374004bbcb7f2c64, which already
contains the standard width43/37 data blocks. Its new geometry and conditional assembly have separate independent acceptance, giving

$$
\kappa=\frac{1639226629}{10^{14}}=1.639226629\times10^{-5},\qquad
T(n)=O\!\left(n(\log n)^{1-\kappa}\right).
$$

The ordered factors become $(45,47)$. A new compatible common boundary basis
changes the data profile from eleven singleton children plus widths43,37,1933
to nine singletons plus widths43,39,1933. All other histogram entries, role
count, rank mass, maximum child and paid endpoint correction are retained.
The bit saving is $1639253501/10^{14}$; the unchanged complex saving is $18/10^6$.
The composition uses $\beta=1/20$, the actual semantic guard and product stock
$p^{47000}$. No separate producer improvement is included.

Relative to the pinned PR33 witness $1638103206/10^{14}$, the gain is
$1123423/10^{14}$. The older 91-singleton checkpoint is not the comparison base.
These are asymptotic exponent savings, with no practical speedup or unconditional
whole-machine/Lean claim. Current-record status is not asserted.

- [Geometric proof](GEOMETRY_PROOF.md)
- [Conditional assembly](ASSEMBLY_PROOF.md)
- [Exact selected geometry](REVERSED_45_CERTIFICATE.json)
- [Exact arithmetic certificate](ASSEMBLY_CERTIFICATE.json)
- [Review and remaining hypotheses](REVIEW.md)
- [Source hashes and pins](SOURCE_MANIFEST.json)

## Reproduction

Use a scratch copy of this branch. From this directory:

    python3 -m unittest test_package.py -v
    python3 certify_reversed.py
    python3 independent_controls.py
    python3 check_author_data.py
    python3 check_negative_controls.py
    python3 reproduce.py --source-root ../..
    python3 check_assembly_independent.py --source-root ../.. --author-certificate ASSEMBLY_CERTIFICATE.json

The optional h53 certificate is also included and can be reconstructed with
`python3 certify_reversed.py --h 53 --output REVERSED_53_CERTIFICATE.json`.
The adapter copies ten exactly pinned native input files into temporary storage
and invokes the byte-identical author checker. It executes no predecessor
program. `--prepare-only EMPTY_DIRECTORY` verifies this packaging without
running scientific calculations. Raw logs and private review records are omitted.

## Exact base and later correction

PR33 subsequently corrected a display typo in the standard row-label sequence:
its final label is 44, not 43. The note's hash and generated patch were updated;
the numerical data, graphs and hypotheses did not change. A later commit added
validation only. This increment remains based on e039 and uses its exact pinned
bytes; its own reversed basis supplies all 91 labels explicitly. See
[the correction](https://github.com/DominikScholz/integer-mult-bounds/commit/301c0d0a2117c62742bb74b532b5ac84ac4c03a5).

## Attribution

Dominik Scholz supplies PR33's selected producer dimensions and standard43/37
composition. Rohan Arun supplies PR31's rank-partition data-corner method;
Zhihao Chen (jacklightChen) supplies PR29 and PR21/23 interfaces; Aurel Prosz
(Paureel) supplies the two-stage topology and paid correction, with Swapnil Jain's
linked development retained. icekylinx supplies the producers and controlled
basis; RaD/hipotures supplies the semantic/balanced/routing/phase-cell/bulk
mechanisms. eumemic, Douglas Colkitt, OpenAI, Harvey–van der Hoeven and all earlier
contributors, licenses and recorded assistance remain credited. The new reversed
boundary family and this explicit composition were prepared with OpenAI assistance.
