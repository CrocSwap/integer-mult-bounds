# Rank-eight helper split on the exact #7108 word

The input is the #7108 normalized native word with canonical SHA-256 `34085a6c502ac07530001bdcbc85ad0ec9637f5dda28c9593a0b0d6dd6613d24`. It has 71,238 events, 1,481 public fields and 51 owned labels. The independent `cut.py` replay authenticates that payload and derives the exact transferred split at source cut 37412. This is the rank-eight helper split from the #7107 authors, applying Ali Romman's helper-split construction with the retained owned-label convention. [Pinned #7107 witness](https://github.com/dillona/integer-mult-bounds/blob/5b59588fbf54c392dfb90aa4a7e7e60f0c41c351/research/p104-rank8-retimed-split/WITNESS.json), [retiming emitter](https://github.com/dillona/integer-mult-bounds/blob/5b59588fbf54c392dfb90aa4a7e7e60f0c41c351/research/p104-rank8-retimed-split/construct.py), [split emitter](https://github.com/dillona/integer-mult-bounds/blob/5b59588fbf54c392dfb90aa4a7e7e60f0c41c351/research/p104-rank8-retimed-split/split.py)

## Literal changes

All indices refer to the #7108 source word. Its only contact with role 533 in [37403,39691) is the public MOVE 3→747 at 38784. Move that paid contact to cut 37412 and divide it into 3→745 and 745→747. Both chart paths strictly nest. The cut basis sits between the two new moves. At the raw cut, roles 843, 1454 and 1468 are already in chart 745, and the first new move puts role 533 there. Role 1251 is in chart 747 at that cut and does not occur in the cut basis.

The retained pivot is 1468. Append the fresh helper role 1481, increase all old owned role labels by one, set the retained pivot's final chart to 745 and give the new role initial/final charts 745/245. Prepend the inverse input basis at chart 3, then apply the cut basis J and its inverse rebound onto the successor at chart 745. Rename role 1468 to 1481 at exactly seven source suffix contacts, 38770, 38771, 38772, 40911, 40914, 42636 and 42638. Finish with the rebound output basis at chart 245. The receipt lists every inserted and rebound event.

The canonical result has SHA-256 `db9b86eba69ca556be5abc1eb85292566fc065ddebad9a26b2da0475f22aec6b`, 71,253 events and 1,482 public fields. The audit checks each chart argument, all 155 owned-motion events under the label shift, and seven affected endpoint rows. Per LOCAL the paid delta is +2 at rank three and −1 at rank six. The productive delta is +1 each at ranks three and five and −1 at rank eight. The complete signed gain is positive for 0<κ<1 by strict concavity of x^(1−κ).

## Full-domain normalized map

Let P and S be the normalized scalar prefix and suffix at the intermediate cut after retiming role 533. A MOVE is the identity in normalized coordinates. The moved contacts are isolated throughout the stated interval, so the retiming leaves the old full normalized map T=SP unchanged. Every scalar operation in each basis takes place at one chart. The exact backward row and forward column checks give

```
a = e533* − 2 e1454*
b = e533 + e1468 − e843
c = e533* + 4 e1251* + e1468* − 2 e1454*
d = e1468

a P = c
S b = d
a b = c d = 1
```

These are full vectors, including all public coordinates and the owned-label state. The suffix direction at the earlier split's cut 43039 has zero entries at roles 843, 1123 and 1480 and entry one at 1468. The two split operations therefore introduce no conflicting cargo at that cut.

Write p=1468, and let G be the boundary basis with pivot row c and Gd=e_p. Let J have pivot row a and Jb=e_p. The explicit ADD lists satisfy these identities. For the old full endpoint, the audit also checks e_p*T=e_p*, T e_p=e_p and αT=α with α=c−e_p*. Since G=I+e_pα, these identities give GT=TG on the full normalized state.

For arbitrary old public input x and fresh scalar z, with the owned state initially zero, the state just after J is JP G^-1 x. Its pivot coordinate is cG^-1x=x_p. Freeze that coordinate as the retained output. Replacing it by z for the rebound suffix adds (z−x_p)b after J^-1. The output basis and suffix therefore produce

```
G S (P G^-1 x + (z−x_p)b)
  = T x + (z−x_p)e_p .
```

Thus the retained pivot returns x_p at chart 745, the successor returns the independent input z at chart 245, and every old nonpivot output is unchanged. The suffix correction has no owned component. The calculation is coordinatewise in the normalized chart columns, so it applies to all columns under the retained exact child and native all-column contracts. Physical Clifford, complete invoice, compiler and outer gate verification are separate from this cut audit.

## Replay

Run the registered package from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/signed-rank9-rank8-split
```

The verifier reruns the independent cut emitter against the
reconstructed #7108 source and compares its exact CUT.json.

Prior CrocSwap native, caller and rank-eight helper work supplies the inputs. Codex assisted the independent transfer audit and proof.
