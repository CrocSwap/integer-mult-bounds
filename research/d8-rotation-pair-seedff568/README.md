# A noncentral D8 rotation pair still costs four calls

## Result

For the exact two-role model over the formal group algebra `F2[D8]`, the target
`diag([r],[r^-1])`, where `r=st` has order four, needs exactly four paid calls
when the only paid labels are the reflections `s,t`. Free scalar `GL2(F2)`
changes do not reduce the minimum. The direct four-call word attains the bound;
complete exact enumeration rules out every word of length zero through three.

This is a scoped target result, not a change to the selected bit supplier or a
new multiplication-exponent bound. The selected complex-side moment remains the
binding one, so no new `kappa` follows.

## Model and complete price

Write the eight elements as `r^i s^e`, with `i mod 4`, `e in {0,1}`, and
`s r = r^-1 s`. Set `t=r^-1 s`; then `s^2=t^2=1`, `st=r`, and `ts=r^-1`.
The paid alphabet is exactly

```text
F_g(N) = I + ([g] + 1) N,   g in {s,t},
```

over `F2[D8]`. Here `N=u v^T` is a rank-one idempotent on the two scalar
roles, so `u,v` are nonzero binary two-vectors and `v^T u=1`. There are six
such projectors, hence twelve paid factors. Both role inputs are arbitrary;
the exact formal matrix boundary therefore includes restoration of all
cross-role information. No extra role, address map, copy, clean state, or
unpriced operation is available.

The direct word is

```text
F_s(E11) F_t(E11) F_t(E22) F_s(E22)
  = diag([s][t], [t][s])
  = diag([r], [r^-1]).
```

Its complete paid bill is four calls. Every paid call is charged once.

## Exact minimum

Any interspersed free scalar matrices can be pushed to the right through the
paid factors by conjugating each projector: `M F_g(N) M^-1 = F_g(M N M^-1)`.
The conjugated matrix is still one of the six rank-one idempotents. Under the
augmentation `F2[D8] -> F2`, each paid factor maps to the identity and the
boundary also maps to the identity. Thus the total remaining free scalar map
must be `I`. The twelve-factor alphabet already covers every allowed sequence
with arbitrary free `GL2(F2)` changes.

The exact verifier multiplies full 2x2 matrices of eight-bit group-algebra
coefficients. It enumerates all words at each length `n=0,1,2,3`, checking
`1, 12, 144, 1728` words respectively. No product equals the target. A second
implementation in `verify.py` uses generic group-algebra and matrix
multiplication, rather than the rank-one update used by the search. It repeats
the full enumeration, confirms the direct four-call word, and checks altered
and truncated words as negative controls.

A separate rank screen shows why three calls were plausible. In the left
regular representation on eight group elements, each reflection difference
`L_g-I` has rank four, while `L_r-I` and `L_(r^-1)-I` each have rank six. The
target difference has rank twelve; one paid factor changes rank by at most
four. Subadditivity therefore forces at least three calls, but does not rule
out three. The exact coefficient search supplies that missing call: the
minimum is four.

## Relation to prior work

Merged [PR #1443](https://github.com/CrocSwap/integer-mult-bounds/pull/1443)
uses this same `F2[D8]` group, the same two reflection labels, exactly two
roles, and free `GL2(F2)` mixing. Identifying its `x,y` with `s,t` gives
`r=xy`, so its endpoint `diag([xyxy],[xyxy])` is the central target
`diag([r^2],[r^2])`. It proves an eight-call minimum for that different endpoint. This result changes the endpoint
to the noncentral order-four inverse pair and tests the shorter, four-call
bill. It does not re-run or alter PR #1443's central-target result. The related
open [PR #1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822)
uses a quaternion central-pair target; [Discussion #1738](https://github.com/CrocSwap/integer-mult-bounds/discussions/1738)
concerns a D8 central pair with a third dirty role. Scope and exact overlap
coverage are recorded in `OVERLAP.json`.

The normalization of free scalar mixing follows the prior D8 and three-register
work. The exact group law, word domain, target and rank calculation here are
specified in this package. Substantial OpenAI Codex assistance; no independent
human review is claimed.

## Reproduce

```sh
python3 -I -B research/d8-rotation-pair-seedff568/search.py
python3 -I -B research/d8-rotation-pair-seedff568/verify.py
python3 scripts/research_package.py --package research/d8-rotation-pair-seedff568 --check-only
```

The search prints the exact length census and the direct four-call witness. The
independent verifier prints:

```text
PASS_D8_ROTATION_PAIR minimum=4 lengths=[1,12,144,1728] regular_ranks=(4,6,6) positive_controls=2 negative_controls=2 no_new_kappa
```

The registered package replay requests Python 3.12. Direct verification in this
session was run with the installed Python 3.14.7; the full registered replay
could not be run because Python 3.12 is unavailable here.

## Open next questions

The result covers exactly two scalar roles, this reflection alphabet, and this
one target. It establishes no physical/compiler cost, selected supplier
admission, recursive profile change, or `kappa` improvement. It does not cover
three or more dirty roles or other group alphabets.

A natural next construction question is whether a third arbitrary dirty scalar
role can realize `diag([r],[r^-1],1)` in three reflection calls. The regular
rank screen still permits three, while the two-role exact search rules it out.
