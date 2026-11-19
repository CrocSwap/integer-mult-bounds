# Sources and credit

Ali Romman (@aliromman) prepared the complete finite capacity proof,
checker and package with substantial OpenAI Codex assistance.
New material is Apache-2.0. No independent human or formal
proof-kernel acceptance is claimed.

Ali Romman's [PR #7768](https://github.com/CrocSwap/integer-mult-bounds/pull/7768)
supplied the [general strict defect bound](https://github.com/aliromman/integer-mult-bounds/blob/fefebaf8285f3c46f75a815657acbf48780763fb/research/mixed-cycle-column-defect/PROOF.md)
and [open attainment question](https://github.com/aliromman/integer-mult-bounds/blob/fefebaf8285f3c46f75a815657acbf48780763fb/research/mixed-cycle-column-defect/README.md).
Three source notes are retained unchanged. This is motivation for the
finite task; the new capacity proof does not use its spectral bound.

Ali Romman's [PR #7762](https://github.com/CrocSwap/integer-mult-bounds/pull/7762)
supplied the [projected-star proof and full eight-root census](https://github.com/aliromman/integer-mult-bounds/blob/d33fe8562c86888307cbba4a2aa92490212c8d78/research/mixed-cycle-column-obstruction/PROOF.md)
and [unchanged checker](https://github.com/aliromman/integer-mult-bounds/blob/d33fe8562c86888307cbba4a2aa92490212c8d78/research/mixed-cycle-column-obstruction/verify.py).
All sixteen package files remain byte-exact under `retained/source7762/`.
The finite census supplies the pair-normalization input.

Nick Petalas (@petalas) supplied the two-prime projection and original
mixed-cycle question in [PR #7744](https://github.com/CrocSwap/integer-mult-bounds/pull/7744).
Its [proof and question](https://github.com/petalas/integer-mult-bounds/blob/7dc85513e8ee9b771a5856f027cf199936f85af0/research/two-prime-column-completion/README.md)
and [checker](https://github.com/petalas/integer-mult-bounds/blob/7dc85513e8ee9b771a5856f027cf199936f85af0/research/two-prime-column-completion/verify.py)
remain in the source closure and replay unchanged. All predecessor
notices, including the earlier completion work and David Ganz's
atlas credit, remain intact.

The source credits T. Y. Lam and K. H. Leung for the classical
vanishing-cycle theorem. The present fixed-alphabet proof can use the
complete finite census instead. No global literature-priority claim
is made. Source commits are content pins, not claims of ancestry.
`SOURCE-PINS.json` authenticates all nineteen retained files.
