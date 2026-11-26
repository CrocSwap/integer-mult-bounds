# Adaptive time, fixed payload space: a source-compatible closure interface

Status: **written conditional command-interface theorem and narrow kernel-
checked resource inequalities; independent review requested**. This is a
formalization bridge, not a new supplier or multiplication bound. No OAI
target or comparator was built in this session.

Primary source: OpenAI math
`3344da59991ed94f9ba711217b29c1d760badfa6`, all paths below under
`lean/OAI/Computability/NearSquareRoot/`.

## 1. What the existing formalization already supplies

The lead read the complete statements and proofs of Main,
InterchangeROMUniform, InterchangeROMOuterComponents,
InterchangeROMBinarySelected, SelectedWalshProcedure,
SelectedWalshRowProfile, UniformWorstCase, InterchangeROMFamily,
InterchangeROMFamilyComponents, InterchangeROMFamilyGeometry,
InterchangeTemplateSelect, InterchangeROMOuterCompile,
InterchangeROMFrontNode, InterchangeROMFrontBound,
InterchangeROMRecursion, InterchangeROMRecursionThick,
InterchangeBQuestClock, InterchangeBQuestMixedResolve,
InterchangeBQuestResolve and InterchangeROMDriver.
This is selected source coverage, not the entire transitive closure.

The actual main proof uses a native interchange family and selected
CRT/permutation/Walsh procedures. `UniformWorstCaseSpec` quantifies one
finite machine and one visited-space coefficient before input length;
its output is the exact 2n-bit product, and its maximum is over actual
halting traces. Its exponent excess only tends to zero.

`InterchangeTemplateSelect.first` uses terminating search through finite
certificates. `computable_select` proves computability, not a runtime
profile uniform in a growing exponent index. `NativeFamily` does have
one register cutoff and one record-padding degree across all selections.
Those facts do not bound all selected coefficients, constructor work,
thresholds or constants as that index grows.

In particular `InterchangeROMRecursion.Certified` contains an existential
constant K multiplying its displayed time and space expressions. The
notation `ceil(recordVolume * width^alpha)` in `Executes` does **not**
mean unit leading constant uniformly over a varying family. In
`ComponentRuns`, B,C,U are chosen after the numerical template.

The useful positive fact is more general than the fixed-exponent API:
`InterchangeROMRecursion.resolve_controller` accepts any real-valued
fare on requests, with uniform positive fractional slack. Only its
`resolve_controller_width` specialization imposes a power of width.
`InterchangeBQuestClock.exists_floor_clock` already accepts an arbitrary
local work function. No new real-to-integer clock theorem is needed.

## 2. The actual interface mismatch

`Sharp` in InterchangeROMRecursion charges local time C V and also
uses C V as the payload parked on contracted children. Its full-volume
children retain H(log2 V+1), and its mixed space proof uses the potential

    3 C V + H(h+1)(log2 V+1).

An adaptive supplier may instead take V m(h)^K local steps while using
only C V payload cells. Replacing V everywhere by V m(h)^K loses the
linear-space statement. Bounding a long local run by `Fits` alone also
does not prove that smaller cap: the source's generic `of_fits` conversion
can bound temporary growth by time. A direct `BoundedFits` contract with
the claimed payload cap must be supplied.

There is a second difference: adaptive descriptors can be a fixed
polynomial in address length, larger than H log V. This is affordable
on complete arrays, but it must be included in the resource induction.

## 3. A separated open-body contract

Let X be the request type and **c one fixed command**, serving every x.
Let S(x),F(x) be finite ordered lists of contracted and full-volume child
requests; repeated calls remain repeated list entries. Let V(x)>=1,
h(x) be natural numbers, w(x) the actual local step allowance, and B(V)
a descriptor allowance. Fix one natural payload coefficient C.

Require the following open-body contract on every ambient environment and
every parked deck. If each child y runs the same recursive command with
time t(y), data cap d(y) and return depth r(y), then the body on x has:

    time <= w(x) + sum_(y in S(x)++F(x)) t(y),
    data <= base + max(C V(x) + peak_S d,
                       B(V(x)) + peak_F d),
    return depth <= max(C V(x) + peak_S r,
                        B(V(x)) + peak_F r).

Here `peak` is the source `childPeak`, including zero for an empty list.
The type is the source `BoundedFits (c::env) c` for both the body and
inductively supplied child executions, with its exact query/reply trees,
parent command, environment and deck quantifiers. The outer `.tie c`
appears only after closure. The full-volume branch
has transferred ownership of the payload before descending; merely
declaring it dead without reusing the same regions does not supply this
contract. The w(x) invoice includes jumps, dispatch, preparation, head
returns and cleanup that its chosen interpreter actually charges.

Assume every child has h(y)<h(x), V(y)<=V(x), and B(V(y))<=B(V(x)).
Contracted children also satisfy 3V(y)<=2V(x). Assume one fixed D gives

    (h(x)+1) B(V(x)) <= D V(x).                       (AS1)

More general fixed contraction ratios use a larger fixed payload
coefficient in the potential. The exact Lean arithmetic here verifies
the source's two-thirds contraction case, not every possible ratio.

Finally let P(x)>=0 be a real-valued fare and let A,epsilon be fixed with
epsilon>0, such that

    w(x)+1 <= A P(x),
    sum_(y in S(x)++F(x)) P(y) + epsilon P(x) <= P(x). (AS2)

No algorithm is asked to evaluate P or choose an optimal plan from it;
P is an analytic witness for the already specified command. Conversely,
a different command for each input width does not meet this hypothesis.

## 4. Conditional closure theorem AS

Under the preceding contract, the same tied command `.tie c` satisfies
the source `Certified` predicate with time `ceil(P(x))` and space V(x),
with one common constant independent of request and recursion depth.

**Time proof.** Apply the source `exists_floor_clock` to the actual w,
the concatenated child list, and P. It gives a natural K with

    w(x)+1+sum_children floor(K P(y)) <= floor(K P(x)).

Downward rounding is essential: no additive error proportional to the
number of children is silently discarded. Let t(x)=floor(K P(x)). The
clock therefore pays the open step and the initial tie transition. The
source `floor_clock_le_mul_ceil` gives the final uniform ceiling bound.

**Space proof.** Put

    Q(x)=3 C V(x)+(h(x)+1)B(V(x)).                    (AS3)

For a contracted child, C V(x)+3 C V(y)<=3 C V(x), and
(h(y)+1)B(V(y))<=h(x)B(V(x)). Thus C V(x)+Q(y)<=Q(x).
For a full-volume child, 3 C V(y)<=3 C V(x), and adding the parked
B(V(x)) to its descriptor term gives at most (h(x)+1)B(V(x)).
The same inequalities hold with empty lists, using the two local lower
bounds on Q. Taking maxima over children supplies both stack caps.
By AS1, Q(x)<=(3C+D)V(x).

Apply the source `resolve_tie_exact` with clocks t, both stack allowances
Q, the same body c, and height h. Its well-founded induction preserves
the exact command, query/reply trees, environment and parked-deck contract.
Scale the time and space constants once to obtain `Certified`. QED.

This theorem closes a **command-level contract**. Instantiating it with
the new adaptive physical supplier, and carrying it through the source
interpreter/finite-tape and final visited-cell theorems, remain distinct
obligations. The abstract potential alone does not prove actual address
reuse or transfer a RAM algorithm to tapes.

## 5. Relation to CT and the remaining formal work

For CT-I, the intended fare is V sqrt(e) (log2(e+2))^p. Fixed-power
arity m~e^delta with delta K<1/2 makes V m^K fit AS2's local allowance.
Its proved potential contraction gives uniform fractional child slack.
Complete address ranges have e=O(log V); with h=O(log V) and
B(V)=O((1+log V)^d) for one fixed absolute degree d, AS1 follows after increasing a constant
for finitely many small volumes. That last analytic implication is
written here, not newly kernel-checked.

The source's literal `node prelude stage b n` fixes b,n and its stage.
An adaptive instantiation must prove one request-decoding dispatcher
meets the separated contract, rather than substituting input-dependent
code into that fixed node. Finite-alphabet/register bounds, actual
constructor costs, source record formats and any field changes remain
part of that proof. Numerical precision and the integer caller are
outside AS; CT records their separate written implications.

## 6. Exact new kernel-check scope

[ResourcePotential.lean](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S005/lead/formal/ResourcePotential.lean) proves the natural-number small-child,
full-child, empty-list local bounds, sibling maximum and AS1-to-linear-cap
inequalities for an arbitrary monotone descriptor allowance. It uses
pure Std and the available Lean4.35.0 toolchain; printed axioms are only
propext and Quot.sound. It does not import OAI, prove AS's physical body,
or pretend that an upstream 4.34.1 target was built.

The important reuse decision is to build on the existing general clock
and exact-command recursion theorem, while strengthening the local
supplier's independent time/space proof. Re-proving only a fixed-power
recurrence would not resolve this interface.

Credits: OpenAI's exact-command recursion, clock and mixed-space framework;
S003 adaptive schedules and S005 CT; Jerry Chen (@CubeJerry), with substantial
ChatGPT assistance. No priority claim is made for the elementary potential.
