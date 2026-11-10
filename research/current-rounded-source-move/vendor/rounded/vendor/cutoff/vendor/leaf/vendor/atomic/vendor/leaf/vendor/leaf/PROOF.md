# Fused Gaussian coefficients on encoded sequential tapes

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I implement the coefficient boundary after PR3087. I retain PR2287's Gaussian
operator/grid convention, James Chang's PR1869 finite ripple-addition lineage,
AAAmirinu's PR2327 staged-arithmetic audit, and Alejandro Zarzuelo Urdiales's
Gaussian parity and tensor-grid results. I distinguish this implementation from
Nick Petalas's PR2772/3089 prefix and capacity arguments. I supply a written
structured-program refinement under the named source contracts.

## 1. Signed coefficient contract

Supply canonical encoded width h>=2 and distinct complete h-bit component
tapes at their origins. Interpret each component as a two's-complement integer
on one common fixed grid. I preserve the input component tapes and append the
result to a separate owned output. At the enclosing engine boundary I return
the output at its origin and erase the owned scratch contents and markers.

For two Gaussian inputs a=ar+i*ai and b=br+i*bi, the credited C operation is

    p=a+b, q=i(a-b), outputs ((p+q)/2,(p-q)/2).

Writing X=(ar,ai,br,bi), the four output numerators have rows

    (+1,-1,+1,+1), (+1,+1,-1,+1),
    (+1,+1,+1,-1), (-1,+1,+1,+1).

The inverse uses rows 3,4,1,2. Each row has three positive terms and one
negative term. I implement these rows without storing p, q or a complete
unhalved numerator as an h-bit signed coefficient.

For aligned ADD/subtraction I implement x+y and x-y on each real/imaginary
component. I preserve both borrowed packets, including the original target.
The caller supplies their common address order and scale. Equal byte lengths
cannot establish semantic alignment.

For a nested caller, I suspend its allocation scope and supply physical
`borrowed_tape`/`borrowed_count` views. After return I restore the caller scope,
copy the protected output into a caller lease, then clear the callee output
and marker. I test this exchange with live parent Counts and payload leases
across a leaf call followed by subtraction.

## 2. Finite carry and exact acceptance

Let L=2^(h-1). For a C numerator N, signed inputs in [-L,L-1] imply

    -4L+1 <= N <= 4L-3.

Thus h+2 signed bits suffice for N. At bit k I read the fixed tuple of input
bits and use

    s_k = c_k + sum_i epsilon_i*x_(i,k),
    d_k = s_k mod 2, c_(k+1) = floor(s_k/2), c_0=0.

I use floor division for negative values. Since the signed bit sum belongs
to [-1,3], the four carry states {-1,0,1,2} form a closed set. Induction gives

    sum_i epsilon_i*low_k(X_i)
        = sum_(j<k) d_j*2^j + 2^k*c_k.

After the h input bits I supply each input's sign bit for two further steps.
The emitted h+2 digits therefore represent N modulo 2^(h+2). The displayed
signed bound identifies its exact two's-complement value.

I require d_0=0, discard it, and emit d_1 through d_h. I then require
`d_(h+1)=d_h`. The first test is equivalent to exact integer division by two.
The second is equivalent to representability of N/2 in h signed bits: the
discarded high bit must agree with the retained sign bit. Together they give
necessary and sufficient acceptance for this component operation. They do
not merely certify a modular residue.

All four C numerator parities equal `ar+ai+br+bi mod 2`, the credited Gaussian
parity condition. I retain a check at each executed component. A caller may
use the tensor-grid theorem below to establish those conditions in advance;
an arbitrary changed pairing still requires its own argument.

For two-input ADD, the carry belongs to {0,1}; for subtraction it belongs
to {-1,0}. The untruncated signed sum/difference fits h+1 bits. I retain the
first h digits and compare one extra sign digit with their last digit.
This gives the same necessary/sufficient final-width test, without separately
negating the source in subtraction.

These acceptance domains extend the old staged h-bit arithmetic. For h=3,
`a=b=3+3i` remains unchanged under C, while the staged p=a+b has components
six and cannot fit. Likewise `(-4)-(-4)=0` fits although separate negation of
the second input does not. I change the implementation, not the mathematics
or the correctness of PR2327's stronger premises for its actual program.

## 3. Complete axis and leaf execution

Fix an ell-field vocabulary and one selected field. Supply encoded field
widths, f>=1, K>=1, `0<=rho<K`, coefficient count r>=1 and outer-row count
C>=1. The selected field has width fK. Other complete fields may be dirty and
may have width zero. Put

    R=2hr, a=sum(field widths), V=C*2^a*R.

Within each record concatenate r Gaussian fields, each as h real bits then
h imaginary bits, least significant bit first. Supply the complete borrowed
payload and descriptors at their local origins.

For an encoded address position j counted from the left, `c_axis` derives
`before=2^j`, `after=2^(a-j-1)`, and `suffix=after*R`. For each outer row and
prefix it copies the two suffix blocks into separate streams. Their order
aligns precisely the records whose selected bit differs, with identical
trailing addresses and coefficient fields. I traverse `after*r` Gaussian
pairs, use four reusable component buffers, and write two output suffixes.
I merge them in their original left/right order before the next prefix.

Induction on the pair, prefix and row counters gives the C axis on the whole
packet. I preserve the spectator coordinates and coefficient-field order.
I check exhaustion, erase the suffix buffers and consume the owned input only
after success. I allocate no physical stream per prefix, record or field.

`run_leaf` clones the borrowed payload once, then applies the f distinct axes
at low-bit positions rho+jK. I keep the axis counter and positions on Count
tapes. For inverse execution I traverse those axes in reverse order and use
the inverse component rows. At successful return I copy the current packet
to the protected output and erase the owned intermediate.

The successful domain requires exact division and signed fit at each axis
output. If a forward leaf succeeds, its reverse-axis inverse revisits the
preceding accepted states and succeeds without re-encoding. The C inverse
identity establishes this conclusion; a byte roundtrip is only finite evidence.
I do not infer arbitrary intermediate headroom from a final endpoint alone.

## 4. Realize the credited tensor-grid bound

Alejandro Zarzuelo Urdiales's Gaussian-parity paper and tensor synthesis already
give the sharp binary reserve. Put pi=1+i. Since

    C = pi^-1 * [[i,1],[1,i]],

each entry of a k-axis tensor, or its inverse, is a Gaussian unit times
pi^-k. At even k=2s, one real or imaginary part is nonzero with magnitude
2^-s. At odd k=2s+1, both parts have magnitude 2^-(s+1). The common binary
denominator is exactly 2^ceil(k/2); an impulse proves uniform sharpness.

The same prior synthesis gives the real-component row l1 norm
`2^ceil(k/2)`. Nick Petalas applies the prefix statement in PR2772 and PR3089.
For arbitrary Gaussian-integer input encoded with `ceil(f/2)` reserved bits,
each completed prefix k<=f remains integral on the chosen grid. Its next C
numerator therefore has even low bit. If initial encoded components have
magnitude at most M and

    2^ceil(f/2)*M <= 2^(h-1)-1,

the same row norm supplies sufficient signed headroom for every prefix.

I realize these credited conditions through the fused transducer. I never
interpret its partial digit stream or finite carry as a stored h-bit numerator.
The old root-grid and staged-intermediate bounds remain sufficient. For the
new direct leaf I can also admit inputs under the weaker exact guards above.
Arbitrary interleaved scalars or recursive implementations need their own
prefix analysis. Normalized Hadamard conversion retains its separate f-bit
denominator requirement; I do not transfer the C reserve through normalization.

## 5. Complete time and space

In one C pair I copy four h-bit inputs and perform four width-h finite-carry
traversals, each followed by two literal extension steps. Rewinds and clearing
cost O(h). Each Counter initialization costs O(log h), which the following
complete traversal pays. Thus a Gaussian pair costs O(h).

For one axis I move each payload bit a bounded number of times through split,
arithmetic and merge. Counter resets fit the ensuing complete suffix scans.
Encoded setup costs `O_ell((a+log(R+1))^2)` once; this fits O_ell(2^aR).
The outer counter adds O(C+log(C+1)). Including source rewind, erasure and
output handling, I obtain O_ell(V) per axis without a long-record hypothesis.

Initial payload cloning, final protected-output copying and leaf parameter
setup cost O_ell(V). Encoded position changes fit the axis charges. I obtain
O_ell(fV) for f>=1 in either direction. A rejected invocation costs at most
that upper bound. This is the direct leaf tariff. I retain PR2287's stopping
predicate `e<73 or e^1000<root_d`; this implementation cannot replace its
faster recursive child at arbitrary width.

For N aligned Gaussian fields, write `V_add=2hN` for each operand's size.
I perform 2N component operations and obtain O(V_add), including both source
rewinds, encoded counters, clearing and return. I do not charge an unproved
alignment operation as zero: alignment is an explicit input premise here.

I allocate `8*ell+192` physical scratch roles and one protected output before
numerical input. A conservative live-role census is ell+64: ell+3 Layout
Counts; at most eight engine setup/iteration Counts and its current packet;
nine axis streams/component buffers, three extents, up to three loop counters
and bounded nested arithmetic temporaries. The ADD branch uses fewer roles.
The constructor seal stays active throughout execution.

Including borrowed payload, a conservative occupied-content bound is

    6V + O_ell(log(V+1))

for a leaf, and `4V_add+O_ell(log(V_add+1))` for ADD with both borrowed operands.
The declared layout bounds descriptor lengths by these logarithmic terms.
I count frozen source compilation separately as a fixed constant.

For a fresh engine each role reaches `O(V+log(V+1))` backing cells, or the
corresponding ADD bound. Multiply by the fixed capacity and include external
input/output storage. A reused tape retains the maximum extent that its role
reached in prior calls: clearing blanks the simulator's cells without shrinking
its bytearray. Successive axes reuse roles, so f does not multiply that maximum.
I treat the simulator's meters and Python object bookkeeping as instrumentation,
not numerical registers available to the tape program.

## 6. Named rejection and evidence

On `CoefficientDomainError`, `linear_word` closes its counter and rewinds its
component inputs. The pair helper clears four reusable component bodies. The
axis clears its partial output, suffix streams and component leases, and closes
its extents and counters. The enclosing leaf clears the current owned packet,
closes Layout/setup state and checks an empty pool. ADD rewinds both borrowed
inputs and closes its buffers/counters. The common finish path erases markers,
clears any partial protected output and closes the engine before rethrowing.

I preserve borrowed payloads and descriptors during this named rejection on
otherwise admitted input. Cleanup costs O(V) or O(V_add). The low-level axis
consumes owned intermediates; it does not promise a borrowed-source interface.
I make no rollback claim for arbitrary malformed inputs or interruptions.

I compare component arithmetic against separate integer C formulas, covering
37,640 C-row cases and 1,124 signed sums/differences. I test complete spaced
leaves, several coefficient fields, arbitrary positive outer-row examples,
inverse order and reuse on a smaller boundary input. I execute the credited
sharp-reserve impulse at one through eight axes and reject one fewer reserved
bit. I compare those outputs with independent products of 1+i and 1-i.

I also test later-field parity/overflow rejection and retry across both engine
methods. Eight injected faults cover source binding, truncation of negative
carry, suppressed guards, inverse direction, skipped coefficient fields and
unconsumed protected output. I disable decoded Count helpers during execution.
Finite results complement the quantified argument; they do not prove the full
selected caller, its native/hosting identities or its analytic transfer.
