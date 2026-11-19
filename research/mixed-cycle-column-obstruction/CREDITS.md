# Sources and credit

Ali Romman (@aliromman) prepared this proof, exact checker and package
with substantial OpenAI Codex assistance. New material is Apache-2.0.
No independent human or formal proof-kernel acceptance is claimed.

Nick Petalas (@petalas) supplied the two-prime projection and modular sign
argument, the released eight-row/fifteenth-root question, and the unchanged
fixture checker in [PR #7744](https://github.com/CrocSwap/integer-mult-bounds/pull/7744).
The retained [proof and question](https://github.com/petalas/integer-mult-bounds/blob/7dc85513e8ee9b771a5856f027cf199936f85af0/research/two-prime-column-completion/README.md)
and [checker](https://github.com/petalas/integer-mult-bounds/blob/7dc85513e8ee9b771a5856f027cf199936f85af0/research/two-prime-column-completion/verify.py)
identify the exact consumed version. All five source package files remain
byte-exact under `retained/two-prime/`.

Nick Petalas also supplied the normalized missing-column formula and the
doubled-alphabet theorem in [PR #5865](https://github.com/CrocSwap/integer-mult-bounds/pull/5865).
Its [retained proof](https://github.com/petalas/integer-mult-bounds/blob/7dc85513e8ee9b771a5856f027cf199936f85af0/research/cyclotomic-column-completion/PROOF.md)
is a dependency of Section 2. The source credits David Ganz for atlas B097
and the pilot application in [PR #2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849)
and [PR #2855](https://github.com/CrocSwap/integer-mult-bounds/pull/2855).
Those applications are credited through the retained notices; their
scientific suites are not rerun here.

T. Y. Lam and K. H. Leung supply the classical two-prime cycle decomposition
in [On Vanishing Sums of Roots of Unity, Theorem 3.3 and Corollary 3.4](https://arxiv.org/pdf/math/9511209#page=7).
The new argument uses projected Gram positivity, classifies the resulting
directed edges, removes the completion sign in the mixed case, and applies
a Hermitian trace obstruction. No global literature-priority claim is made.

Source commits are content pins, not claims of ancestry. `SOURCES.json`
records the canonical main selection and catalogue. `SOURCE-PINS.json`
authenticates all six retained source files before the source replay.
