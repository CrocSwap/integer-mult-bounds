# Sources and credit

Ali Romman (@aliromman) prepared the new proof, checker and package
with substantial OpenAI Codex assistance. New material is Apache-2.0.
No independent human or formal proof-kernel acceptance is claimed.

Ali Romman supplied the projected-star classification and mixed-case
obstruction in [PR #7762](https://github.com/CrocSwap/integer-mult-bounds/pull/7762).
Its [proof](https://github.com/aliromman/integer-mult-bounds/blob/d33fe8562c86888307cbba4a2aa92490212c8d78/research/mixed-cycle-column-obstruction/PROOF.md)
and [checker](https://github.com/aliromman/integer-mult-bounds/blob/d33fe8562c86888307cbba4a2aa92490212c8d78/research/mixed-cycle-column-obstruction/verify.py)
are retained with all source notices and inputs. All sixteen files are
byte-exact under `retained/source7762/`.

Nick Petalas (@petalas) supplied the two-prime projection and the
released mixed-cycle question in
[PR #7744](https://github.com/CrocSwap/integer-mult-bounds/pull/7744).
The [source proof and question](https://github.com/petalas/integer-mult-bounds/blob/7dc85513e8ee9b771a5856f027cf199936f85af0/research/two-prime-column-completion/README.md)
and [prime-power arithmetic](https://github.com/petalas/integer-mult-bounds/blob/7dc85513e8ee9b771a5856f027cf199936f85af0/research/two-prime-column-completion/verify.py)
remain unchanged. The new checker reuses that arithmetic. The source
also retains Nick's completion theorem and its credit to David Ganz;
those notices remain intact. Completion is not needed for the new
rectangular argument, but its source check is still replayed.

T. Y. Lam and K. H. Leung supplied the classical cycle theorem in
[On Vanishing Sums of Roots of Unity, Theorem 3.3 and Corollary 3.4](https://arxiv.org/pdf/math/9511209#page=7).
The classical quadratic-subfield fact is stated and proved in
[Romyar Sharifi's Algebraic Number Theory, Lemma 3.2.2](https://www.math.ucla.edu/~sharifi/notes/algnum-ch03.html).
The new result applies these facts to the rectangular rank defect,
then excludes equality through row orthogonality. No global
literature-priority claim is made.

`SOURCE-PINS.json` authenticates retained bytes. `SOURCES.json` records
canonical main provenance. A source pin does not assert ancestry.
