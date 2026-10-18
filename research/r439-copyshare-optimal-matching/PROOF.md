# Fixed-class optimum and its finite implementation

All circuit identities below are over F2. Positive integer envelopes are
computed separately and never use binary cancellation.

## Recipe and exact cost

Let K be the helper-to-target matrix of the original PR589 D. For an oriented
pair `(a,b)` execute `h[a] ^= h[b]`, rewrite each target's helper reads by
toggling b whenever it reads a, then restore `h[a] ^= h[b]`. For several
disjoint pairs let H be the product of their helper transvections. Disjointness
makes the factors commute and gives `H^2=I`. The middle matrix is K H, hence
the complete target response is `K H H h = K h` for every dirty helper h.
Sources are untouched, targets keep their original identity block and every
helper is restored. No zero-initialization premise is used.

Let S_a and S_b be column supports of K. Right multiplication by H replaces
column b with the symmetric difference of columns a and b. The fully paid
saving from one oriented pair is therefore

`g(a,b) = |S_b| - |S_a symmetric_difference S_b| - 2`.

The last two units pay preparation and restoration. Disjoint pairs affect
distinct columns, so savings add exactly. For an unordered pair define
`w(a,b) = max(g(a,b), g(b,a))`. The best orientation attains w and any
orientation is bounded by it. Nonpositive edges can be omitted when maximizing
saving. Every member of this specified recipe is therefore bounded by an
undirected matching on the 430 allowed helper operands. This reduction does
not apply to overlapping helper changes or a different target basis.

## Checkable upper bound

The certificate supplies nonnegative integer doubled vertex prices q_v and
positive doubled prices z_S on 47 odd subsets. Each subset has distinct
vertices and cardinality at least three. The verifier reconstructs S_v as
ordinary Python sets, independently of the packed-column nomination, and
checks all 92,235 unordered pairs, including nonpositive edges:

`2 w(a,b) <= q_a + q_b + sum(z_S : a,b in S)`.

For any matching M, sum these inequalities. Each vertex occurs at most once
and at most `floor(|S|/2)` matching edges have both endpoints in S. Since all
prices are nonnegative,

`2 weight(M) <= sum(q_v) + sum(z_S floor(|S|/2)) = 12744`.

This elementary counting proof works even for overlapping odd sets; no
matching-polytope theorem, floating point, laminarity or trusted optimizer is
needed. The published 210-pair witness has exact saving 6,372 and attains the
bound. Thus the complete minimum is `24305 - 6372 = 17933` ADDs in this class.
The chosen witness passes both precision guards, so imposing those two guards
does not change this class's ADD minimum. This says nothing about minimizing
F or B subject to that minimum.

## Bounded nomination and comparison

NetworkX 3.6.1 nominated three optima. Sorted and seed-3 insertion order use
ordinary weights w. The third maximizes `L*w - c_destination`, where c_a is
the coefficient of helper a at the largest unchanged positive source/helper
suffix endpoint, and `L=1+sum(c_a)`. All c_a are nonnegative; disjointness means
the total secondary charge lies in `[0,sum(c_a)]`. A unit of primary saving
therefore outweighs every possible secondary change. Each edge uses a
best-saving orientation, breaking equal-gain ties by the smaller c_a. This
proxy need not be the actual maximum intermediate envelope. The chosen point
is simply the smallest-F member of these three exact ADD optima.

The optional nomination captures the solver's vertex/odd-set state, following
PR941's source-hashed introspection technique. Verification independently
checks every resulting inequality and attaining witness. Discovery and replay
are separate: no NetworkX installation is required for the certificate check.
The predecessor PR2487 matching is byte-pinned and freshly invoiced by the
same literal implementation used for the new candidate.

## Frames and chronological boundary

All helper preparation, rewritten injections and restoration occur at the
common zero frame. There are no internal children, allocations, observations,
COPY/ERASEs or frame changes. Helpers and targets already enter at that frame;
sources are never read by D. The endpoint equation holds on arbitrary F2
modules because it is an identity of finite binary matrices. Consequently it
also holds pointwise on the inherited compatible streams.

The actual D and original D give exactly the same entire state and frames at
the D/A cut. Every later gate, source access, frame change, COPY/ERASE and
cleanup operation is unchanged. The original-D virtual splice is exactly the
selected PR589 word and passes the unchanged owner checker. PR1194's
chronological substitution bridge therefore applies under its inherited
common-frame interpretation. No later operation is commuted or reordered.

The replacement violates target-only H2 syntax and the old literal K
extraction, as explicitly reported. Its semantic response remains N=K;
H1, H3, H4, H5, U-block form, J=I and C=U inverse remain true. This does not
silently promote a failed syntactic check to selected supplier admission.

## Complete finite invoice and evidence

The D circuit has 210 + 11,293 + 210 = 11,713 ADDs and the fixed continuation
has 6,220. The literal full-word stream includes all nine COPY/ERASE pairs and
their scatter reads. Every record agrees with the unchanged official exporter;
the latter independently reproduces the frame/COPY profile. Ordered frame
paths are unchanged and a separate owner-based dimension count agrees.

Two literal positive recurrences, one over the constructed stream and one
over official exported records, give F=72,715 and B=1,147,320. Reverse replay
reverses instruction order and swaps COPY with ERASE. Every intermediate ADD
uses addition of nonnegative envelopes, COPY inherits its source and ERASE
resets its slot. These values give strict 104-bit and 192-bit inherited guards.
Every actual helper change and restoration is charged; the proof-only virtual
D is not executed or invoiced a second time.

For each of the three optima, a row-vector replay and a separate numeric
input-column engine check the complete D matrix on all 661 input columns.
The whole literal COPY/ERASE program is checked forward and backward. These
finite replays support the stated algebraic boundary; they are not a formal
proof of an all-size physical multiplication implementation.

Ten negative controls reject an underpriced dual, a negative price, an even
odd-set, repeated helper use, a nonattaining matching, omitted restoration,
omitted middle read, nonzero D frame, source read and target feedback outside
the chosen H2-sem contract. The feedback control tests this inherited contract,
not necessity under PR2721's broader H2-F interface. Three package controls
reject source-byte, dual-certificate and expected-result corruption.

No native C++/hosted replay, all-size/compiler construction, common-label
realization, physical routing, precision/tape implementation or outer analytic
admission is proved. The recursive profile is unchanged and the selected
complex supplier remains binding. No new κ is asserted.
