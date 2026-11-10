# Cross-review of the DDG code audit and coordinator hand bound

Reviewed after both main drafts were sealed: `DDG-CODE-DRAFT.md` (provided SHA256 `8c651f694de81d8884dc41c7008798f8665605f17ef518652e02f380381b7e96`) and `COORDINATOR-SMALL-BOUND.md` (`0a6dfdeb0a6ccad6c803cc4f072817e74f7c8c383017c1752e14e1bb012154ac`), against my frozen `DDG-DERIVATION-DRAFT.md` (`c4690b2f575a97e287e791e71e4b9426001a82ead4252a28f07485ecaad83efa`). No original or sealed file was edited. This was written/static review only: no program, import, compilation, source verifier, numerical experiment or census was executed.

**Verdict: PASS within the stated fixed-pair, fresh-fair-bit and trusted-table domain. No mathematical contradiction or actionable defect found. The coordinator's small-pair bound is correct as a nonsharp hand deduction and does not verify the source's large exact fraction.**

## Controller association and stopping

The peer agrees with the phase convention: phase k stores remainders at depth k and supplies digits at depth k+1. Its subtraction/index proof accounts for every child and surviving index rather than asserting only matching aggregate counts. The actual hard-coded output base312 is justified by the uniform phase inventory, not by assuming that a reported finite census passed.

The peer's independent modular hand calculation is consistent: 2^26=-22 modulo169, 2^39=(-22)*80=99 modulo169, 99^2=58*169-1, and 2^52=(-22)^2=-23 modulo169. Together with 2^12=40, the proper-prime-divisor tests establish order156. This is a different short written check from the prime-square lifting argument in my draft, with the same result. Pairing opposite phases gives the same 312 inventory.

The wrap155→0 correctly retains a live branch. At that point the unfinished index set has the single root index, and the consumed history is still156 bits long. Re-entering the same control state is not termination, a fresh uncharged seed or cancellation of previous cost. The peer expressly makes this distinction.

The `census` interpretation is also correct: earlier completed leaves double when represented at a deeper common cylinder resolution. Their unused suffixes are counted for probability, not charged as consumed sampler bits. `run` stops when it reaches an output and reports only actually consumed bits. A finite tape returning None is unresolved execution, not a fifth output.

The 312 figure is the number of states in this chosen phase/node construction, not a lower bound on all equivalent finite-state realizations. The peer does not claim minimum control-state size and separately disclaims optimal storage/table-access cost. Publication should retain the explicit “not a minimized-controller bound” sentence from my draft, so the expected-bit optimum cannot be mistaken for a state-size optimum. The 702 bytes are a logical packed-target payload, not Python resident memory or complete physical control cost.

## Probability and optimality quantifiers

Both notes fix a,b before any entropy is read, start at the deterministic root, and require fresh iid unbiased bits with no free initial random reservoir. The all-depth prefix law proves the exact four masses and almost-sure stopping. It does not infer them merely from finite eight-bit tape counts.

For every competing exact fair-bit tree under that same initial-state contract, completed output-i mass at depth k is an integer multiple of2^-k bounded above by its eventual target mass. This gives the same lower survival bound at every depth and therefore the expected-bit bound even when a competitor has infinite mean. The constructed sampler saturates all these bounds. No restriction to periodic or bounded-memory competitors is silently inserted.

The peer's low-level API qualification is explicit and appropriate: source `run` does not authenticate arbitrary table/bit packets, whereas the original source caller passes a valid `make` table and actual0/1 tuple values. Negative Python indices, bool aliases or other malformed values are not inside the proved randomness contract. This is a qualification of the helper interface, not a gap in the product-law theorem. Neither note claims independence from the consumed tape or permission to choose b adaptively.

## Coordinator's `(1,1)` bound

For weights `(144,12,12,1)`, the six displayed floor vectors are correct by hand integer comparison. In particular 1152 lies between6*169 and7*169; 2304 lies between13*169 and14*169 while192 has floor quotient1; and4608 lies between27*169 and28*169 while384 has floor quotient2. The resulting counts are exactly

    (n0,n1,n2,n3,n4,n5)=(1,1,1,2,1,1).

Their weighted contribution is

    1 + 1/2 + 1/4 + 2/8 + 1/16 + 1/32 = 67/32.

The all-depth bound nk<=3 gives the remaining contribution from k=6 onward at most

    3*(2^-6)/(1-1/2)=3/32.

Thus E[T]<=70/32=35/16, while9/4=36/16. The final strict `<9/4` conclusion follows without relying on equality of the tail bound. There is no omitted n0 term, double-counted fifth term or off-by-one in the start of the remainder. This is a valid finite handwritten prefix plus rigorous all-depth geometric tail argument, not a recomputation of the exact displayed expectation and not a runtime observation. The coordinator note accurately discloses source exposure and its use of the already supplied general tail argument.

## Credit and retained limits

All conclusions above audit the existing zxv6072 sampler, counts and expected-bit claims, using classical DDG and depthwise tail optimality. The original exact fraction and source execution/census claims retain their source status. No new sampler, catalogue, physical inverse, entropy-recycling protocol or numerical join is claimed. Actual table selection/access, tape movement, ownership, stopping-record retention, reversible cleanup, current/native/physical/error/caller admission and the selected frontier remain separate. The distinct6096/6546 numerical work is not characterized as missing.
