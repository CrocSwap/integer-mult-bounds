# Four queries attain the equal-orientation fragmentation contract

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. This is a written algebraic proof with exact executable controls,
not proof-kernel or independent human verification.

## 1. The question left by the preceding header obstruction

CrocSwap/integer-mult-bounds#6764 proves that a three-query binary header cannot
support even one auxiliary fragmentation under its positive-body, atomic-native
contract. Its mixed-orientation gain is less than one extra query, but the
equal-orientation gain can exceed one at sufficiently unequal body ranks.
That leaves a specific question: can four queries actually realize the latter
boundary, and can it improve the complete caller?

This note answers the algebraic question affirmatively, with four queries
minimal under the inherited contract. [ECONOMICS.md](ECONOMICS.md) separately
answers the complete-invoice question for the pinned two-pair root. Neither
the classical three-shear identity nor a new general query-factorization
theorem is claimed here.

The already published fork branch at
[`d87e4a38890f6962162d00a68031ab2476f58f6e`](https://github.com/CubeJerry/integer-mult-bounds/tree/d87e4a38890f6962162d00a68031ab2476f58f6e/research/four-query-fragmentation-ceiling)
establishes the same endpoint and a broader complete-tree ceiling. This note's
distinct construction uses 20 literal six-field events instead of 21, with
the same exact source convention and two final auxiliary normalizers in both
cases. [CONCURRENT-WORK.md](CONCURRENT-WORK.md) gives the checked comparison
and limits the novelty claim; neither first attainment nor first ceiling is
claimed here.

## 2. Exact boundary and alphabet

Let F be any field, and work over

    F[L^±1,R^±1,S]/(S²−1),

where L and R are independent body variables. Ordinary scalar operations are
F-valued and independent of all three variables. All six input registers
X,Y,A,B,E,F0 are arbitrary and independent. No zero helper, erasure, copied
independent input, or unpriced inverse body is used.

For an ordered pair (u,v), write

    Q_uv(c): u ← u+c S v,
    N_D(u,v): (u,v) ← D(u+S v,v).

Q is a thin rank-one square-zero central query. N is one existing native
child, whose two main ports carry D and whose query is atomic with that body.
Each native child's own productive helpers and owned work retain their
existing disjoint contracts; they are not identified with A,B,E,F0.
An ordinary whole-body idle applies D to one register and is fully paid.

The target is

    Xout = LR(X+S Y),        Yout = LR Y,
    Aout = SL A,             Bout = SL B,
    Eout = R E,              Fout = R F0.                 (1)

Thus both old auxiliary outputs have the same SL prefix orientation and
both genuinely fresh suffix inputs receive R. This has the same target and
paid-body multiset as splitting both original SLR auxiliary jobs at that
orientation. It is a changed history: it does not factor the old fixed
prefix from #6726 through a new basis and its inverse.

## 3. The attaining word

Execute, in this chronological order:

1. N_L(A,B).
2. Q_BA(−1).
3. Q_AB(+1).
4. Swap A,B, then negate A.
5. Apply the two paid L idles to X and Y.
6. N_R(X,Y).
7. Apply the two paid R idles to E and F0.

After step 3 the auxiliary pair is

    (L S B, −L S A).

Step 4 gives (SL A,SL B), and those outputs are never touched again. Steps
5–6 give LR(X+S Y,Y). E,F0 are untouched before step 7, so no correlation
or prior processing of a purported fresh input is concealed. The displayed
endpoint follows coefficient by coefficient on every arbitrary input.

Equivalently, the three central shears on A,B have matrix

    Q_AB(+1) Q_BA(−1) Q_AB(+1) = S J,
    J = [[0,1],[-1,0]],

and step 4 applies J^−1. The first shear is supplied by the L-native child;
the other two are thin queries. The R-native child supplies the fourth
query on X,Y. All controls have integer coefficients and determinant ±1.
The identity works unchanged in characteristic two, where negation is
the identity.

There is also an equivalent four-register caller: omit E,F0 and step 7.
Those two independently paid R jobs and their two R targets cancel from
the signed invoice exactly. This is cancellation of entire independent
jobs, not credit for spectators or removal of a required input within a
fixed interface. If the six-input interface is required, retain all six
inputs and all four body idles.

## 4. Literal q⁴=1 normalization

The retained #6726 caller uses a central q with q⁴=1 and

    λ = (1+i)/2 + (1−i)q²/2,
    λ^−1 = (1−i)/2 + (1+i)q²/2,
    S = λ q^−1.

Exactly λλ^−1=1 and λ²=q², hence S²=1. In each q² sector λ is an ordinary
scalar unit (1 or i). The frozen source's query wrapper is

    LAMBDA(u,−1); QUERY(u,v,−1); LAMBDA(u,+1).

Its QUERY performs u←u+q^−1 v, so the wrapper performs u←u+S v.
The corresponding leaf wrapper replaces QUERY by LOCAL(stage,v,u), which
performs that query and multiplies both ports by the stage body. It therefore
implements N_D(u,v) exactly. A negative query is obtained by negating its
destination before and after the same wrapper.

`verify_caller.py` binds those two literal wrapper bodies to the immutable
frozen source by SHA256 and AST comparison. Its separately written sparse
polynomial interpreter executes the entire changed word in
Q(i)[q,L^±1,R^±1]/(q⁴−1). It retains all four q classes, rather than checking
only q=1 or dropping the absolute phase.

The six-register word has 20 literal events: two LOCAL, two QUERY, four
IDLE_ONE, eight LAMBDA, three SCALE and one SWAP. The four-register word
has 18 events and two IDLE_ONE. All eight λ normalizers, the signs and the
swap are explicit ordinary work. A physical implementation must also pay
the child port routes and its actual field storage/movement; the scalar
identity does not grant those for free.

The surrounding #6726 caller applies a final λ^−1 to its ordinary auxiliary
outputs. That converts our SL outputs to q^−1L, as required for its normal
Gaussian job convention. If the six-register form is placed under a tail
that also acts on E,F0, those R-only outputs need canceling λ normalizers;
they must not silently become λ^−1R. The equivalent four-register form
has no such suffix-only outputs. No complete physical installation is
claimed by this standalone algebraic realization.

For the BIT transfer, first specialize q²=1, which makes λ=1 and S=q.
The combined coefficients are then integers and can be reduced modulo two.
The checker verifies that order of operations and separately executes the
normalized word over F2[S]/(S²−1). It does not reduce isolated Gaussian
halves modulo two.

## 5. Four is the minimum in the inherited positive-body contract

At L=R=1, normalize (1) by its value at S=1. The header is

    I+(S−1)K,       K=E_XY+I_{span(A,B)},

with rank K=3. A product of k normalized rank-one central queries has
coefficient rank at most k, so fewer than three cannot suffice.

If there were exactly three queries, apply the saturated-body theorem in
#6764, `HEADER-SATURATION.md`, to body R. The final R projector is the
ordinary projector onto span(X,Y,E,F0); it commutes with K and omits both
S-target directions A,B. Positive unit body exponents force its total rank
to be saturated by determinant comparison. The retained R-native query is
atomic with and supported on its own R projector. The predecessor theorem
then requires the final R projector to contain both S-target directions,
a contradiction. The four-register form has final R projector span(X,Y)
and the same contradiction.

Consequently four is sharp for this contract, with any number of unchanged
ordinary spectator registers. The lower bound inherits the positive-body,
ordinary-control, independent-formal-body and atomic-query hypotheses.
Negative body calls, body-dependent controls, changed native primitives,
noninvertible operations and a different target boundary are not excluded.

## 6. Complete local invoice

Let a,b>0 be body ranks and H(r)=r^t for 0<t<1. Count every body idle,
native child, thin query and productive target. Relative to the original
binary node, whose two auxiliaries each have target rank a+b+1 and paid
idle rank a+b, the six-register change is

    ΔT = 2[H(a+1)+H(b)−H(a+b+1)],
    ΔP = 2[H(a)+H(b)−H(a+b)] + H(1).

Native child invoices are unchanged. There are two thin queries instead
of one; their difference H(1)=1 is essential. Thus, with
i(x)=H(x+1)−H(x),

    Δ(T−P) = 2[i(a)−i(a+b)]−1.                         (2)

Removing the two canceling R-only fields yields precisely the same result.
After the native children are accounted separately, the old internal-node
contribution is 2i(a+b)−1 and the new contribution is 2i(a)−2<0. An extremely
unequal pair can make (2) positive, but that does not make the entire caller
profitable. The separate all-size analysis in ECONOMICS.md keeps the full
native and root invoice and does not infer a new κ from (2).

## 7. Exact controls and remaining scope

The executable checks all 36 forward coefficients of the six-input word,
all 16 coefficients of the four-input word, both inverse compositions
against the explicit mathematical inverse, source-wrapper binding, exact
operation counts, characteristic-two transfer, and the symbolic invoice.
Controls delete each of the 20 literal events, reverse a q exponent,
omit a body idle, alias a fresh input with a completed output, miscount
the extra thin query, and alter the retained source. A q=1-only control
deliberately fails to detect a phase fault that the full q⁴ ring rejects.

This proves a finite exact scalar identity and a sharp query count within
the stated contract. It supplies no new native all-column theorem, complete
physical caller, finite compiler admission, selected-frontier update,
unconditional multiplication algorithm or discharge of the five selected
framework assumptions.

Credit Cinna Davis's native/binary supplier lineage, Ali Romman's #6398
mixed-query root and shortest-word lineage, thu-nmrc's #6716/#6717 stages,
zxv's #6726 paid fragmentation and explicit remaining question, and the
#6764 saturation proof and precise equal-orientation exception. The
elementary three-shear identity is classical. Frozen source attribution and
the original NOTICE remain unchanged.
