# Free address twists: one-sided twists keep the nine-call floor

**Scoped written proof with exact finite corroboration, plus a relaxation
barrier. No new κ, no supplier and no native implementation.**

## Changed hypothesis

[The three-register bound](../bit-three-register-lower-bound/README.md)
(Ali Romman, #468) excludes free address maps between paid calls. So do its
dirty-workspace, clean-ancilla and odd-denominator successors. This package
allows them.

Between calls, any role may be relabelled by an additive automorphism
$B\mapsto PBQ$ of the address group, with $P,Q\in GL_m(\mathbb Z_{(2)})$.
These relabellings are free. Binary XOR mixing and any number of restored dirty
roles are also free. Paid calls are unchanged: $D_N([A])$ with rational
rank-one $A$ and binary rank-one idempotent $N$. Conjugating an XOR by a twist
gives the twisted XOR $f_r\mathrel{+}=\varphi(f_s)$. Operators therefore lie
in matrices over the skew group ring
$\mathbb F_2[M_m(\mathbb Q)]\rtimes G$, a nonabelian operation family.

Counted roles: $W$ data roles with diagonal targets $[C_s]$ and any number of
dirty helpers restored to $1$. Every paid call counts, including any call that
acts only on a helper. Twists and XORs cost nothing in this formal model.

## Result

**Theorem A (uniform, [PROOF.md](PROOF.md) §3).** Assume every paid frame
lies in $M_m(\mathbb Z_{(2)})$. Assume also that every twist reduces modulo
two to a one-sided map: $X\mapsto\bar PX$ for all twists, or
$X\mapsto X\bar Q$ for all twists. Then every exact word needs at least
$\sum_s\operatorname{rank}_{\mathbb F_2}(C_s\bmod 2)$ paid calls. This holds
for any number of dirty helpers. For three targets invertible modulo two,
such as $I$, $I+E_{10}$ and $I+E_{21}$, the bound is nine. The direct word
attains it, so nine is exact.

The proof uses the square-zero homomorphism $[A]\mapsto(1,A\bmod 2)$ of
#2110 (1337isnot1337 / Cinna Davis). The twists are equivariant for this map.
One-sidedness then keeps every call's contribution rank one in a suitable
flattening.

**Proposition B (finite exact, PROOF.md §4).** Two-sided twists break this
argument. Let $\sigma$ simultaneously swap address axes $0$ and $1$, so that
$B\mapsto SBS^T$. An explicit seven-call word for
$\operatorname{diag}([I],[I],[I])$ then agrees with the target in the
complete square-zero image $M_3(\Lambda\rtimes G)$, in all $5040$ call
orders. The word has:

- one all-role call on $E_{00}$;
- three private calls on $E_{11}$, with $\sigma$ applied to the other two roles;
- three diagonal calls on $E_{22}$.

Exact products show that no order is a real identity. Therefore no square-zero
argument, including Theorem A and #2110, can prove nine once two-sided twists
are free. Whether two-sided twists can beat nine **remains open**. This
package claims neither a seven-call word nor a lower bound for that model.

Answer to the card: one explicitly specified nonabelian register model, with
one-sided address twists, does **not** escape the scoped obstruction in the
odd-denominator domain. For two-sided twists, the inexpensive obstruction
method fails. That leaves a precise open target.

## Scope limits

The result concerns formal group-algebra identities. It does not cover:

- clean ancillas;
- twists not of the form $PBQ$, such as transposition;
- even-denominator frames;
- mixtures of left-only and right-only twists.

A finite address identity is not a supplier. The physical meaning and price of
a free relabelling are not established. The random-word checks corroborate
Theorem A but do not prove it.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -B research/bit-address-twist-register-floor/verify.py
python3 scripts/research_package.py --package research/bit-address-twist-register-floor --check-only
python3.12 -B scripts/research_package.py --package research/bit-address-twist-register-floor
```

The verifier runs in about six seconds. It checks:

- the exact direct nine-call word, with zero and one dirty helpers;
- controls rejecting a deleted call and a mutated frame;
- 120 seeded random words for each of the left-only and right-only twist
  models, with mixing and helpers, where the correct flattening has rank at
  most the number of calls;
- that the opposite flattening exceeds the call count, so the side condition
  is necessary for the argument;
- all 5040 witness orders exactly, with relaxation agreement and no exact
  identity;
- controls rejecting an altered target, untwisted private calls and left-only
  private twists.

## Open next questions

1. **Can two-sided twists beat nine exactly?** If they can, the free-relabelling
   premise changes the bit primitive's paid count. Otherwise the floor extends
   to all $PBQ$ twists. A first step is to compute the order-two term, modulo
   the cube of the augmentation ideal, for the seven-call frame multiset over
   all $S_3\times S_3$ twist assignments. That gives a second-order cut or a
   candidate. A complete search is blocked by the size of the twist alphabet.
   An exact identity also needs a rank-type invariant that survives
   $\mathbb F_2[G]$ zero divisors.
2. **Is a free address relabelling legal and free in the native bit
   supplier?** Any formal saving matters only if a native layout implements a
   per-register $PBQ$ change for less than the call it saves. The first step
   is to identify which address maps the selected bit word's physical layout
   applies without paid work. That needs a native model, which this package
   does not provide.
3. **Do mixed left-only and right-only twists help?** Neither flattening
   applies directly when both kinds occur. The first step is a small exact
   relaxation search over left and right axis swaps with at most eight calls.

## Credit

The three-register model and nine-call theorem are by Ali Romman (#468), using
eumemic's model (#288 §1.2) and huxint's flag method (#203). The square-zero
method and the odd-denominator floor are by 1337isnot1337 / Cinna Davis
(#2110, `research/bit-odd-denominator-register-floor-seed16c946`). Theorem A
extends that method to address twists. The twist model, Theorem A,
Proposition B and the verifier are new here and were prepared by JoyboyBrian,
with substantial assistance from Anthropic Claude (Claude Code, Opus 5.5).
No independent human review or proof-assistant formalization is claimed.
New work is Apache-2.0.
