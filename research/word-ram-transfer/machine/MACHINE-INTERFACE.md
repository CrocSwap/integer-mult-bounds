# A concrete logarithmic-word interface from the Problem 1.8 compiler

This packet reuses the actual Problem 1.8 word RAM and proves a sufficient bridge from bounded numerical IMP computations to logarithmic-width executions of a fixed finite RAM program. It does not assert that the complete multiplication algorithm has already been rebuilt or that κ improves.

## The actual machine

The implementation is `Lax13.Ram` in `Problem18RAMLax13Ram20261001.lean`, extended conservatively by `RamStd20261007.lean`. Memory and register cells start at zero. A finite program is fixed before the input and word width. Every produced value and every memory address is reduced modulo $2^w$. Each direct or indirect access costs one instruction. Input and output are word streams; reading exhausted input halts, and writing appends one word.

The extension adds wrapping subtraction, high-word multiplication, remainder, OR, XOR, right shift and strict comparison. Its `runsTo_ofLax13` theorem preserves exact successful-step counts, output and halting. Multiplication of an entire unbounded input is not primitive: permitted word multiplication has operands of only $w=\Theta(\log n)$ bits. The elementary TM simulator needs only an explicit smaller instruction whitelist. Existing `basicOps` and `noMulOps` exclude Boolean operations and shifts, so those predicates should not be misused as the desired whitelist.

## An admissible input interface

Existing `RamStd.ComputesIn` quantifies over all lists of natural numbers and requires every input entry to fit at the prescribed width. This is appropriate in the polynomial-width regime. Its `LogWordTime` specialization cannot be used unchanged for arbitrary lists: the single item $2^m$ has encoded size proportional to $m$ and does not fit in $c\log m$ bits for fixed $c$.

The supplied `ComputesInOn D f p W T` restricts the quantifier to an explicit input predicate $D(x)$ while keeping precisely the same RAM. It requires fitting of the input length prefix, all input items and all output items, then correctness at every word width at least $W(\operatorname{bitSize}(x))$. `BinaryWords` is the one-bit-per-item admissibility predicate. Packed inputs can supply a digit-width predicate; their representation must be specified independently of an unbounded input-sized word primitive.

`LogWordTimeOn` uses $c(\lfloor\log_2(n+2)\rfloor+1)$. The appendix includes conservative restriction, input-domain monotonicity and exact base-machine transfer lemmas. It changes neither the machine nor any instruction cost.

## A positive compilation theorem

Fix an IMP command $c$ and a well-formed layout $L$. Put
$$
A=L.\mathrm{temps}+2+|L.\mathrm{scalars}|,\qquad q=|L.\mathrm{arrays}|.
$$
The existing compiler places array $j$ at index $i$ in memory cell $A+j+qi$. This interleaving is independent of input size, array capacity, numerical bound and word width. The address span for indices below $B$ is $A+qB$. The implemented compiler constant is exactly $10$.

**Theorem.** Let `BigStepB B c (initEnv ext x) s k` be an actual bounded IMP execution, with a well-formed command, all input values below $B$, and fixed constants $d,a$ satisfying
$$
1<B\le(n+2)^d,\qquad A+q\le2^a.
$$
Then the particular finite program
$$
(\mathrm{compileProgram}\ L\ c).\mathrm{map}(\mathrm{RamStd.ofLax13})
$$
halts with output exactly $s.\mathrm{out}$ in at most $10k$ successful RAM instructions, at every
$$
w\ge(d+a)(\lfloor\log_2(n+2)\rfloor+1).
$$
The compiler is the already implemented Problem 1.8 compiler; none is postulated.

**Proof.** Set $\ell=\lfloor\log_2(n+2)\rfloor+1\ge1$. We have $n+2<2^\ell$, hence $B\le2^{d\ell}$. Since $B\ge1$,
$$
A+qB\le(A+q)B\le2^a B\le2^{a+d\ell}
\le2^{(a+d)\ell}\le2^w.
$$
Also $B\le2^w$. These are exactly `Layout.FitsWords`, including $1<B$. The source theorem `compileProgram_runsTo` now yields at most `L.const*k = 10*k` steps, and `RamStd.runsTo_ofLax13` transfers the exact run. The supplied Lean appendix formalizes this argument against the actual compiler.

The semantic initial array lengths `ext` describe zero-filled arrays; they are not hidden input or a computation oracle. A later allocator that reuses dirty storage must explicitly establish and pay for its clearing or reuse contract. Every intermediate value and used index must satisfy the numerical bound in the actual bounded execution.

For a length-prefixed logical input, instantiate the theorem's physical $x$ with `logical.length :: logical` and include that prefix in its value bound. Given output equality, an admissible input/output fitting proof and an IMP cost bound $k\le K(n)$ with $n=\operatorname{bitSize}(\mathrm{logical})$, the conclusion gives a logarithmic-word RAM implementation with cost at most $10K(n)$. This is a constructive component contract for packing, permutations, transforms, arithmetic and recursion.

## Evidence and credit

`AUDIT.json` records the actual status, source hash and fresh transitive axiom output for the new appendix; a timed-out or failed audit is not a checked theorem. `SOURCE-MAP.json` pins sixteen selected sources. Historical artifact presence is not a fresh source/kernel certificate.

The existing Problem 1.8 work supplies the concrete RAM, bounded IMP semantics, physical layout, compiler and semantic simulation. This packet does not claim to invent standard RAM simulation or the logarithmic-word model. Historical RAM-TM sources also contain a computability-equivalence proof; their concept file exposes an axiomatized interface. Neither their axiom nor their separate historical proof environment is imported here, and their statements do not provide the needed near-linear fine-grained time comparison.

Retrieval used the registered source catalog, canonical tree and exact typed DAG queries. The catalog returned 153 Problem18RAM modules and nine base Lax13 modules. It omitted the newer RamStd and RAMRoot source identities despite on-disk artifacts. Exact typed lookups for the selected interfaces returned no records. These are explicit coverage limits, not evidence that the relevant source lacks a proof.

A faster RAM execution is a separate model result from a better multitape-TM exponent. A justified return simulation is required before claiming any improved TM κ.

The later `Problem18RAMRootLog20261007` already supplies an explicit-domain trans-dichotomous route, with word width twice the maximum input-item bit width plus O(log n). Its `MpSparse20261007` dependency replaces huge arrays by linear-scan logs and composes limb arithmetic from `MpGlue20261007` and `MpLimbs20261007`. It preserves polynomial time, but does not assert the sharp 10 k overhead of the direct polynomial-numerical-bound theorem above. Large 2^poly-valued intermediates require that separate multiprecision lowering before applying a short-word contract.
