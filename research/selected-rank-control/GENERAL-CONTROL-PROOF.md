# Online rank-dependent recursion on three fixed tapes

Prepared for @CubeJerry with substantial OpenAI assistance; Apache-2.0.
Written all-width theorem with finite executable corroboration. No kernel proof.

## 1. Domain and theorem

Fix integers m>=2 and a nonempty ordered paid list (r_0,...,r_(s-1)), with
1<=r_i<m. These are compile-time constants. For every positive width f, stop
if f<m; otherwise visit all s ordered children of widths floor(r_i*f/m).
Repeated equal ranks remain distinct child sites. Set rho=max_i(r_i/m)<1.
Every internal child width lies in [1,f-1], so the tree is finite.

Input: a marked unary WIDTH stream 1^f, marked-empty CHILD, and STACK at a
blank top h immediately after its original separator. The entire stack below
that separator is arbitrary over the finite alphabet. Origins may be translated
independently. Unused suffixes are blank. K0 counts every retained entry cell,
including arbitrary warm blank backing; it is never declared free by erasure.

The literal three-tape program has exactly

    Q = 10m+13+s(67+3m)+2*sum_i r_i

instruction locations and s+4 symbols. It emits the ordered contour, restores
all initial cells and heads, never visits STACK below h-1 and never writes
below h. No input length, supplied depth/tree, host recursion, run-time
arithmetic, dynamic tape selector or input-sized alphabet chooses an action.
If f_v denotes each visited node width and D is the maximum number of descents,
its complete transition count satisfies

    T <= 100(s+1)*sum_v f_v.

Time depends on s. Retained allocation satisfies

    S <= K0+2(f+2)+f/(1-rho)+D+2
       <= K0+(3+1/(1-rho))*f+6.

Only the backing bound is independent of sibling count. The latter inequality
uses D<=f-1; it deliberately has slack. All historically visited erased prefixes
are included. The finite program is machine control, not run-time storage;
compiling a different fixed profile is outside this theorem.

## 2. Machine and interface

`controller.py` compiles read, write, unit-move, goto, emit and halt instructions.
Each is one global multitape transition; unmentioned tapes stay stationary.
Reads branch solely on the scanned symbol. An emit is a labelled stationary
finite-control edge: E for internal entry, L for leaf, D_i for descent at site i,
U_i for return at site i, and X for completed node. It does not append to a
physical event tape. Python event lists, counters and visited-interval logs are
verifier observations and are never read by an instruction.

A later consumer may be linked to these finite states if its own transitions
are paid and it preserves the controller's three-tape frame at return. No
payload consumer or binary external-descriptor conversion is supplied here.
In particular a materialized event transcript is not free storage.

At enter, the classifier scans at most m WIDTH symbols, rewinds and emits E
or L. Zero width rejects. Internal entries execute the fixed ordered site list.
A completed site's finite tag determines the next site or node completion.
The only changing control value is the finite program state.

## 3. Exact child widths

For fixed rank r, the scanning state stores c in {0,...,m-1}. On each unary
parent symbol it replaces c by (c+r) mod m and appends a CHILD symbol precisely
when c+r>=m. After k symbols, CHILD has floor(rk/m) symbols and c=rk mod m.
Induction on k proves this Euclidean-division invariant. At scan completion,
n=floor(rf/m), and both heads rewind. For internal f>=m and 1<=r<m, 1<=n<f.
Termination follows without a depth descriptor or inspecting payloads.

The source's `divmod` constructs finite transitions at compile time. Neither
`divmod` nor any decoded width appears in `Machine.step`.

## 4. Continuation and restoration

Before descent, parent WIDTH is copied to STACK and erased from WIDTH. The
fixed site tag t_i is appended. CHILD is moved into WIDTH and physically erased;
both heads rewind. D_i is emitted and control jumps to the single enter state.
Thus STACK contains blocks 1^(parent width) t_i along the live ancestor path,
and its head is at the next blank. It contains no dynamic objects or pointers.

On X, one left move reads the preceding tag. If it is the original separator,
the root is complete: advance right and halt without erasing root WIDTH.
Otherwise retire tag t_i, clear/rewind the owned child WIDTH, and copy the
immediately preceding unary parent block back into WIDTH while erasing it.
Stop at the preceding tag or original separator, preserve that symbol, move
STACK right to the old record origin, rewind WIDTH, emit U_i and resume the
next fixed site. Unary reversal does not alter the restored descriptor.

Induction over the finite tree proves the contour and all exact endpoints.
Every push writes at or above its entry top. Every pop reads at most its own
preceding separator and writes only its own record. This proves locality for
every execution prefix; endpoint restoration alone is not used to infer it.
The machine never scans farther ancestors. This is a valid-input theorem;
malformed input need not roll back.

## 5. Complete transition invoice

Literal loop counts for parent f and child n<=f are as follows. They include
terminal reads, delimiter work, erasures and head returns.

| Phase | Bound |
| --- | ---: |
| Generate child and rewind both streams | 6f+5n+8 |
| Park/erase parent, append tag and rewind | 9f+6 |
| Move child into WIDTH and rewind both | 12n+7 |
| D_i and jump to entry | 2 |
| Erase returned child and rewind | 7n+4 |
| Pop parent and rewind | 9f+5 |
| Return dispatch, tag retirement, U_i and successor | 6 |

An n-cell rewind takes 3n+3: one initial left move, three instructions per cell
and two at the marker. Adding the table gives a round trip outside the child
execution of at most 48f+38. Entry classification and E/L take at most 6f+7;
X takes one. The root's final check and halt add at most four.
Internal local cost is therefore at most s(48f+38)+6f+8 and leaf cost at most
6f+8, with that root constant. Since every f_v>=1 and s>=1, summing proves
the stated 100(s+1)*sum_v f_v. Each sibling repeats its own generation and
park/return bill; no sibling-independent time constant is asserted.

## 6. Retained backing and shape inflation

WIDTH and CHILD remain between their fixed marker and an endpoint at most f
cells away, including historical prefixes left blank by smaller later uses.
At an active path f_0=f,f_1,...,f_D, one has f_j<=rho^j*f. STACK holds one
unary parent and one tag per descent. All its visits lie between h-1 and
h+sum_(j<D) f_j+D. Adding the three historical tape intervals gives the stated
K0+2(f+2)+f/(1-rho)+D+2 bound. Every path obeys that same cap and reuses the
same origins. Erased regions are never reclaimed by assumption.

For m=2, three ranks r_i=1, and root f=2^d, the complete tree has exactly
(3^(d+1)-1)/2 nodes. A literal one-symbol-per-node contour needs superlinear
space in f, whereas the online controller uses O(f) backing. The node count is
the geometric series, not an inference from tests. This observation does not
exclude other compressed encodings. The verifier's retained event lists are
outside the machine whose backing is bounded.

## 7. Selected-source compatibility and limitations

The selected #7000 application review, Section 5, keeps the original complete
D-bit root factor in each descendant and partitions only external ROW axes.
If a consumer maintains this invariant, supplies at least one complete root
factor per node, and has f_v<=D, then for D>=1 its logical bit volume satisfies
V_v>=2^D>=D>=f_v. The producer overhead is consequently at most
100(s+1)*sum_v V_v, a fixed node-volume fee. This is a conditional implication;
it does not prove that an actual selected dispatcher has made those grants or
that its exact rank-rounding rule equals this floor recurrence.

Different cutoffs, remainder jobs, multiple backend types and different rank
rounding must be bound to actual source before substitution. This producer does
not emit #6719's H/A/R grants, route payloads, execute native maps or provide
binary-to-unary input conversion. Stock, numerical precision, ownership of
payloads and analytic recovery remain separate. All five selected assumptions
and selected kappa are unchanged.

## 8. Novelty and credit

JoyboyBrian's #5158 already gives physical fixed-bank dyadic complete-row
recursion. Thu-nmrc's #6719 already gives a richer delayed-cover root, recursive
grant and payload program from binary inputs and supplied unary depth. ToikY's
#6722 reviews a specific producer/router join. Their results retain credit;
this does not claim the first fixed-tape recursion or geometric backing proof.

The delta is the rank-dependent termination and heterogeneous-child shape
producer with no supplied depth/tree, arbitrary fixed paid branching, an exact
small transition census and a sibling-independent retained-space bound.
Finite remainder machines, depth-first stacks and geometric sums are standard.
This is one enabling interface theorem, with payload integration and external
descriptor preparation open; no new exponent, assumption discharge, complete
multiplier, independent human verification or proof-kernel acceptance is claimed.
