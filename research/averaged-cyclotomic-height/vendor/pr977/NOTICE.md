# Attribution and scope

New effective-depth argument, cubic-stride integration and checks by Chafik
Boukhalfa (@chafreaky), with substantial OpenAI Codex assistance, under the
repository's Apache-2.0 license. No independent human/delegated-agent review
or literature-priority claim is made.

- Rohan Guliani (@Rohansguliani), PR846, head
  `4bdb3e755ea7118170a7a34764df955880dec282`: arbitrary-stride Euclidean
  chain/closure solver, fixed-tape FIFO accounting, uniform error argument
  and kernel integration. Its solver, checker, proof, source record and
  notice are retained unchanged. `early.py` is an explicitly attributed
  adaptation of its `solve` function, adding a charged exact-zero base case.
- Charles Bethin (@cbethin), PR764, head
  `983d66f0f2e48ee500ec7eee2da9244c001c5064`: shared-suffix scan identity and
  inverse-square error analysis, used through the retained PR846 proof.
- Chafik Boukhalfa, PR628, head
  `0768f97d06c623b8211e651543c66135796b62bf`: root-factor certificates,
  preparation/phase budgets and exact arithmetic. The five files retained
  by PR846 remain byte-identical and independently hash-bound here.
- Chafik Boukhalfa, PR862, head
  `57e0659150d323b784580110b36aa64a2dca2a33`: common-operator complement
  bound and cubic preparation/execution precision. Its proof and notice
  are retained unchanged.
- Ali Romman (@aliromman), PR621, head
  `520774462b19b29af41554b74def31f9d01e997e`: prime-power kernel and its
  uniform inverse bound, retained through the cited preparation lineage.

Original notices retain the OpenAI exact-DFT manuscript, classical
Mahler/Wiener arguments, Pan factorization, fast elementary arithmetic,
and the standard queue-from-two-stacks attribution. Their credits and
licenses remain unchanged. Nearest-grid extinction and pointwise-zero
substitution are elementary; no priority claim is made for those ideas.

The new result removes the stride solver's length-dependent precision
admission and combines its unchanged local error with PR862's cubic bound.
It does not replace the inherited preparation theorem with the finite root
fixtures or claim that the Python reference implements its asymptotic cost.
Clean scratch, phase access and all remaining transform/physical obligations
stay explicit. No new multiplication exponent is claimed.
