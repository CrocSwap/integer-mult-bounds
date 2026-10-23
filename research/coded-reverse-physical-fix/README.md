# A physical thin source and boundary for the coded reverse controller

**Verified local physical pair; conditional outer endpoint 0.0034 (+12.5% over 0.00302015).**

PR4940 consumes the center-free coded word with reverse stages carrying the code
`A` and thin forward stages mixed by scalar `A^-1`.  PR4933 realizes the same
owner transformation as the physical code

```
C_ij = A_ij K_i^-1 K_j,        C = K^-1 (A tensor I) K,
```

not as the scalar `A`.  The first backward FULL followed by the next thin shear
therefore leaves the Y-to-Y block `D(I - A^-1 C)` (PR5036).  This package gives a
changed thin source and x-boundary that make the *physical* local pair equal the
standard pair exactly.

## Local construction

Let `Q` be the actual central Gaussian on address bit 0, `D` the product of the
eight fresh-axis Gaussians on bits 1..8, and `C` the physical 112-owner code of
PR4933.  Set

```
S = Q D C^-1 Q^-1 D^-1          (thin-stage source)
R = Q C Q^-1                    (input x boundary)
L = D Q C^-1 Q^-1 D^-1          (output x boundary)
```

The backward pair is `B = [[D, -D Q C],[0,D]]` and the thin shear is
`T = [[I,0],[Q^-1 S,I]]`.  With `D Q = Q D` and `C` invertible,

```
L (T B) R = [[D, -D Q],[D Q^-1, 0]],
```

the standard pair, block by block.  The four equations are
`L D R = D`, `L D Q C = D Q`, `Q^-1 S D R = D Q^-1`, and
`D - Q^-1 S D Q C = 0`; the displayed S, R, L solve them.  This is the explicit
changed thin/boundary word left open by PR5036.

`verify.py` checks the identity on the signed physical code in two independent
ways: the copied signed-normalizer functions and a separate NumPy implementation
of `C,C^-1,Q,D,S,R,L`.  The PR5036 witness (owner 1, address 1) and random sparse
banks give zero residual on all 112 x 512 coordinates in both.  It also checks
`A A^-1=I` exactly over Q, `Q^-1 Q=I` and `D^-1 D=I` on the full 512-address
basis, and the signed `C^-1 C=I` witness.  Controls reject the literal scalar
`A^-1` thin source with the scalar boundary, the `C^-1` thin source without the
changed boundary, and the identity output boundary.

## Coded invoice

The same moment model as PR4940 reproduces the published p16 raw root
`0.0030201659770` and gives coded raw complex roots

```
p=8:  0.0079264044
p=19: 0.0075785352
```

The p19 tail guards pass at `C=0.0034` (`alpha<1`, `gamma,delta<0.97`).  The
strict outer ledger passes at `0.0033999971`; at `0.0034` the only failing
predicate is the BIT cap.  Thus the complex side stops binding and the BIT
supplier caps the conditional endpoint at **0.0034**, about **+12.5%** over
`0.00302015`.

## Cost and scope

The new S is applied at each thin stage and R/L at the controller boundary.
They are physical codes: `C`/`C^-1` conjugated by native central Gaussians
`Q`/`D`.  The added work is monomial field maps plus the scalar code, not new
recursive Gaussian jobs; the PR5036 local ledger already charges 896 wrapper
maps, three eight-mode recodings (2688 scalar ADDs, 48 clears), 112 query
copies and 112 inverse Pauli maps.  The fixed-tape field-map tariff, the
denominator 13/52 implementation and the compiler constants for ambient rank
153 remain open, as do the full p19 controller replay, all-stage bridges/IDLEs,
BIT-side admission, hosted CI and formal-kernel review.

This is a verified local physical pair and a conditional outer endpoint, not a
new selected kappa and not a complete multiplication theorem.

## Reproduce

```sh
python3 -B research/coded-reverse-physical-fix/verify.py
```

## Open next questions

1. Full p19 coded-reverse controller: lift the p=2 448x448 owner identity to the
   address-dependent S/L/R and replay every stage, bridge and IDLE on the actual
   word.
2. Fixed-tape field-map tariff for the added C/C^-1 sources and boundary,
   including the PR5036 local ledger's 896 wrapper maps and the extra
   recodings.
3. Denominator 13/52 implementation and the ambient-rank-153 compiler
   constants; BIT-side admission, hosted CI and formal-kernel review.

## Credit

PR4940 coded reverse controller: Cayden Burkart / SethBurkart123.  PR4933
signed physical normalizers and code: Dillon.  PR4929 center-free producer:
Dugongue / mdumitrean.  PR5036 physical gap: JoyboyBrian.  PR4440/4470
controller and query thinning: Cinna Davis / 1337isnot1337.  Retained native,
Clifford, ownership, compiler and precision lineage as credited in those
packages.
