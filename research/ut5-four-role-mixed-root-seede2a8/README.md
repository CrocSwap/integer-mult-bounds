# Four-role UT5(Z) target needs five paid factors

**Exact scoped result; no new kappa.** In the four-register formal model below,
the fixed mixed-height endpoint has minimum paid length five. A parity character
rules out every even length, support rules out one factor, and an exact join in
the full group algebra rules out all 884,736,000 ordered three-factor words.
The five-factor coordinate word is replayed exactly. The result rules out a
40% saving for this target in this alphabet; it does not prove a general tariff.

## Model and endpoint

Let `G = UT5(Z)`, the group of 5 by 5 upper-unitriangular integer matrices,
and let `R = F2[G]` be its **full formal group algebra**. A paid factor acts on
four scalar registers by

```text
D_N(g) = I + ([g] + [1]) N,
```

where `g` is one of `g_i = I + E_{i,i+1}` or `g_i^-1 = I - E_{i,i+1}`
for `i=1,...,4`, and `N = x y^T` ranges over all binary rank-one idempotents
of size four (`x,y != 0`, `y^T x = 1`). There are 120 such `N` and 960 paid
factors. Each factor costs one. There are no free address changes, clean
registers, copies, erasures, or unpaid restoration. Equality is in
`Mat_4(R)`, so the four roles are arbitrary and dirty at input.

The target is

```text
T = diag([g1*g2], [g2], [g3], [g4]).
```

Every target entry is a distinct nonidentity group element. The address
differences `g_i - I = E_{i,i+1}` and `g_i^-1 - I = -E_{i,i+1}` have rational
rank one. Thus the chosen letters have native rank-one address differences in
the stated integer matrix model; this does not supply an implementation in a
recursive integer-multiplication construction.

## Exact minimum

The direct word uses `N=E_11` for `g1` and `g2`, then `N=E_22` for `g2`,
`N=E_33` for `g3`, and `N=E_44` for `g4`. Its five factors multiply to `T`
in the full formal algebra. The checker replays all matrix entries.

There is a homomorphism `chi : G -> C2` that sends a unitriangular matrix to
the sum modulo two of its four first-superdiagonal entries. Under the induced
ring map `F2[G] -> F2[C2]`, every allowed signed simple-root letter maps to
`z`, where `z^2=1`. Since `N` is a rank-one idempotent with trace one,
`det(I+(z+1)N) = z`. The determinant of the target is also `z`. Therefore
every realizing word has odd length. Length zero is excluded because `T != I`.
One factor is excluded because its support contains only `1` and one address,
whereas `T` has four distinct nonidentity diagonal addresses.

It remains to decide length three. For any two legal factors,

```text
D_N(g) D_M(h) = I + lambda_g N + lambda_h M + lambda_g lambda_h NM,
lambda_g = [g]+[1],       NM = x (y^T u) v^T  when M=u v^T.
```

Each entry of a two-factor product has support in `{1,g,h,gh}`. The verifier
enumerates all 960^2 ordered pairs, stores their exact 16-entry formal matrix
keys, and checks all 960 equations `A B = T C^-1`. These cover every ordered
three-factor word. The pair map has 736,361 distinct states; there are zero
matches. Every right-query formula is also checked against a direct sparse
matrix multiplication in the full group algebra. A separate tiny positive
fixture checks all 16 pair formulas against full-algebra multiplication and
finds the expected two-factor endpoint.

The parity and support obstructions leave only length three below five. Its
exhaustive rejection plus the positive five-factor word proves the exact
minimum for this fixed endpoint and alphabet. [RESULT.json](RESULT.json) stores
the deterministic transcript hashes and counts; [verify.py](verify.py)
recomputes them. The support universe is formed from exact integer group
elements needed by pair products and right queries, not from a finite quotient
or a finite-column sample.

## Cost and scope

The direct bill is five paid factors. A three-factor construction would save
two calls (40%) for this target, with no other unpaid setup or restoration
expenses in the formal model. No three-factor construction exists in this
alphabet, so there is no saving to transfer. The result does not change the
selected construction, certify a supplier, or improve a conditional
integer-multiplication exponent. It covers no other endpoint, address group,
or operation alphabet.

The selected task was `bit-new-register-model`, priority revision 4. Its
predecessors include the three-register additive model, the bounded GL3
mixed-target census (PR #1974), and UT4(F2) mixed-root tariffs (PR #2027).
The live overlap review also compared the UT5(F2) height-three target in
Discussion #1769 and the recent A4 claim in Discussion #2095. The closest
completed comparison is the five-call `F2[D8]` result in Discussion #1773:
its endpoint has three nonidentity roles and one restored identity role, with
two involutory labels in a finite group. This experiment uses the torsion-free
`UT5(Z)` group, signed rational rank-one root differences, and four active
mixed-height outputs. The equal minimum of five is recorded as a nearby result,
not presented as a new general sharing method. Claim and overlap records are
in [TASK.json](TASK.json); exact input blobs, including the D8 comparator, are
in [SOURCES.json](SOURCES.json).

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -I -B scripts/research_package.py --package research/ut5-four-role-mixed-root-seede2a8
```

The registered command checks the input SHA256 pins, replays the exact pair
join, its positive controls and the one-factor negative control, and checks
that the result receipt is deterministic. The run that produced this package
used Python 3.14.7; the full registered command is included for CI and
reproduction under the repository's Python 3.12 convention.

## Open next questions

Could another four-role target in the same `UT5(Z)` alphabet admit a paid-word
saving? A useful first case has two repeated simple-root outputs and one
height-two output. Derive its character and support constraints before a
bounded word search. This package proves no uniform family tariff and supplies
no fully charged physical supplier interface.

## Attribution

The factor normalization, rank-one idempotents, and full formal group-algebra
setting follow the prior register-model line, including PR #288. The exact
join method is standard meet-in-the-middle enumeration; this work claims no
new general algorithm for it. The contribution is the scoped UT5(Z) target,
its exact five-factor minimum, and the reproducible complete three-factor
obstruction. Prepared with substantial OpenAI Codex assistance; no independent
human review or proof-assistant verification is claimed.
