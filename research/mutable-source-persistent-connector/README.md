# Carry a dirty connector across a paid source mutation

For two consecutive products A1 B x and A2 B x with the source update
x += C u between them, maintaining the coherent boundary z=z_initial+B x
requires exactly the correction z += B C u. That correction can be cheaper
than restoring and rebuilding B x. The explicit fixed three-bit pilot removes
two complete B calls and reduces **43 to 31 scalar XOR updates**, with the
two-entry correction paid. Sources, output dirt and all connector dirt are
checked exactly; the source update is part of the intended map.

This is a typed two-call pilot, not an instantiated contracting supplier
recurrence. It changes the immutable-source premise of the inherited carried
connector model. It neither changes the selected frontier nor claims a new
kappa. The mixed-provider catalogue explicitly excludes deferred restoration
that changes its paid call contract; its dual is not contradicted here.

## Exact contract and proof

All five length-L F2 rows x,u,z,y1,y2 are distinct and arbitrarily dirty.
A1,A2,B,C are fixed linear maps of compatible dimensions; no commutativity,
invertibility or clean row is assumed. A complete additive call preserves
other rows and restores private scratch and heads. The two boundary types are
closed z=z_initial and open z=z_initial+B x. Outputs may be observed only
after their respective call; an open connector remains reserved and hidden.

The requested final map is x'=x+C u, u'=u, z'=z,
y1'=y1+A1 B x and y2'=y2+A2 B(x+C u).

Execute, in order:

    y1 += A1 z; z += B x; y1 += A1 z;
    x += C u; z += B C u;
    y2 += A2 z; z += B x; y2 += A2 z.

The first paired readout cancels the old connector dirt and gives A1 B x.
After the source mutation the stored connector is initially z_initial+B x_old.
Adding B C u makes it z_initial+B x_new. The second paired readout then gives
A2 B x_new, and its intervening B call restores the connector. Linearity alone
establishes this for every L and all admissible maps, including singular maps.
The inverse is the literal reversed sequence of these self-inverse shears.

If the adapter is restricted to a source-independent additive operation
z += D u preserving x,u, the typed boundary is valid for every input iff
D=B C. Subtract the two required expressions for z to prove necessity. Thus
omitting the correction is legal exactly when B C=0. Under the scalar rank-one
update alphabet, an adapter needs at least rank(B C) rank-one updates by
rank subadditivity. This rank bound does not price basis conversions or compute
D u for free; the literal pilot pays its two nonzero scalar entries instead.

## Completed costs and a useful stopping rule

Let complete fixed-port costs include arithmetic, source/coefficient access,
scratch restoration, head returns, routing/frames and per-call dispatch. With
all preparation and admission denoted I, the naive two closed echoes cost

    I + 4 c_B + 2 c_A1 + 2 c_A2 + c_C.

The coherent pair costs

    I' + 2 c_B + 2 c_A1 + 2 c_A2 + c_C + c_BC.

Use actual orientation/port prices if they differ. I' also includes preparing
the BC adapter and reserving z across the source mutation. The saving is real
only if c_BC+(I'-I)<2 c_B. For k calls and successive source mutations C_t u_t,
the same typed identity gives 2 c_B+2 sum_i c_Ai+sum_t(c_Ct+c_BCt), plus actual
admission, preparation and dispatch. This is a chain cost, not a new all-size
contracting recurrence. No selected owner schedule satisfying it is supplied.

For the k-call formula, first apply y_i += A_i z_initial to every output while
the connector is closed, then open it once. Complete each output with its second
read when its source version is current, apply the coherence correction after
each source mutation, and close the connector after the final output. Thus
future outputs receive early dirty prewrites. This is permitted by the stated
observation-only contract; the formula does not apply to a stricter contract
forbidding output writes before that output's request interval. The explicit
two-call pilot above needs no early write to the second output.

In the literal pilot (rows are binary bitmasks),
B=(3,6,7), C=(1,0,0), A1=(2,4,1), A2=(3,2,4), BC=(1,0,1).
B has rank3, C and BC rank1. Every matrix entry1 becomes one source-to-target
XOR; there are no hidden scratch or COPY operations. Baseline cost is
4*7+2*3+2*4+1=43; candidate is 2*7+2*3+2*4+1+2=31. B and C do not commute,
so replacing BC by CB fails. The fixed map constants are compiled into the
instruction list; computing arbitrary runtime BC coefficients is not included
in this fixed-map comparison and must be added for a dynamic backend.

The data tape has 15 bits, and each XOR is implemented by visiting its source,
visiting its target and returning to origin. Its exact movement is 2 max(s,t),
plus two reads, one write and one XOR. The receipt reports both totals.
Instruction fetch/decode is charged once per scalar gate using equal record
width in both programs; the candidate has 31 versus43 records. One clean scalar
temporary may be initialized once in the common admission and restored per
gate. These are explicit macro counts, not a measured native runtime.

## Reproduce and scope

```sh
python -O -B research/mutable-source-persistent-connector/verify.py
python scripts/research_package.py --package research/mutable-source-persistent-connector
```

Python3.12+ standard library suffices. The primary engine propagates all10
arbitrary-input columns for all65,536 quadruples of 2x2 matrices, including
singular, zero and noncommuting maps, in both orientations. An independent
literal scalar engine compares both three-bit words on all32,768 dirty inputs.
Three controls omit the adapter, reverse BC, or omit final B restoration.
[EXPECTED.json](EXPECTED.json) contains exact results; [SOURCES.json](SOURCES.json)
pins predecessor Git blobs and SHA256. No imported executable is trusted for
the identity. Selected cold replay, native compilation and a contracting
multitype supplier realization were not performed or inferred.

Overlap search of the fully paginated863-PR/112-discussion cached snapshot
found source-mutation mentions but no coherent-connector scope. Offline
freshness and body-only search limitations remain; no absence-of-overlap proof
is claimed. Prior forty rounds, including fixed-source port borrowing and
cleanup read corridors, have different objects and hypotheses.

## Open next questions

Find a concrete selected-call boundary whose source mutation has a cheap BC
adapter. First extract both complete entry/exit contracts and compare the full
cost above, including reserve width and frame admissions. The blocker is a
verified hosted supplier instantiation, not the scalar identity; without one,
no contracting recurrence or exponent improvement follows.

## Credit

Prepared by woklerx with substantial OpenAI Codex assistance; Apache-2.0.
Ross Richardson's universal connector/PR934 work supplies the dirty-readout
contract and its predecessor attribution; Ali Romman's heterogeneous owner
assembly identifies deferred restoration as outside its frozen catalogue.
All selected supplier and dirty-commutator lineage remains credited. No
independent human peer review or full multiplication theorem is asserted.
