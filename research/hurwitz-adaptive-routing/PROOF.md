# Adaptive supports with a paid routing header

**Scoped negative result; no new κ.** On the ten Hurwitz E8 lines, choosing
message supports from the input does not beat the `sum_t b_t` copy floor
in the header model below. The conclusion is an **expected-cost** bound for
uniform independent inputs, hence also a worst-case bound. It is not a
pointwise lower bound on every execution.

The geometry, charge table and transversal weights are Douglas R. Colkitt's
[PR703](https://github.com/CrocSwap/integer-mult-bounds/pull/703). Alexander
Templeton's [PR785](https://github.com/CrocSwap/integer-mult-bounds/pull/785)
extends them to fixed-support nonlinear messages by transcript injection.
Both proofs are retained verbatim under `reference/`. The new step here pays
for an input-dependent routing header, rather than assuming the supports are
fixed. The finite four-port census below supplies additional exact evidence.

## Model and theorem

Port t has an independent uniform string X_t of b_t bits. Receiver t initially
knows only X_mate(t), where the ten lines form five orthogonal pairs. Source
roles and receiver roles are distinct: a receiver does not initially own its
own demanded X_t. Let B = sum_t b_t.

A central encoder, optimistically given free access to every source, chooses
a header M = h(X). Its binary encoding belongs to one finite prefix-free code
(the empty word is allowed only if it is the sole codeword). Write ℓ(M) for
its length. Every receiver and every payload encoder receives the header,
and may use its **entire content**, including any source information it reveals.
The header is charged **2ℓ(M) quaternionic units**: its declared source and
reader spans are both the full two-dimensional quaternionic space.

Given M=m, there is a fixed finite list of payloads. Payload j has source set
A_j(m), reader set R_j(m), nonnegative integer width q_j(m), and value

    Y_j = f_j(m, X_{A_j(m)}) ∈ {0,1}^{q_j(m)}.

Every reader in R_j(m) receives the same payload. The list, order, supports,
widths and functions depend only on m, and carry no further uncharged
information about X. The number of payloads can vary with m. Encoders and
joint decoders can be nonlinear. Payloads do not relay other payloads; this
is one round of support selection followed by local encodings, not arbitrary
interactive communication. All demanded strings must decode on every input.

For source and reader line spans define

    c(R,A) = rank_Q(V_R V_A^T) / 4,
    P(m) = sum_j q_j(m) c(R_j(m), A_j(m)),
    C(X) = 2ℓ(M) + P(M).

Additive per-bit pairing-rank pricing, including the header's full-space
price, is an **explicit model premise**. It is not derived for arbitrary
physical nonlinear circuits from a scalar copy-tree theorem. Localized or
private metadata, cheaper shared realization, and interactive relays are
outside the model. Encoding, source access, decoding and side-information
preparation are granted free, making this an optimistic cost screen.

**Theorem.** Every code in this model satisfies

    E[C] ≥ B,                 max_X C(X) ≥ B.                 (1)

This is sharp: the inherited fixed-support direct-message code is a special
case with empty header and cost B. There are also genuinely adaptive attaining
codes, including the exact example and complete census below.

## Proof with the routing information retained

A transversal T chooses one line from each of the five mate pairs. There are
32 transversals and each line appears in 16. The inherited charge table gives

    sum_T [R ∩ T ≠ ∅ and A ∩ T ≠ ∅] ≤ 16 c(R,A).              (2)

For clarity, c=0 for empty sets or orthogonal singleton pairs; c=1 when at
least one nonempty set is a singleton and the pairing is nonzero; c=2 when
both sets contain at least two lines. The last case follows because any two
distinct lines span the quaternionic plane. For c=1, a singleton belongs to
only 16 transversals. For c=2, there are only 32 to count. The verifier rebuilds
the rational geometry and exhausts all 1,048,576 support pairs.

Fix T and all inputs outside T. Given M=m, retain the payloads with both
supports meeting T, in their m-determined order; call this tuple Z_T.
Then **(M,Z_T) determines X_T**. Indeed, omitted payloads received by T have
source sets disjoint from T and can be recomputed from m and the fixed outside
inputs. All mate side information is outside T. Thus two X_T assignments
with the same (M,Z_T) would give identical complete decoder inputs at every
receiver in T, contrary to zero-error recovery.

Use Shannon entropy in bits, only on finite uniform input spaces. Injection
and the conditional fixed widths imply

    sum_(t∈T) b_t
      = H(X_T | X_{Tᶜ})
      ≤ H(M | X_{Tᶜ}) + H(Z_T | M, X_{Tᶜ})
      ≤ H(M | X_{Tᶜ})
        + E[sum_j q_j(M) [R_j(M) meets T and A_j(M) meets T]]. (3)

The last inequality is valid even though conditioning on M correlates the
inputs: at each fixed m and outside assignment, the tuple has at most
2^(sum of its widths) values. No conditional independence is assumed.

Sum (3), divide by 16, and apply (2) separately on every branch:

    B ≤ (1/16) sum_T H(M | X_{Tᶜ}) + E[P(M)]
      ≤ 2 H(M) + E[P(M)]
      ≤ 2 E[ℓ(M)] + E[P(M)] = E[C].                         (4)

The final inequality is the prefix-code entropy bound. For completeness,
Kraft gives K=sum_m 2^-ℓ(m) ≤ 1; with a_m=2^-ℓ(m)/K, nonnegativity of
relative entropy gives H(M) ≤ E[ℓ(M)]+log₂ K ≤ E[ℓ(M)]. This argument also
covers deterministic headers with empty codeword. Maximum cost is at least
average cost, proving (1). This is a written all-width proof; the finite
replay is not its replacement or a proof-assistant formalization.

The coefficient 2 is necessary for this unrestricted public header model.
Put all five mate-pair XORs of b-bit strings in the header, with no payloads.
Its length is 5b and every receiver decodes using its mate. Pricing that
header at λ per bit with λ<2 would give 5λb<10b. The same conclusion holds
after any invertible nonlinear recoding of the header bits.

## Exact four-port adaptive census

Choose two mate pairs and one input bit at each of their four ports; the other
six demands are zero. The header is any Boolean function of the four bits,
encoded in one bit. There are exactly **65,536** functions, including two
constants. Both constants can instead use the empty header, as a separate
baseline. Payload widths and supports may depend on the header, as above.

For a header value r, its fibre F_r is a subset of the 16 inputs. For each
of the four active transversals T, define

    n_(r,T) = max_u |{x ∈ F_r : x_(Tᶜ)=u}|,
    L_r = ceil((1/2) sum_T ceil(log₂ n_(r,T))).

An empty fibre contributes zero. On a nonempty fibre, injection requires at
least ceil(log₂ n_(r,T)) relevant payload bits. Averaging the four transversal
inequalities gives P(r)≥L_r, since the same charge table has weight 1/2 on
each active transversal and P is an integer. Thus for nonconstant headers

    E[C] ≥ 2 + (|F_0| L_0 + |F_1| L_1) / 16.                (5)

Every quantity in (5) is an integer or rational; the checker uses no floating
logarithms. It checks all functions, not a random search or a solver timeout.

Exactly **30 nonconstant headers** have the numerator in (5) equal to 32,
so are not excluded from the optimal cost four. For each of these 30, and
each header value, the certificate supplies **two raw source bits** which,
together with the header and the receiver's mate, determine every demand.
Each raw bit can be broadcast at charge one. Literal truth-table decoding
therefore attains cost four for all 30. The other 65,504 nonconstant headers
have a strictly larger lower bound in (5), so cannot attain cost four in
this model. This is a complete optimum-header classification for these four
one-bit demands and a one-bit header, not a classification for arbitrary b.
The receipt stores the entire bound histogram and all attaining witnesses.

There is a compact description of the 30 tables: writing z_0=X_0⊕X_1 and
z_1=X_2⊕X_3, they are exactly

    h = z_1 ⊕ g(X_0,X_1)   or   h = z_0 ⊕ g(X_2,X_3),

where g is any Boolean function of two bits. Each family has 16 elements;
their intersection is z_0⊕z_1 and its complement. The separate conflict-graph
checker reconstructs the witness family and checks this equality of sets.
Broadcasting the two arguments of g supplies an explicit decoder: each
receiver in the other pair obtains its pair parity from h and those arguments.
Of these 30 headers, 14 are affine and 16 are nonlinear.

For a concrete support-adaptive code, let the two pairs be (0,1) and (2,3).
Broadcast the parity r=X_0⊕X_1⊕X_2⊕X_3 as the paid header. When r=0 broadcast
X_0,X_1; when r=1 broadcast X_2,X_3. The header relates the two pair parities,
so each receiver decodes with its mate. Charge is 2+1+1=4 in both branches.
Seed 42 chooses the two actual Hurwitz pairs and parity/complement convention
for the ten-port control. Three remaining pair parities cost another six,
giving a genuine adaptive, constant-cost-ten code on all 1,024 ten-bit inputs.
The census also supplies nonlinear headers attaining four; an algebraic
normal-form check distinguishes them from affine functions.

A separate prefix-code control illustrates the expectation qualification.
Let z be the five pair parities; send header `0` if z is all zero, and `1z`
otherwise, with no payloads. All receivers decode, but 32 of the 1,024 inputs
cost only two, while the other 992 cost twelve. Its mean is 187/16≥10. Thus
strengthening (1) to a pointwise cost-ten assertion would be false.

## Optimistic complete budget and limitations

Under the **additional** inherited Dfc accounting for b bits per port,
rational port rank k=4b, v=10 and a copy allowance cst at least the worst-case
4C, equation (1) gives cst≥40b. Hence at every positive stage count s,

    D/T ≤ (s−1)40b − s·40b = −40b.

This grants helpers, source accesses (including header generation and delivery
beyond the declared rank charge), frame changes, restoration, extra copying,
payload processing and recursive children **zero extra expense**. Any
nonnegative added charges only worsen the screen. No other supplier or outer
assembly can turn this nonpositive supplier deficit into a saving in this
format. We therefore stop before implementing a physical supplier or claiming
a new κ. The result does not assert a general impossibility for integer
multiplication, other geometries, localized headers, different stage invoices,
correlated inputs, errors, or variable-length payloads not determined by M.

The all-size compiler, physical realization/hosting, precision/tape and
analytic transfer assumptions remain inherited. Prepared for Jerry Chen
(@CubeJerry) with substantial OpenAI Codex assistance. Apache-2.0.
