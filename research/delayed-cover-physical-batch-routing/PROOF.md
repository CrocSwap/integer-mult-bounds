# A physical low-type splitter for whole-high delayed-cover batches

This is a physical realization of one existing address map, not a new cover,
Gaussian supplier or multiplication theorem. The whole-high batch geometry is
Ali Romman's PR5829. The seven-symbol machine, finite assembler and exact
binary-to-unary counter are David Arias's PR2776 sources, copied unchanged with
their notices. The new contribution is the fixed-control split/merge table at
the actual delayed-cover batch boundary, including binary setup, restoration,
erasure and visited-space accounting. New work: thu-nmrc with substantial OpenAI
Codex and parallel-agent assistance, Apache-2.0. Reviews here are author-side.

## Quantified statement and physical ABI

For every fixed integer L>=2, `router.build(L, merge=False)` and
`router.build(L, merge=True)` compile two finite programs on L+7 physical tapes
over seven symbols. The assembler receives only L and the fixed direction.
Both tables are independent of the positive runtime integers A,R, every atom
width, recursion depth and payload. Put V=A*L*R.

The split input is an arbitrary binary stream in lexicographic (a,l,r) order,
0<=a<A, 0<=l<L, 0<=r<R. It returns one stream per fixed l, in (a,r) order.
The merge accepts arbitrary such streams, including child outputs different
from the original input, and restores their (a,l,r) order on one output stream.
The source streams are preserved. New output copies are owned storage and
receive no productive credit.

Input streams and positive canonical least-significant-bit-first binary A,R
have LEFT at local position0, their symbols at1,...,length, RIGHT next, and
their heads at1. A binary data zero is ZERO, not the physical BLANK. Thus an
encoded logical blank may be included in an opaque payload without terminating
it. Destination and conversion tapes start physically blank at their specified
local origin0. Their complete local work extents must be available and the
ports distinct. Other backing and inaccessible ancestor prefixes may exist;
their entry footprint K_entry is not deallocated or counted as free space.

The tables restore input and descriptor heads to1, preserve their bytes and
markers, return each marked output head to1, and erase all conversion work,
unary guides and installed scratch markers, with scratch heads at0. Every
valid execution uses at most94V microtransitions and13V newly visited local
cells, so total retained backing is bounded by K_entry+13V. These are bounds
for each isolated direction, not an uncharged whole-caller invoice.

Each emitted instruction branches on one scanned symbol, writes one symbol,
moves one head by one cell, jumps to a fixed state, halts or rejects. It is
directly a transition of a finite multitape machine. The program cannot read
the interpreter's head coordinates, elapsed count, dictionaries or payload
lists. L is a finite unrolling of low types; no runtime high matrix becomes
a new tape or program state. The input encoding is a contract: this is not a
claim that every malformed global backing store is recognized before writing.

## Loop and return invariant

The retained counter converts the positive binary A and R into unary guides,
preserving both descriptors and reusing one blanked binary work tape. It emits
all descriptor processing as microinstructions. At the start of repeat a, the
source split head has consumed a*L*R bits and each destination has a*R bits.
The unary A head is at mark a. For each of the finitely unrolled l values, the
R guide is rewound to its first mark and exactly R opaque bits are copied.
Both ZERO and ONE take equal-length paths; the source is never overwritten.
At the guide's RIGHT marker, the next fixed low type begins. After L blocks,
the A guide advances one mark. This reestablishes the invariant for a+1.

On A's RIGHT marker, all V source bits have been copied. The input RIGHT check
rejects a long input and each bit check rejects a short input. Output terminators
are written, inputs and outputs rewound to their own LEFT markers, and all
scratch is erased backward through its local origin. No head crosses a valid
local LEFT marker. The merge uses the same induction, replacing the single
source by the fixed l-th source and writing all blocks to one destination.
It therefore reconstructs arbitrary returned data at its exact parent address,
without substituting the saved original input for a child result.

## Exact action and visited-space ledgers

Let ell(x)=bit_length(x), pop(x)=popcount(x). The unchanged counter's proof gives

    c(x)=24x-7pop(x)+15ell(x)+12 <=44x.

For either direction let d be its number of destinations: d=L for split and
d=1 for merge. Counting the actual table paths gives

    T=c(A)+c(R)+18V+4AL+7A+R+4L+3d+33.             (1)

Here copying all blocks and rewinding R costs12V+4AL-3R. The A loop costs
3A+1; marker setup costs3d+9. Input end checks cost one in split and L in
merge; writing output terminators costs d, and all source/destination returns
cost6V+3(L+1). Scratch erasure costs4(A+R)+18, and the final halt costs one.
These terms sum to (1). Both data symbols have identical paths, so (1) does
not depend on payload bits. It includes failed terminal tests and fixed jumps.

For A,R>=1 and L>=2, A+R<=2AR<=V, AL<=V, A,R<=V/2, L<=V and V>=2.
Thus c(A)+c(R)<=44V, 4AL<=4V, 7A+R<=4V, 4L+3d<=7V and33<=16.5V.
Equation(1) gives T<=93.5V<=94V. Split at L=2,A=R=1 attains187 steps on
V=2; merge takes184. The bound is proved by these inequalities, not fitted to
finite execution times.

All visited sets are contained in the listed contiguous local extents:

| Physical extents | Total span |
| --- | ---: |
| Single stream and all fixed low-type banks | 2V+2L+2 |
| Two preserved binary descriptors | ell(A)+ell(R)+4 |
| Two unary guides | A+R+4 |
| Reused binary conversion work | max(ell(A),ell(R))+2 |

The total is exactly

    S=2V+A+R+ell(A)+ell(R)+max(ell(A),ell(R))+2L+12.     (2)

In particular ell(A)+ell(R)<=A+R<=V and max(ell(A),ell(R))<=AR<=V/2.
Therefore S<=12.5V<=13V, with25 cells at the smallest V=2 instance. Erasing
a cell never removes it from this bill. Equation(2) bounds every execution
prefix, including setup and completed but blanked scratch. Tapes not used by
one direction contribute only their fixed entry inventory to K_entry.

## Binding to the actual delayed-cover child batch

Fix the final finite template B,N,q, as in the retained bridge. Let

    G=|GL_N(F_q)|, H=q^(N*N*(w-1)), L=B*G,
    P=T*(L*H)^D, root volume=P*R_body.

The compiled L tapes are fixed before w varies. For a child edge take D>=1
and 0<=j<D; at a leaf j=D there is no such split. The predecessor's
current parent row and returned child row are

    b =(U_prime*(L*H)+l*H+h)*H^j+ancestor,
    b'=(U_prime*H+h)*H^j+ancestor.

Retain all h in[H] and all ancestor in[H^j]. In the physical lexicographic parent
stream, for each U_prime and l the (h,ancestor,body) portion is one contiguous
block. The splitter's positive binary descriptors are exactly

    A=T*(L*H)^(D-j-1), R=H^(j+1)*R_body.

Deleting l preserves that block's complete order, which is precisely b' and
the unchanged body coordinate. Each child bank has V_parent/L bits; no high
matrix, original independent input, row reserve or body spectator was dropped.
The merge's inverse deletion reinstalls the complete returned child batch in
its original parent order. This equality is an identity of integer addresses
for every allowed w,D,j,T,R_body, not an inference from small-field tests.

Consequently this supplies a literal O(V_parent) fixed-port routing macro and
local O(V_parent) visited-space bound for the specific split/return edge left
abstract in PR5829. It consumes valid binary extents; constructing those extents,
evaluating generated weights, and executing right-matchers/fallbacks are separate
source-bound routines. None is declared free by this theorem. The address map,
fresh-cylinder theorem, volume divisor L, ancestor-weight independence and
geometric active-chain argument remain predecessor results.

The segmented allocator can confine these local tapes using its existing
symbol codec, park a parent, copy the designated child batch to a bridge,
and save a changed child output before pop. This theorem by itself does not
prove that the selected full compiler emits that production schedule, or supply
the Gaussian child, weight evaluator or old-BIT primitive. A composed physical
fixture must distinguish those interfaces from its named semantic leaf.

`composition/PROOF.md` and its actual physical program supply one such
source-bound composition for each fixed L, with K=max(16,L+8) payload tapes
and seven control/relay/grant tapes. Binary child-shape grants
and a zero/one-edge unary descriptor are physical inputs. Two sequential sibling
calls execute the unchanged router tables through a stateless three-bit codec,
park actual parent packets, and save changed child outputs before destructive
pop. The semantic leaf complements bits and is explicitly not a Gaussian child.
The child grants obey A_parent=L*H*A_child and R_child=H*R_parent.
For the actual two-level source edge R_parent=H*R_body and
R_child=H^2*R_body. The exact identity, with
a_parent=(a_child*L+l_child)*H+h_child and
r_child=h_child*R_parent+r_parent, is

    a_parent*R_parent+r_parent
      =(a_child*L+l_child)*R_child+r_child.

Thus the child retains both high fields and every ancestor/body bit; matching
volumes alone would be insufficient. A child and its parent both split only
when D>=j+2. The finite evidence has33 exact fixtures,
including all sixteen four-bit root inputs, real H2/H3 shape changes and an
L9 case with24 tapes and return slot16. It does not claim an arbitrary-depth
production traversal or a free generated-descriptor evaluator.

## Evidence and remaining obligations

The read-only checker authenticates all retained source bytes, executes both
literal tables on110 arbitrary-data/descriptor fixtures, and compares actual
physical outputs to coordinate-product expectations. The largest isolated
fixture has all96 low types and81 high matrices of the two-role GL2(Z/9Z)
layout. Additional complete address cases use the actual retained PR5829
Layout.split/join functions at every tested depth. Six malformed-input controls
exercise short/long sources, physical holes, nonpositive/noncanonical extents
and occupied owned output. These are implementation evidence for the written
unbounded induction, not formal-kernel verification or external human review.
The separately written interpreter in `independent/` checks198 split/merge
cases and256 counter cases without executing the producer's Machine/Tape
classes, together with an independent static review of the unbounded proof.

Open next questions are the production descriptor/weight evaluator, the actual
route and fallback local-space applications, the full compiled dispatcher and
its precision/owned-child return. All five project assumptions remain retained.
There is no new kappa, paid-profile change, selected-frontier update, complete
multiplier or scientific-admission claim in this package.
