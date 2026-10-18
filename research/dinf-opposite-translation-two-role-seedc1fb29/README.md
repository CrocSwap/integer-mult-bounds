# Opposite translations in the infinite dihedral two-register model

**Exact bounded minimum: four paid factors. No selected supplier or new κ.**

Let

```text
D_infinity = <r,s | r^2=s^2=1>,    t=rs,    t^-1=sr.
```

The two-register target is `diag([t],[t^-1])`. A paid factor is

```text
D_N(g) = I + ([g] + [1]) N,
g in {r,s},  N any rank-one idempotent in M_2(F_2).
```

Two independent coordinate projectors give the four-factor word

```text
D_E11(r) D_E11(s) D_E22(s) D_E22(r)
  = diag([rs],[sr]).
```

I exhaustively checked every word of length 0, 1, 2, or 3 over all twelve
factors. None equals the target in the full formal group algebra
`F_2[D_infinity]`. Thus this exact endpoint has minimum four in the stated
model. A three-call identity would save one call, or 25%, relative to the
direct word.

## Exact model and completeness

Represent a group element by `(k,e)` acting on integers as
`x -> (-1)^e x + k`. The product is

```text
(k,e)(l,f) = (k + (-1)^e l, e+f mod 2).
```

This is the faithful normal form for `Z semidirect C2`; with `r=(0,1)` and
`s=(1,1)`, both generators are reflections, `rs=(-1,0)`, and `sr=(1,0)`.
The pair representation keeps all translations distinct, so coefficient
equality is equality in the infinite group algebra, not in a finite quotient.

Every rank-one idempotent over `F_2` is `u v^T` with nonzero `u,v` and
`v^T u=1`. Enumerating these pairs gives exactly six distinct matrices in
`M_2(F_2)`. Together with the two paid labels this gives the complete
12-factor alphabet. The verifier checks all ordered words, with counts
`1, 12, 144, 1728` at lengths 0 through 3, for 1,885 products total. It also
checks the direct four-call positive control, reflection relations, translation
orientation, all idempotent equations, a wrong-label mutation, and a dropped
factor.

The verifier prints a SHA-256 digest for the ordered exact matrix products at
each length, plus the support-size histogram. These digests make the exhaustive
finite result reproducible; correctness rests on the explicit enumeration and
the faithful `Z semidirect C2` normal form.

## Scope and limits

The result is only for two arbitrary dirty registers, the two reflection
labels `{r,s}`, all rank-one idempotents in `M_2(F_2)`, and the fixed opposite
translation endpoint. It is distinct from finite D8/D16/Q8 models because no
finite-order relation identifies nonzero translations. Discussion #1884 had
listed the infinite-dihedral algebra as a broad future direction; this package
answers one target-specific word-length question and does not prove a
per-reflection bound for arbitrary register counts or powers.

There is no physical integer-multiplication supplier, κ improvement, or
complete theorem claim. The experiment stops at radius three because the
four-call direct word is already known.

## Open next questions

- **Which other fixed infinite-dihedral diagonal targets have a shorter
  reflection word than their independent-coordinate construction?** A second
  endpoint could reveal a reusable sharing mechanism. The first step is to
  choose one target with direct length at least five, state its full call
  budget, and search one small complete radius. This cycle did not extend the
  search beyond the opposite-translation endpoint.

## Reproduce

```sh
python3 -I -B research/dinf-opposite-translation-two-role-seedc1fb29/verify.py
python3 scripts/research_package.py --package research/dinf-opposite-translation-two-role-seedc1fb29 --check-only
```

Expected first line: `CERTIFICATE` with counts `[1,12,144,1728]` and zero
target hits at every length. Expected final line:
`PASS_DINF_OPPOSITE_TRANSLATION_RADIUS3 alphabet=12 words=1885 radius=3 direct=4 saving_if_found=25% ...`.
The verifier also cross-checks the semidirect-product multiplication against
reduction of alternating `r,s` words over a finite range, and compares its
parameterized idempotent list with an independent scan of all 16 matrices.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in choosing
the target, implementing the exact search, and preparing the package.
