# A source-bound backward provider with eight coupled rank-eight outputs

The construction has 632 arbitrary original inputs and nine arbitrary owned
inputs. Its paid native profile is
`{1:2193,2:412,3:510,4:127,5:40}`. It returns 400 unchanged native helper jobs
and a coupled block on the 224 main and eight remaining helper owners:

\[
 X=Dx-Ry+RW h,\qquad Y=Dy,\qquad H=D(h-Zy).                 \tag{1}
\]

Here `R=DQ` is the full native rank-nine Gaussian, `D` acts on the eight
noncentral axes, and `Q` acts on the central axis. The eight `H` outputs remain
coupled; they are **not eight autonomous H8 targets**. No complete caller or
new multiplication exponent follows. All nine owned outputs are zero.

## 1. Exact source and the changed word

`SOURCES.json` pins the main-branch source, code, normalizers and Clifford
compiler. The native source's decompressed SHA256 is
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
`WITNESS.json` retains Ali Romman's PR5383 candidate verbatim, with SHA256
`24599011da06325e1012619b2b84a4dd3aceb90ab42d3caaf6414879e7d16591`.
It supplies candidate sites and rational rows; it is not a proof oracle or a
pending Git-object dependency. Every used identity is checked again against
the pinned main source.

For witness row `i`, after the indicated original `cached_event`, CLEAR owned
`C[i+1]` and COPY the indicated persistent row into it at its actual chart.
Every cache precedes every removed center. At the original center event,
replace the H8 call by CLEAR `C0`, then COPY `C[i+1]` into `C0` at that same
rank-eight chart. At the indicated later H1 call, replace the call by a
`zero_retag`: this is physical identity on the **exactly zero** field, with
its bookkeeping chart changed to the old call's output chart. All other
instructions, including inherited physical metadata, remain unchanged.
`WORD.json.gz` emits the complete resulting backward native word; the verifier
regenerates it from the canonical source and compares its parsed content.

The replay begins with one independent formal column per field, including
all nine owned fields. It tracks exact rational coefficients in the free
group on the source's native warp symbols, their inverses, and actual chart
tags. Every ordinary operation is checked at its true chart. COPY fills only
owned zero; CLEAR acts only on owned fields. Before each of the eight retags,
every one of the 641 input coefficients is zero. All initial owned dirt is
cleared before use and is absent from every endpoint.

The source's ten `phase` records are named stage annotations, not scalar
Clifford phase gates; its 448 `adapter` records retain the predecessor's
physical entrance/exit bindings (there are no `residual_adapter` records in
this backward word). As in the pinned predecessor normalized-row semantics,
these do not update formal rows. They are preserved in the emitted word,
not deleted or priced away. Their physical interpretation and native cost
are inherited; this package separately verifies every new physical boundary
identity including absolute phase.

The same interpreter replays the original source, obtaining its full
632-row normalized backward endpoint `(x-y,y,h)` and clean original temporary.
It separately replays center deletion to derive the native coupling below.
The changed word has eight fewer H8 and eight fewer H1 calls than the original
source, with no additional Gaussian call. It has 16 extra COPYs and 16 extra
CLEARs. This is a changed source construction, not a constraint such as
`Delta h=0` on otherwise independent inputs.

## 2. Source-derived coupling and an ordinary helper basis

Use the inherited 112-by-8 matrix `M`, stored transposed as `mode_columns`.
The verifier checks all entries of

\[
 M^T M=56I_8,\qquad A=I-MM^T/4.
\]

Fresh replay of the center-deleted source gives

\[
 X=x-A^Ty,\qquad Y=y,\qquad H=h-B^TM^Ty.
\]

The verifier derives every entry of `B` by projecting the actual 408-by-112
helper-to-Y coefficient matrix onto `M/56`; it then checks the entire
factorization and all 632 endpoints. The eight candidate rows `Delta` satisfy
`Delta B^T = S`, an exactly checked signed permutation. Put `E=S^-1 Delta`.
Thus `E B^T=I8`. Fresh original-prefix replay also binds the candidate cache
rows, their chronology and their actual rank-eight charts.

In these coordinates the changed word has normalized endpoint

\[
 X=x-y+(M/4)Eh,\quad Y=y,\quad H=(I-B^TE)h,              \tag{2}
\]

and its canonical mode-`k` cache is

\[
 f_i(E_kh-M_k^Ty),\qquad f_i=\texttt{zero_factor}_i\,S_{ik}. \tag{3}
\]

The registered check composes all changed endpoint rows with the following
basis, rather than accepting (2) or (3) from a saved endpoint registry.

The union of supports of `B` and `E` comprises 122 actual cold H9 owners: each
has ground entrance chart and full-R exit chart. Choose the eight original
mode owners `[224,225,227,229,240,241,256,257]`. Define `L` on these 122 owners:
its mode columns are `B^T`; its other columns are `(I-B^TE)e_j`. Exact
Gauss-Jordan reduction constructs `L^-1` and verifies both inverse products,
`EL` selecting precisely the eight mode coordinates, and `L^-1B^T` embedding
precisely those coordinates. Every coefficient is dyadic. The emitted
`input_basis_program` and `output_basis_program` execute these two maps in
place, without extra owned basis storage.

Both bases mix only fields sharing the appropriate physical chart, so scalar
owner operations implement them ordinarily. After entrance `L` and exit
`L^-1`, every one of the 632 persistent rows is checked: the eight selected
helper rows are zero, the other 400 helper rows are unchanged, `Y=y`, and
`X=x-y+(M/4)h_mode`. Each cache is exactly
`f_i(h_mode,k-M_k^T y)`. Thus the cache fills a vacated original direction;
it supplies no additional productive input or job credit.

## 3. Literal physical boundary maps and ownership

Backward frames use complex conjugation of the native frames, as in the
pinned source convention; they are not silently replaced by adjoints. Let
`Kp` be the 112 inherited main normalizers. For each actual cache frame `F8`,
the verifier constructs an orthogonal, phase-correct monomial `Km` from its
unique missing odd noncharacteristic line, and compiles a monomial `N` with

\[
 N\overline{F8}K_m=D,\qquad K_mR=RK_m.
\]

`PROVIDER.json` contains all eight literal `Km` and `N` words, signed tableaux
and nonzero zero-column phase anchors. The compiler's output is checked
explicitly even under Python `-O`. All `Kp` commute with `R`, including
absolute phase. Every boundary word contains only monomial gates.

Apply `2Km` to the eight original mode inputs before `L`. At the exit, apply
`N/(2f_i)` to each cache. Use the inherited **fused compiled** backward main
input/output wrappers. The verifier checks 336 main diagonal/shear blocks,
896 nonzero main/helper coupling blocks and eight helper diagonal blocks,
for 1,240 exact physical equations. Comparison includes the signed tableau
and exact zero-state vector, so an undetected global phase is impossible
within this Clifford model. These equations yield (1), with

\[
 W=\operatorname{diag}(K_p^{-1})M\operatorname{diag}(K_m)/2,
 \quad
 Z=\operatorname{diag}(K_m^{-1})M^T\operatorname{diag}(K_p)/2.
\]

The main code is the predecessor's `C=diag(Kp^-1) A diag(Kp)`. Exact word
cancellation and the scalar factorization give
`ZW=14I8`, `WZ=I-C`; `W` and `Z` intertwine `R` on their respective banks.
No commutation with `D` or `Q` is assumed. These are finite ordinary code
maps with exterior scalar coefficients, not additional Gaussian calls.

After normalization, SWAP each cache's **whole physical field and chart tag**
with its identically zero original mode output. The original owner now holds
the normalized coupled output; the owned slot holds zero and can be CLEARed.
There is no persistent erasure and no attempted free chart conversion of a
nonzero field. `C0` is already zero, so all nine owned outputs are zero.
Ordering the coupled input/output banks as `(y,h,x)` makes (1) triangular
with invertible diagonal `D`. Together with the 400 unchanged native jobs,
this proves preservation of all 632 original input directions. It does not
emit an inverse schedule or establish a same-cost inverse/transpose.

## 4. Exact local bill

Relative to the original raw backward source, the selected schedule adds:

| Ordinary operation | Added field operations |
| --- | ---: |
| ADD | 1,644 |
| SCALE | 40 |
| COPY | 16 |
| CLEAR | 24 |
| Whole-field SWAP, with chart tag | 8 |
| Monomial field map | 464 |

Each basis direction uses 822 ADD and 12 SCALE: its three elimination swaps
are expanded into three ADDs and one SCALE each. Eight input scalings and
eight cache scalings give the remaining 16 SCALEs. The source rewrite adds
16 COPY and 16 CLEAR; final cache consumption adds eight CLEAR. The 464
monomial maps are 448 fused inherited main standardizers, eight `Km` and
eight `N`. This counts the newly installed boundary schedule; all unchanged
source warp/phase/adapter traffic and native child implementations remain in
the emitted word and retain their inherited costs. In particular, this table
does not assert that a field monomial map is zero machine work.

The original source has 16,273 ADD, 1,164 SCALE and 16 CLEAR. Including the
new boundary scalars, the schedule therefore has 17,917 ADD, 1,204 SCALE,
16 COPY, 40 CLEAR and eight whole-field SWAP, plus the explicitly described
monomial boundary maps and inherited native operations. Nine owned fields
suffice: the original center temporary and eight retained caches. Their
initial values are arbitrary; their final values are zero. The autonomous
helper profile is `{4:28,7:7,8:47,9:318}`. The physical implementations of
those unchanged native helper jobs are inherited from the pinned source;
scalar identity rows alone are not a new proof of those implementations.

For an explicit local stability bound, use the maximum of field Euclidean
norms. ADD by `a` has norm at most `1+|a|`, SCALE has norm at most
`max(1,|a|)`, and unitary Gaussian/monomial maps, COPY, CLEAR and SWAP have
norm at most one. The verifier sums upward-rounded base-two logarithms for
every scalar operation in this finite schedule, obtaining **18,996**. Hence
every suffix amplifies an injected field error by at most `2^18996`; at most
`m` injections of norm `epsilon` give the conservative bound
`m*2^18996*epsilon`. All dyadic constants and word lengths are fixed. This
establishes local bounded amplification, not a complete coordinate rounding,
tape movement, recursive precision or outer multiplier budget.

## 5. Every positive fiber width and verification boundary

A free-group identity evaluates in any assignment of invertible native warp
operators. Therefore the exact rational row equalities and zero-retag
premises hold uniformly when native operations act on any positive fiber
width `f`. The scalar owner coefficients and scalar `L/L^-1` programs stay
outside the tensor product; in particular `ZW=14I`, not `14^f I`. Each
compiled monomial word uses the inherited prescription: `P` and `X` act
columnwise, `D` sums its Z4 polynomial over the columns, and a `phase` gate
contributes its phase once per column. Each address-operator identity is lifted
columnwise; an absolute phase `i^gamma` lifts to `i^(f gamma)`, rather than
being confused with an exterior scalar sign. Exact one-column operator
identities, word cancellation and rational matrix identities then prove the
same physical boundary composition for every `f`. The inherited native
uniform implementation hypotheses remain inherited.

The registered verifier performs complete 641-column native row replay,
exact scalar endpoint composition, and the 1,240 physical boundary checks.
It does not claim a separately flattened 641-column physical-matrix replay,
a formal-kernel proof, independent human approval, hosted CI, or a complete
caller. It rejects a nonzero zero-retag, a single changed basis ADD
coefficient, a changed saved-cache coefficient and a phase-only error with
the correct tableau. Normal and optimized runs use explicit checks for the
new claims. The caller must close all 224 main and eight coupled helper
outputs, preserve the other 400 jobs, charge every added child and ordinary
operation, and discharge precision, storage and outer-budget obligations
before any new target credit or exponent is admitted.
