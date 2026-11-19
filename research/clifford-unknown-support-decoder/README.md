# Recover every unknown Clifford term from an exact tensor train

Give the decoder the tensor-train cores of an observation. It returns the complete list of projective Clifford matrices and their exact complex coefficients, or rejects membership in the stated class. It accepts arbitrary signed cancellation and arbitrary internal bond bases. It needs no list of candidate circuits or symplectic fibres.

For four qubits the dictionary has 12,128,668,876,800 labels. The decoder handles arbitrary support at width 27 and above. At width 25 it handles any 58,040,063 labels, and more if at most 226,718 symplectic fibres are complete. At width 23 it handles any 447,742 labels. At width 13 it handles any 19. A sufficiently small observed bond also makes a negative answer exclude the entire Clifford span. At width 25 a twelve-site cut of rank below 58,040,063 suffices. Work and storage are polynomial in the stated train parameters and the exact input bits. Output size still grows with the number of reported terms. [Recovery and costs](PROOF.md) · [Width and cut certificates](SUPPORT.md)

The published predecessor decoders solve threshold, inversion, noise-norm and named-row problems. This package constructs a different input/output interface and certifies the entire observation. The selected multiplication bound remains κ=0.00363005817. No multiplication supplier, physical tape program or discharge of a frontier assumption follows. [Candidate comparison](SYNTHESIS.md) · [100-result inventory](INVENTORY.md) · [Sources and credit](CREDITS.md)

## Run the decoder

Use CPython 3.12 and its standard library. From the repository root run

```sh
python3.12 -B research/clifford-unknown-support-decoder/example.py /tmp/clifford-parity.json
python3.12 -B research/clifford-unknown-support-decoder/decode.py /tmp/clifford-parity.json
```

The example produces an exact 13-site observation from two parity registers with 16 and 4 states. At each site the six input-bit products on the edges of a four-vertex graph select its transitions. The end accepts one syndrome of each register and multiplies the second by i. No list of Clifford labels is stored. The all-zero observation entry vanishes. Its 6,144 sparse records in three cores represent 2^104 dense entries. The decoder returns 19 distinct symplectic fibres, with the complete signature and coefficient of each term. The two parity indicators have Fourier expansions on 16 and 4 controlled-Z masks with the identity mask in common. Their common coefficient is 1/16+i/4. Each of the other coefficients is ±1/16 or ±i/4. The registered check constructs all expected columns separately from gates. [Parity producer](example.py) · [End-to-end check](verify.py)

## Input and output

The UTF-8 JSON object uses `format="clifford-tt/1"`, a positive integer `qubits`, a `cores` array and a nonempty `sites` array. A site selects a zero-based core index. A core has positive integer fields `left`, `right` and an `entries` array. An entry is `[q,i,j,real,imag]` for row i and column j of its q-th matrix. Indices start at zero. Duplicate entries are invalid. Omitted entries are zero. Real and imaginary parts are integers or strings containing a signed decimal integer or integer fraction with a positive denominator. Fractional values use explicit digits. At qubit count n, q=2^n·x+y selects input x and output y. Adjacent dimensions must match and both ends must have dimension one.

For example this exact one-site identity has one output coefficient 1+i in the one-qubit phase convention.

```json
{"format":"clifford-tt/1","qubits":1,"cores":[{"left":1,"right":1,"entries":[[0,0,0,1,0],[3,0,0,1,0]]}],"sites":[0]}
```

A member has `status="member"` and an array `terms`. In the signature string the symbols `.`, `+`, `i`, `-` and `j` mean zero, one, i, minus one and minus i in physical-index order. Read the string as W. Its first nonzero entry is one. Each column has 2^h nonzero entries. For four qubits the output convention is A=vec(W)/(4(1+i)^h). Each `coefficient` is a pair of reduced rational strings for its real and imaginary parts in the expansion by A^(tensor f). The general phase convention is in the proof. The empty list represents zero.

The optional `--max-terms B` tests a specified smaller support class. The output gives its cardinality and complete-fibre limits, with `null` for an absent limit. An unsupported cardinality request at a bounded width exits with status 2. A valid input outside the tested class returns `status="outside_model"` with exit status zero. If `full_span_decision` is true, rejection excludes every full-span representation. A `cut_certificate` gives the cut position, its bound and the strict independence threshold when the observed train establishes that stronger decision. A member always has a full-tensor equality check. Nonzero tolerance and approximate support selection require a different interface.

## Verification

```sh
python3.12 -B scripts/research_package.py --package research/clifford-unknown-support-decoder
```

Expected final line

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/clifford-unknown-support-decoder outcome=completed
```

The eight registered commands exercise the public decoder, a separate dense two-component oracle, the Pauli-neighbour census, and the two character projections in normal and optimized Python. The dense oracle makes 280 decisions on 140 complete tensors. Its support and coefficient calculations use integer minors. The [flank verifier](flank_certificates.py) independently obtains the strict row-sum cutoffs and checks a complete one-qubit kernel. [Registered commands](VERIFY.json) · [Dense oracle](verify_dense.py) · [Pauli census](nearest_check.py) · [Exact pins](SOURCE-PINS.json)

For the optional primary-source comparison, supply the authenticated CTblLib 1.3.11 release. The reader compares all 81 projected rows and 324 ordinary character values with the retained tables. [Release archive](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbllib-1.3.11.tar.gz)

```sh
python3.12 -B research/clifford-unknown-support-decoder/archive_check.py /path/to/ctbllib-1.3.11.tar.gz
```

## Open next questions

- Which actual multiplication caller can supply a train with a sufficiently small bond? Price construction of its entries, Gaussian-rational division, movement, output delivery and restoration on the same layout.
- Can a noisy observation support certified identification at useful separation and cost? The exact rank predicates can change under perturbation. The proved posterior coefficient bound assumes a proposed reconstruction and a residual.
- Can a different decoding procedure cover all supports at width 13 from compact inputs with an output-sensitive cost? Sharp full-dictionary independence alone supplies no support-enumeration method.
