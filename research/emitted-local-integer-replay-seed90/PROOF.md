# Coverage-preserving port to the emitted local audit

This is a workload-specific port of existing integer-row and fixture-copy ideas, not a new arithmetic representation. Wronskode's PR1137 and Sagar Thakrar's PR1156 apply such ideas to `hpe_audit_and_transport.run`; earlier PR367/824 also use integer rows. The present target is the distinct `hpe_audit_local.py` emitted-program checker and its own complete control driver.

## Exact row invariant

A Row stores a dictionary of integers N and a nonnegative exponent e, representing the same sparse mapping as `j -> N[j]/2^e`. Initialization uses identity rows, and CLEAR creates the empty mapping. COPY duplicates both the dictionary and exponent; subsequent updates cannot alias the source. For a reduced dyadic q=a/2^d, SCALE produces numerator a*N[j] and exponent e+d. It retains explicitly stored zero entries, exactly as the original SCALE dictionary comprehension does; this detail matters to the original truth and equality tests.

For ADD into a row (N,e) from (M,f), let E=max(e,f+d). Replace each existing numerator by N[j]*2^(E-e) and add a*M[j]*2^(E-f-d) on each source key. Remove a key exactly when its resulting numerator is zero, matching the original Fraction loop. Missing keys represent zero. This proves equality of the entire updated row, for every dyadic q including zero and every signed coefficient, without sampling columns. Python integers have arbitrary precision; no overflow or floating arithmetic is introduced. No gcd reduction is required for correctness.

Truth testing retains dictionary nonemptiness, including explicit zero keys. Equality with the original expected Fraction dictionary requires the same key set and cross-multiplied equality of every value. Source code still constructs and validates each coefficient as a Fraction before reaching the row operation, in the same order. Norm and prefix calculations remain the original Fraction expressions. Non-dyadic or invalid input handling in the retained checker is not replaced by a looser arithmetic admission.

## Independent mutation fixtures

The pinned driver originally deep-copies the same immutable forward program separately before each of its 25 mutations. That program came directly from JSON and the honest replay never mutates it. The adapter encodes it once, then decodes a fresh JSON tree for each mutation. On this input, a tree of JSON lists, strings and integers, each result has the same values and independent mutable lists as deepcopy. No candidate mutation is shared with another trial. This is a fixture-allocation optimization; the mutation expressions, trial order and acceptance/rejection checks are unchanged. It is not a generic deepcopy replacement for arbitrary Python object graphs.

## Pinned transformation and unchanged checks

Seven exact, single-occurrence source replacements change row initialization, CLEAR, COPY, SCALE, ADD, and mutation-fixture allocation. An unexpected source hash or rewrite count fails closed. The verifier separately compares the complete AST of all 31 original `assert` statements before and after transformation. Compilation explicitly uses optimize=0 for both engines even under an outer `python -O`, so these guards remain active.

The honest programs retain every event and all original source control flow: phase order; common frames; paid climb ranks and containment; center chains and private state; pre/post helper wrappers; complete data and dirty-helper columns; final endpoint maps; full paid profiles; and coefficient-work prefix bounds. Both full drivers produce the identical receipt and stdout. A separate hook captures all 27 local-call outcomes (two passes and 25 rejections), requiring the same exception type and argument representation on each rejected mutation.

A second independent differential pass observes every changed row after every scalar operation. It compares the exact Fraction representation of that row, its norm, and the running prefix peak across both implementations at all 19693 forward and 19693 backward scalar prefixes. Initially all rows agree; each scalar changes only its target row, and other events do not alter these algebraic rows. Thus matching every changed row establishes the complete intermediate matrix equality by induction, not merely final endpoint agreement. Every input column participates; no probes, modular hashing, or random inputs replace the retained exact check. SHA-256 is used only to retain deterministic trace evidence after exact conversion of all entries.

The saved certificate additionally requires 441 independently computed signed/zero/dyadic arithmetic cases, a non-aliasing COPY test, and seven extra rejection controls: missing source pin, duplicate JSON, nonfinite JSON, floating seed, changed rewrite boundary, a deliberately dropped-ADD engine, and a deliberately uncleared-private-row engine. The last two must fail the complete retained audit.

## Scope and provenance

The exact base is `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`, selected PR1094. Its published result binds the PR1042 baseline receipt, whose archived `slots/local` R480 canonical word and emitted programs are the inputs here. The canonical payload is `4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`. Five mandatory source pins bind the checker, archive, baseline receipt, selected receipt and immutable assembly. Runtime replay does not rely on a moving selected-result pointer.

This preserves the finite mathematical coverage of one local checker. It does not verify the entire cold construction chain, transport control suites, native physical implementation, recursive precision proof, global hosting or outer exponent. No selected source or default command is modified. Performance results are host-specific and stored separately; faster verification is not a multiplication-runtime or kappa improvement.
