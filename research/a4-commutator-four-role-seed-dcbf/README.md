# A four-output A4 target has no six-call implementation in the stated alphabet

**Scoped bounded negative result; no new `kappa`.** For the exact target
`diag([a],[b],[c],[d])` over the full formal algebra `F2[A4]`, the complete
240-factor rank-one alphabet has no word of length at most six. A direct
eight-call word exists. The search therefore rules out the proposed two-call
saving; it does not decide whether a seven-call word exists or establish the
exact minimum.

## Model and target

Take `a=(123)`, `b=(124)`, `c=aba^-1b^-1=(12)(34)`, and `d=ab=(13)(24)`.
Each paid call is

```text
D_N(g) = I + ([g] + [1])N,
g in {a,b}, N = xy^T in M4(F2), x,y nonzero, y^T x = 1.
```

There are 120 rank-one idempotents and 240 paid factors. The target uses all
four nontrivial outputs. Since `a` and `b` have order three, neither inverse
label is a free paid operation. In this presentation `c=abba`, so the
separate-role direct word is `a` on role 1, `b` on role 2, `abba` on role 3,
and `ab` on role 4: eight calls total. The Python replay independently
multiplies the formal matrices and checks the induced regular action on all
48 role/address basis inputs.

This is a deliberately favorable formal bill: each rank-one factor costs one;
the complete idempotent alphabet already includes arbitrary scalar mixing.
No separate helper, copy, or restoration operation is charged in this model.
Address/compiler conversion, physical source access, hosting, stream routing,
precision, recursive interfaces, and supplier admission have no established
prices here. Thus the result makes no selected-supplier or `kappa` claim.

## Exact bounded result

The `A4/V4 ~= C3` quotient character has `a -> 1`, `b -> 2`, and `c,d -> 0`
in `Z/3`. Under this character, each paid factor has determinant equal to
the character of its label. The target determinant is one, so the exact join
can compare only prefix/suffix pairs whose character exponents sum to zero.
All accepting comparisons still use the entire 4-by-4 matrix of 12-bit
coefficient masks; the character is only a necessary-condition screen.

The C++ search stores every right product of lengths zero through three,
deduplicated only when its full coefficient matrix and quotient class agree.
It then checks every left prefix of lengths zero through three against the
required exact complement `L^-1 T`. This covers every word of length at most
six. The run reports:

| Evidence | Count |
|---|---:|
| Raw right prefixes, lengths 0 through 3 | 13,881,841 |
| Distinct exact right states after deduplication | 6,697,991 |
| Left prefixes checked, lengths 0 through 3 | 13,881,841 |
| Complete search outcome | no target word through length 6 |

The direct eight-call target and a planted six-call word pass exact controls.
The direct word fails if any one of its eight calls is omitted; the verifier
also rejects a missing fourth output and a mutated fourth label. The earlier
three-output A4 target had its own six-call direct word `a,b,abba`; it yields
no saving and is not counted as a construction here.

## Scope and attribution

The selector assigned `bit-mechanisms / bit-new-register-model`, seed
`dcbf94d85fe6d264c5345f44ec8ac7ce`, priority revision 4, exact base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The selected-record SHA-256 is
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
The local task card records the selector and refined scope keys, cost screen,
and live claim in [TASK.json](TASK.json); exact source pins are in
[SOURCES.json](SOURCES.json).

The nearest completed nonabelian register studies include the S3 two-target
census [PR #1870](https://github.com/CrocSwap/integer-mult-bounds/pull/1870)
(head `538d194e69420a6a773612e0b5ad0c94575f8aaa`), the binary-tetrahedral mixed triple
[PR #2010](https://github.com/CrocSwap/integer-mult-bounds/pull/2010)
(head `125ed77d114e0db0cb2c684494c7a5c90f559d60`), and the D16 central pair
[PR #1821](https://github.com/CrocSwap/integer-mult-bounds/pull/1821)
(head `a986127fa82b680a5bbb29f49fec4c8c3a944bde`). This package changes the
group to A4 and studies a four-role heterogeneous commutator/product endpoint.
It imports no predecessor code and makes no novelty claim for meet-in-the-
middle search itself. Recent nearby results use other objects and endpoints:
the completed four-role S3 target `diag([z],[z],[s],[t])` in Discussion #2023
has exact minimum eight; merged [PR #1777](https://github.com/CrocSwap/integer-mult-bounds/pull/1777)
finds minimum five for a D8 reflection/order-four target; and the free-group
two-role commutator handoff in Discussion #1997 was released after its relation
to the infinite-dihedral tariff in PR #1911 was identified. The UT5 four-role
claim #2094 has the adjacent exact result in open PR #2103. Open PR #2069 is a
Dic3 diagonal census; open PR #2085 is a rational-frame floor on four roles.
Cycle 22 in Discussion #2091 adds a rational rank-one frame to an additive
four-role target; its claim explicitly distinguishes that task from this
finite A4 endpoint. These overlaps change the comparison set, not the object
or result proved here.

## Reproduce

From the repository root, with Python 3 and `g++` available:

```sh
python3 -I -B research/a4-commutator-four-role-seed-dcbf/verify.py
python3 scripts/research_package.py --package research/a4-commutator-four-role-seed-dcbf --check-only
```

The verifier compiles with `-std=c++17 -O3 -Wall -Wextra -Werror`, independently
replays the direct word, then runs the complete bounded join. Expected search
status is `PASS_A4_NO_WORD_THROUGH_SIX`; the positive controls and complete
prefix counts are printed. Local execution used Python 3.14.7 and g++ 16.2.0.
The generic package runner requests Python 3.12; it was not available locally.

## Open next questions

Does a seven-call word realize this four-output target? A one-call saving
would still change the formal paid bill and would identify whether the failed
six-call target was only just outside the reachable boundary. A first step is
to derive sharper quotient and support constraints for a 4+3 exact join, then
estimate state counts before allocating the larger search. A naive radius-four
side has over three billion raw words, and no mapping of this A4 alphabet to
the selected physical supplier is established.

## Credit

Prepared for Cinna Davis with substantial OpenAI Codex assistance in scope
selection, derivation, implementation, exact replay, and writing. No
independent human review is claimed. Apache-2.0.
