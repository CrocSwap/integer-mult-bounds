# Saturated headers: the sphere-braid relation and the Hurwitz classification (no κ)

**No new κ.** A saturated header is a product of `n+1` square-zero rank-one units on `n` fields equal to `-I`. This package proves
that it is the matrix image of the sphere-braid relation on a chain of transvections, that Hurwitz moves act on it linearly through the
Burau representation at `t = -1`, and that in a fixed integral frame its Hurwitz orbits are classified exactly by the mod-2 multiset of the unit
vectors. It also proves an arc law for site masks and reproduces literal Hurwitz words between the chain-nested roots and the root of #6726.

## Results (hypotheses first)

Standing hypotheses: `char != 2`; `n` even; exactly `n+1` units (`N - r = 1`, `r = n`); for path form, `q^2 = 1` with `E(q) = 0`, ordinary controls
absorbed, diagonal controls specialised at `D = 1`, target `q`-odd. Theorem 4 needs an integral frame (`Omega` integral on `Z^n`).

1. **Structure and rigidity (Theorem 1).** Every header is gauge-equivalent to one with Gram `sgn(i - j)`; the `x_t` span with the single relation
`sum (-1)^t x_t = 0`; `y_t = omega(x_t, .)` for a unique skew nondegenerate `omega` whose Gram on `x_s - x_{s+1}` is the path `A_n`; any two such headers
differ by exactly one `g in GL_n`. Hurwitz moves therefore never produce a new abstract root.
2. **Sphere relation (Proposition 2).** For the chain `tau_0..tau_{N-1}` of transvections, `tau_0...tau_{N-1}tau_{N-1}...tau_0 = -I + 2 rho e_0^*`;
for `N` odd this is `-I` on `V/rad` (equivalently `M(-1) = -M(1)`), for `N` even it is not `-I`. The Birman–Hilden theory gives the interpretation, not the identity (the
cited survey does not state the relation; the sphere braid relation is Fadell–Van Buskirk's).
3. **Path theorem (Theorem 2).** Under the standing hypotheses a path-form header has tridiagonal path Gram with `Gamma_{i,i+1} Gamma_{i+1,i} = -1` for every `i`
(no other value), after a gauge that fixes all units; conversely the chain gives a header for every even `n`. Exhaustively on `F^2` with entries in `{-1,0,1}`: 160 solutions, all of this shape.
4. **Hurwitz action (Theorem 3).** A move equals the linear action of the transvection `g_i` along `d_i = x_i - x_{i+1}`; the `g_i` satisfy the braid relations and the orbit is `rho_T(B_N) T`.
Only the two moved units change and the prefix products agree off the cut. Legality: in the sector algebra `F[q]/(q^2-1) = F x F` a conjugate of a sector unit is a sector unit; in path form
the conjugate of adjacent units has a nonzero `q`-even part (the units leave the form `I + q(rank one)`), non-adjacent units commute. "Legal" means within this algebra only, not for any compiler or supplier.
5. **Classification (Theorem 4).** In an integral frame, tuples are in one orbit **iff** the multisets `{x_t mod 2}` coincide; the number of orbits is `|Sp_n(F_2)|/(n+1)!`
(1, 6, 288 enumerated for `n = 2, 4, 6`; 130560 for `n = 8` from the formula). Headers with different frames are never connected by moves. This uses one cited theorem,
`rho(PB_{2g+1}) = Sp_{2g}(Z)[2]` (Brendle–Margalit, Theorem 3.3; their first statement is attributed to A'Campo), which is checked independently here
only at small level (orbit sizes mod 3, 4, 8 for `n = 2, 4`).
6. **Arc law (Theorem 5).** In the frame `S_n` with `x` 2-locally integral, if `M` contains the supports of both `x` and `y` and `x` has two odd coordinates `A, j`, then `M` contains one of the two cyclic arcs
from `A` to `j`; with an odd number of odd coordinates `M` is everything. Supports of `y` alone do not suffice (explicit counterexample in `PROOF.md`).
7. **Literal words.** All 40 chains `(a|b)` with `n = 4..12` have the same frame and the same mod-2 multiset. Shortest Hurwitz words: `(2|2)-(3|2)` 2 letters; `(3|2)-(1|4)` 4; `(3|3)-(5|1)`, `(3|3)-(1|5)`, `(5|5)-(7|3)` 6 each.
The root of #6726 is exactly **5 letters** from chain `(3|3)` after a signed relabeling of its fields. This is one instance; nothing here says that every retirement is a Hurwitz move.

## Corrections and limits found while reproving the statements

* The sphere relation is not in the Birman–Hilden source as such; the identity is proved directly (Proposition 2) and fails for even `N`.
* The level-2 theorem is cited to Brendle–Margalit Theorem 3.3, not to A'Campo directly (A'Campo is credited there for the first statement; his paper was not available to read).
* Only the *two* moved units are claimed to change; the claim that a site-idempotent condition is necessary and sufficient for the diagonal-control identity is not part of this package.
* The arc law needs both `x` and `y` supported in the mask.
* The closed form for the thin queries of the chain-nested family at shapes `(even|odd)` does not give a sign-Gram header (transcribed from #6833 at `51f54e3c`; `(2|1), (2|3), (4|1)` fail).
* Not covered: central `q` of order 3, non-central controls, non-uniform columns, characteristic 2, more than `n+1` units, non-integral frames, pricing of any word.

## Exact checks

| Section | Check |
|---|---|
| 1 | `P_N = -I + 2 rho e_0^*` for `N = 1..40`; radical and `M(1)+M(-1)`; four altered words fail |
| 2 | headers `n = 2..18`: product `-I`, sign Gram, alternating relations, rank-one identity, `omega` on the difference path; rigidity against chains `(3|3), (1|5), (2|2)` and the #6726 root; five-unit control |
| 3 | star to path and back for `n = 2..10`, chains and #6726; converse `N = 3..11`; exhaustive `n = 2` search; `t != -1` control |
| 4 | all moves of five roots: linear action, braid relations, locality, random words, sector versus path legality |
| 5 | orbit sizes `12, 24, 96` (n=2, mod 3, 4, 8) and `25920, 61440` (n=4, mod 3, 4); class counts `1, 6, 288`; an explicit second class |
| 6 | arc law on 83,562 vectors and on literal roots and walks; the `y`-only counterexample |
| 7 | shortest words and invariants of 40 chains; #6726 at distance 5; flat versus chain frame |

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-header-braid-classification
```

or directly (about 20 s): `python3 -I -B research/p104-header-braid-classification/verify.py`, expected marker `PASS_HEADER_BRAID_CLASSIFICATION`.
`retained/` holds an unmodified copy of the root of #6726 (zxv), pinned in `retained/SOURCE-PINS.json` and recorded in `SOURCES.json`.

## Relation to earlier work

The rank identity and window bound are #6832 (DreamingOfClouds); the chain-nested root is #6833 and its idle cover #6836 (DreamingOfClouds); the global chain ceiling and the coupling-root obstructions are
#6839 and #6840 (CubeJerry); the root compared with the chain is #6726 (zxv). None of them states the sphere-braid form, the Hurwitz classification or the arc law. Searches of open and closed pull
requests for Hurwitz, Burau, orbit, sphere braid and braid-group terms found nothing on this object. Related but different: #6817 (zhaobenny, concave Coxeter batch tariffs), merged #2738 (Coxeter root tariffs),
#6550 and #6655 (shortest words for a fixed braid or rank-two endpoint), merged #4900 (Hurwitz budget versus decoding success).

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

* Can the level-2 step (the pure braid group maps onto `Sp_n(Z)[2]`) be proved directly for the header lattice, so that Theorem 4 does not cite it? (The exact checks cover `n = 2, 4`.)
* Is there an analogue of the path theorem for a central `q` of order 3 or non-central controls, and what replaces `-1`?
* How do the two moved positions of a Hurwitz move constrain site masks when masks are commuting idempotents in constant bases?
* What are the correct thin queries of the chain-nested family for shapes `(even|odd)`?
