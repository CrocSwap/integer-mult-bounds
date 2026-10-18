# An observation floor after an invertible selected shear

This is a rational information obstruction for the specified modified QQ16
interface. It grants all operations and observations in its contract zero cost.
It is not a native-word lower bound, an exclusion of all changed first pairs,
or a multiplication theorem.

## Contract and notation

Fix the actual conserved F0 and B1 maps in
`research/joint-query/evidence/JOINT-QUERY-TRANSFER.md`, the actual selected
minors A and T, and the retained ordinary schedule. Work on fields constant
in every tensor payload coordinate, with arbitrary dependence on the finite
owner group. Let N be the number of owners. A centre-query array therefore
has dimension 8N over the rationals. All maps below act on complete owner
arrays; their factors need not commute.

Write `B_s = R_s iota_U`, `A_s = ell_(s,A)`, `T_s = ell_(s,T)`, and use
`P_(s,A)` and `P_(s,T)` for their two-sided selected sections. Here A_s and
T_s are restricted to their named selected coordinate spaces. Let

```text
C = [B0; B1; B2],                 r = rank_Q(C).
```

Between complete F0 and B1, allow a fixed invertible linear map Q from the
raw A array to the raw T array, acting by the paired shear

```text
X_T += Q X_A;
Y_T -= Q X_A.
```

This includes pairing the displayed A/T lists in their displayed order.
No ordinary field is changed. Also allow an added linear transcript of
rank at most d, retained through the endpoint. It may read ordinary fields
at the cut, including dense old-chart queries, and it may drive additional
paired selected updates. The latter must vanish when that entire transcript
is zero. In particular a retained eight-coordinate dense B0 read may be
injected into T with opposite signs on X and Y. The transcript includes
every additional independent retained record or source read allowed to
drive those updates. It cannot include a free, uncounted copy of a
transient selected cut. The input-dependent boundary action, including the
transcript, is linear; fixed parameters are allowed. The transcript is not
allowed to modify F0, B1, or the ordinary schedule.

Grant the decoder all selected fields immediately after B1, all final
selected fields, all completed-X descendants, all five forward histories,
and the transcript. Subsequent homogeneous selected-only linear controls
are allowed, including controls using that transcript. Arbitrary new
ordinary reads later in the schedule are outside this contract.

The theorem concerns recovering the original individual selected inputs,
not merely their conserved pair sums. None of those input registers is
assumed initialized. The zero-sum inputs used below form a permitted
subspace of differences between arbitrary inputs.

## Ordered invisible family

For an arbitrary ordinary array h define

```text
K = -(1/11) Q^(-1) P_(1,T) B1,
k = K h,
G = 11 B2 + (A_2 Q^(-1) + T_2) P_(1,T) B1.
```

The factors are in execution order from right to left. In particular
`Q^(-1) P_(1,T)` must not be replaced by `P_(1,T) Q^(-1)`. The rational
factor 1/11 is used to describe a witness, not to claim a legal primitive.
One may clear all denominators to obtain integer representatives in this
finite-dimensional rational model.

Initialize other pairs to zero and pair 0 to

```text
X_U = h,                         Y_U = 0,
X_A = -P_(0,A) B0 h - k,         Y_A = -X_A,
X_T = P_(0,T) A_0 k,             Y_T = -X_T.
```

The original selected pair sums and the F0 query are zero, since

```text
f0 = B0 h + A_0(-P_(0,A) B0 h-k) + T_0 P_(0,T) A_0 k = 0.
```

The conserved F0 map therefore gives

```text
X_U = Y_U = h,
X_A = k,       Y_A = -k,
X_T = Y_T = 0.
```

Restrict the added transcript to this family. It is a linear map `Lh`
whose rank is at most d, even when the original transcript reads selected
fields as well as ordinary fields. Restriction and substitution cannot
increase rank. On `ker L`, transcript-driven paired updates vanish and
the only boundary change is the fixed shear, so

```text
X_T = Qk = -(1/11) P_(1,T) B1 h,
Y_T = -Qk.
```

At B1 its future query and old target driver are

```text
q2 = B2 h - A_2 k - T_2 Qk = (1/11) G h,
a1 = T_1 Qk = -(1/11) B1 h.
```

If `Gh=0`, the future logger sets its A output to zero. Its current
query is then

```text
b1 = B1 h - T_1 Qk = B1 h - a1 = (12/11) B1 h.
```

Consequently `b1+12a1=0`. The conserved B1 target T output is zero;
its source T output is also zero, since the T pair sum is zero. Both A
outputs are zero for the same reason. The complete first-pair output is

```text
X = 0,
Y_A = Y_T = 0,
Y_U = g = h -(1/11) K_(1,U) B1 h.
```

Thus every `h in ker G intersect ker L` gives zero post-B1 selected
observations and zero retained transcript. This is an ordered identity on
the actual map spaces, not an assumption of scalar or commuting charts.

The residual map does not discard h. Put `Z=K_(1,U) B1`; the actual
response identity `B1 K_(1,U)=12I` gives `Z^2=12Z`. Hence
`(I-Z/11)(I-Z)=(I-Z)(I-Z/11)=I`. In particular the map sending h to g
is invertible, with inverse `I-K_(1,U) B1`. This observation uses only
products of the same operator Z and commutes no different chart factors.

## Why the complete retained tail remains invisible

The original selected-witness tail applies to every ordinary residue g
in the displayed first-pair state. It does not require `B1 g=0`, `B2 g=0`,
or any condition on a later query of g.

The first positive bridge places `-g` in pair 1's Y ordinary bank, while
pair 0 retains `g`. F2 acts on pair 0 with its entire X source zero, so
its history is zero and it leaves that state unchanged. The subsequent
negative bridge cancels `-g` before B3. Every later active local pair is
zero. The remaining bridges leave g only in pair 0's Y ordinary bank.
At the terminal exchange it becomes named final X0 with the former-Y
native type. It is not a completed-X descendant. All completed-X
descendants, final selected fields, and all five histories are zero.
The selected cuts after B1 and any later homogeneous selected-only
controls also remain zero. The package's source-bound schedule check
tests the required pair binding and the canceling bridge.

There is no claim that the transient F0 A array k is zero. Giving its
complete value to the decoder for free would change the observation
contract and invalidate the stated observation count. It can instead be
included in the charged transcript.

## Rank of the lost original selected data

Let S map h to the original pair-0 X_A and X_T in this family. Since the
selected sections and Q are invertible,

```text
S h = 0  iff  B0 h = 0 and B1 h = 0.
```

Moreover, G together with B0 and B1 determines B2, by subtracting the
displayed ordered multiple of B1 and dividing by 11. It follows that

```text
ker [G;S] = ker [B0;B1;B2],      rank [G;S] = r.
```

For any finite-dimensional linear maps O and S,

```text
dim S(ker O) = rank [O;S] - rank O.
```

Apply this with `O=[G;L]`. Appending L cannot decrease the combined
rank, while `rank [G;L] <= 8N+d`. Therefore

```text
dim S(ker G intersect ker L) >= r - 8N - d.       (1)
```

Every vector counted in (1) has exactly the same allowed observations
as zero, including the full retained tail. Thus a positive right-hand
side rules out every decoder, linear or otherwise, on arbitrary inputs.
The assertion is about the dimension of different required original
selected values, not merely the dimension of irrelevant ordinary inputs.
The same linear kernel also gives indistinguishable pairs about any
background input for the stated linear interface.

## Applying the separately checked actual-source rank bound

The following fourth-moment argument and numerical certificate are reused,
with credit, from [commdata2338's PR #2189](https://github.com/CrocSwap/integer-mult-bounds/pull/2189).
That predecessor applies its capacity bound to the unsheared first pair.
The quantified changed-shear transcript implication above is the
contribution here. Concurrent @starship-s PR #2368 independently proves
the overlapping B0-read case using a graph intersection and the second
moment. Its kernel is equivalent on that restriction. This package extends
the count to arbitrary rank-d records and applies the credited fourth
moment; it does not claim the first obstruction for the B0-read case.

Here is the complete spectral implication of the finite source checks.
Let `E_s = B_s* B_s/48` and `H = E_0+E_1+E_2`, where * denotes real
transpose together with inverse owner route. The ordinary Gram identity
`B_s B_s*=48I` makes each E_s an orthogonal projection of rank 8N.
Moreover `H=C*C/48`, so `rank H=rank C=r`. All matrices are rational;
their real and rational ranks agree.

For completeness, the finite contractions behind the moments are as
follows. Every source column r_p has squared norm four and their outer
products sum to `48 I_8`. Thus
`sum_(p,q)(r_p^T r_q)^2=18432`, with diagonal contribution 1536.
For different stages, the checked relative-route product table has only
the 96 diagonal pairs at the identity and has singleton nonidentity
fibres. Its matrix coefficient at the identity is `192 I_8`.
The two product tables with a common first stage intersect only there.
Under the regular owner action, a route has trace N at the identity and
zero otherwise. These finite facts give the following reduced cyclic
projection-word traces, all divided by N:

```text
tr E_s                                      = 8,
tr E_s E_t                                  = 2/3,
tr E_s E_t E_u           (s,t,u distinct)    = 1/18,
tr E_s E_t E_s E_t       (s != t)            = 23/216,
tr E_s E_t E_s E_u       (s,t,u distinct)    = 1/18.
```

In particular the alternating fourth trace is
`[8*192^2+16*(18432-1536)]/48^4=23/216`, and the mixed fourth
trace is `8*192^2/48^4=1/18`. In the distinct-stage triple the checked
route intersections force its three port indices to coincide, giving
`96*4^3/48^3=1/18`. Cyclic removal of adjacent repeated projections
classifies the fourth-power expansion into respectively
`3,36,24,6,12` words of the five displayed kinds. The lower powers are
expanded in the same way. Consequently the exact source certificate
gives

```text
(tr H, tr H^2, tr H^3, tr H^4)/N = (24,28,109/3,1823/36).
```

Use the rational polynomial

```text
p(t) = 1-(1-81t/40+9t^2/10)^2
     = (81/20)t-(9441/1600)t^2+(729/200)t^3-(81/100)t^4.
```

It satisfies `p(0)=0` and `p(t)<=1` for every real t. By the real
spectral theorem, zero eigenvalues of H contribute zero to `tr p(H)`
and each nonzero eigenvalue contributes at most one. The exact moment
substitution therefore proves

```text
r = rank H >= tr p(H) = (117/5) N.
```

Substitution in (1) gives a lost selected-data dimension of at least
`(77/5)N-d`. In particular:

- A single eight-coordinate ordinary query has `d <= 8N` and leaves
  at least `(37/5)N` lost selected dimensions, even when its record also
  drives paired selected updates.
- Any transcript of at most fifteen scalar owner arrays has
  `d <= 15N` and leaves at least `(2/5)N` lost selected dimensions.
  Hence at least sixteen scalar owner arrays are necessary in this
  interface. Sixteen are not proved sufficient.

For orientation, the weaker source bound `r >= (144/7)N` would already
exclude the eight-coordinate query, with defect at least `(32/7)N`.
The fourth-moment source bound is needed for the stated sixteen-array
floor. An owner-array count is not a recursive rank, native-call count,
or completed supplier bill.

## Verification boundary

`algebra.py` verifies the ordered family in two independent finite
rational matrix models with noncommuting selected sections and shears.
It separately constructs the complete first-pair observation matrix on
all arbitrary input coordinates and checks its kernel and selected-data
defect. These are regression fixtures for the ordered proof; they are
not substitutes for binding the actual QQ16 source rank and tail. The
package verifier handles those actual-source obligations separately.

`tail.py` independently replays the 17 events following B1 on a formal
arbitrary ordinary residue g, checks the exact trajectory against the
retained QQ16 witness, and binds the nine local pair indices to the
literal `expected_pairs` assertion in the inherited replica-prefix
auditor. It reads that assertion as syntax; it does not execute that
auditor or replay its compressed parent template. The final former-Y
classification is inherited explicitly from the QQ16 witness, rather
than established by a fresh native field-type check. Removing the first
negative bridge makes B3's source nonzero. Assigning F2 to pair 1 is a
source-binding rejection: both candidate X sources are zero on this
particular family, so that mutation alone would not change its ordinary
trajectory. Counting the final former-Y hole as completed-X is separately
rejected.

The local maps, selected sections, and retained tail are credited to
Ali Romman's QQ16 package. The triple-query moment/rank input is
credited to its pinned predecessors. This proof's contribution is the
arbitrary-record transcript floor for an independently derived changed-shear family,
including dense reads used for paired selected updates. It does not
claim native implementability, a favorable cost, or a changed frontier.
