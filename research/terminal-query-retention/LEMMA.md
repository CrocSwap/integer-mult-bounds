# Query retention at a retiring linear node

Status: elementary exact linear-algebra lemma, applied here to a new supplier
interface. No claim of publication-level novelty or of a new multiplication
exponent. This statement does not identify subspaces of equal dimension.

Let a node hold `d` physical scalar streams `z` at one *exact common frame* U.
All d streams retire here: none is an outgoing edge, source, target, or promised
donor to a later reuse. Its queried values are `L z`. Let rank(L)=k. All other
node operations and source corrections, if any, have already been performed.
Choose k independent rows Q spanning L and complete Q to an invertible d by d
matrix T. Execute T at U. Keep the k query coordinates unchanged until their
consumers can copy/read them. All other coordinates may immediately make their
already paid transition U→H. Delay the k remaining U→H transitions until the
last query read, without changing those transitions' exact endpoints.

Correctness: if L=BQ, each query is exactly B applied to the retained k slots.
T is invertible on arbitrary dirty data. No initial zero assumption is needed.
No later use is changed, by the retirement hypothesis. The final dirty map M
changes, so the final cleanup must use the *new* inverse map, not an old receipt.
If the copied query values are identical, their old-dirty response J is
unchanged. The usual dirty lift subtracts Jz initially and applies
M^{-1}(z_final−Vx) finally. This is an identity of all columns.

If the invocation also changes its sources, use the joint invertible block
P=[[U,0],[V,M]] on (x,z), rather than assuming U=I. After the target response has
been produced, undo the source-only U word and then the dirty/source-controlled
word. This restores (x,z) while leaving targets alone. Using the current Ux
as though it were the original x in a dirty-only cleanup is generally wrong.

The lower bound k is for linear retention of arbitrary z with no other available
information: factoring L=BQ through s retained scalars implies rank L≤s.
It is not a lower bound for unrestricted algorithms, nor when source values or
other retained streams provide side information. In particular rank(L modulo
other rows) is usable only if those other rows are still available unchanged at
the consumer, not merely if they were once computed.

## Cost and precision

The recursive movement histogram is unchanged: the same d old transitions
occur, with only k moved later. A basis of k independent center copies costs
k recursive children of rank dim U; reconstruction at their delivery frame
costs the literal scalar additions/scalings and temporary streams. This does
not justify removing copies whose consumers need incompatible frames.

For one nonzero query ℓ choose p with ℓ_p≠0 and take T=I with row p replaced by ℓ.
Its determinant is ℓ_p. Realize it by scaling z_p by ℓ_p then, for j≠p,
adding ℓ_j z_j to z_p. The inverse subtracts those terms and scales by ℓ_p^{-1}.
There are ≤d scalar primitives forward and ≤d backward, all at U. Coefficients
and their reciprocals must enter the exact grid/precision and finite work bill.
Holding a pivot does not add a stream to the live denominator: it was already
one of the retiring physical streams. It can extend lifetime and conflict with
reuse; those are explicit admission checks, not consequences of this lemma.

## Concrete application under investigation

The pinned PR233 flow has 22 center-query nodes with d=9, no outgoing coordinates,
one rank-20 query each, and no reused retirement at those nodes. A pivot per node
would preserve all 22 center copies and all rank-2 final climbs, hence the full
moment, while recovering the single global center cut expected by the five-stage
compiler. Exact coefficients and allocator checks are in composition-notes;
the generic statement alone does not certify that supplier.

## Two-query ansatz and negative controls

`verify_query_retention.py` checks a genuinely mixed two-query, four-dirty-stream
example, one redundant third query, all basis columns, and rejection of a
singular pivot, an overwritten query and falsely assumed side information.
It illustrates a reusable interface, not an exponent improvement: rank-two
queries need two independent retained streams, so merging them into one without
side information fails. No expensive synthesis is warranted for that ansatz.
