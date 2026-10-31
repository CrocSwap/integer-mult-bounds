# Independent review of the optimal two-stage recovery theorem

Reviewed source: canonical base `a7638a4ce2a29947457ae8d6bf8cd70a234dfeac`,
fixture SHA256 `2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8`.
The final scientific draft reviewed is
`worker-b/research/refined-native-recovery/PROOF.md`, headed “Optimal two-stage
refined recovery over mode-preserving integer frames”. Its source construction
has selectors `(0,1,2,4)` and the four columns independently transcribed in
`independent_optimal.py`.

Prepared for @CubeJerry with substantial OpenAI Codex assistance by a separate
review agent. This is an adversarial mathematical review, not human acceptance
or formal proof-kernel admission. No new κ.

## Review conclusion

No mathematical objection remains to the exact minimax theorem in the stated
class of fixed integer unimodular frames preserving Mᵀ. The sharp minimum is
`51,008,161² = 2,601,832,488,601,921`, requiring 52 packed abstract tag bits.
Binary image separation is both necessary and sufficient. The explicit source
frame satisfies it. This changes the declared output function; no physical
storage, selected supplier, accepted caller, or multiplication-bound improvement
is inferred.

## Independent reasoning

1. **Full fibers and half ties.** The reverse formula is
   `2x = U⁻¹(y+Mq2)+Mq1`. Writing `s=Mᵀy`, the scalar quotient conditions are
   `q2∈Q(s)` and `q1∈Q(s+56q2)`. Consequently `T=q1+q2` determines
   `q2=T−R((s+56T)/52)`, with no appeal to translation invariance of half-away
   rounding. Such invariance would be false at some half ties. Integrality of
   the displayed reverse formula is the entire lattice obligation. Actual
   mode preservation gives both literal rounded quotients; distinct T have
   distinct mode vectors `2Mᵀx=s+56T` and thus distinct inputs.

2. **Universal lower bound and necessity.** At zero, q2 lies in `[-6,6]^8`
   and q1 lies in `[-6,6]^8−14q2`. The shift is even and both scalar parity
   counts are positive. The `C×C` quotient parities therefore give exactly
   F² distinct actual inputs for every admissible U. If a nonzero vector lies
   in both binary images of M and U⁻¹M, select the two nonkernel quotient
   parity cosets mapping to that vector. Every coordinate parity has a lift
   in the corresponding 13-element interval. These yield additional actual
   zero preimages, disjoint from the F² family by the quotient uniqueness
   just proved. Therefore equality requires disjoint binary images.

3. **All-integer Walsh bound.** I independently derived the endpoint rules
   for Q(s), including the removed half-away endpoints, and verified the
   author's exact three-case formula for s=4k+2. For s not congruent to 2
   modulo 4, the inner interval is Q(s)−14q2. For s≥34 in the tie class,
   all inner parameters are at most −78, so their endpoint convention is
   uniform. Negation preserves both parities. Thus only the eight positive
   exceptional values 2,6,…,30 remain, and their literal quotient counts
   match all eight displayed tables. This is an exhaustive analytic
   reduction, independent of the finite census below. Their absolute Walsh
   coefficients are bounded componentwise by `(169,1,13,13)`.

   A separate derivation is possible from inner alternating parity sums:
   every inner interval has length 13 except a possible single length-12
   interval; the preferred inner parity has at most one sign change as q2
   increases. The alternating outer sum bounds the T-parity coefficient
   by 1. The other coefficients are bounded by 169,13,13; the only outer
   odd-length/short-inner cases are s=±30 and give magnitude 12. This
   corroborates why the exceptional tables do not invalidate the bound.

4. **Sufficiency and Fourier normalization.** Disjoint binary images give
   one affine coset of `C×C` in `(q1,q2)` parities, or no solution. The
   invertible change `(q1,q2)↦(q1+q2,q2)` preserves `C×C`. Its orthogonal
   subspace has 256 elements, so the character formula has coefficient
   1/256. The nonnegative zero-table Walsh coefficients bound every output
   by the zero output. At zero, direct q1,q2 parity weights factor and give
   exactly F². This proves sufficiency and the minimax value.

5. **Actual source witness.** I checked the integer Gram identity, MᵀV=0,
   EV=0, both inverse compositions on every owner basis vector, and mode
   preservation. Independently enumerating all 256 binary mode masks gives
   two 16-element source images whose intersection is `{0}`. This direct
   image calculation does not reuse the author's rank-elimination routine
   or dual proof. I also checked the exact dual witnesses LM even and LV=I.

6. **Codec.** I read `optimal_codec.py` and independently checked its
   syndrome derivation: δ=Ly; `Mp=y+Vδ` and `EMq=δ+Ey`. The Cartesian
   joint-cell blocks are disjoint and complete. The displayed rank/unrank
   operations use consistent block and mixed-radix order. Its forward and
   inverse formulas agree with the literal source-sized trajectories in
   the independent checker. The proof makes clear that abstract tag width
   does not include workspace or arithmetic costs.

## Independent executable evidence

`independent_optimal.py` imports no primary module. It authenticates the pinned
fixture, transcribes the four source columns independently, and AST-checks that
the primary construction declares the same constants without executing it.
It uses direct quotient enumeration and direct 112-bit binary image grouping;
it does not reuse the primary interval algorithm, binary-rank implementation,
codec, or character-sum count.

Executed in both ordinary and optimized Python, with identical JSON output:

```
python -I -W error -B independent_optimal.py --source ../precision-state-frontier/FIXTURE.json --construction construction.py
python -I -O -W error -B independent_optimal.py --source ../precision-state-frontier/FIXTURE.json --construction construction.py
```

The explicit scratch paths were used for the review runs; the shown relative
paths are the equivalent package commands. Results:

- All 20,001 scalar parameters in `[-10000,10000]`, including the eight
  exceptional tables, satisfy the exact Q classification and Walsh caps.
- All 65,536 binary quotient pairs are grouped into 256 actual source
  parity syndromes; the maximum is the stated F², attained at syndrome zero.
- All 224 inverse basis compositions pass.
- 1,152 source-sized forward/reverse checks pass: three representatives in
  every one of 256 zero parity blocks and 384 arbitrary-input trajectories,
  giving 384 distinct sampled outputs.
- Removing one frame column creates binary intersection size two and raises
  the zero count to `5,201,116,111,850,821`, explicitly detecting the
  necessity of complete image separation.
- Identity frame count is independently `41,588,538,787,713,121`.
- Controls detect changed mode coefficient, nonnilpotent selector, image
  overlap, half-away tie errors, the false entrywise-domination argument,
  omitted inverse frame, and the false optimality of the identity frame.

These finite counts corroborate the universal proof; they are not presented
as proving a statement by searching a finite domain. The script SHA256 is
`ca8c10a15c33ea802132433842d8c42c8db51023ebbcb78e7bae43b779433772`.


## Final reviewed-file binding

The final three-stage addendum was reviewed independently. Directly enumerating
q3∈Q(s), q2∈Q(s+56q3), and q1∈Q(s+56(q2+q3)) gives character sums 13 at
s=0 and −14 at s=2. At s=2 only (q2,q3)=(0,0) has a length-12 inner
interval; every other inner interval has length 13. The displayed reasoning
and narrowly stated failure of that particular Fourier majorant are correct.
It does not claim to disprove a three-stage optimum. The cost discussion
explicitly requires an accepting caller or charged restoration; the separate
cost-scope audit is credited separately and is not included in this review's
mathematical verdict.

This review is bound to the following final package bytes (SHA256):

- `PROOF.md`: `d54eac2e7d464ff30f9eada02b049435ca48dfb335e37e74a3c1cc67871aedb9`
- `optimal_codec.py`: `bd22cdca435a3677b2ab29da3a5c32b5fb2e0fa452fcf2e280484983fde288cd`
- `construction.py`: `dc3d8de42055262389c1fe4ab6635367807a4ce7fbec088fddffabd3466a4e09`
- `independent_optimal.py`: `ca8c10a15c33ea802132433842d8c42c8db51023ebbcb78e7bae43b779433772`
