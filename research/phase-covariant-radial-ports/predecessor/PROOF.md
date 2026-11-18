# A conserved, reversible nearest Gaussian grid map

## Object and prior work

The ideal pair map is

    C_sigma(x,y) = ((s+sigma*i*d)/2, (s-sigma*i*d)/2),
    s=x+y, d=x-y, sigma in {-1,1}.

Inputs are Gaussian integers times a retained grid spacing h=2^-g. The
mathematical proof first sets h=1. The arrays contain stored grid values;
it does not recover information lost by initial quantization of real inputs.

JoyboyBrian's PR5485 gives a fixed-grid nearest-even implementation, direct
cost and source-ordered error budgets for the actual PR4743 C0/C2 ports.
Tekalign's `p104-reversible-lifting` already gives a nearest-error bijection
and exact paired cleanup. Its pair preserves a rounded midpoint and rotates
the difference. It does not preserve the exact sum. Neither generic integer
lifting nor reversibility alone is new here. `native-rounded-loop-defect`
already distinguishes inverse replay from consistency around a native graph.
The new contract adds exact sums and Gaussian phase covariance, classifies
the optimal centers below, and binds them to both complete port schedules.

## Construction and exact inverse

For a Gaussian integer s, choose c(s) as follows:

- If the real and imaginary parts of s have equal parity, set c=0.
- If the real part is odd and the imaginary part is even, set
  c=sign(Re s).
- Otherwise set c=i*sign(Im s).

The sign in each nonzero case is defined: an odd integer is nonzero.
Set

    d' = sigma*i*(d-c(s)) + c(s),
    x' = (s+d')/2, y' = (s-d')/2.

The sum remains exactly s. Write c=u+iv. A Gaussian integer center gives
integer outputs exactly when

    u+v = Re s+Im s (mod 2).

To prove this, use d=s modulo2 and compare the two components of
sigma*i*d+(1-sigma*i)c with s modulo2. Both component conditions reduce to
the displayed parity equation. The selected c meets it. The executable
checks that both final numerators are even before the two exact shifts.

The inverse uses the same sum, the same c(s), and -sigma. It maps
sigma*i*(d-c)+c back to d. Thus the pair is a bijection of the full Gaussian
integer grid, with no stored error bit or history. This is state-map
reversibility, not a reversible tape circuit for the scratch arithmetic.
Four repeated positive
pair maps give identity. The same statements hold for a layer of disjoint
pairs. They do not assert that four complete calls on several axes give
identity: different rounded layers need not commute.

## Pointwise minimum error and center classification

Subtract the ideal pair result. The two output errors are

    e = (1-sigma*i)c/2, and -e.

Their combined squared Euclidean norm is |c|^2. In the affine-on-difference
family above, legal centers have the stated parity. If Re s+Im s is even,
the unique minimum-norm center is zero. If it is odd, the four minimum-norm
centers are 1,-1,i,-i. This classifies every least-error center at every sum;
it is not a search-box conclusion.

The chosen map has an even stronger pointwise accuracy property. When the
sum parity is even, the ideal outputs are already Gaussian integers and the
map is exact. When it is odd, all four ideal real components are half-integers.
Every grid output then has squared pair error at least4*(1/2)^2=1. Our map
attains1. Thus it is a nearest Euclidean grid point for every input, among
all grid-valued maps, with or without an inverse. Each complex coordinate
error is at most h/sqrt(2), and pair Euclidean error is at most h. These
bounds are sharp at a mixed-parity input. They are not global precision
lower bounds for a different representation or a complete supplier.

## Exact symmetries and observable channels

The center rule satisfies c(i*s)=i*c(s) and c(conj(s))=conj(c(s)). Direct
substitution gives global Gaussian-unit phase covariance and conjugacy of
the positive and negative pair maps. Equal inputs are fixed. Zero is fixed.
These properties hold for every magnitude, provided finite words do not
overflow. They also hold through exact monomial maps and integer additions,
so both complete port programs commute with a global Gaussian unit phase.

For Cj tensor f on N=8^f coordinates, the active bits are3k+j, with j=0 or2.
Each update preserves its pair sum. Fixing all other2f bits defines4^f disjoint
spectator fibers, each of size2^f. Every such fiber sum is preserved exactly
by the complete call. The ideal call has the same property. Its actual error
therefore lies in the kernel of4^f independent complex sum functionals, a
subspace of dimension N-4^f. No claim is made that every vector in that
subspace is attainable as an error.

If an exact grid monomial R precedes the call and L follows it, the wrapped
result satisfies

    ell * L^-1 * rounded_U(x) = ell * R(x)

for each of these sum rows ell. Thus the exact observables can be moved
through the actual paid monomial wrappers. Their setup and execution costs
remain payable. This is an explicit completed-call error restriction that
independent coordinate balls do not express.

## Limits of the invariant

No map in the displayed family can also commute with pair exchange at every
input. Exchange sends d to -d at fixed s. Commutation would require
(1-sigma*i)c=-(1-sigma*i)c, hence c=0. Mixed-parity sums forbid that center.
Likewise, no center rule in this family can have both common-grid-translation
covariance and global Gaussian phase covariance. The first would give
c(s+2z)=c(s). The second gives c(-s)=-c(s). Taking z=-s forces c=0.
These are restrictions of the stated affine family, not universal exclusions
of every nonlinear or history-carrying program.

The actual implementation is nonadditive. Its map on inputs(1,0),(0,0) is
identity, while on(2,0),(0,0) it gives(1+i,1-i). It also fails pair exchange
and common translation covariance, as the verifier records.

Two rounded axes need not commute. On four complex entries with only the
last equal to1, axis0 then axis1 gives

    (-i, 1+i, 1, -1),

while axis1 then axis0 gives

    (-i, 1, 1+i, -1).

Both exact linear orders are equal. This is a concrete limitation, not an
assumed one. The inverse of a multi-axis call must reverse its literal stage
order. Independently lowering an ideal inverse or using native graph
identities is not justified. Native graph flatness and full additivity
remain open obligations.

## Complete-call accuracy and finite words

Every pair has the same per-coordinate error bound as the retained PR5485
service. For the exact first k factors on the actual stored input, let delta_k
be the maximum complex-coordinate error. The exact factor has infinity norm
sqrt(2), so

    delta_0=0,
    delta_(k+1) <= sqrt(2)*delta_k + h/sqrt(2),
    delta_f <= (2^(f/2)-1)/(2-sqrt(2))*h < 2*2^(f/2)*h.

No independent-error assumption is used. Reverse stage order has the same
bound. The Euclidean field bound is f*sqrt(N/2)*h by unitary propagation.
For completed-call tolerance2^-q, the retained grid choice

    g=q+ceil(f/2)+1

still suffices. The pair computation uses sums and differences of grid
integers, two center tags in{-1,0,1}, and two exact final halves. If input
components are bounded by M grid units, its largest raw data numerator is
at most4M+1. This includes the added parity correction. Range checks occur
before each stored arithmetic result; there is no modular wrap or saturation.

The source port budgets set

| Port direction | q |
| --- | --- |
| two-call forward | P+f+3 |
| three-call forward | P+ceil(3f/2)+3 |
| two-call reverse | P+ceil(f/2)+2 |
| three-call reverse | P+f+2 |

They are reused with attribution. The new kernel satisfies their actual-input
error premise, so the full coordinate error remains at most2^-P. For original
coordinate magnitude at most2^H, H>=0, retain

    w=H+g+2f+ceil(f/2)+9

signed component bits. To check the additional numerator unit, the source
port entry bound is U=2^(H+2f+4). A native prefix has component magnitude below
3*2^ceil(f/2)*U. In grid units the new numerator is below
192*2^(H+g+2f+ceil(f/2))+1, which is less than the positive w-bit limit
256*2^(H+g+2f+ceil(f/2)). Thus the old width margin covers the new rule.
Initial quantization, if used, keeps its original separate error charge.

## Complete dirty-port inverse

`ports.py` is an explicit copy of the retained port body with a backend
argument, exact source monomial/mix dependencies, and a distinct-bank guard.
A static AST check allows only those interface edits. No source function or
class is patched. The exact monomials preserve the grid and have literal
inverses. Each triangular mix leaves its source bank unchanged and is undone
by the opposite addition. Each new Gaussian call is undone by its reversed
stage program. The complete reverse port is precisely these operations in
reverse order. Induction gives exact return of both arbitrary stored dirty
banks, in either composition order. Native error bounds and exact return
are separate statements; neither is inferred from basis vectors alone.

## Complete direct cost and workspace

A call executes fN/2 pair operations, including zero pairs. A port with k=2
or3 calls executes B=kfN/2 pairs. Each pair has10 full-word additions or
subtractions, two exact arithmetic half shifts, two small center-tag additions,
a bounded number of sign/parity/branch operations,16 signed-word checks,
four real reads and four real writes. The trace records the data arithmetic,
range checks and every pair; center selection and control are additional
bounded work, not free oracles.

Eight signed data words suffice: load four inputs in slots0..3, form the two
sums and two differences in4..7, overwrite0..1 with the corrected numerators
and then their halves, and overwrite2..3 with sum-minus-output. Store0..3
and clear all eight owned scratch words. The center and signs need a fixed
number of control bits. Initialization and clearing cost O(w) bit writes
per pair and are included in the direct bound. Python locals and oracle
snapshots are semantic instrumentation, not a physical register allocator.

Both ports also perform the retained two monomial mixing terms:4N real
additions and2N left shifts, plus sign/check work. A two-call port executes
four full monomial wrapper passes; a three-call port executes six. Every
pass builds its N address/phase records in O(fN) word work, traverses the
permutation cycles, and clears its owned route/visited records. Its O(Nf)
control bits and held values are payable. The arrays are updated in place;
no dirty array or error transcript is cleared.

The complete indexed reference thus has O(fN) bounded-word work and
O(fN*(w+f)) bit work, including ordinary arithmetic, control, indexing,
source reads, writes, allocation and cleanup. Storage is O(N*(w+f)) bits,
including both dirty banks and owned route data. This is not an accelerated
recursive Gaussian tariff or a fixed multitape schedule. Physical routing,
recursive funding, compiler stock and outer admission remain unproved;
unknown costs are not charged zero.

## Evidence and expansion decision

The verifier uses a direct Gaussian-rational tensor convolution and a separate
three-bit monomial oracle. It checks all source port directions, actual
inputs at every paid cut, integer round trips, phase covariance, every fiber
sum, exact predecessor ports on aligned inputs, source/format/overflow controls
and the explicit nonlinear failures above. Finite domains corroborate the
all-size proofs; they do not prove them by extrapolation.

The changed invariant and explicit complete direct bill justify this bounded
interface construction. Further construction requires a caller that can use
the conserved observables and fund the full native/physical implementation.
No kappa, universal native admissibility, scientific acceptance or selected
frontier change follows from this package.
