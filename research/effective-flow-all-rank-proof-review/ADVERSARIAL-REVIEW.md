# Adversarial interface review of the assembled all-rank audit

**Conditional approval; no blocking gap found in the assembled implication.**
I cross-read PROOF-REVIEW, the mixed/onset/tail notes, README, TASK and VALIDATION
after preparing the separate MIXED-REVIEW. The reviewed coordinator draft was
identified as11,411 bytes, SHA256
`0bad146f0b93678a4d79c43f752c7fe3cba7b3eafb5d2608fd7b4b5bfbbffae8`.
This is written mathematical/static review only: no scientific code reading,
program execution/import/compilation, numerical experiment or proof-kernel run,
and no edits to the coordinator or other reviewers' files. The source author's
already-stated theorem is being reviewed, not newly discovered.

## Normalization and the transition between layer regimes

The independently derived mixed prefactor is
A^(G-1)q^h exp(-alpha B); the leaf prefactor is A^G exp(-alpha B).
Dividing by F_G=A^G exp(-alpha B)/(J c_sigma sqrt(G)) therefore gives
J/A=1-q and J P(s)/121^s respectively. The assembled argument preserves
both; it does not silently replace the leaf coefficient or reciprocal of1-q.
The root capacity being discarded is nonnegative under the literal rank caps;
all signed boundary and leaf exits remain in the lower bound. G>0 and J>0
are needed for F_G; the initial range is handled separately, not by that
normalization at G=0.

The crucial geometric bookkeeping is sound. With w_h=(1-q)q^h,

    sum_(h=0)^(G-1)w_h F_h-M
      =sum_(h=0)^3000 w_h(F_h-M)
       +sum_middle w_h F_h+sum_late w_h F_h
       -M*sum_(h=3001)^infinity w_h.

Thus the first block contributes(1-q^3001)M, and the entire missing M mass
is charged once, including indices beyond the finite last layer. Middle actual
values use12Q, missing M uses5Q, explaining17Q*q^3001. The late actual
values are then charged separately, rather than accidentally omitted or
subtracting their M twice. For the middle range ell>=G/2-1>=n_LLT;
for the late range ell may be0, but only a probability/supremum bound is used.
The h=G-1 deterministic paid-sum case is therefore included without an LLT.

The first block has a conditional shift bounded uniformly in the actual
target word and offset delta. Middle interval masses use location-uniformity,
not a false bounded-shift assertion. The late bound uses neither Gaussian
flattening nor a long paid word. This split is consistent with the onset
note's distinction between shift-uniform Gaussian comparison and the
shift-dependent flat-density correction in source formula(14).

## Endpoint-sensitive kernels and the entire leaf

The assembled review correctly needs each unsigned kernel to be decreasing
only on its own finite window. The signed sum/zero extensions can jump and
need not be globally decreasing. The x=1 derivative singularity is harmless
because the component is continuous and has finite monotone variation.
Stieltjes integration retains its terminal-constant whole-window term, so
it remains correct for a constant kernel and for discrete probability laws.
Every half-open cap interval uses the inherited endpoint-uniform estimate.
A Gaussian's zero endpoint mass is not substituted for a discrete cap atom.

The leaf estimate includes[0,5000) and the complete disjoint partition
[5000+j,5001+j), j>=0. Every atom, including at0 or5000, is assigned once.
Positive summation justifies the infinite upper bound. Comparison with1/tau
also separately pays the Lebesgue tail; it does not merely bound the probability
tail and then identify the truncated integral with the whole one. Multiplying
both errors by B_leaf gives the displayed1/5+2*10^-7 bound. The all-rank-one
paid word has positive probability and lies in the nominal tail for large G,
so declaring that tail absent would be wrong even for this actual law.

A concrete additional written terminal-cap control is valid already atN=121.
Here G=floor(log_5(N/121))=0 and the empty paid base has product1, allowed by
cap floor(N/121)=1. Under the inherited complete mirror leaf identity, the
terminal paid letter r=48 produces exit rank48 with multiplicity P_48=448.
It exceeds the base cap1 but remains strictly below parent121. A second cap
on terminal rank would delete these actual positive inherited exits and change
the recurrence/conservation identity. This hand control is conditional on the
stated mirror identity; it is not an independent execution of the source flow.

## Hand exponential certificate and symbolic onset

The small certificate can be checked directly without a large-power program.
Successive partial sums through j=6,7,8 are1553/80,5557/280 and89641/4480.
Thus

    sum_(j=0)^8 3^j/j!=89641/4480=20+41/4480>20.

Positive remaining Taylor terms give exp(3)>20, and exp(3/2)>1+3/2=5/2.
Consequently exp(36)>20^12=4096*10^12>10^15 and
exp(37.5)>20^12*(5/2)=10240*10^12>10^16. These justify exactly the small
tail inequalities used here, without claiming to have executed the source's
alternative large integer comparisons.

The onset note's substitution w=log n is also compatible with the assembly.
For w>=60, multiplying the first remainder by w gives a decreasing multiple
of w exp(-w/2). The second remainder's logarithmic derivative is
2/w+1/2-exp(w/2)/640<0. At60, exp(30)>2^40 and monotonicity of
u exp(-u/320) give the displayed upper bound below2^65 exp(-2^31)<1/2;
5001*60^2<2^25 and2^40/320>2^31 justify its integer slack.
The two remainders therefore sum to less than1/w. Passing from2/log n to
10^-8 at the symbolic n_LLT uses the separately declared variance/pi bounds.
No huge integer, probability convolution or practical onset is asserted.

## First moment, all ranks and finite-premise boundary

The combined mixed/leaf loss is below1564.2010002<1600. Conditional on the
complete margin D_full>40000 and positive F_G, this gives D_N>0. The
identity H_N=1-D_N/C_N then uses the inherited C_N>0. Each parent offset
was bounded, or eliminated by a location-uniform estimate, so every integer
N>=121*5^G0 is covered, not merely a subsequence of powers of5.

The first-moment identity must be the complete one, including all exits:
sum c_z z-sum d_e e=608 U_N(1)>0. It gives the linear test exactly
N-608 U_N(1)/C_N<N. Nonnegative coefficients, L(0)=0 and every positive
child strictly below its parent yield L(n)<=n by strong induction.
For1<=n<N0, this implies L(n)<=N0^(1-s)n^s because0<s<1. For n>=N0,
the power comparison at every smaller positive child and0^s=0 at the zero
child give the same bound using H_n(s)<1. No initial-range census up to the
giant N0 is required or claimed. An independently unverified conservation
identity cannot be replaced by this induction argument: it remains a premise.

README/TASK/VALIDATION retain the correct boundary. The finite mirror/flow
identities, inventories, exact numerical q/J/variance/margin gates and uniform
LLT/Fourier/classical approximation premises are inherited as named. Prior
PR6723/6728 cover their distinct H/root/local-limit scopes, not all those
finite gates or the historical recurrence's executable realization. This
review did not independently repeat the coordinator's canonical-predecessor
text comparison or admit actual source constructors/operators. Its conditional
mathematical approval must not be reported as a passing source replay.

Scientific execution is explicitly SKIPPED. Written hand controls are not
executed tests, and later byte/history/archive/CI controls concern integrity
and workflow rather than mathematical kernel certification. No selected
analytic_recovery or other five-assumption admission, physical/native or
compiler/precision/tape/ownership bill, paid-profile/exponent/frontier change,
scientific adoption or merge follows. Source-aware AI roles and inherited
source/earlier-review exposure are disclosed; no blind human acceptance is
claimed. The source and classical predecessors retain their stated credit.

No correction is requested within this conditional assembled scope.
Substantial OpenAI Codex assistance; Apache-2.0.
