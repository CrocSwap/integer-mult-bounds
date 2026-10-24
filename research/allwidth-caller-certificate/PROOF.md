# A lifting lemma and its certificate for the selected caller

Mark (Matarener), with substantial Claude Code assistance. Apache-2.0. No new κ.

## 1. Setting

Fix a finite group `G` of exact complex matrices on `D = 2^n` coordinates. Here `G` is the dyadic Clifford group of
nine (locally) or 145 (globally) binary axes with its absolute phase, so the central scalars `i^k I` are elements
of `G`. A scalar register program with fixed coefficients evaluates, at column multiplicity `f`, to an operator
whose entries are finite sums

    A_f = sum_g c_g g^{(x) f},        c_g in C fixed, independent of f.

The native operators enter only through `g^{(x) f}`; the coefficients `c_g` of ADD and SCALE instructions stay
outside the tensor power. This is the free-word evaluation convention of the selected proof review (#4359
`PROOF-REVIEW.md` section 2) and of PR5376.

## 2. Lemma

**Lemma.** For `a = sum_g c_g g` in `C[G]`, the operators `A_f = sum_g c_g g^{(x) f}` vanish for every positive
integer `f` if and only if `a = 0` in `C[G]`.

*Proof.* The map `rho_f: g -> g^{(x) f}` is a group homomorphism `G -> GL(D^f)`, because
`(gh)^{(x) f} = g^{(x) f} h^{(x) f}`. Its linear extension to `C[G]` is an algebra homomorphism, so `a = 0`
implies `A_f = rho_f(a) = 0` for every `f`. Conversely suppose `rho_f(a) = 0` for all `f >= 1`. Let `rho = rho_1`,
which is faithful because `G` is a group of matrices. The representation `rho (x) R`, with `R` the regular
representation, is `D` copies of `R` and contains every irreducible representation of `G`. By Burnside's theorem
every irreducible representation of `G` occurs in some tensor power `rho^{(x) m}`, `m >= 0`, so every irreducible
representation occurs in some `rho^{(x) (m+1)}` with `m + 1 >= 1`. Hence `a` acts as zero in every irreducible
representation, and `a = 0` in `C[G]`. ∎

Three consequences are used below.

1. **Group identities lift.** If two products of native generators are the same element of `G` (same Pauli
   tableau and same action on the basis state `|0>`, which fixes the absolute phase), they agree at every width.
   This covers inverses, exponent two (`C_0^2 = X_0`), commutation of operators on disjoint axes, Hadamard
   children, phases and spectators (tensoring with the identity on the untouched axes is again an element of the
   larger Clifford group).
2. **Free-word identities lift.** An identity that holds in the free group algebra on the native symbols, with
   only adjacent inverse cancellation, holds in `C[G]` under every assignment of symbols to group elements, hence at
   every width.
3. **Linear relations between distinct elements do not lift.** `C_0 = (1+i)/2 I + (1-i)/2 X_0` is an identity of
   matrices at width one and a nonzero element of `C[G]` (three distinct group elements); it fails at width two.
   The same holds for the scalar `i` against the element `iI`, whose tensor square is `-I`. A certificate must
   therefore keep the scalar layer and the group layer apart, exactly as the selected convention prescribes.

The census `a = 0 in C[G]` is a complete decision procedure: no finite set of widths has to be evaluated. PR5369 and
PR5376 prove the same criterion in the quantitative form of finite width cutoffs (four and eight widths), which is
what one needs when the distinct group elements cannot be canonicalized; here they can, by `clifford_exact.py`.

## 3. The selected caller as a composition of liftable identities

The runtime of PR5413 is the controller `NEUTRAL-CALLER-v16c` with eighteen backward calls of the body
`NEUTRAL-BACKWARD-v16c`, whose `PROVIDER_5402` is the changed #5383 word with the port wrappers of
`NORMALIZERS.json`. [verify.py](verify.py) checks the following.

**A. Port binding (896 exact group identities).** For each of the 112 ports and both orientations, the physical
path operators of the body are, with absolute phase,

    x -> X : D,      y -> Y : D,      y -> X : D C_0,      Q_p := A_y A_x^-1 = C_0,

where `A_role` is the input wrapper followed by the inverse canonical chart of the entrance frame, `O_role` the
canonical chart of the exit frame followed by the output wrapper, `D` the positive rank-eight Gaussian on axes 1..8
and `C_0` the positive central Gaussian on axis 0. The backward orientation uses the entrywise-conjugate chart and
operator semantics of PR5376 `PROVIDER.md`; mixing conventions produces a different element on every port. These
are statements about elements of `G`, so by consequence 1 they hold at every width: the body is the controller's
`X = D x - D Q y`, `Y = D y` on every column.

**B. Body endpoint (free-word identity).** The free-word replay of the body with the provider expanded ends with
every native warp cancelled, the main rows `X_p = Nout_x (Nin_x x_p - Nin_y y_p)` and `Y_p = Nout_y Nin_y y_p`
carrying only the port wrappers, the 400 autonomous helpers returned as their own input under an alias pair of exact
signed monomials (318 pure central phases, 82 with an address action; none is the identity) with the recorded exit
frame reached by their paid climbs, the eight mode owners returned as the paid rank-eight Gaussian of `h - Z y` (own input plus 56 `y`
inputs with `±1/2` entries), and all seventeen owned fields zero. By consequence 2 this endpoint is the same at
every width. Combined with A, the body's physical endpoint on main data is exactly `D x - D C_0 y`, `D y`.

**C. Controller (free commutative identity, abelian realization).** The controller's thirty-two bank rows are
replayed in the free commutative Laurent ring on `Q` and `D_1, ..., D_33` (the semantics of
`check_wholecaller_v1.py`, no finite-order quotient); the endpoint is the recorded diagonal with exterior
coefficient `+1`. The plan `WHOLECALLER-PLAN-v1.json` realizes `Q = C_0` on the global central axis 0 and `D_s` as
the rank-eight Gaussian on the eight private axes of stage `s`; the eighteen private planes are pairwise disjoint
and disjoint from axis 0, so all realized symbols commute as exact group elements. A polynomial identity in
commuting invertible variables holds for any commuting invertible assignment, in particular for the tensor powers
`C_0^{(x) f}` and `D_s^{(x) f}`, which still commute. The sixteen banks whose diagonal carries `Q^{-1}` are
corrected by the central translation `X_0 = C_0^2`, and `C_0^{-1} X_0 = C_0` is an exact group identity (phase
included), so every main target is the positive canonical Gaussian with absolute phase at every width. The scalar
`Q_POWER` events are `X_0^{±1}` (even exponents), and the signed swaps use the fixed scalar `-1`.

**Conclusion.** The complete caller identity of PR5413 is a composition of identities of types 1 and 2, with
fixed real dyadic coefficients. Each lifts to every positive column multiplicity. This is the algebraic half of
the retained assumption `native_all_columns` for the selected caller. It does not address the physical half: that
the lifted operators, spectators and whole-job adapters are realized on the fixed tape at the retained tariff.

## 4. Controls

[verify.py](verify.py) evaluates the four traps of section 2 on dense `2x2` and `4x4` matrices over `Q(i)`: the
Reynolds-type relation and the scalar phase trap vanish at width one and fail at width two, while the census
reports three and two distinct elements; exponent two is one element written two ways and vanishes at widths one to
three; reversed noncommuting factors are distinct elements and already differ at width one. [test_verify.py](test_verify.py)
rejects: input drift, a wrapper phase mutation, a mixed-convention reading, a leftover native warp in the body
endpoint, an owned field left nonzero, overlapping private planes, a missing `Q_POWER`, and a tampered result.
