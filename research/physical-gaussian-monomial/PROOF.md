# Physical Gaussian monomial on complete record packets

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I implement the Gaussian phase boundary left open by PR3055. I retain
PR2250's affine word, PR2378's coordinate and signed-word identities,
PR2422's coefficient-field composition, and PR3055's physical Compact
argument. I give a structured tape-program refinement under those source
contracts. I have not proved this Python program in Lean or expanded it into
a complete transition table.

## Quantified interface

Fix a field schema with ell fields, m distinct vector coordinates, and
`1 <= m <= 73`. Fix an invertible binary m-by-m matrix L, an offset v,
a constant c in Z/4, linear coefficients l_i in Z/4, and strict-upper
quadratic coefficients q_ij in {0,1}. I compile these finite data before
reading the input. I use the source convention: diagonal phase terms already
belong to l_i; I do not reinterpret lower or diagonal matrix entries.

Supply canonical encoded Counts for positive f,K,G,h,r,C and `0 <= rho < K`,
with h>=2. Each vector field has width fK; u,t,b each have width `(f-1)G`.
Place u,t before the vector fields and b after them. Other complete spectator
fields may have width zero. Supply the complete C-row payload at its local
origin, with

    R = 2hr, a = sum(field widths), M0 = 2^a, v0 = M0*R,
    M = C*M0, V = C*v0, A = 2+a+ceil(log2(R+1)).

Within each record, concatenate r coefficient fields. Within each field,
store the h real bits followed by the h imaginary bits, each least significant
bit first in two's-complement notation. Interpret these integers on one common
caller-supplied grid. I neither change that grid nor round coefficients.

For record address x, let x_j contain the m selected coordinate bits at low-bit
position `rho+jK`. Define

    P(x) = f*c + sum_(j=0)^(f-1) [sum_i l_i*x_(j,i)
                              + 2*sum_(i<k) q_(i,k)*x_(j,i)*x_(j,k)] mod 4.

Let F apply `x_j -> L*x_j+v` independently at each selected position, fixing
the other address bits and the outer-row label. The forward endpoint sends
each Gaussian coefficient z at x to `i^P(x)*z` at F(x). The inverse takes
the coefficient at y, recovers `x=F^-1(y)`, and sends `i^-P(x)*z` to x.

I require representability of each component that the requested unit phase
negates. A most-negative h-bit component may remain or move without negation.
The exact guards are:

| Phase | Components that must exceed -2^(h-1) |
|---|---|
| 0 | none |
| 1 | imaginary |
| 2 | real and imaginary |
| 3 | real |

On admitted input, I preserve the borrowed payload and descriptors, return a
distinct protected output at its origin, and erase owned scratch contents and
markers. The caller consumes that output before reuse. For the named signed
headroom rejection on otherwise admitted input, I also erase owned work and
allow a valid retry. I make no rollback claim for arbitrary malformed input,
internal failures or interruption.

## Encoded phase accumulation

In `Recipe.phase`, I copy f, divide by the literal four, and retain only its
remainder in the finite control. I initialize the phase with `(f mod 4)*c`.
I traverse f columns using an encoded ripple counter and advance a Count
position by K after each column. I read one selected bit per compiled vector
coordinate. The fixed linear and strict-upper quadratic loops update a
four-state accumulator.

By induction over the column counter, after j columns I hold
`f*c + sum_(k<j) column_phase(x_k)` modulo four. The returned state therefore
equals P(x). For inverse mode I negate that state modulo four. I never decode
the varying f,K,rho or record address into a host integer. I use a fixed tuple
of m bits, with m part of the compiled schema.

In `scan`, I enumerate each complete row's addresses with an encoded Count.
I decode that address through the inherited encoded Layout, compute P once,
then traverse its r coefficient fields. I reset the local address at each
outer row. The outer row ordinal never enters phase arithmetic.

## Signed component traversal

In `read_component`, I consume exactly h binary cells. Before the final bit
I retain a Boolean recording whether the lower bits were zero. At the final
bit I retain the sign. Their conjunction detects precisely the most-negative
two's-complement word. I read both components and check the phase-specific
guards before writing either output component of that pair.

For negation, `emit_component` complements each bit and adds one using a
one-bit carry. Induction over the bit position gives the residue of -z modulo
2^h. The guard excludes the sole signed value whose negative cannot fit, so
this residue represents the exact integer -z. For copying, I consume and emit
exactly h bits, including leading zero bits. I do not normalize components as
unsigned Counts.

I implement the four unit phases as `(x,y)`, `(-y,x)`, `(-x,-y)` and `(y,-x)`.
I clear the two component bodies through borrowed physical views after each
pair, retaining their active leases until the complete scan ends. Thus I use
two reusable component buffers rather than one buffer per coefficient.

For each address the phase remains fixed throughout its r fields. By induction
over the field, record and row counters, I obtain the stated phase endpoint
on the whole packet. I check exhaustion before disposing of the owned input.

## Affine composition and returned ports

I use the authenticated `binary_word` compiler from PR2250 once, before input.
It decomposes the invertible affine map into XOR and toggle gates. Each gate
acts on the selected bits in parallel. For f>1, I execute the corresponding
physical Compact gate from PR3055 with n=f-1. I retain its dirty-field repair,
highest-bit step, complete-row scope, binary B1 calls and source hypotheses.

`PairDispatch` owns one Compact inventory. I select only an action in the
compiled word and require a closed callee, empty leases and consumed protected
output before changing its finite source, target and order. I suspend the
parent allocation scope during the call. After return I copy the callee's
protected output to one parent lease, clear the callee return and its marker,
and consume the previous parent stream. I keep the constructor seal active
through this exchange.

For f=1, the compact fields have zero width. I use the inherited complete-row
digit permutation or toggle, preserving spectator bits and concatenating rows
in their original order. I make no Compact/B1 call in that branch. I construct
the compact width as literal zero instead of multiplying zero by G: the
caller may supply an arbitrarily long unused G descriptor.

Forward execution phases the original record before applying the affine word.
Inverse execution reverses the involutive gates before evaluating the negative
phase at the recovered address. These compositions give the quantified
endpoint. A phase evaluated at the destination address would in general give
a different inverse; the failure suite injects that error.

## Complete time charge

For each record, the encoded Layout decodes at cost O_ell(a^2). A selected
bit lookup uses a scan of O(a) cells, and fK<=a with K>=1. I therefore charge
O_m(a^2) for the column loop and its position/counter maintenance. I charge
O(h) for each signed pair, including reads, emissions, rewinds and erasure.
The coefficient and component counters add no larger term: the subsequent
complete traversals pay their initialization. One phase pass costs

    O_(ell,m)(V + M*A^2).

I perform the whole-packet extent multiplication once. Its cost
`O((A+log(C+1))^2)` fits `O(V+M*A^6)`, using `log^2(C+1)=O(C)` and M>=C.
I keep C out of the per-record arithmetic. Initial cloning, final output
copying, complete rewinds and returned-port disposal cost O(V).

Let g_E count early XOR gates and toggles, g_L count late XOR gates, and
`g=g_E+g_L`, `S=4g_E+12g_L`. These constants depend only on the fixed recipe;
the source elimination gives the coarse bound `g<=m^2+3m`. For f>1 set

    delta = min(1,(f-1)*(2*2^(-G)+8*2^(G-K))).

Assume the pinned completed binary ordinary contract
`T_B1(v,b)<=K_q*v*(1+b^tau)` from PR3055, with its eligible fixed prime q,
source preservation, completed spectators and restored owned work. I obtain

    S*sum_(j=1)^C T_B1(v0,(f-1)G)
      + O_(ell,m)((g+1)*(V+M*A^6) + g*delta*M*A*(R+A)).

I count SC binary calls. The binary padding below q^2, native restoration and
disposal already belong to the inherited B1 bound. I retain that factor there.
At f=1 I obtain `O_(ell,m)(gV+M*A^6)` without B1. The positive-G check reads
only a constant-size prefix under the canonical-Count premise.

In the retained long-record domain `f<=p`, `A=O(p)`,
`G=4*ceil(log2 p)+6`, `K/log p -> infinity`, with R exceeding each fixed power
of p, PR3055 gives `delta=O(p^-3)`. I absorb the displayed preparation and
repair terms and obtain `O_(q,ell,m)(V*(1+((f-1)G)^tau))`. I retain the
unabsorbed invoice at independent finite sizes. I do not infer these universal
charges from the fixture timings.

## Inventory, space and rejection

I allocate `8*ell+256` parent scratch roles, one protected output, and one
Compact/Binary/native inventory before numerical input. A conservative parent
census is `2*ell+96` live roles: ell+3 Layout Counts, at most ell decoded
fields, seven persistent setup Counts, current/output/component streams,
counters and nested encoded arithmetic temporaries. I close a predecessor
before replacing its role. I allocate no physical inventory per gate, column,
record or coefficient field.

Including borrowed payload, a conservative occupied-content bound is

    6V + 2*delta*M*a + M + O_ell(A+log(C+1))
       + W_B1(v0,(f-1)G) + F_q.

I omit B1 and exceptional terms at f=1. I add D_in, the total borrowed
descriptor storage, when counting parameter input tapes. At f=1, an untouched
G tape can exceed V; I exclude it only from owned workspace and execution time.
The common-grid denominator is a caller convention, not another scanned
parameter in this interface.

For fresh backing storage, each parent role reaches at most
`O(V+A+log(C+1))` cells. Each Compact role has the PR3055 allowance
`O(v0+delta*M0*a+A+log(C+1))`; I retain separate protected-output and B1
allowances. Multiplication by the fixed role capacities preserves the stated
asymptotic bound. For a reused engine I take each role's maximum extent over
prior invocations: the simulator blanks cells without shrinking its backing
bytearray. I do not charge the fixed word as separate persistent inventories.

For `SignedHeadroomError`, I clear both component bodies, then the partial
phase output and its counter/buffer leases. The parent clears its current
owned packet, including an inverse call's permuted packet, closes Layout and
setup Counts, checks the empty pool, erases markers and closes the invocation.
I remove the empty protected-output marker before rethrowing. No Compact call
remains active during a phase rejection. I preserve the borrowed input and
descriptors; cleanup costs O(V) plus the charged descriptor scans.

## Evidence and scope

I exhaust the signed-pair domain at h=2,3,4, including 109 rejected pairs.
I compare encoded phases with a separate integer polynomial, including all
512 selected one-column addresses and wider repeated tensors. I compare
complete physical packets against integer Gaussian/address oracles using
orientation anchors and distinct Gaussian record labels. I test both
directions, multiple coefficient fields, dirty spectators and outer rows.

Gaussian negation carries depend on payload bits. I therefore use exact
Gaussian value oracles and the signed-pair argument above; I do not apply the
predecessor's linear bit-provenance technique through negation. During physical
execution I disable the indexed monomial and Compact reference methods.
The small complete fixtures use the ordinary elementary branch. I retain the
faster B1 contract as a source obligation, with PR3055's separate fitted-handoff
evidence, rather than a conclusion from these fixtures.

I test later-field rejection and a valid retry on the same inventory, and an
unused 4097-digit G at f=1. I inject missing repeated constants, destination
inverse phases, skipped coefficient phases, omitted signed guards, uncompiled
actions, unconsumed returns and source-binding failures.

PR2534 already supplied a selected-child fixture with the earlier indexed
Compact. PR2378/2422 already established the phase/record algebra. I contribute
the encoded fixed-inventory phase implementation and its joined physical
monomial endpoint. A caller still needs a common grid and adequate signed
headroom, coefficient arithmetic, proper-width recursive dispatch, private
lifetimes and a complete physical cost argument. I leave the selected result
and the higher PR2979 candidate outside this contribution.
