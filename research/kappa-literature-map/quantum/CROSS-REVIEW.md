# Independent cross-review: exact encodings, adjoints and native implementation

This is a separate Codex-worker review, not human peer review or a Lean kernel audit. The reviewed constructions establish scoped algebraic interfaces; they do not exhibit a new multiplication supplier or κ. Both `algebra/test.py --check algebra/EXPECTED.json` and `root/test.py` passed in isolated optimized mode during review.

## Hecke coupling: accepted as a whole-input sufficient construction

Let g and h be the literal generating transpositions of S3, represented by exact unitary permutation operators. Set e=(I+h)/2, T=e g e and M=(I-e)+T. The identities e^2=e and T^2=(e+T)/2 imply

    M^-1 = I - 2e + 2T,
    M^2 = (M+I)/2.

Both inverse multiplication orders hold in the actual group algebra, not just after restricting to the image of e. Since e and g are self-adjoint, T and M are self-adjoint. The polynomial puts M's spectrum in {1,-1/2}; hence its Euclidean norm is at most 1 and its inverse norm at most 2. Dropping I-e would discard an independent complementary input sector and is not a full-input inverse.

At every positive width, apply the representation to the fixed group-algebra identity. In particular e_f=(I+h_f)/2; it is not the tensor power of the base projector e. The scalar halves stay outside tensor powers. Literal permutation realizations satisfy the group relations including absolute phase. A projective representation would require a separate phase/cocycle audit before the same coefficient identity could be applied.

There is an explicit in-place native implementation. The diagonal S3 action on all address digits partitions the V addresses into orbits of size at most 6. Enumerate addresses, compute their six group images, and process an orbit only at its least address. Load all distinct old orbit entries before any store, evaluate the fixed linear combinations for every orbit coordinate, and then write them. Duplicate images from stabilizers have their coefficients added. This uses constant many complex-entry temporaries, not a hidden output field.

Three periodic bit-lane masks implement each fixed permutation of the three bit positions simultaneously over f digits using constant many shifts/masks. The masks can be initialized in O(f) shifts, avoiding division and any need to store 2^(3f). With 3f-bit addresses fitting the specified bounded number of native words, every group image costs O(1) word operations. The whole forward or inverse therefore costs O(V) native work. Dyadic coefficient heights are fixed per application; repeated exact applications must accumulate their actual grid-height and magnitude guards.

This orbit argument is a general sufficient implementation rule for a fixed finite monomial group whose address/phase action costs O(1): a fixed group-algebra operator preserves its constant-size address orbits and can be evaluated orbit by orbit. It does not make a growing group or an expensive address map constant cost, and it does not admit unpriced non-dyadic scalar division.

## Anchored Pauli coupling: accepted with an explicit grammar boundary

For self-adjoint involutions A and B with AB=-BA, the three-bank map is

    r = y + A z,
    s = -x + B z,
    t = -A x - B y.

Its explicit inverse is

    z = (AB t + B s + A r)/2,
    x = B z - s,
    y = r - A z.

Substitution proves the inverse for every input. The designated-bit realization uses A=Z and B=X on one fixed address bit, with every other bit a spectator. For each pair of addresses differing in that bit, load the six old bank entries before storing outputs. All computations then stay inside that pair, requiring constant temporary words and O(V) work. Arrays must be physically disjoint, their entries must occupy the specified bounded number of words, and the inverse's extra dyadic bit must be retained.

The sharp useful bounds also follow algebraically. For the full block matrix M, M*=-M, and N=M^2+2I obeys N^2=2I-N. Thus (M^2+I)(M^2+4I)=0; Euclidean singular values lie in {1,2}, giving norm(M)<=2 and norm(M^-1)<=1. A separate exact six-dimensional rational check confirmed that polynomial during review. Expanding the displayed inverse into three monomial terms per output also gives inverse infinity norm at most 3/2.

The identical-tensor realization is different: A=Z raised to tensor width f and B=X raised to tensor width f commute when f is even. Its rank then drops to two banks' worth. The anchored construction fixes that specific all-width defect by changing the native address grammar. It must not be promoted to an admitted identical-tensor-letter supplier or to extra independent Gaussian output credit without an actual caller and physical word.

## Root adjoint and transparent translation: accepted with the Hermitian convention

For U=[[A,0],[ALA,A]] with unitary A, the checked Hermitian adjoint and inverse-adjoint are

    U* = [[A*, A*L*A*],[0,A*]],
    (U^-1)* = [[A,-L*],[0,A]].

The root test's complex inner products include conjugation, and its actual phase-bearing P and Q monomials are correct. This is a Hermitian-adjoint statement, not an unqualified bilinear transpose. The reverse uses paid Gaussian inverses, which the current letters implement with one forward call and a literal free translation. A forward call is not automatically its own adjoint; the explicit rejecting controls are appropriate.

Conjugating a translation of the first output by U gives the exact all-baseline map

    U^-1 ((U(x,y)) + (delta,0))
      = (x + A^-1 delta, y - L delta).

The original implementation uses two forward and two reverse paid calls. Delta is an actual length-V array or an explicitly generated stream, whose storage/generation and addition passes must be counted. The formula does not turn the transformed delta array into a free precomputed object.

## Finite-character selector and pricing: accepted only in its stated model

The root test chooses a primitive cubic character over F13, where 3 is invertible. Character averaging selects each of four input channels after applying a linear map to every encoded query. The union contains nine queries, so assigning three paid calls to each costs 27, exceeding the direct 12-call comparison. This is a valid positive decoding example and an honest model/invoice rejection; it is not a complex Gaussian supplier. A complex implementation would separately need admitted phase constants, their approximation/grid costs and the actual transform schedule.

A fixed scalar outside the total algorithm's running-time bound does not change its logarithmic power exponent. In contrast, multiplying the paid child multiplicities at every recursive level changes the moment equation. The two statements must not be conflated. The algebra funding receipt explicitly marks its hypothetical five-in-fourteen supplier as unexhibited; its conditional numerical arithmetic is not a newly achieved κ.

## Precision contract that must accompany recursive use

A recurrence E_(L+1)<=C E_L+rho yields a geometric error factor, but its error norm must be stated. If rho is a global Euclidean perturbation at each layer, the tested fixed geometric bound applies in that norm. If rho instead bounds each of D coordinate errors, a Euclidean argument first contributes a factor sqrt(D), requiring an additional O(log D) precision allowance. For codes with a dimension-independent infinity norm, a coordinatewise recurrence can instead be justified directly.

Before claiming bounded-word execution, relate the maximum layer depth L and dimension D to the external word/precision parameter. A sufficient guard O(L+log D), together with explicitly bounded input/output magnitude and denominator height, is compatible with a fixed number of C log n-bit words when those quantities are O(log n). Fixed-degree Laurent dependence inside one macro does not prove a fixed recursive degree: its degree may add at each level, and its bit cost must be included. None of the exact small tests alone proves these whole-recursion hypotheses.
