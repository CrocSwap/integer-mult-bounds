# A fixed-anchor externalization compiler

Prepared for Dugongue with substantial OpenAI Codex assistance. This is a positive exact compiler for the native complex-scalar model. It preserves a completed supplier's strict moment sign and all independent inputs. It establishes no new supplier or multiplication exponent.

## Statement

Let V=C^8 and f>=2, and select one of the f base-8 digits as the anchor. A bank is V tensor V^(tensor(f-1)). Consider a fixed finite chronological program on such banks with:

- arbitrary fixed anchor matrices with coefficients in Q(i);
- individually tensorized admitted free monomials on the other f-1 digits, including fixed anchor-controlled choices of such maps;
- fixed scalar bank mixing, copies and erasures with explicit owner preconditions;
- paid calls C_j,f=C_j raised to tensor f, for j=0,1,2.

Every free operation is required to have an actual finite expression in these operations. This hypothesis does not allow an arbitrary unexplained O(N)-time oracle.

**Theorem.** Split every bank by its anchor value. A program with r arbitrary independent input banks and c paid calls compiles to a program on eight times as many banks, each of length 8^(f-1), with exactly 8c paid calls C_j,f-1. The coordinate encoding and decoding are bijective; all eight component banks of every arbitrary input can vary independently. Each additional free operation uses O(N d(w)) ordinary word operations per original bank, where N=8^f and d(w) is the explicitly charged worst cost of its fixed-coefficient scalar update on the chosen w-bit entry representation, including fixed-denominator arithmetic and rounding. For the actual dyadic C_j/K anchor maps and the anchored Pauli maps, d(w)=O(1) using a fixed number of ordinary ADD/SUB, sign/exchange and dyadic-shift operations, so the overhead is O(N). All owners, dirty inputs, exact phases and productive endpoints are transported literally.

For a completed homogeneous supplier with r independent K_f outputs, K_f=C_2,f C_1,f C_0,f, the compiled program gives 8r independent K_f-1 outputs after a fixed free anchor correction. If the original construction is correct for every f>=2, this is correct for every remaining width g=f-1>=1.

## Exact compiler and proof

For x, define its eight component banks x_s(t)=x(s,t), with s in {0,...,7}. This is a literal partition of coordinates. It neither creates a copy nor assumes any component is zero. Concatenation is its inverse, so independence and every stated equality or owner invariant are preserved.

An anchor matrix B acts by the fixed eight-bank scalar update x'_s=sum_t B[s,t] x_t. A remaining-digit free letter acts separately on each bank. An anchor-controlled choice is likewise one prescribed admitted map on each component. Products, sums and chronological scalar updates therefore compile by substitution, with every intermediate bank retained as in the actual program.

A paid call factors exactly as

    C_j,f = C_j on the anchor tensor C_j,f-1 on the remaining digits.

Apply C_j,f-1 independently to each of the eight component banks, costing eight paid calls. Then apply the fixed anchor C_j matrix by scalar mixing. The factors act on disjoint tensor coordinates and commute, proving the identity on every vector. C_j has entries ((1+i)/2) and ((1-i)/2) on its two-entry blocks, with the actual absolute phases. No projective phase identification is used.

For a target, K_f=K_anchor tensor K_f-1. Thus its eight outputs are the fixed anchor K matrix applied to the eight desired K_f-1 outputs. Apply the free inverse K_anchor to those banks to return the canonical independent smaller outputs. Each original arbitrary bank had eight independent components; the compiled outputs retain precisely those eight inputs, without counting a dependent response as a new job. Apply the same coordinate partition to every borrowed or owned field. Zero fields split into eight zero fields; arbitrary dirty fields are transported with their full preconditions, and unrelated memory is unchanged.

Induction over the literal instruction list proves the complete endpoint statement. For f=1, the whole bank has eight entries and all C_j,1 and K_1 operations are fixed eight-by-eight rational-complex maps; compute that constant-dimensional base case directly. It is not passed to a nonexistent width-zero recursive supplier.

## Native invoice and numerical scope

The eight component descriptors can refer directly to the original storage. A layout conversion, when needed, is a charged O(N) permutation, not a hidden data copy. A fixed anchor matrix is applied by loading eight complex entries at a remaining-digit index before storing any output; constant temporary words suffice. A fixed finite coefficient list takes O(N d(w)) ordinary word operations under the scalar cost contract in the theorem. This is O(N) unconditionally for the displayed dyadic C_j/K and Pauli maps on a fixed number of ordinary machine words per entry. The particular C_j and K anchor matrices use only dyadic Gaussian-rational coefficients of fixed height, so they use ADD/SUB, sign and real/imaginary exchange, and fixed dyadic shifts. General allowed Q(i) anchor coefficients require their explicitly charged fixed-denominator arithmetic. No n-bit integer multiplication is an instruction.

The remaining-digit monomials have the same O(N) native implementation as in the original program. Free anchor-controlled choices are a constant number of such passes. O(f) mask/descriptor setup is included in O(N). The total storage is the same data volume, with eight descriptors per original bank and constant-entry temporary storage for anchor mixing. Any separately used address workspace remains explicitly owned and charged.

Anchor C_j and K matrices are unitary, and the coordinate partition preserves Euclidean norm. Thus splitting does not introduce a width-dependent norm loss. Their actual rounded fixed-size implementations add constant local rounding and guard costs, which must be added to the complete compiler's existing error recurrence. An inherited precision theorem is not replaced by treating these new scalar updates as exact machine instructions. If the original word already has a valid O(log n)-bit entry representation and stable fixed-coefficient recurrence, these extra fixed-size updates have the same kind of constant coefficient/rounding invoice. A complete claimed multiplication bound still needs that numerical contract bound to the actual compiled word.

## What moment is preserved

For the three-axis homogeneous supplier, the normalized strict moment is

    r * 3^(1-q) - c.

The externalized profile is exactly

    8r * 3^(1-q) - 8c = 8 * (r * 3^(1-q) - c).

The relative productive rank is 3(f-1) and paid rank is f-1. The fixed anchor rank has been computed by charged linear native work. Therefore any strict paid-moment exponent proved by the original complete supplier survives this compiler. Transfer of the full native complexity bound additionally requires its scalar overhead to be funded: the displayed dyadic compiler has O(N) overhead, while a general nonconstant d(w) must be charged separately. This is a sufficient transfer theorem for an exhibited word, not evidence that the current unfinished controller has a positive moment.

There is an exact equivalence of coordinate input/output ABIs. The priced-program claim is a forward compilation, not a converse compression theorem: eight unrelated smaller calls cannot automatically be replaced by one larger call. Reverse compression is valid only for literal synchronized groups executing the same C_j on all eight components, with the required anchor mixing restored. The compiler also uses Q(i) scalar mixing. It does not automatically admit a construction to the narrower rational-mixing Lean engine in PR #4628.

This applies the anchored Pauli construction from REVIEW.md to a fully explicit carrier boundary: the anchor can be made external, its operators and costs exposed, and its independent inputs tracked. It does not create free productive jobs or a new kappa. Credit the complex C_j conventions and small-unit model to Jacob Alan Sussman's PR #4628, the repaired prefix to Yiyang's PR #4710 and lee-phys's PR #4688, and the native bounded-array/Word RAM framing to the retained provider/compiler lineage. No worldwide novelty or new Lean verification is claimed.

## Exact finite replay

From the package root:

    python3 -I -O -B algebra/anchor_check.py --check algebra/ANCHOR-EXPECTED.json

The self-contained standard-library check compares every width-two complex-linear basis vector for every paid direction, then checks canonical K targets after inverse anchor correction. It also checks arbitrary complex vectors at width three, the eight independent input components, zero owner slices and preservation of untouched dirty memory. These finite checks corroborate the tensor-factor proof; they do not infer all-width correctness from sampling. No optional hook engine, floating arithmetic, network, Lean or solver is used.
