# Post-first static primary review

Verdict: **PASS under the frozen scalar-header instruction interpretation.** I found no material defect in the primary's direct formal transport, Gaussian row rank, phase-sensitive endpoint, controls or complete-packet checks. This is a written code/data review after both first receipts were sealed, not another scientific execution or native semantic admission.

Reviewed `PRIMARY/primary.py` SHA256 `ab66ca8716ec9768b5cf59f8be64ce75e9c2392a555ad5f8cadac2e4540cc331`, its method note, shared CONTRACT/CASES/SOURCE-PINS, instruction-contract prose, primary preseal/run records and both actual first packets. A metadata-only SHA/byte comparison confirms the two 56,434-byte packets are identical, SHA256 `f9203bdcf39e4f14bd85520d564c9412ad1d8b4835e9863935cf7f4ee72742ff`. No source constructor, source checker, primary/oracle engine, compiler or scientific replay was run during this review.

## Exact transport and phase

The primary keeps independent Gaussian-rational A and B matrices in each quotient q squared equal to theta, theta=1,-1. Starting A=I34 and B=0 retains all 34 independent inputs, including fields32 and33. The `dispatch` odd branch uses the old source rows and the correct identity q^e=theta^(floor(e/2))*q for odd e. Thus A_destination receives theta*c*B_source and B_destination receives c*A_source. For the actual e=-1, c=theta, so the even update coefficient is one and the odd update coefficient is theta. This preserves q^-1, including its minus sign in the negative sector.

LOCAL operands are read as stage, source, destination, whereas QUERY uses destination, source, exponent. This distinction is correctly implemented at lines232-244 and agrees with the literal contract. Distinct ports are checked. The original subsequent LOCAL body multipliers specialize to one, as do IDLE/IDLE_ONE; neither operation is silently counted as an additional odd shear.

LAMBDA at lines217-222 is ((1+theta)/2, sign*(1-theta)/2): it is one in the positive sector and sign*i in the negative sector. Even Q_POWER uses parity rather than negative integer powers producing floats. Odd Q_POWER reaches its explicit `odd_free_control` gate. ADD/SCALE/SWAP act on both A and B. Later events update current rows, preserving chronological left action.

The target routine interprets each actual 20-integer monomial vector, retains the central exponent and specializes only the 18 body variables. In particular, the 32 exponent-minus-one targets are B=theta, not universally B=one; the other two targets are in A. `endpoint` compares every cell in both A/B matrices in each sector. The four serialized full 34-by-34 matrices therefore retain 4,624 Gaussian entries. The two comaximal sector quotients jointly distinguish the full q^4 quotient over Q(i); equality in only one sector would not suffice, and the primary does not use that shortcut.

## Rank and observed trace

`row_rank` copies the entire matrix, selects nonzero Gaussian pivots, divides by their exact positive rational norm and eliminates below each pivot. It counts ordinary rank over Q(i), without tolerance or integer-only pivot assumptions. Zero initial B is checked before the first paid instruction. First-query rank is required to remain34, and every recorded paid shear is required to lose at most one even rank.

Both retained actual traces have33 records. Their first pair is34-to34; the remaining32 pairs descend by one from34-to33 through3-to2. Each record retains original event index, one-based ordinal, opcode, source, destination, stage/null and exponent. The healthy inventory independently derives18 LOCAL+15 QUERY,606 events and32 odd+2 even targets from the literal controller, then checks the frozen expected inventory. The returned33 lower bound is explicitly the written r+1 argument applied to the actual32 odd targets. A finite trace alone is not represented as a proof over all possible words.

The primary's row elimination and direct A+qB propagation differ from the oracle's column-space basis and four-character propagation. Their full packet agreement is stronger than matching a count or final rank, while both still share the declared literal contract and source data.

## Controls and receipt gates

The actual deleted-first-query, flipped-first-LAMBDA and wrong-target-phase cases transport modified instructions/target through the healthy dispatcher and full endpoint routine, with rank tracking disabled. The free-odd-power case enters the same instruction path and must fail at its particular alphabet gate. Only the named `GateFailure` with the expected reason is counted; a generic parser or arithmetic exception does not pass a semantic control. The retained packets report three `endpoint_mismatch` outcomes and one `odd_free_control`, in the frozen order. The LAMBDA/phase faults require the negative sector to be checked; positive-sector rank agreement is insufficient.

Before controller parsing, all eight source objects are authenticated by exact size, SHA256 and Git blob identifier; all three metadata files have literal SHA256 gates. Source paths are unique, restricted to the direct inputs directory and cannot traverse upward. Strict JSON rejects duplicate keys, floating tokens and nonfinite tokens. The complete incoming packet has closed object keys, matrix dimensions, reduced positive-denominator Gaussian quartets, integer-not-Boolean proof fields, trace/control order and actual Boolean control outcomes checked. It is then compared byte-for-byte against fresh canonical regeneration of the entire packet. A permissive isolated field cannot bypass that final complete comparison. No correctness check relies on `assert`, so optimization preserves gates.

## Scope, exposure and credit

This review does not independently admit the native LOCAL/operator interpretation, all paid/ordinary prices, physical phases, input/ownership/stock/erasure, compiler or precision tapes, outer recovery, analytic hypotheses or selected all-five assumptions. Body specialization is deliberate, not a full symbolic D-variable endpoint claim. Runtime/RSS values in RUN/comparison records are coordinator measurements, not new measurements by this reviewer.

Historical source-aware exposure is explicit: this reviewer previously read caller.py, algebra.py and scalars.py as inert contract text during B12S1 acquisition. No such original code or earlier engine was read or copied while writing the current oracle. Current peer code/receipts remained unavailable until both firsts were sealed. Accordingly this is separately implemented, code-disjoint application verification under a shared source-aware contract, not blind discovery.

Credit zxv/PR6726 for the literal word, existing33-query proof and author checks; Matarener/PR6114, Cinna Davis and the retained even-rank/pruning lineage for the lower-bound method; PR6120 for the output-boundary repair; and the exact notices for the controller/caller/native/dual-pair predecessors. There is no claim of a new query minimum, physical invoice, human/proof-kernel acceptance or frontier change.
