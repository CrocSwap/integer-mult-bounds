# Independent mathematical review of the 24-array claim

**Finding:** exactly 24 retained complete arrays are necessary and sufficient
under the stated rational-linear information contract. No mathematical defect
was found in the proposed recovery. This is an all-finite-dimension written
proof, supplemented below by an independent exact finite operator check. It is
not a formal-kernel proof or a native implementation/cost result.

This review was prepared independently by the recursive-interfaces specialist
for this run, with substantial OpenAI Codex assistance. Only this review file
is owned by that specialist. The new package's implementation was not imported
or read to obtain the derivation or finite check below. The predecessor
definitions and displayed/source formulas were inspected.

## Sources and precise contract

The inspected predecessor heads are:

- starship-s, [PR2443](https://github.com/CrocSwap/integer-mult-bounds/pull/2443),
  `545c05e17243c962b112b91e7f84b4c1a41de7b8`: ordered F0 inverse and
  the original two-cut decoder.
- thakrarsagar, [PR2470](https://github.com/CrocSwap/integer-mult-bounds/pull/2470),
  `1b2eee3bf1ec67e68c0b0fa7f47c7b2a66febe56`: d1 L2 identity and its
  sufficient 32-retained-array variant.
- ywz65, [PR2456](https://github.com/CrocSwap/integer-mult-bounds/pull/2456),
  `665ba8d7bffab92a434413096e9d5c0df7db40bd`: exact operator audit of
  PR2443 and the logical-D/physical-A chart distinction.

These predecessor claims retain their own premises. In particular, PR2456's
operator result for its original observation contract does not automatically
certify this changed contract.

Let a complete array belong to one common vector space `W = Q^n`, where
`1 <= n < infinity`. Coordinates include every owner and payload coordinate
of that array. All 224 input arrays `(x,y)` in `W^112 x W^112` are arbitrary
and independent. Let `A,T,U` be the pinned disjoint port sets of sizes
`8,8,96`. The consecutive events are exactly

```text
(x1,y1) = F0(x,y),
(X2,Y2) = B_1_2(x1,y1).
```

At d1, immediately after the second event, the decoder is granted exactly
`C=X2_U`, `V=Y2_U`, and `Z=Y2_A`: 200 complete arrays. Additional information
consists of `r` retained arrays in `W`, each a rational-linear function of the
arbitrary inputs. No other reads, prior promises on the inputs, auxiliary
input-dependent records, or nonlinear encodings are admitted. Reading is
assumed to return the stated exact arrays; its implementation and restoration
are outside this contract. The decoder itself need not be linear for the
lower bound to apply.

Other bank pairs do not enter these two local events. They may be arbitrary;
they are not recovered here. Allowing retained records to depend on them
does not defeat the bound: fixing those other inputs still leaves all
`224n` pair-zero input coordinates independent.

## Ordered maps

For chart `s`, let `D_(s,p)` be the admitted invertible logical map on `W` at
port `p`, and let `D_(s,L)` be their block diagonal direct sum. Write scalar
matrix actions with the identity on `W` understood:

```text
ell_(s,L) = R_L D_(s,L),                 L=A,T,
B_s       = R_U D_(s,U),
P_(s,L)   = D_(s,L)^(-1) R_L^(-1),     L=A,T,
K_(s,U)   = D_(s,U)^(-1) R_U^T / 4.
```

The selected Grams `R_A R_A^T = R_T R_T^T = 4I` give two-sided inverses
`R_L^(-1)=R_L^T/4`; hence `ell_(s,L) P_(s,L)=I` and
`P_(s,L) ell_(s,L)=I`. Each section first applies the scalar inverse and
then each port's inverse cover map. No step below commutes a port-dependent
map through a scalar mixing matrix. Products act rightmost first.

The relevant B1 equations are exactly:

```text
a     = ell_(1,T) x1_T,
C     = x1_U - y1_U,
V     = y1_U + K_(1,U) a,
Z     = y1_A + P_(2,A) (B_2 y1_U + ell_(2,T) y1_T).
```

The last equation uses the future logger at chart 2, which changes only A,
and the fact that the B1 source A output is that logger's output. Replacing
chart 2 by chart 1, or replacing its logical maps by physical native
alignments without the required conjugation, is not justified.

## Recovery with 24 retained arrays

Retain `x1_A`, `x1_T`, and `y1_T`. Compute in this order:

```text
a     = ell_(1,T) x1_T,
y1_U  = V - K_(1,U) a,
x1_U  = C + y1_U,
y1_A  = Z - P_(2,A) (B_2 y1_U + ell_(2,T) y1_T).
```

This reconstructs every post-F0 array. In the last line, form the two
chart-2 queries, add their eight output arrays, apply `R_A^(-1)`, then
apply the separate `D_(2,p)^(-1)`. The old-A baseline is the unknown being
recovered; it is not an extra retained input. No unread ordinary minor or
88-array record is needed.

For completeness, the inherited F0 inverse is:

```text
f     = ell_(0,T) x1_T,
t     = P_(0,T) ell_(0,A) x1_A,
x_U   = x1_U + K_(0,U) f,
x_T   = t,
x_A   = P_(0,A) (f - B_0 x_U - ell_(0,T) t),
y_U   = -C,
y_L   = x1_L + y1_L - x_L,             L=A,T.
```

Indeed F0 sends `x1_T=P_(0,T) R_0 x`,
`x1_A=P_(0,A) ell_(0,T)x_T`, and
`x1_U=x_U-K_(0,U)R_0x`; its ordinary Y equation is
`y1_U=y_U+x1_U`, and it preserves the selected pair sums. The displayed
inverse follows from the two-sided selected inverse identities. Conversely,
for arbitrary `x1,y1`, it produces an input whose F0 image is exactly that
state: its centre query is `f`, its two selected X outputs are the prescribed
ones, and the Y formulas invert the ordinary addition and selected sums.
Thus F0 is an isomorphism under this contract, without needing a separate
assumption about all of B1's unobserved outputs.

All equations are exact over `Q`. No zero initial Y assumption, owner-constant
restriction, payload-constant restriction, commutativity of cover maps, or
bounded precision assumption enters this argument.

## Lower bound and exact kernel

Let `H:W^224 -> W^200` be the granted-observation map from original inputs,
and let `L:W^224 -> W^r` be any permitted retained record. Successful recovery
of every input requires `(H,L)` to be injective, irrespective of the
decoder's subsequent operations. Its target has dimension `(200+r)n`,
whereas its source has dimension `224n`. Therefore

```text
224n <= (200+r)n, so r >= 24.
```

There is also an explicit exact description of the information lost by `H`.
Work in post-F0 coordinates, which is legitimate because F0 is invertible.
Choose arbitrary blocks `r_A,t_T,h_T` in `W^8`, and set

```text
x1_A = r_A,
x1_T = t_T,
y1_T = h_T,
a    = ell_(1,T) t_T,
y1_U = -K_(1,U) a,
x1_U = y1_U,
y1_A = -P_(2,A) (B_2 y1_U + ell_(2,T) h_T).
```

Then `C=V=Z=0`. Conversely, those three zero-observation equations force
exactly this form, leaving precisely the three displayed selected blocks
free. Consequently `ker H` is isomorphic to `W^24`, and `rank H=200n`.
The proposed record is a coordinate system on this kernel. This establishes
the exact floor rather than only an upper bound from counting observations.

For a concrete dropped-block obstruction, set two of `r_A,t_T,h_T` to zero
and take the third nonzero in the preceding construction. The observations
remain zero and the other two retained blocks remain zero, but the input
is nonzero by F0 invertibility. Thus simply discarding any of the three
eight-array retained blocks fails. The dimension proof additionally excludes
every other rational-linear record with fewer than 24 complete arrays.

The restriction to a common, positive, finite dimension matters. The count
does not establish a claim for infinite-dimensional array spaces, variable
record capacities, nonlinear encodings, extra reads, or a decoder asked to
recover only a quotient of the inputs.

## Independent finite operator check

An independent standard-library Python calculation was first run in memory,
then preserved as [independent_check.py](independent_check.py). Reproduce it
from the repository root with:

```sh
python3 -I -B research/qq16-l2-minimal-retention/independent_check.py
python3 -O -I -B research/qq16-l2-minimal-retention/independent_check.py
```

It reads only the packet to obtain R and the partition; it imports no
predecessor executable or new-package implementation. The
packet SHA-256 was checked as
`a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7`.
The selected Grams were recomputed exactly.

The fixture used `W=Q^2`, stage-0 identity maps, and these invertible,
port-dependent maps for `s=1,2`:

```text
t = 1 + ((p + 2s) mod 3),   u = (-1)^(p+s),
D_(s,p) = [[1,t],[u,1+ut]],
D_(s,p)^(-1) = [[1+ut,-t],[-u,1]].
```

Each output coordinate was stored as a sparse exact `Fraction` linear form
in all 448 independent input coordinates. The F0 formulas and four B1
observation equations above were implemented separately from the recovery
formulas. Complete coefficient comparison proved both compositions were
the identity: original inputs to observations/retention to original inputs,
and independently arbitrary observations/retention through the reverse
composition. Hence this finite check covers every rational input in this
two-coordinate fixture, rather than a finite sample of input values.

Five incorrect decoders were rejected. Witnesses below encode
`(output side, output port, output coordinate; input scalar index; residual)`;
side 0 is X, side 1 is Y, and input scalar index is
`2*(112*side+port)+coordinate`. Set that one input scalar to 1 and every
other input scalar to 0 to obtain the stated residual.

| Fault | Exact nonzero residual witness |
| --- | --- |
| Omit the `K_(1,U)a` correction | `(0,0,0; 0; -10)` |
| Reverse C's sign when recovering `x1_U` | `(0,0,0; 226; -1)` |
| Omit the future-T logger term | `(1,0,0; 0; -3)` |
| Add the logger instead of subtracting it | `(1,0,0; 0; -76)` |
| Apply port inverses before the scalar A inverse | `(1,0,0; 0; -32)` |

The last mutation replaced `D_(2,A)^(-1)R_A^(-1)` by
`R_A^(-1)D_(2,A)^(-1)` in recovering `y1_A`. The tested order matters even
though all individual scalar coefficients commute with maps on `W`:
different ports carry different maps.

The calculation returned `PASS_INDEPENDENT_TWO_COORDINATE_REVIEW`, with
448 formal input coordinates, 448 formal observation/retention coordinates,
two inverse identities, and all five faults detected, in both normal and
optimized Python modes. Explicit failure checks remain active under `-O`.
The fixture maps are
synthetic rational operators, not the actual 73-dimensional owner routes.
It is an algebraic stress check, not a second source-specific route-binding
audit. Its finite result supplements, and does not replace, the written
all-finite-dimension proof above.

## Relation to predecessors and remaining obligations

PR2470's L2 variant supplies `x1_U` using the same 200 granted live arrays
and 32 retained selected arrays. Once `y1_U` is reconstructed, the future-A
logger also reconstructs `y1_A`; those eight retained arrays are redundant.
Thus the change is from sufficient retention 32 to optimal retention 24 for
that enlarged d1 read set. PR2470 did not claim 32 was minimal. Its 120-array
floor for PR2443's smaller 104-live-array read set is a different, unchanged
statement.

PR2443 supplies the F0 inverse and the logger relation. PR2456 supplies an
important source-specific caution: logical D and physical A have different
payload semantics. The present written proof permits arbitrary invertible
logical D but does not certify a physical routine that inserts native A in
only some of those positions. The run's primary checker owns its packet
registration and complete-coefficient checks. It was subsequently inspected
and replayed as recorded below; that inspection did not enter the independent
derivation or the independently written matrix checker.

No legal native read of `Y2_U` or `Y2_A`, retention method, restored scratch,
copy cost, chart-map cost, source access, precision growth, final endpoint
availability, post-d1 schedule behavior, four-bank recovery, or complete
supplier invoice is supplied by this information theorem. In particular,
the eight-array reduction cannot be converted into a new kappa or physical
cost saving without those obligations. The result is conditional on the
logical local contract, with no selected-frontier change.

## Open next questions

1. Can the 200 granted arrays be read at d1 by a permitted native interface
   while restoring all source and private scratch? A first step is to bind
   each `Y2_U` and `Y2_A` read to its actual endpoint frame and price its
   literal inverse. This is a recursive/native-interface obligation.
2. What is the fully charged cost of retaining the 24 arrays and applying
   the ordered decoder? The independent information floor does not price
   controller work or permit borrowing caller-owned arrays. Supplier and
   asymptotic specialists own the subsequent complete cost transfer.

New review text is Apache-2.0. Predecessor attribution and licenses are
retained in the surrounding package's source manifest.

## Final package-claim audit and direct replays

After completing the independent derivation and matrix checker, the reviewer
inspected the completed README and primary verifier. No mathematical or scope
defect was found. The examined files had these SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `README.md` | `b9de74e9e888496c2dff77326b5c078aec348b76529ece1c1072a41a4e832b3b` |
| `verify.py` | `639bebcde1003e9cc8d923f455a67c917f32cf506eb05c5081bc9850b99fc8ea` |
| `RESULT.json` | `d334ebd141e27f46e5a71be85d8efefacffe37a727cac4c11ebd0cb9a6e171c6` |
| `independent_check.py` | `5b20175e4d5e604fd7c08b7f9f2495d73bad99e0d8df0b798dfa017111861303` |

The finite-dimensional information lower bound is stated at its actual scope:
fixed rational-linear records of equal capacity, all arbitrary pair-zero
inputs, and precisely the 200 specified live arrays. The code implements the
same ordered inverse. In particular, its F0 inverse subtracts
`c=ell_(0,A)x1_A`, equal to `ell_(0,T)t` in the displayed proof.

The primary checker works in a rational free-group ring with separate
invertible symbols for each positive-stage port/chart map. Its zero formal
residuals specialize to zero for every admitted invertible realization,
including the pinned logical owner maps. This gives stronger algebraic
coverage than a test of one chosen representation. Conversely, a nonzero
free-group residual need not remain nonzero at every concrete specialization.
The README correctly identifies the 32 faults as formal controls rather than
actual native input counterexamples.

The source checks bind the authenticated packet's exact `F_contract` and
`B_contract` strings, R/K, selected Grams, first two events, and map
registrations with both inverse orders. They do not
independently reconstruct chart phase geometry or derive the logical F/B
semantics from native programs. The README states these inherited-contract
limits explicitly. The review does not promote these checks into a physical
read, restoration, finite-precision, full-schedule, or supplier-cost result.

Direct replay outcomes from the repository root:

- With Python **3.14.6**,
  `python3 -I -B research/qq16-l2-minimal-retention/verify.py` returned
  `PASS_QQ16_L2_MINIMAL_RETENTION retained=24 live=200 inputs=224 identities=6 faults=32 no_new_kappa`.
  This direct replay used the preceding verifier version
  `4e379b4f72ab7e90e3ace313b377d0db631cf97bbd199634ca7d5b70d5647780`;
  the narrowly reviewed update below adds only source guards.
- With Python **3.12.12**,
  `python3.12 -I -B research/qq16-l2-minimal-retention/independent_check.py`
  returned `PASS_INDEPENDENT_TWO_COORDINATE_REVIEW`, with the same two
  448-coordinate inverse checks and the five residuals listed above.
- The independent checker also passed normal and `-O` execution with
  Python **3.14.6**.

The subsequent verifier update adds exact equality checks for the pinned
forward/backward contract strings. The reviewer parsed those two guards,
checked their constants against the authenticated packet, and removed just
those two syntax nodes in memory: the remaining bytes hash to the previously
reviewed verifier above. Thus the current reviewed hash in the table differs
only by these two explicit source checks. This audit returned
`PASS_EXACT_TWO_GUARD_DELTA_AND_PACKET_TEXT`; the unchanged mathematical
replay was not repeated by this reviewer. The guards bind contract metadata
and do not derive native semantics or the definition of the future logger.

The final README update distinguishes the run owner's registered replay from
this specialist's direct replays. Its adjacent-work statement was checked
against ywz65's linked PR2470 comment, created at `2026-10-15T12:12:54Z`:
that claim targets native L2 reconstruction with restored borrowed sources
and 96 owned outputs, and expressly excludes minimizing the retained record
or claiming the complete ordered decoder. The README correctly treats it as
a complementary lead without verified native evidence for this package.

This reviewer ran the direct checks above. The generic registered replay,
behavioral test suite, preservation, publication, and hosted CI are separate
run-owner gates. No formal proof assistant was used.
