# Independent review of the literal positive C leaf

**Disposition: accepted for the stated packed, positive, all-column direct-leaf
interface.** This review establishes no complete MOVE, old-format bridge, new
kappa, or unconditional multiplication theorem. Root's separately written
full-packet runtime review is a separate receipt.

Reviewed at canonical base `e54523517d0f03e58352e647c403a5af3e525a57`:

- `leaf.py`: `bb46c1a55f1119957a52cd61f2cd957f3f7ad1e9b818c54a852bde09a0773744`.
- `PROOF.md`: `c99157c3c43ae490b858cdbce04d85f3661ca5d9752770506d18ec4876c4ed6c`.
- Fixed graph and alphabet, canonical sorted compact JSON:
  `ac8f5e05a4e0264e94eacb7887b568bead2cce5583607b5047ac560aaf434dc9`.

The reviewer was the separately executing worker B, with OpenAI assistance,
working for Jerry Chen / @CubeJerry. No author science file was edited. Two
requested clarifications were applied by the author: the suffix-stream caps
use the maximum `U*`, and private-owner versus all-owner historical accounting
is explicit. The code and table did not change. The suggested final-only
integrality counterexample was also included before the reviewed proof froze.

## 1. Exact source and admission

I checked all eleven retained source files against their byte hashes and the
actual Git objects at each specified `commit:path`; `check.py` records the
objects in its receipt. In particular, the selected native artifact is the
current #7000 word, not the historical #6030 word used by #6967. Its event
24472 is exactly `["MOVE",415,3,99,false]`, with frames `[]` and `[239]`.
The retained source lowers the rank-one child as right monomial, positive
`fourier(...,range(1))`, then left monomial. `cgate` defaults to positive sign.
Thus the central matrix is

`C = [[1+i,1-i],[1-i,1+i]]/2`.

The denominator and its sign are essential. Neither the full source MOVE nor
one of its monomial factors is identified with this central operation. The
rank is one coordinate in each column. With f columns, that means f separate
C factors on the f bits of coordinate zero.

The packed input is exactly `[P] x [2^f]^9 x [S]`, with r Gaussian w-bit MSB
pairs at each address. The first five Gamma fields are those of the published
literal phase package at `172f4535ce8dcff79f626410af845f757c1563be`; a sixth
Gamma field supplies the cutoff. The old #6967 twenty-three-field, coded-LSB
ABI is different and remains an explicit caller obligation. The theorem
requires positive f,r,P,S,cutoff, w>=2, actual f<=cutoff, complete payload, and
the private blank-window/owner premises. No host-origin, stride or coefficient
provider is supplied by the checker or smuggled into the program.

## 2. Numerical invariant and all-column domain

For an independent arithmetic oracle I used the Walsh spectral formula

`C = H diag(1,i) H / 2`, where `H=[[1,1],[1,-1]]`.

The k-axis coefficient at row y, column x is consequently

`2^-k sum_z (-1)^((x xor y) dot z) i^popcount(z)`.

This oracle uses exact rational Gaussian coordinates and a frequency sum. It
does not use the author's product-of-Gaussian-factors oracle, butterfly loop,
or expected-value implementation. It independently derives the four scalar
numerator rows and checks the exact kernels for k=1 through 8, including row
unitarity and the constant-fibre eigenvalue one.

Universally, with pi=1+i, the equivalent identity
`C=pi^-1 [[i,1],[1,i]]` makes every k-factor entry a Gaussian unit times
`pi^-k`. At k=2s exactly one coordinate of each entry has magnitude 2^-s;
at k=2s+1 both have magnitude 2^-(s+1). Hence the common binary denominator
is sharply `2^ceil(k/2)` and a real-component row has l1 norm
`2^ceil(k/2)`. This proves the inherited sufficient reserve/headroom condition
for every completed prefix, rather than treating finite k checks as the
universal proof. These statements are credited #3091/predecessor results,
not new mathematics in this package.

The actual accepting domain is broader: each executed axis must produce
integral components fitting the signed width. A final tensor endpoint alone
does not imply this. At f=2, the real fibre `[1,0,0,1]` has exact final output
`[0,1,1,0]`, but its first low-bit pairs have half-integral output. Correct
execution rejects it before a public write. Constant fibres with every real
and imaginary component equal to `-2^(w-1)` are fixed by C and are accepted;
this rules out implementations that negate the minimum value in an
insufficiently wide temporary.

For the scalar lowering, let the original component bound be L=2^(w-1).
Each row has three positive terms and one negative term, so its exact
numerator belongs to `[-4L+1,4L-3]`. The finite carry set {-1,0,1,2} is closed
under the emitted digit recurrence. The written digit identity gives an
induction for every width. Two sign-extension steps produce a w+2-bit
representative in a range that identifies it uniquely with the actual
numerator. Testing its low bit gives exact divisibility by two. Equality of
the two highest remaining sign bits is exactly signed w-bit fit of the half.
The emitted MSB bits therefore represent the intended result, including the
most-negative endpoint. The private unhalved numerator is never restricted
to w bits.

## 3. Physical geometry, ordering and lifecycle

At axis j, the two halves within a prefix have

`A_j=P 2^(f-1-j)`, `U_j=Sr 2^(8f+j)`, and `2 A_j U_j=N`.

Writing a physical coefficient slot as
`(outer*2^f + coordinate)*tail + rest`, with `tail=Sr2^(8f)`, replacing the
half side maps it precisely to the slot with `coordinate xor 2^j` and the
same outer/rest values. This is an exact integer identity. The independent
checker probes it in 432 axis geometries and 10,224 full-integer addresses,
including first/last/interior spectator positions; these are checks of that
identity, not an exhaustive claim over arbitrary inputs.

The encoded construction doubles U eight times per F mark and P f-1 times.
Each subsequent axis doubles U and halves an even A, and F advances exactly
once. This proves the f-loop and its low-bit-first order without treating
rank one as f=1. Splitting two whole suffixes, operating corresponding
Gaussian pairs, and merging left then right preserves every spectator and
coefficient position. The target bank is complete before either bank is
rewound and MODE changes. No payload address is computed by the controller.

The original DATA is cloned and returned before any numerical work. The
clone checks exactly V binary cells and then a blank. All exactness and
range failures happen in private storage, before the final commit. Width
and cutoff failures happen earlier. Thus the public DATA and HEADER remain
unchanged on the stated failures. Private cleanup and head return after
failure are expressly absent; I do not infer a retry contract from public
atomicity. On success the bank/suffix/component induction gives complete
retirement, original-owner DATA installation, and every original head. The
commit has no unverified numerical branch: its source is an already proved
complete binary bank.

## 4. Independently counted full work and backing

I counted the actual emitted local instructions, including reads, jumps,
rewinds and halt. Important exact prices (without an artificial wrapper
halt) are:

| Operation | Cost |
| --- | --- |
| Successful scalar `c_component` | `43w+57` |
| One complete half load of U coefficients | `28Uw+14U+7` |
| One complete prefix, including both loads, all arithmetic, merges and local returns | `372Uw+306U+45` |
| One complete axis, through the branch selecting finish/next-axis | `99V+153N+48A+16` |
| Next-axis geometry update and jump | `47U+15A+33` |
| Initial complete source clone and return | `20V+14N+14A+11` |
| Commit itself, including trace return and bank return | `16V+7` |

The checker independently executes isolated component graphs and 27 isolated
axis slices to confirm the exact counts. The small axis slices use arbitrary
positive guide lengths to test the subroutine census; they are explicitly not
claimed to be complete selected nine-coordinate arrays. The exact algebra
of these counts follows from the fixed loops and is independent of payload
values whenever the call succeeds.

For w>=2, N<=V/4 and A,U<=N/2. A complete axis plus its possible geometry
update is therefore at most `151V+49`, well inside the author's allowance
`8192(V+1)`. The separately verified unary helper prices bound all initial
geometric sums. Gamma conversion for the first five values is bounded by
the sum of represented values, each <=V; the cutoff is never converted to
unary. Its binary acquisition, length comparison and cleanup cost O(E),
even when its value is arbitrarily larger than V. These observations pay
header repetition, copy, helper scans, source clone, all axes, public commit
and cleanup within the stated `65536(fV+E+1)` envelope. This is a direct-leaf
bill; the old-codec bridge, input transport and nonleaf work remain outside
it and must be charged by a caller.

I checked the per-role maximum-capacity argument. In particular DOUBLE never
exceeds the largest final guide; each of LEFT/RIGHT/LOUT/ROUT has cap
`2wU*`, and all component/NUM banks have fixed roles. There are twenty
volume-bounded roles, six header-bounded roles and MODE. Including endpoints
and guards gives `20V+6E+57`. This bounds new visits, not total history after
erasure. For private owners the total is previous private history plus this
increment. For all 29 owners, adding at most V+E+2 public positions still
fits the same conservative `64(V+E+1)` envelope, with the full prior source
and opaque history included in K0. Repeated calls require per-role history
unions/maxima, not a maximum current aggregate volume. Relocated entry
origins also require their actual transport corridors. The corrected proof
states these distinctions explicitly.

## 5. Independent finite evidence and controls

`check.py` imports the frozen compiler only to obtain its local instructions;
it uses its own CPU for the reviewed helper graphs and uses the exact
spectral oracle above for expected arithmetic. It never imports the author
checker or calls the author's `Machine`. It checks:

- All 17,408 scalar-row instances from every four-component input at widths
  two and three, plus 120 wide endpoint instances through width 2,048.
- 17,528 total component cases, 8,132 accepts, and 4,994,452 independently
  interpreted local transitions, including exact successful cost and private
  numerator retirement.
- Twenty-seven complete axis cost slices, with 875,232 local transitions,
  target/input-bank retirement and returned local heads.
- The fixed 6,826-location/29-tape/four-symbol local language, all 256 finite
  carry branches, and absence of unary value expansion in the cutoff decoder.
- All eleven exact Git source bindings in this run.

Three changed local programs are detected: accepting an odd numerator,
using conjugated/wrong C signs, and a functionally unchanged extra instruction
that violates the exact helper cost census. The latter is a census control,
not a claim that one extra instruction violates the generous asymptotic
budget. Root independently checks full packet execution; the author also
reports a genuinely complete f=2 run. Those are distinct from this review's
helper and universal-proof methods.

Reproduce from the package root after these artifacts are retained there:

```sh
python -I -W error -B independent/peer/check.py .
python -I -O -W error -B independent/peer/check.py .
```

For this run, replace the script path with `reviews/c4-peer/check.py` and
pass `worker-c4/research/literal-positive-c-leaf`. Normal and optimized receipts
must agree. Git-object authentication is repeated when the shared repository
objects are available; portable execution without that checkout still checks
all retained source byte pins and the frozen science/graph identities. The
saved receipt records the actual authenticated Git objects from this review.

The remaining obligations are the ones the package lists: actual full source
MOVE composition, both surrounding monomials and placement, old-format
conversion, cutoff/precision admission, caller lifecycle requirements,
nonleaf tariffs and the five global foundational assumptions. None is
silently supplied by this acceptance.
