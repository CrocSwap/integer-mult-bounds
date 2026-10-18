# Direct guarded wrappers for the original paired collector

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
This is an ordinary mathematical argument with executable checks, not a
proof-assistant theorem or a fast physical execution trace.

## 1. The interface being changed

PR3131 at `0c9e344d5a5295a218558fa4a51d867f39ff5311` constructs exact dense
Gaussian address gates using integer lifting. Its `address_word` is already a
reversible in-place word, but `address_oracle` first converts that word into a
source-preserving XOR oracle by running it forward and backward. `address_gate`
then uses two such oracles to overwrite the original bank and clear the old
bank. This is a valid general construction. It is unnecessary for this specific
word once its invariant lattice is known.

We retain PR3131's exact field-major layout, its compiled binary gate word,
its native phase convention, its paired collector and both nonlinear cores.
We change only the enclosing realization of each monomial wrapper. We retain
PR3109's in-place lifting backend, including its own protected evaluations,
copies, inverse cleanup, narrow work, history and source/compiler premises.
None of that internal work is removed by this result.

The selected conditional kappa remains 0.001672660197076918 (PR1094). The
frozen P104 consumer still fails its complete zero-saving screen 599/584.

## 2. Invariant-lattice refinement

Let X be a data space, E:X -> Y an injective reversible embedding that attaches
known-zero storage, and R a reversible word on Y. Suppose R(E(x))=E(f(x)) for
every x, where f is a bijection of X. Then

    f = E^-1 R E

is an in-place realization on the embedded domain. Its inverse is the literal
word E^-1 R^-1 E. The extra coordinates are known zero at contraction; erasing
an unknown nonzero value is not permitted. This elementary restriction of a
bijection is not a new reversible-computation theorem.

This reasoning does not convert an arbitrary protected XOR oracle into an
in-place algorithm. The decisive hypothesis is an actual reversible word R
preserving the embedding. It does not authorize overwriting a source that a
caller promises to retain. Here the overwritten object is the private collector
bank. Its five source arrays remain read-only, and its later return is paired.

## 3. The actual lattice and two-call gates

Let lambda >= 1 be the size of a contiguous target field. For any fixed order
of its lambda distinct axes, L denotes the literal Gaussian integer lift and
U the corresponding ideal C tensor. PR3033's scalar-period identity, also used
by PR3131, gives, for g=floor(lambda/2)+1,

    L(2^g z)=2^g U z,       L^-1(2^g z)=2^g U^-1 z.

The first equality follows by propagating even translations through each
pair's parity correction. After j ideal stages the component denominators
divide 2^ceil(j/2); g >= ceil(j/2)+1 for j<lambda. The literal reverse order
has the same denominator bound. We reuse this theorem; our separately written
pair interpreter uses the ideal rational pair plus its parity correction.

For matched, disjoint control and target fields define diagonal phases

    Q(c,t)=(-1)^(sum_j c_j t_j),  P(c)=i^(sum_j c_j).

PR3131's credited character identity is

    CNOT = P U Q U^-1 Q.

For one control bit it follows from C Z C^-1 Z=-iX and multiplication by i;
control zero gives identity. Tensor products give the whole field. Put G=2g
and define E(z)=2^G z componentwise. The first L^-1 in the executed word

    R = P L Q L^-1 Q

is exact on E(z). Its output components remain divisible by
2^(G-ceil(lambda/2)), which is at least 2^g. Q preserves that sublattice, so
the second L is exact as well. Hence R(E(z))=E(CNOT(z)). Only **two** L-family
calls occur. The literal inverse is obtained by reversing the operations and
their directions, including P^-1. The implementation does this explicitly;
it does not infer a nonlinear inverse merely from the ideal involution.

Similarly C^2=X on one target bit, so L^2(E(z))=E(X_all(z)), again with two
calls. The reverse word (L^-1)^2 is its literal inverse. Both gates preserve
the entire lattice E(Z[i]^N), including arbitrary negative inputs.

The reserve is sufficient, not claimed minimal. Omitting it is invalid: with
target axis 0, control axis 1 and input

    [(2,0), (-3,2), (-2,2), (0,3)],

the unguarded word produces

    [(2,0), (-3,2), (-1,3), (-2,1)],

instead of the required swap of the last two entries. A returned zero guard
bank also does not alone certify the right endpoint: omitting P can preserve
the lattice while producing the wrong phase. Both failures have controls.

## 4. Keep the guard across the whole wrapper

Every compiled field gate has the same multiplicity lambda and maps E(z) to
E of a permutation of z. The native Gaussian phases preserve E too. Therefore
embed once before a complete monomial wrapper, apply the phase and all field
gates on the embedded bank, and contract once afterwards. No guard growth
with the number of gates is required. The inverse reverses the affine word
first, then evaluates the negative native phase at the recovered address.

The phase is exactly

    lambda*phase + sum_columns(linear_Z4 + 2*strict_upper_quadratic).

In particular the tensor constant is multiplied by lambda and lower-triangular
or diagonal quadratic entries are not silently reinterpreted. The symbolic
affine validator in direct.py separately composes the emitted CNOT/toggle
word over F2 and checks its entire matrix and offset against the native recipe.
It checks the compiler output without reusing the compiler's elimination.

For a signed fixed-width representation, E can be implemented by adjoining
zero low bits and sufficient high sign-extension bits, with charged linear
scans. At contraction the low bits are zero and the high bits equal the
current output sign; inverse sign-extension clears the high ancillas. Phases
can change that sign, so the old input sign must not be used for contraction.
The output amplitude bound is unchanged because the endpoint is monomial.

For an explicit conservative outer-bank bound, declare beforehand that each
input component has absolute value < 2^b. One ideal C pair increases the
largest component by at most a factor two. Two lambda-axis passes therefore
have component magnitudes < 2^(b+G+2lambda); a literal pair's difference,
mean and temporary rotated fields cost at most a further constant factor.
Signed capacity W=b+G+2lambda+4 suffices for those outer data and literal-pair
microstates, with room for output negation. Each gate returns the magnitude
bound of its entry, so the margin is not accumulated over the gate word.

This is not a bound on every private state inside the fast backend. The
backend's own quotient/residue/history/compiler margins remain separately
paid under PR3109/3131. Those margins are O(lambda) in the stated fixed family;
choose the full working width and p once, before input, as the predecessor
requires. Our finite adapter additionally checks signed capacity at each
visible lift boundary. It does not model the backend's physical interiors.

## 5. Complete local invoice and unchanged asymptotics

The pinned outbound native recipe at event 2031 has 11 CNOTs and seven toggles
on its right, and eight CNOTs on its left. The numerical return inverts these
same wrappers, rather than independently rounding event 2033's recipe.
Thus the actual paired collector has 38 CNOTs and 14 toggles, or 52 field gates.

| Work at the wrapper boundary | PR3131 | This refinement |
|---|---:|---:|
| L-family calls per field gate | 8 | 2 |
| L-family calls over the collector's four wrappers | 416 | 104 |
| Enclosing protected address-oracle invocations | 104 | 0 |
| Guard embeddings and contractions | 104 each | 4 each |
| CNOT character/phase passes | 456 | 114 |
| Native recipe phase passes | 4 | 4 |

The 312 removed calls are wrapper-level invocations of the same L backend.
This does not remove 312 calls from an admitted recursive supplier histogram.
The backend may itself use many primitive operations and protected oracles.
The checked full N=512 fixture keeps all original core calls; RESULT.json
records both complete executor counters and separate wrapper counters.

Let A be the fixed number of compiled field gates, V=Nw the outer bank size,
and T_L,S_L the complete paid time and workspace of one inherited in-place
lifting call at the declared full width. The new wrapper costs

    T_wrapper <= 2 A T_L + O((A+1) N(n+w)),
    S_wrapper <= S_L + O(Nw+n) + F,

under the same sequential field/phase-scan premises as PR3131, writing S_L
for backend working storage before the shared compilation allowance. The latter
includes guard/sign backing, counters and scan scratch; F is retained
compilation storage, not zero. Input/output guards and all low-bit checks can
be implemented as sequential scans. Retaining the executable's per-gate
boundary audits costs O(A Nw) within the displayed tariff. Each L call returns
its private history before the next one starts. No old-bank copy is needed
at this enclosing level because R itself is reversible on the scaled domain.

For the fixed nine-field family A is constant, n=9lambda and w=Theta(lambda).
The wrapper time remains O(N lambda^(2-997/600000)); its history upper bound
remains inherited. The entire collector consequently retains PR3131's

    T = O(N lambda^(2-8003/6000000)),
    S = O(N lambda^(5991997/3000000)) + F.

The two original nonlinear cores, four native wrappers, five gathers, query
ADD, five ungathers, grid policy, metadata, source access and private return
remain in the full bill. The wrappers' endpoints agree exactly, so the original
query, adaptive grid, numerical error and literal private zero agree as well.
This is a constant-factor wrapper refinement, not a new asymptotic exponent,
linear-space result, physical speed measurement or full supplier admission.

## 6. Evidence and limits

The independently written pieces are the parity-formula pair interpreter,
exact Q(i) character-identity checks, symbolic affine-word validator, guarded
wrapper and tensor address-formula oracle. The PR3131 compiler/backend,
collector binding and nonlinear core are explicitly reused and authenticated.
This does not independently reprove those dependencies or the full theorem.

The replay checks 1,250 signed pair cases, exact two-by-two complex matrix
identities, 13,122 exhaustive two-axis gate cases, sixteen actual-wrapper
comparisons, sixteen synthetic tensor cases at multiplicities 1..4, and four
complete collectors including 257-bit dirty-source cancellation. For tensor
multiplicity >=2 the real inherited macro invokes nonempty inner XOR-oracle
cleanup; it is not replaced by an uncharged primitive in that comparison.
Multiplicity four uses the genuinely changed inner order (0,2,1,3). The
bit-boundary test also checks 9,144 signed words and 196 phase-changing
Gaussian outputs, including actual low-bit and sign-extension ancilla return.
Controls distinguish wrong phases from dirty guards and include malformed
words/layouts/types, overflow, inverse faults, signed shifts and source changes.

Finite tests are regressions and source binding. The argument in sections 2–5
establishes the parameterized refinement under its stated backend hypotheses.
The fast physical C trace, finite useful crossover, caller clean-stock hosting,
compiler/precision realization, complete P104 supplier and multiplication
theorem remain open. Python timings measure only the complete semantic model.
