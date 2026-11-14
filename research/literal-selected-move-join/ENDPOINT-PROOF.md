# Literal endpoint-promised scale and width around the complete MOVE

## 1. Exact strengthened boundary

The byte-frozen core in move.py is the direct complete MOVE proved in
PROOF.md. Its graph hash is
`14f38b15157a9c9cd2828861f6904701a29b1e27507a7e43d60030e1ae4d9238`;
neither move.py, verify.py nor a retained source byte is changed here.
The new endpoint.py embeds all 82,813 core instructions in a fixed
84,803-location graph on 52 tapes with the same four-symbol local language.

Let U be actual selected MOVE24472, and write its complete tensor factors
as `U=L F R`, with `F=C^(tensor f)` and L,R the source monomials. Supply
the same complete packed `[P] x [2^f]^9 x [S]` array with r Gaussian
coefficients and original signed MSB component width w>=2. HEADER still
contains `Gamma(f,r,P,S,w,cutoff)` and may have an opaque tail. Require
positive parameters, `f<=cutoff`, and a common grid on which both the input
x and intended complete output y=Ux have Gaussian-integral numerators in
the symmetric endpoint range

`[-M,M]`, where `M=2^(w-1)-1`.

This is the **supplied endpoint promise**. It does not assert that an actual
selected caller produces those endpoints. Put

`k=floor((f+2)/4)=ceil(floor(f/2)/2)`, `w'=w+2k`,

`N=PSr2^(9f)`, `V=2Nw`, `V'=2Nw'`.

The new fixed program returns exactly y on the original public DATA owner
and the original grid/width, with all 52 heads, private bodies/guards and
opaque exteriors restored on success. It physically supplies scaling,
width/header conversion, the unchanged literal core, exact unscaling,
whole-call staging, sole final public commit and retirement. Its complete
direct bounds are

`T<=2^26(fV'+E+1)`,

`K_final<=K_entry+4096(V'+E+1)`,

where E is the actual original six-code length. All public and private
history is included in K_entry, and erasure never subtracts it. The grid
is unchanged: the temporary semantic numerator is multiplied by `2^k`,
then divided exactly. V', rather than the smaller V, is paid. This remains
a direct reference/leaf implementation, not a recursive `f^sigma` supplier,
caller admission, global assumption discharge, new kappa or multiplier.

## 2. Credited sharp integral scale and endpoint width

Nick Petalas #7468 at `8b0dd714d30e9c1574387587eb6418ae99ac34e1` proves the
sharp integral prefix scale for endpoint-integral C tensors. Its unchanged
proof is retained in endpoint-reference and pinned in ENDPOINT-SOURCES.json.
For `pi=1+i`, `pi C` and `pi C^-1` are Gaussian integral. If b and Fb are
Gaussian integral and S contains j axes, then C_S b belongs to both
`pi^-j O` and `pi^-(f-j) O`, coordinatewise, where O=Z[i]. Their intersection
is `pi^-d O` with `d=min(j,f-j)`. Therefore `2^k C_S b` is integral for all S.
The common binary scale and its matching lower bounds are credited #7468,
not reproved or claimed new by this physical wrapper.

The induced real/imaginary component maximum norm of `C^(tensor j)` and
its inverse is `2^ceil(j/2)`. This is known norm lineage, including
#7211/#2772/#3089/#3091. To check the normalization directly, each tensor
coefficient is a Gaussian unit times `(1+i)^j/2^j`. When j=2t each real row
has `2^j` nonzero real-component coefficients of magnitude `2^-t`; when
j=2t+1 it has `2*2^j` coefficients of magnitude `2^-(t+1)`. The row absolute
sums give the stated component norms; conjugation gives the same inverse
norm. Consequently, if both b and Fb have component magnitude <=M,

`|C_S b|_component <= min(2^ceil(j/2),2^ceil((f-j)/2)) M
                      =2^ceil(d/2) M`.

The second bound uses `C_S b=C_(S-complement)^(-1) Fb`. Thus all scaled
prefix components have magnitude at most `2^(2k)M`. They fit the symmetric
signed width w+2k, since

`2^(2k)(2^(w-1)-1) <= 2^(w+2k-1)-1`.

The crucial transfer direction for this actual MOVE is **b=R x and
Fb=L^-1 y**. L,R and their inverses are address permutations times unit
Gaussian phases, including their complete f-column constants. They preserve
Gaussian integrality and component maximum. The supplied x,y endpoint
promise therefore supplies exactly the two central endpoints needed above.
Scaling by `2^k` commutes with every factor of the complex-linear MOVE.
The frozen core's phase/range and all C-prefix predicates follow at width
w', so it accepts and returns exactly `2^k y`. No stronger original
`2^f` input divisibility assumption is used by this wrapper.

The common width is sharp for the fixed common scale `2^k` under this
symmetric endpoint promise. At a cut with d=min(j,f-j), choose d axes in S
and d outside. On those 2d axes let z be `2^ceil(d/2)` times the zero-address
impulse, and put the all-ones tensor factor on every unused axis. Set
`b=C_S^-1 z`, `Fb=C_(S-complement) z`. Both endpoints have Gaussian-integral
components in {0,+/-1,+/-i,+/-1+/-i}, with component maximum one. At a middle
cut the scaled prefix reaches positive `2^(2k)M` after multiplication by M;
one fewer signed bit cannot hold it for w>=2. Monomial inverses transfer this
witness to x,y. This is optimal common width for this fixed common scale,
not an optimality claim over adaptive grids, input-specific scales, different
algorithms or variable-width schedules.

## 3. Literal header, scale count and generated complete geometry

Public ports are HEADER=0 and DATA=1. Wrapper-private ports 2,...,22 are
WH, WD, OUTPUT, traces and a fixed set of metadata roles. The core's 31
ports are relocated injectively to `(WH,WD,23,24,...,51)`. Its public
HEADER/DATA thus become private WH/WD; all 29 core-private owners are
disjoint from every wrapper role and the real public owners. Its fixed
jumps are relocated and its successful halt becomes one unit-cost goto.

The wrapper installs guards only on its own 21 roles. Its Gamma decoder
copies the original first four complete codes into WH while decoding
f,r,P,S to unary guides. It decodes the fifth, w, without copying it. Every
public header advance records HTRACE. The original w>=2 is checked locally.
No decoded number is held in the machine control.

The actual unary F loop runs a four-state remainder counter initialized
at state two. Each F mark advances the remainder, and crossing 3->0 writes
one K mark. On completion K has exactly `(f+2)//4` marks, including zero
marks for f=1; F and K return to origin. The graph appends w unary marks and
twice k unary marks to form WIDE=w'. This is an input-size-independent
finite graph with a runtime loop, not unrolling in f.

To emit Gamma(w'), WIDE is copied to TMP. Alternating TMP and HALF, each
floor-halving pass consumes pairs of unary marks, leaves the quotient on
the other tape and pushes one parity digit on DIGITS. The geometric sum
of consumed lengths is <=2w'. When the quotient is zero, popping DIGITS
emits the canonical MSB binary word on BINARY and retires both unary work
roles and DIGITS. Its exact helper census is

`19w'-12popcount(w')+19ell(w')+7`,

or one more with the unit-test halt. Scanning this binary word makes a
unary bit-length guide BLEN. The graph writes ell(w')-1 zeroes followed by
the canonical binary word to WH, retiring BINARY. This is Gamma(w') in
O(w') local steps, not a quadratic repeated full-width increment.

The sixth original code is copied by counting its leading zeroes and then
copying exactly that many trailing bits after its first one. The represented
cutoff is never expanded to unary. A very large cutoff costs its encoded
length in E. HTRACE returns the public header head, and WH rewinds to its
private guard. WH now contains exactly Gamma(f,r,P,S,w',cutoff), followed by
a blank; the original public six codes and opaque tail are unchanged.

The component clock COUNT is physically generated as `2PSr2^(9f)`: two
ordinary unary guide products, nine actual doublings for every F mark and
one final doubling. It is exactly the number of real/imaginary components,
not the number of Gaussian coefficients. Products, doubling, F control,
head return and temporary guide retirement are literal instructions.
There is no supplied collapsed volume or host arithmetic service.

## 4. Literal signed ingress and exact egress

For each of COUNT components, ingress reads its original sign bit, emits k
copies of that bit, copies all w original bits, then emits k zeroes. The
complete w'=w+2k bit string is the two's-complement representation of
`2^k` times the original signed integer. This follows by sign extension to
w+k bits, which preserves its value, then shifting left k bits into width
w+2k. The loops use the actual K and WIDTH guides and return both after
each component. Every public DATA advance writes TRACE. After exactly
COUNT components, the graph requires DATA's next cell to be blank, returns
its original head by consuming TRACE and rewinds WD to its guard.

The transformation changes only component format. The order remains real
then imaginary, coefficient, S spectator, all nine complete native axes,
then P outer row. WD is exactly the original complete packed array with
width w', not a strided view or a selection of active coefficients. All
tensor/spectator addresses are preserved. HEADER and DATA values remain
original throughout conversion and core execution.

The literal core now has its actual legal private packet. WH and WD are at
their origins; all 29 core-private owners are blank with distinct supplied
windows, untouched by the wrapper. Section 2 supplies its exact numerical
predicate at w'. Its sixth cutoff remains the original cutoff. The core
returns WH unchanged and WD=`2^k y`, every head restored and every mapped
core-private body/guard blank. The wrapper guides were not core ports and
remain live, unchanged and at origin.

Egress again runs COUNT components. It remembers the first widened sign
bit in finite control, checks k leading bits all equal it, then checks the
first retained middle bit equals the same sign. It copies the next w bits
into OUTPUT and checks the final k bits are zero. Thus it accepts precisely
the redundant k-bit sign extension of a w-bit integer followed by k zeroes.
These checks are necessary and sufficient for exact division by `2^k`
whose result fits signed w bits. They handle negative values, not merely
unsigned dropping; when k=0 they become the identity conversion.
The extra symmetric endpoint promise was used to prove core admission;
the egress guard itself accepts the ordinary signed w-bit representable
range. No rounding, truncation or signed overflow is hidden in this step.

Every WD advance records TRACE. After all complete components, the next
cell must be blank; TRACE returns WD to origin, OUTPUT rewinds to its guard,
and COUNT returns. All numerical and cardinality guards occur before any
public DATA write. The wide source is retained until cleanup rather than
silently deallocated or aliased with OUTPUT.

## 5. Original-owner commit, rejection and successful reuse

Only after complete egress does the graph copy OUTPUT to original public
DATA, erase OUTPUT, record public advances on TRACE, return the public head
and rewind the blank OUTPUT. It writes precisely V public bits. The table
contains no earlier write to public DATA and no write to public HEADER.
Every wrapper role is then explicitly cleared using its local guard; its
guard is erased and its head returned. The core's 29 private roles were
already cleared by the unchanged core. All 52 owners, public opaque tails
and private exteriors are retained.

Finite acquisition/conversion/core rejection before that final commit
preserves both original public values, including when WD or OUTPUT contain
partial work. Failure heads, private retirement, interruption rollback and
same-bank retry after rejection are not claimed. A valid endpoint-promised
packet does not take these rejecting paths. A later smaller successful
packet can reuse the same physical owners because every private cell is
blank on success and every head is restored. It scans only current guide
and body lengths. Historical backing and older blank tails remain charged;
they are not scanned merely because a larger prior call used them.

## 6. Complete conversion/core time and retained history

Let E' be the actual private six-code header length. Only the width code
changes. Since `ell(w')<=w'` and `w'<=V'`,

`E'<=E+2w'<=E+2V'`.

All costs count every local instruction, including branches, fixed jumps,
head returns, guard setup, copying, erasure and terminal replacements.
The core's halt is replaced by one goto of the same unit cost. Its complete
bill is the unchanged `2^24(fV'+E'+1)`; its internal transaction, complete
child and every enlarged signed scalar row are included at V'. There is
no uncounted recursive child or numeric callback.

Here are conservative allowances for **all additional** wrapper work:

| Additional operation | Complete allowance |
|---|---|
| guard setup, six-code acquisition/return, k and w', Gamma(w') | `2^14(V'+E+1)` |
| generated COUNT, products, all doublings and resets | `2^14(V'+1)` |
| complete signed ingress, public return, WD and guide returns | `256(V'+1)` |
| complete exact egress, WD/OUTPUT and guide returns | `256(V'+1)` |
| public commit, all wrapper clearing/guards and halt | `4096(V'+E+1)` |

The allowances can be checked directly from the emitted loops. A Gamma
field of value n takes <256(n+1) steps, including the optional encoded copy:
strict binary prefix values sum to <n, and each `v->2v+b` round uses only
constantly many scans of v and 2v+b. The b=1 append in this implementation
scans its actual unary DOUBLE, not a host append. All five decoded values
are <=V'. k takes <16(f+1) steps. WIDE/TMP copies are linear in w'; the exact
floor-halving census above is <38w'+8, and Gamma prefix/binary emission is
<64(ell(w')+1). Encoded cutoff copy and HTRACE return are linear in E.
These bounds are far below the first allowance.

For COUNT, unary products have the same fixed nested scan/return pattern as
the credited module. Both product results are <=N. The sum of old lengths
over its `9f+1` doublings is <COUNT; each doubling costs `47n+18` with the
retained copy/clear pattern. There are O(f) fixed loop/reset instructions,
not f scans of the final clock. Thus the second allowance includes all
component-clock construction.

One ingress component costs at most `12w+16k+16` before full-field returns;
one egress component costs at most `12w+20k+17`. Both are <=`24w'` for w>=2.
Their full source/output/clock returns add O(V') with explicit trace/rewind
prices `5n+3` and `3n+3`. The stated 256 allowances therefore include every
component, trace cell and guide reset. No full address word or descriptor
is rescanned per payload bit. Commit plus its returns costs `16V+7`.
Finally, every wrapper-private role's current visited cap is <=`2V'+E`;
there are 21 roles, and clear costs `7n+4`, followed by three guard-retirement
instructions per role. This is below the last allowance. The generous sum
of all five rows is <`2^20(V'+E+1)`.

Combining this with the core, using f>=1, gives

`T<=2^24(fV'+E'+1)+2^20(V'+E+1)`

` <=2^24(3fV'+E+1)+2^20(V'+E+1)`

` <=2^26(fV'+E+1)`.

The widened representation is material: V' is used in the core's copy,
scalar and full-axis work as well as in these conversion rows. The original
cutoff is not replaced by f or expanded into unary. This direct bill is
O(fV'+E). A fixed leaf cutoff makes f bounded; no recursive selected-rate
tariff follows from this inequality.

For backing, WH has length E'; WD has V' bits, OUTPUT has V<=V', TRACE has
at most V', HTRACE has E, COUNT/DOUBLE/AUX at most V', every unary width or
size guide at most V', and binary/code guides at most V'+E. With endpoints
and guards, the 21 wrapper roles add at most `42V'+21E+42` visited positions.
The original public head intervals add at most V'+E+2. These are below
`64(V'+E+1)`. Add the core's full additional history bound
`1024(V'+E'+1)<=3072(V'+E+1)`. Hence the complete increase is less than
`3136(V'+E+1)`, below the declared 4096 allowance. All 52 owners and actual
earlier backing remain in K_entry. Overlap is conservatively double counted,
never erased from the ledger. No private field earns productive credit.

At fixed origins successful reuse keeps per-owner interval unions. Changed
origins require absolute historical unions and separately paid transport
corridors; the wrapper does not make those free. Supplied private blank
windows, the public packet and opaque entry backing are included in actual
entry storage. Test-fixture creation is not a runtime allocation theorem.

## 7. Executed coverage and limits

endpoint_verify.py is standard-library only and does not alter the frozen
core verifier. It executes the emitted fixed graphs with a dense local CPU.
Forty-one complete header producers through f=1023 reproduce the exact
widened header and live guide state, preserving public opaque tails. All
copy a cutoff whose value has 258 bits without unary expansion. The 135
literal binary encoders through unary 1024 match the exact instruction
census. One hundred small-stream ingress/egress executions cover k=0,1,2,3,4,8,16
at selected f values and original widths 2,3,4,7,17, including negative
endpoints, the most-negative signed value, zero and positive maxima.
Ninety changed low-zero or retained-sign inputs reject before public writes.
These are tests of the actual shared converter subgraphs at their explicitly
supplied unary WIDTH/K/COUNT boundary, not complete native f>=2 executions.

The complete full-field f=1 wrapper runs 14,784,628 local transitions on
4096 bits. A direct Gaussian native kernel oracle agrees; exactly V public
writes occur only after egress, all 52 heads/private/exteriors are restored,
and observed visited-span history is 82,251. f=1 has k=0. Nonzero-k evidence
comes from the explicit converter/header boundaries; no full f=2 joined
tape replay is claimed. The universal statement rests on sections 2--6,
not on replacing a full array by a reduced native dimension or sampled prefix.

No selected producer has been shown to satisfy the exact endpoint promise,
and old-codec/strided packing, actual source occurrence emission/owner
transport, global stock/reset, faster nonleaf work, the complete compiler,
precision and analytic recovery applications remain open. All five selected
assumptions and conditional kappa are unchanged. No cold selected replay,
formal proof-kernel or independent human acceptance is claimed.
