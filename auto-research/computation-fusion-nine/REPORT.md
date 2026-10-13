# Two whole-stage fusion designs: readout costs prevent the saving

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
October 8, 2026. No improved multiplication exponent.

## Decision and scope

We considered two concrete replacements for the successive finite scalar
shears. Each removes real computation, rather than sharing storage or
relabeling the existing gates. Both fail a complete optimistic cost screen,
so **no construction experiment was launched**. This is the early stopping
condition in the goal, not an exhausted solver search.

1. **Retain the original target, execute one shear, and reconstruct the
   outputs.** This deletes the second invocation and its auxiliary bank.
   Its readout requires a full interchange of the retained target. With
   the other necessary transformations, even generous costs exceed capacity.
2. **Replace both shears with a single common-frame two-register gate.**
   This deletes both producers and their restoration words. Its four frame
   alignments cost at least 2m per data pair, before the rank-one correction.

These conclusions concern the specified copied readout and common-frame
implementations. They do not exclude a fused computation with genuinely
different readout obligations or a distributed, characteristic-dependent
gate graph. They do not establish a limit on integer multiplication.
No parked search, parameter sweep, merge, push or publication was performed.

## Starting contract

We replay the pinned [target budget](../kappa-nine/target-budget.json),
including its baseline hashes, physical profile reconstruction and 47-row
hypothetical assembly check. The previous
[architecture comparison](../architecture-nine/REPORT.md) is retained.
The target kappa>1/512 requires bit saving a>1/511; at beta=1/20 it also
requires complex saving b>20/9709. Neither required network saving is supplied.

The selected release remains 25508460085039/500000000000000000. The reviewed
PR82 snapshot used for budgeting is a separate, unmerged research baseline.

The actual two-stage source/frame contract is recorded in
[PR29's note, section 3](../../references/copied-centers/pr29/two-stage-16-note.tex).
Use its operation identities with the pinned dimensions a=23,b=25,m=575.
For a pair of triple labels let U=P tensor Q be the rank-one projector,
E=I_a tensor Q, A=E-U and R=I-E. These projectors commute, and their
orthogonal direct-sum identities remain valid for the inherited form.
Let D_S denote the rational partial interchange on subspace S. Put

    T=D_U,       F=D_I,       H=D_(I-U)=FT.

For orthogonal summands D_(S+S')=D_S D_S'. Every D_S is an involution.
The virtual source frames are (T,I), so physical inputs (x,y) correspond
to logical inputs (Tx,y). These virtual frames do not mean a free physical
application of T; the actual source edges remain in the cost list.

The first scalar shear changes logical (xi,eta) to (xi,eta+xi). The second
changes that pair to (eta,xi+eta). With terminal frames (F,H), the physical
outputs are

    A_out=Fy,       B_out=Fx+Hy.

The existing paid endpoint operation retains A_out, transforms a copy by T,
and adds it to B_out, giving (Fy,Fx). Row-bank exchange then identifies the
two desired full-interchange outputs. All ordinary auxiliary inputs are
arbitrary and are restored, with their full address endpoint operation paid.

Inside an invocation the producer word is

    L,J,L^-1,V,L,J,L^-1,V,        JLV=I over F2.

If its auxiliary input is z, the two scatters contribute JLz and
JL(z+Vxi), which sum to xi; the final V cancels Vxi. This proves the
unchanged target shear and restoration for every z, not only zero workspace.
The audit checks the word on independent formal bits and verifies that
omitting its last clearing step leaves incorrect auxiliary outputs.

## Design 1: bypass the second invocation with a retained-target readout

**Exact replacement.** Copy the original physical y before the first
invocation; copies use the existing full-stream copy/read/discard interface,
not an extra independent role. Keep the first invocation and its cleanup.
Its physical outputs are

    X_1=D_A x,       Y_1=D_E x+D_A y.

Discard X_1 after its last required use. Transform the retained y copy by F,
and transform Y_1 by D_R. The latter becomes

    B=D_R Y_1=Fx+Hy.

Retain Fy as the first output and use the existing rank-one correction
B <- B+T(Fy). The final outputs are precisely (Fy,Fx). Thus the original
x input is recoverable in the final output before its obsolete stream is
erased. No zero-input hypothesis was used. First-invocation auxiliary
values remain restored by the original word; the second bank no longer
exists. The retained auxiliary exterior transformations remain charged.

This is a change of operation graph: an entire second producer, its
computation/uncomputation, and its independent auxiliary bank are removed.
It therefore differs from the failed bank-sharing proposal. It does not
assume free movement of the cached y stream.

**Complete optimistic profile.** Let N=4,073,300 and let B denote the
number of retained first-axis auxiliary roles. From the pinned profile,

    B=(N/1771)*27075=62,272,500,       W'=2N+B=70,419,100.

Grant ideal single-child batching for every operation and erase every
fixed central loss. Charge the following replacement and retained work:

| Operation | Count | Child width |
| --- | ---: | ---: |
| Full interchange of the retained original target | N | m=575 |
| Final Y_1 reframe D_R | N | m-a=552 |
| First-invocation source and target growth | 2N | a-1=22 |
| Endpoint correction copy | N | 1 |
| Optimistically packed first compiler, with central loss erased | B | a=23 |
| Retained auxiliary exterior | B | m-a=552 |

Copies, additions and erasures have the inherited linear stream cost.
Each listed recursive operation has volume V/W'. Cached streams are
dependent temporary copies, not extra independently varying input roles
that could increase W'. Parking them is granted under the fixed finite
copying interface; any additional real cost would only weaken the proposal.

The total rank is

    s_relax=W'm+(a-1)N=40,580,595,100,
    W'm=40,490,982,500.

It already exceeds capacity by 89,612,600, before central loss or actual
profile splitting. At the necessary a_bit=1/511, the exact moment is
approximately **1.00253854432330**, whereas acceptance requires less than one.

The full-width child is not certified by the current strictly contracting
recurrence. We nevertheless allow it the favorable moment contribution
(m/m)^(510/511)=1 for this rejection. Therefore the rejection does not
merely rely on an unavailable halving-degree bound.

An even stronger allowance deletes the entire source growth/cleanup charge
N*[22]. Total rank then equals W'm exactly. Its moment is still strictly
greater than one, because there remain positive proper-width children.
Thus the failure persists even if that additional computation could be
removed for free. The missing ingredient is a way to obtain the retained
target's full transformed stream without paying for that full operation;
merely retaining its scalar value does not accomplish it.

## Design 2: replace both shears with one packet gate

**Exact replacement.** The logical composite is the two-register linear map

    S(xi,eta)=(eta,xi+eta).

Equivalently, encode xi+omega*eta over F4 with omega^2=omega+1; the map is
multiplication by omega. This identity suggests deleting both finite
producers and performing one pointwise two-register operation. No extension
field speedup is inferred from this reformulation.

Choose one common frame K, align the two inputs at K, apply S, and align
the two outputs at the required terminal frames I and I-U. Then apply
the original rank-one endpoint correction. Its physical input/output map
is still (x,y) -> (Fy,Fx). There are no auxiliary roles, hence no dirty
workspace to restore. Source and target streams remain independent inputs.

This deletes the entire intermediate computation and both restoration
words. It changes the gate graph, rather than merely changing frame labels
inside the old graph. The proposed implementation does, however, require
a single common frame at the packet gate.

**Alignment budget.** For commuting idempotent cuts, the four charged
partial-interchange ranks are

    rank(K-U), rank(K), rank(I-K), rank(I-U-K).

These are the two source alignments and two sink alignments. The expression
also defines a favorable rank-difference bookkeeping relaxation for arbitrary
rational K; no availability of arbitrary noncommuting address quotients is
inferred. By rank subadditivity,

    rank(K)+rank(I-K) >= m,
    rank(K-U)+rank(I-U-K) >= rank(I-2U)=m.

The second equality uses (I-2U)^2=I. Thus the four alignments alone cost
at least 2m in every dimension. Adding the paid endpoint correction gives
at least 2m+1 against two roles' capacity 2m.

For any fixed K, the complete profile consists of those four ranks (omit
zeros), followed by a width-one correction. For example K=0 gives

    [1]+[m]+[m-1]+[1],       W=2 per data pair.

Grant even more favorable cross-edge packing into [m]+[m]+[1]. Concavity
of t^(510/511) makes this a lower bound for any subdivision of at least
2m+1 integer rank units into children of width at most m. At m=575 its
moment is approximately **1.00088044591703**, already too large. If the
endpoint correction were entirely free, the alignment rank still gives
moment at least one. Adding an unproved full-width recurrence cannot make
this profile contract.

The missing ingredient is therefore not a cheaper expression for the
two-register scalar map. It is an implementation that avoids this
common-frame alignment obligation. A distributed characteristic-dependent
network might do that; the single packet gate supplies none.

## Complex counterpart and changed transfer obligations

The signed complex analogue of the scalar composite is
(xi,eta) -> (-eta,xi+eta), obtained from y+=x followed by x-=y.
With T=C_U and F=C_I, its inherited framed readout is

    A_out=-Fy,       B_out=F T^-2 x+(F T^-1)y.

Adding T^-1 A_out cancels the y term. The retained diagonal/translation
endpoint corrections are still needed to turn F T^-2 x into the required
full output; they must not be silently dropped because bit partial swaps
are involutions. The existing exact phase controls are in
`research/copied-reversed/review/copied_center_operator_audit.py`.

A complex retained-target bypass would likewise retain a full Fy stream
and use the signed inverse-phase readout. A common-frame packet version
would need both input and output phase alignments. Their actual binary
frame ranks, signed scalar charges and ordered profiles would need a
separate certificate. No complex network or improved complex saving is
claimed by these bit-side algebra controls. Since both bit budgets fail,
neither direction proceeds to complex construction.

If either design had passed, its changed W, full-width children, copied
stream lifetime, endpoint map and gate count would require a new finite
bridge and recurrence proof. In particular, the existing halving-degree
and product row-stock checks do not accept a child of width m. The pinned
47-row hypothetical arithmetic is only a baseline replay; it supplies
neither a replacement transfer theorem nor b>20/9709.

## Validation, stopping rule and remaining gap

The audit checks formal stream-operator identities for both readouts,
arbitrary dirty auxiliary restoration, and negative controls that omit
cleanup or omit/misframe the endpoint copy. Rational matrix controls check
the packet lower bound for nonsymmetric projectors and matrices. Exact
root enclosures certify the complete optimistic moments. Small controls
validate general identities; they are not a failed sample search or a
claimed finite characteristic-dependent construction.

Both designs fail even before claiming an exponent improvement. There is
no numerical gap to extrapolate from a small successful instance and no
evidence justifying a larger construction run. The three-hour allowance
was an upper bound; the goal explicitly calls for stopping earlier if no
design passes its budget gate. Two of at most three designs were considered,
and zero of at most one construction experiments were used.

The next proposal would need an explicit readout that preserves useful
information in mixed frames and avoids both a standalone full transformed
copy and one common alignment frame. That is a missing operation-level
ingredient, not a recommended unbounded search. No follow-up experiment is
recommended from the present negative evidence alone.

Reproduce:

```sh
python3 research/computation-fusion-nine/audit.py --output /tmp/fusion-nine.json
python3 -m unittest discover -s research/computation-fusion-nine -p 'test_*.py' -v
```

See [certificate](certificate.json) and [validation record](validation.json).
The existing selected exponent and all pre-existing source/artifact contents
are preserved. These scoped conclusions remain conditional on the stated
retained accounting interfaces; they do not audit the full upstream theorem.
