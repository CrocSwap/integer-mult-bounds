# QQ16: full-owner separation and a sharp 66-port family threshold

**Scoped exact result; no supplier or new kappa.** The common-axis witness
family of Adam Gall's PR2093 and commdata2338's PR2326 has **66 independent
original A-input defects across the whole owner array**. Any fixed set of
fewer than **66 ordinary source-port reads** leaves a nonzero defect in this
family invisible. A specified set of 66 removes this family. This does not
prove full controller recovery with 66 reads.

The finite certificate is a **74-by-74 integer minor** with determinant

```text
36317027395115679744.
```

Its rows are evaluations at actual owners: identity and a subset of the
stage-1 routes for ports 0 through 15. Together with an exact matching
upper bound, it proves rank 74 for the full-owner observation map. It
does not assume that distinct formal bit functions are independent.

This answers PR2326's second open question for its stated coefficient
family. The original nine-port necessary bound used only the identity
owner. The full-owner calculation was developed as a complementary
independent method after seeing
[EdDiboi's parity-subspace claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2205#discussioncomment-18941914).
Our [claim and finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/2205#discussioncomment-18942020)
share the evidence in the same investigation thread. Neither the witness
family nor the threshold question is claimed as new here.

## Contract and notation

Keep the fixed QQ16 `F0/B_1_2` pair, the A/T/U partition, the ordinary
19-event schedule, and the selected/completed-X/history observation
contract. The first maps and ordinary schedule are unchanged. Permit
homogeneous linear selected-field controls after complete F0, which may
read a fixed set S of ordinary coordinates, including their entire owner
arrays and arbitrary owner mixing, but leave ordinary fields unchanged.
Subsequent homogeneous selected-only controls are also allowed. There
is no earlier input-dependent record, ordinary preprocessing, or read of
the final former-Y endpoint. Each source coordinate counts once regardless
of how many times or at how many owners it is read. Dense ordinary queries
and adaptive choices of source coordinates are outside this statement.

Let `r_p` be column p of the actual 8-by-112 matrix R, let `U` be its 96
ordinary ports, and let `b_p` be the first local chart axis. Let G be the
regular owner group from the retained QQ16 construction. Only actual
registered routes and their identity are used below. Define rational-valued
functions, constant in every tensor payload coordinate,

```text
f_b(d) = bit_0(d b) in {0,1},     d in G,
h_p(d) = c_p f_(b_p)(d),         c in Q^96,
V = ker(R_U),                   dim V = 88,
H(c)(d) = sum_(p in U) r_p c_p f_(b_p)(d) = B0 h(d).
```

The claimed dimension is over Q for this 96-parameter family. It is
**not a dimension per owner, a rank-unit charge, or a general transcript
width lower bound**. A dense eight-component old-chart observation can
detect these 66 directions across its whole array without contradiction.

The exact source check gives `R_U R_U^T = 48 I` and `R_A R_A^T = 4 I`.
Thus `rank R_U = 8` and the selected injection at chart zero is invertible.
The verifier reads R from the pinned, reviewed QQ16 packet. It does not
claim to rederive that packet's complete native construction.

## Why this is a hidden-input family

The actual routes satisfy

```text
rho_s(p) b_p = e_(9+8(s-1)),     1 <= s <= 8.
```

Because route action reads the owner at `d rho_s(p)`, for every c in V,

```text
B_s h(d) = (R_U c) f_(e_(9+8(s-1)))(d) = 0,     s=1,...,8.
```

All payload translations act trivially on these payload-constant fields.
The verifier checks the route identities and binds every one of the 1,008
port/stage matrices to the actual QQ16 registry. This establishes the
all-owner cancellation by an identity, rather than by sampled owners.

Initialize pair 0 as in the credited predecessor, with every other pair zero:

```text
X_U=h, Y_U=0,
X_A=-P_(0,A) H(c), Y_A=-X_A,
X_T=Y_T=0.
```

The full initial query is zero. The ordered F0 identities give
`X_U=Y_U=h`, with every selected field zero. When `c_s=0` for s in S,
all permitted ordinary reads are also zero, so the allowed controls keep
this state unchanged. At B1, both `B1 h` and `B2 h` are zero; its output
is exactly `Y_(0,U)=h`, every other field zero. The retained tail leaves
only final `X_(0,U)=h`, carrying the former-Y native type. Every selected
field, completed-X descendant, and all five forward histories are zero.

The written ordered argument is inherited from PR2093/PR2326. The new
checker independently replays its reduced symbolic ordinary trajectory
and checks it against the pinned QQ16 evidence and the actual hosted-call
schedule. It does not execute the native child kernels. Any `H(c) != 0`
therefore gives an original A-input defect that these observations cannot
distinguish from zero. Multiplication by the invertible selected section
`-P_(0,A)` preserves its dimension. Rational coefficients may all be
scaled to integers without changing indistinguishability.

## Exact rank of the whole owner map

Group the ordinary ports by their identical first axes. For each occurring
axis b define

```text
C_b = {p in U : b_p=b},
L_b(c) = sum_(p in C_b) r_p c_p,
L(c) = (L_b(c))_b.
```

Then `H(c)(d)=sum_b f_b(d)L_b(c)`, so H factors through L. The column
groups have disjoint coefficient supports; their ranks add. The exact
source census in [RESULT.json](RESULT.json) has 47 groups:

- The axis-2 group has 30 ports and rank eight.
- Every other group's columns are linearly independent, with 66 ports
  and total rank 66 across those groups.

Consequently `rank L=74` and `rank H<=74` for the entire owner group.

For a matching lower bound, take the 17 actual owners

```text
d = I, rho_1(0), rho_1(1), ..., rho_1(15).
```

Form the 136-by-96 integer matrix E with entries

```text
E_((d,k),p) = R_(k,p) bit_0(d b_p),       0 <= k < 8.
```

Rational row reduction selects 74 original rows and 74 original columns.
Their integer Bareiss determinant is the displayed nonzero value; every
division in the determinant calculation is checked. The receipt contains
all selected owner/component labels, ports, and minor entries, so the
certificate can be checked independently without trusting row selection.
The verifier reconstructs those entries from the pinned sources.

Evaluation factors through H. Therefore

```text
74 = rank E <= rank H <= rank L = 74.
```

In particular `ker H=ker L`, of dimension 22. Also
`R_U c=sum_b L_b(c)`, so `ker H` is contained in V. It follows that

```text
dim H(V) = dim V - dim ker H = (96-8)-(96-74) = 66.
```

The checker additionally verifies `rank([E;R_U])=74`, an independent finite
check of the kernel containment used by this calculation. The 22-dimensional
kernel is exactly the redundancy inside the axis-2 group. An assumption
that H separates every nonzero coefficient vector would be false.

## The sharp coordinate threshold for this family

Fix any S of k accessed ports and put `V_S=V intersect {c_s=0 : s in S}`.
These are at most k scalar conditions on V, even when the controller gets
an entire owner array at each port: each array is just `c_s f_(b_s)` in
this family. Therefore `codim_V V_S<=k`. Choose a complement W to V_S
inside V. Since `H(V)=H(V_S)+H(W)`,

```text
dim H(V_S) >= dim H(V) - dim W >= 66-k.
```

For every k<66 this leaves a nonzero original selected-input defect,
invisible through the full retained schedule. Even if all implementations
and reads cost zero, this class of controller cannot restore it.

The bound is attained **for eliminating this particular family**. Leave
unread exactly the axis-2 group

```text
[44,45,48,49,50,51,52,53,54,55,56,58,59,60,61,62,
 63,64,65,66,67,68,69,70,71,72,73,74,75,77]
```

and read its 66-port complement in U. Every `f_(b_p)` is nonzero at one
of the certified owners. Thus a zero read transcript imposes `c_s=0`
on all 66 read ports. The remaining vector obeys

```text
H(c)(d) = f_2(d) R_U c = 0,     c in V_S.
```

It has no original A defect. Differences between any two members of this
linear family satisfy the same argument, so the read transcript determines
the original A value within the family. No claim is made about a legal
decoder, its retention, physical bill, or other input families. The checker
also removes one tap from this attaining set: the resulting 65-tap case
has exactly one remaining defect, as required.

## Reproduction and checked scope

From the repository root, using Python 3.12 or later and its standard library:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-owner-separation
python3 -I -O -B research/qq16-owner-separation/verify.py
```

Expected direct output:

```text
PASS_QQ16_OWNER_SEPARATION rank=74 defect=66 sharp_family_taps=66 controls=12 no_new_kappa
```

Replay authenticates every consumed source, reconstructs the exact rank
certificate, and compares the whole canonical receipt including scalar
types. It is read-only; `--emit-result NEW_PATH` creates a new receipt
exclusively. All checks stay active under `-O`.

Controls cover a singular separating minor, wrong determinant, payload-only
owner action, an unregistered route, a wrong common axis, confusing the
identity owner with the full array, incorrect F2 bank binding, an omitted
cancelling bridge, source corruption, JSON type corruption, and the false
65-tap sufficiency assertion. The F2 bank mutation is caught by source-call
binding; this particular zero-X trajectory alone would not detect it.

On native Windows, the complete registered replay passed with CPython
3.12.14, including normal and optimized runs and three isolated integrity
tests. The latter check a relocated positive replay, a corrupted receipt,
and a corrupted source manifest without changing frozen inputs. CPython
3.14.6 reproduces the exact receipt. These are local results; hosted CI is
reported separately in the PR.

The proof is a scoped rational linear-algebra argument with exact finite
source evidence. It is not a proof-assistant formalization, independent
human review, native execution, complete supplier replay, all-size or
precision proof. Native hosting, legal final reads, arbitrary-input
controller recovery and a complete invoice remain unproved. The selected
frontier and frozen inputs are untouched.

## Provenance and credit

Scientific base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
priority revision 4. The task picker selected `recursive-interfaces`, nonce
`19ff9482038bcc5873e8a54d230d4e65`. Source hashes and Git blobs are in
[SOURCES.json](SOURCES.json); [TASK.json](TASK.json) records the scoped
assignment, live-overlap coverage, and verification environment.

- **commdata2338 / PR2326**, exact inspected head
  `fb7d64cd4a51c49bc56920305b0aca64011a420c`: coordinate-access contract,
  identity-owner bounds, and the sharp-threshold open question.
- **Adam Gall / PR2093**, head `8b21a900eb520e4f11ea177b310f66316f8e8983`:
  common-axis bit-function witness, its initial A cancellation and retained
  tail. Its source was read through PR2326's byte-retained reference; no
  predecessor executable is imported or vendored here.
- **Ali Romman / PR1969**: the QQ16 local maps, packet, route semantics,
  original lost-query witness and retained schedule.
- **Cinna Davis / PR2216 and PR2268**: the shear and ordinary-tap repair
  question. **EdDiboi**: concurrent parity-subspace threshold investigation;
  our different finite certificate was shared before submission.
- Retained construction and compiler authors, with notices in the
  unchanged [QQ16 package](../joint-query/NOTICE.md).

New code and proof prepared by kyzer1023 with substantial OpenAI Codex
assistance for derivation, implementation, checking and writing. Apache-2.0.
Author-checked only; source reuse and the concurrent investigation are
explicit. There is no change to supplier admission or kappa.

## Open next questions

1. **Does one dense old-chart read close the remaining full controller
   kernel?** This family is detected by `B0 X_U`, so further coordinate
   tapping is a poor route around this particular obstruction. First fix
   the exact read and retention cut, then test the complete ordered kernel
   as in PR2174. Other input families, native access and final retention
   remain blockers.
2. **Does the attaining 66-port set fail on a different input family?**
   Family elimination alone is not controller recovery. First apply the
   full F0/B1 kernel calculation with that exact observation set, retaining
   the actual final-cut contract. The enormous owner representation and
   missing physical implementation preclude a supplier claim from this
   local calculation.
