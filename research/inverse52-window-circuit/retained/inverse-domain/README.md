# The actual two-mode inverse reaches every residue pair modulo 52

**Scoped source-domain proof; no new inverse or κ.** For modes 0 and 1 of the
retained 112-owner inverse, the map
`x -> (M[:,0]^T x, M[:,1]^T x) mod 52` has image `(Z/52Z)^2`.
Every one of the 2,704 pairs already occurs with `x_i in {-1,0,1}`.
The direct denominator-13 probability ABI applies exactly when **both mode
numerators are divisible by 4**: 169 residue pairs, of which 144 have two
nonzero probabilities. The source input `x=e_0` gives the minimal nonzero
integer-input witness `(1/52,1/52)`, outside that ABI.

This answers the actual-residue and nonadaptive-window question left by
[zxv's PR6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072), exact
head `9011bf83e85ecd0443c789cf03259442f750877d`, and complements zxv's
[PR6068](https://github.com/CrocSwap/integer-mult-bounds/pull/6068), exact head
`689e28282fd5259dec7f75b83904617dab2d7b3a`. Those pending heads are contextual
citations, not ancestors or executable dependencies of this package. Their
correct abstract sampling theorems are not disputed. Neither predecessor
asserts that arbitrary actual inputs have denominator-13 fractional parts.
The retained deterministic kernel is not alleged defective.

Canonical base is `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8,
selected PR6030 unchanged. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/6073#discussioncomment-19234406)
is refined to this single missing source-domain implication. All scientific
inputs are already on that canonical base and pinned in `SOURCES.json`.

## Complete image and bounded witnesses

Let `m_0,m_1` be the first two `mode_columns` in the pinned
`research/coded-native-caller/NORMALIZERS.json`, with zero-based owner indices.
Their columns at owners 2 and 12 are `(1,0)` and `(0,1)`. The corresponding
2-by-2 minor is the identity. Thus the integer map onto `Z^2` is surjective,
and reduction modulo 52 proves the complete image assertion without relying
on a random-input search or the finite verification alone.

There are 32 owners with `m_0[i]=±1,m_1[i]=0` and 32 distinct owners with
`m_0[i]=0,m_1[i]=±1`. For any target residues choose representatives `t_0,t_1`
in `[-26,25]`. In exclusive group j choose `|t_j|` owners and set
`x_i=sign(t_j)*m_j[i]`, setting every other owner to zero. The two sums equal
`t_0,t_1` exactly, and `|x_i|<=1`. This proves the same image for every integer
bound H>=1. For H=0 only `(0,0)` occurs. It also avoids suggesting that a
large bound such as H=51 is necessary.

For a numerator s, write `s=52q+r`, `0<=r<52`. Adjacent unbiased stochastic
rounding has output `q+B`, with `P(B=1)=r/52`. This probability equals an
integer multiple `a/13` if and only if `r=4a`, equivalently `s=0 mod 4`.
For both modes the exact input subclass is therefore

```
L = {x in Z^112 : m_0^T x = m_1^T x = 0 (mod 4)}.
```

The identity minor also makes the map modulo 4 onto; hence L has index 16.
It is broader than `4Z^112`: for example `x=e_2-e_3` lies in L, although
neither nonzero coordinate is divisible by 4. Its allowed residue pairs
are exactly `{0,4,...,48}^2`. The 144 pairs with both coordinates nonzero use
PR6072's published nonzero table ABI directly. The remaining 25 pairs have
one or two deterministic zero flags and need explicit endpoint handling.
No frequency assumption on actual inputs follows from these counts.

## First fixture, signs and availability

The predecessor's committed `FIRST-FIXTURE.json` is `x=4e_0`, giving first
four numerators 4 and the calibration 1/13. At `x=e_0` those numerators are
1, giving 1/52. This has minimum possible nonzero integer l1 norm, namely 1;
no lexicographic uniqueness is claimed. At `x=-e_0`, each affected output is
`-1+B` with `P(B=1)=51/52`, not 1/52. Equivalently, sample a magnitude flag
with probability 1/52 and negate the rounded magnitude. These conventions
have the same output law but different meanings for their upper flags.

The actual `round52_into` takes a signed word, copies its absolute magnitude,
saves its two low bits as `low`, and divides the remaining bits by 13.
If the resulting remainder is h, the magnitude remainder is **4h+low**.
Its deterministic nearest rule tests `4h+low>=26`, then restores the sign.
Discarding `low` is not a source-preserving stochastic adaptation.

The source `recode` validates input bounds, computes **all eight original
mode numerators**, rounds the eight mode words, and only then starts owner
writes. Each source column has 56 signed nonzero entries, so every prefix
has magnitude at most 56H; the source width `bit_length(56H+2)+1`
excludes signed overflow during collection. Thus modes 0 and 1 are simultaneously available before any rounded
output is consumed. This is a real nonadaptive arithmetic window for one
scalar component. A stochastic pair could be chosen there using independent
fresh randomness, but parameter extraction, table dispatch, movement, and
any changed scratch lifetime still require implementation and payment. This
does not claim a free batching window across two inverse calls or components.

## A finite conditional adapter contract

For arbitrary floor residues `r_j=4a_j+l_j`, `0<=a_j<=12`, `0<=l_j<=3`, draw
**independent** `U_0,U_1` uniformly from `{0,1,2,3}` (four fresh fair bits).
Set `A_j=a_j+1[U_j<l_j]`. Conditional on both selectors, return independent
flags with probabilities `A_0/13,A_1/13`. Then

```
E[A_j/13] = (a_j+l_j/4)/13 = r_j/52,
P(B_0=b_0,B_1=b_1) = product_j P(B_j=b_j).
```

The second equality follows by conditional independence and independence of
the selectors: each conditional factor depends only on its own selector.
The verifier sums all 16 conditional product distributions for every residue
pair. Sharing one selector fails: for `(r_0,r_1)=(1,1)`, `P(11)=1/676`
instead of `1/2704`, even if the conditional table itself returns independent
flags. Reusing one output flag also fails.

The adapter can dispatch to the existing 144 configurations when both A's
are in `1..12`. Handle `A=0` and `A=13` as deterministic 0 and 1. If only one
A is nontrivial, use a table with that probability and dummy probability 1/13,
then discard the dummy output; if both are deterministic, use no table.
This states a complete finite conditional **law** contract without importing
or auditing the pending table implementation. Conditional on PR6072's exact
sampler contract, it is an exact logical construction with almost-sure
termination and four prefix bits plus less than 7/2 expected table bits.
The resulting upper bound is less than 15/2 expected draws, not a savings
claim; table randomness must be independent of the four prefix bits.
No finite worst-case cap follows. The four selector bits, two adjusted
parameters, output/dummy bits, dispatcher and stopping history have nonzero
storage/cleanup costs; no physical allocation or reversible erasure is proved.

## Reproduction and limits

```
python3.12 -B scripts/research_package.py --package research/inverse-residue-domain
python3.12 -B scripts/check_research_commit.py --package research/inverse-residue-domain --check-source-history
```

Normal and optimized registered checks authenticate all five live inputs;
construct all 2,704 bound-one witnesses; classify all residue pairs; sum 43,264
adapter branches exactly; check 417 signed numerators; and execute 15 source
kernel fixtures against an independent rational nearest-output oracle.
Instrumentation checks that all eight numerators and original owners are
present at the first rounding, and that owner writes follow all eight rounds.
Eight negative controls reject changed source bytes, rank collapse, dropped
low bits in the probability law, wrong signed flags, shared output flags,
shared selectors, actual divider low-bit deletion, and an actual early owner
clear. Checks use explicit exceptions and remain active under `-O`.
The direct verifier uses only the standard library, writes nothing, invokes
no Git, and runs in an official exported tree. The registered metadata runner
separately authenticates historical provenance through Git.

The all-input image and subclass statements are written algebraic proofs;
the exhaustive residue check corroborates their source binding. The adapter
is a conditional probability construction, not an emitted physical sampler.
No full native/controller replay, Lean/Docker build, all-eight joint optimizer,
outer error propagation, complete tariff or selected-frontier change is supplied.
The physical C^-1 consumer still owes its actual K wrappers, movement,
precision/guard propagation and legal restoration.

## Open next questions

1. Can the proven arithmetic window host a concrete exact sampler with a paid
   dispatch, tape and cleanup ledger? Start at the first `round52_into` call,
   preserve both full signed remainders and price the endpoint cases. Blocked
   by the absence of a physical stochastic service ABI and caller allowance.
2. Is a direct denominator-52 joint graph cheaper than this deliberately simple
   conditional adapter? Start from the four product weights over 2704 and an
   explicit dispatcher. Compare total hosting cost, not expected fair bits
   alone; no new construction round is justified without a caller budget.

## Credit

JoyboyBrian, with substantial OpenAI Codex assistance; Apache-2.0. zxv's
PR6072/6068 supply the precise sampling and open reachability questions.
JoyboyBrian's PR5037/5069 supply the deterministic kernel and physical pair.
Dillon's PR4933 supplies the signed normalizers, actual mode factorization and
physical ABI; Dugongue/mdumitrean's PR4929 supplies the coded producer.
Nick Petalas's PR6026 motivates the stochastic comparison. Cinna Davis,
Cao Yifan/intqwq, zxv, Jacob Alan Sussman and the retained native, Clifford,
ownership, precision and compiler lineage retain predecessor credit. Sources
are unchanged. No independent human or formal-kernel acceptance is asserted.
