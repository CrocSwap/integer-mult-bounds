# Sharp source-ordered native-port error channels

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.

## Result and exact interface

This answers [PR4828](https://github.com/CrocSwap/integer-mult-bounds/pull/4828)'s Open next question2 for the literal [PR4743](https://github.com/CrocSwap/integer-mult-bounds/pull/4743) full-input ports. Sharp Euclidean endpoint conditioning and coordinatewise chronological error propagation are different quantities. Keep every individual tensorized phase letter, two arbitrary independent input banks, and every forward/reverse paid call. Write `L=2^(f/2)` for every integer f>=1.

Assume independent initial input-coordinate perturbations and an additive complex-coordinate defect after each completed paid call, each of modulus at most rho on that call's actual stored input. Monomial updates, integer mixing and their reverses are exact on the common grid. Then the **exact largest output-coordinate error**, over those abstract independent defect balls and both output banks, is bounded by `E rho`, with these sharp constants:

| Literal schedule | E(f) | Sufficient completed-call/input tolerance for output2^-P |
| --- | --- | --- |
| two-call forward | `3L^2+4L+1` | `rho=2^(-P-f-3)` |
| three-call forward | `2L^3+4L^2+2L+1` | `rho=2^(-P-ceil(3f/2)-3)` |
| two-call reverse | `L+4` | `rho=2^(-P-ceil(f/2)-2)` |
| three-call reverse | `L^2+L+4` | `rho=2^(-P-f-2)` |

The original sufficient tolerance `2^(-P-2f-6)` remains valid. These are improved **external completed-call accuracy requests**, not measured word/time savings from a new Gaussian implementation. The abstract independent defects need not all be attainable errors of one concrete rounded algorithm. Sharpness is a property of this explicitly stated error contract; it is not a lower bound on every numerical realization. No paid calls are removed and no new κ is claimed.

## Actual chronology and defect maps

Use source `A=C0`, `P=S U S`, `Q=S V01 S`, `W=Z0 Z2`, `M=Z1 V01`, `J=M C2`, `D=J W A`; each subscript f tensors the individual base matrix before addition. In this section suppress f. Source order is

```
t = A(x+dx)+e1;
s = A((y+dy)+P t+2Q t)+e2;
u = M(C2 W s+e3)                 # three-call variant only
```

The third defect is immediately after C2 and before M. It cannot be replaced by an identity channel when checking the actual vector error, even though M has coordinate norm1. With `F=A P A+2 A Q A`, `B=D P A+2 D Q A`, the lower-bank maps of the independent error variables are

| schedule | dx | dy | e1 | e2 | e3 |
| --- | --- | --- | --- | --- | --- |
| forward2 | F | A | `A P+2 A Q` | I | absent |
| forward3 | B | D | `D P+2 D Q` | `J W` | M |

The upper bank has error `A dx+e1`. There are no products between defects: the maps are linear and every paid-call error is defined against its actual perturbed input. Using a defect guarantee only at an ideal input would change the premise.

For the reverse3 program, apply M^-1 then C2^-1 to the second input, insert its first defect, apply W^-1 then A^-1 and insert its second defect. Subtract P t and2Q t using the retained first input **before** its final A^-1 call. That last call's defect reaches only the first output. Reverse2 omits the first C2 stage. Thus the lower output channels are

| schedule | first-input quantization | second-input quantization | first paid defect | second paid defect | third paid defect |
| --- | --- | --- | --- | --- | --- |
| reverse2 | `-(P+2Q)` | A^-1 | I | zero | absent |
| reverse3 | `-(P+2Q)` | D^-1 | `A^-1 W^-1` | I | zero |

The upper bank is `A^-1 dt+e_last`. An inverse paid call can use the source's forward-call-plus-X realization; its exact monomial merely transports the defect ball and preserves its coordinate tolerance. No optional odd division by15 is executed in these schedules.

## Uniform norms and sharpness

For a finite row r of a complex matrix, the induced complex-coordinate norm is `sum_j |r_j|`. Tensor products multiply row1-norms. The following exact eight-coordinate facts follow by multiplying the literal Gaussian-rational source letters. The verifier binds the source declarations and independently reconstructs those matrices; it imports no predecessor checker.

* A,A^-1,JW,A^-1 W^-1 have flat rows of1-norm sqrt2; D,D^-1 have flat rows of1-norm2; P,Q,M are monomial.
* The two separately tensorized branches of F have flat row1-norm2, those of AP+2AQ have flat branch norm sqrt2, those of DP+2DQ have flat branch norm2, and those of P+2Q have flat branch norm1.
* B's first branch `D P A` has flat row norm sqrt2; its second branch `D Q A` has flat row norm sqrt8, as checked directly from the literal matrices. The source residual identity names another monomial M; it differs from this note's post-call `M=Z1 V01` and is not substituted here. Neither branch statement tensors the sum B.
* In base row0, every overlapping nonzero entry of each listed branch pair has the same complex phase: `x_j conjugate(y_j)` is positive real. This includes B's unequal-magnitude branches.

The triangle inequality therefore gives the uniform upper bounds

```
||F_f||inf=3L^2,       ||A_f P_f+2A_f Q_f||inf=3L,
||B_f||inf=2L^3+L,     ||D_f P_f+2D_f Q_f||inf=3L^2,
||P_f+2Q_f||inf=3.
```

The equalities are attained by row `(0,...,0)`: entrywise same-phase overlap is preserved by products under tensorization, including support intersections, so the triangle inequality is exact there for every f. All the other single-unitary channels have their stated flat row norm. The proof is an application of explicit finite base identities and tensor functoriality, not extrapolation from the later width1/2/3 tests.

For independent coordinate errors, concatenate all channel matrices horizontally. Its induced norm is the maximum, over output rows, of the sum of all channel row1-norms. Every channel above attains its own bound at the same row0, so summing gives the asserted E. For a sharpness witness, independently set each error coordinate to rho times the conjugate phase of its channel's row0 entry (zero entries may receive0). Every summand then points along the positive real axis and attains E rho. The two banks' upper error constant is only L+1, smaller than the lower-bank total. The mathematical witnesses can use eighth roots of unity; the finite execution tests use exact Gaussian-rational perturbations and do not claim that a dyadic quantizer necessarily generates every sharpness witness.

## Guard consequence and retained costs

Since f>=1, L>=sqrt2. Dividing forward2/forward3 constants by L^2/L^3 gives respectively at most `7/2+2sqrt2<8` and `3+(9/4)sqrt2<8`. Reverse2/reverse3 divided by L/L^2 are at most `1+2sqrt2<4` and `3+1/sqrt2<4`. Rounding the exponent upward yields the four stated dyadic tolerances with strict output margin. The checker uses rational squared comparisons, not floating logarithms. These guards are sufficient; the exact minimal dyadic guard can instead be selected by the explicit E table, and no optimality of the integer constants3/2 is claimed.

The original conservative intermediate allowance `2^(H+2f+4)` for inputs of magnitude2^H remains sufficient: at most three Gaussian stages contribute at most L^3, the one mixed update contributes total coefficient3, and all new tolerances are at most1/8 for H,P>=0. Writing M0=2^H, the forward stages are bounded by `(3L^3+L^2)M0+(3L^3+4L^2+L+1)rho` and the reverse stages by `(L^2+3)M0+(L^2+L+4)rho` (the smaller two-call cases fit these envelopes). Each is below `8L^3 M0 <= 2^(H+2f+3)`. The looser original allowance therefore accommodates the perturbed states. Exact free monomial/scalar passes and their existing owned address workspace remain charged as in #4743. The Gaussian implementation's internal-prefix guard, internal error guarantee and execution cost are additional; this package neither installs nor prices one. It also does not price complete recursive substitution, general nonunitary encodings, full supplier/outer transfer or physical tapes.

Research decision: stop at the actual error interface. Inherited paid/source/ownership/native contracts keep their status; source-ordered amplification and a sharper completed-call tolerance are established here; physical implementation and recursive consequences remain open. This is a focused precision obligation and does not reopen a fixed-word paid-saving search.

## Evidence and reproduction

Generated `RESULT.json` records12cases (two/three calls, forward/reverse, f1/2/3),54exact dirty perturbed trajectories and144independent impulse columns at width1. Exact row norms and row0 sharpness are checked at every row of the bounded lifted matrices. A separately executed chronological vector program agrees with the independent error maps. Six controls reject unsupported width, wrong phase family, wrong defect order, a false cap, dropping the third defect's post-call monomial and unsupported entry-angle assumptions. Complete typed receipt comparison rejects altered fields and bool/int substitutions. Normal and optimized commands use only CPython3.12 standard library.

```
python3.12 -B scripts/research_package.py --package research/native-error-channel-amplification
python3 -B scripts/check_research_commit.py --package research/native-error-channel-amplification --check-source-history
```

The official committed export can execute `verify.py` directly with `-I -W error -B`, and separately `-O`, without Git/network. `--emit NEW_PATH` writes a new deterministic receipt and refuses overwrite. Source pins bind the exact base and retained source bytes. Hosted CI is unverified at publication.

Base canonical main `bee95ce88f9f19802f0613f92838895cd0e14a1f`, priority7, selected conditional κ0.00302015 unchanged. Entry overlap at06:05–06:06UTC October23 covered310openPRs,4096Discussion records and6690base notes with complete reported pagination/inventory. Related #4828/#4743, shared-port/cascade and later compensated-port work were distinguished. Coverage is advisory, not novelty proof; arbitrary diffs and unpublished work remain outside it. Canonical claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19139368.

Credit Nick Petalas #4828 for sharp endpoint conditioning and the explicit error-channel question; Dugongue #4743 for literal all-input schedules and conservative precision contract; Yiyang/Lyy-iiis #4710 for repaired phases; lee-phys #4688, Jacob Alan Sussman #4628, eumemic, Swapnil Jain and all notices retained in those packages. No source archive is modified or reissued. No independent human or formal proof-kernel acceptance is claimed.

## Open next questions

Can one concrete rounded Cj_f implementation meet these completed-call tolerances on each actual stored input with its internal range, data-grid, movement and time costs retained? Begin with one nonzero-rounding invocation and compare its actual radius/tolerance to the table. The sharp external contract supplies no internal Gaussian guarantee. Complete recursive substitution requires its own error-channel composition and is outside this package. Structured question: TASK.json.
