# Finite-tape bridge for the six-stage last-tick profile

## Decision and scope

For the newly chosen constants, the operations **that this note lowers**—fixed-rank integer generation, powered-label and epoch indexing, sequential image navigation, and the positive stopping comparator—do not require an additional mathematical oracle or an extra unbounded-word instruction. A serial fixed-alphabet multitape machine can carry them out with the charges below. This statement is conditional on the same all-column native action, typed owner/erasure and restoration, compiler transfer, precision/tape accounting, and analytic recovery premises identified in [#8035](https://github.com/CrocSwap/integer-mult-bounds/pull/8035). It does **not** prove those premises, the entire physical multiplier, or uniform transfer of an arbitrary compiler. A concrete finite-parameter recheck is not a proof for arbitrary future powers or ranks.

The literal Python program is **not** an all-size implementation on this host. With its actual rank, `ordinary_carrier.stage_body` evaluates `1 << H` and `prepare_native` also evaluates `1 << log_rank`. Here `1 << 10**21` raises `OverflowError: too many digits in integer`. Near the host limit another oversized shift raised `MemoryError`; the exact exception need not be uniform. `len(range(sys.maxsize+1))` raises `OverflowError`, and a `TemporaryFile.seek` beyond `sys.maxsize` raised `ValueError` on this host. The Python finite controls exercise the same algorithms at feasible scales; they do not execute production.

There are further obstructions even if the first shift is replaced. The inherited `SourceRule.targets` and `.paid` are eager Python tuples. The source has 444 target labels of rank 15, so at least 444^430 distinct retained target paths exist. This is greater than 2^3440 and vastly exceeds `sys.maxsize`; it cannot be a Python tuple. The abstract tape implementation must enumerate the occurrences and pay for the corresponding data. It must also replace growing Python lists, dictionaries, frames and offsets with serially searched, delimited tapes. A fixed alphabet means finitely many symbols and a fixed number of physical tape heads, not finitely many occupied cells.

## Construct the actual fixed integers

Write H in ordinary binary as a constant in the finite program. The largest H here is `1024000000000000000000000`, whose encoding has 80 bits. Use a separate counter tape holding H least-significant-bit first and an output tape. Write `1`, then repeatedly test/decrement the counter and append `0`. This emits the binary integer N=2^H as exactly H+1 digits. A zero test and decrement each scan at most the counter and return to its marked beginning. If k is the length of the input encoding, the concrete routine in `check_bridge.py` uses at most

    20 (H+1) (k+2)

read, write and single-cell head-move steps and H+O(k) cells. To see the bound for every H, a zero test scans at most k digits and returns, and a decrement flips at most k digits and returns. Including the output write, one iteration costs at most `9k+16` elementary tape actions; the final failed test and initialization cost at most `4k+7`. Their sum is bounded by the display. At the largest H the upper bound is `1679360000000000000000001640` steps, a 91-bit integer, and is <2^H=N. This is a mathematical finite tape, not a statement about attainable hardware. The 129-case toy replay writes the true binary strings for H=0,...,128 and counts every read, write and movement.

An H+1 digit encoding of N is not a stock of N axes. Where the reference constructs `tuple(range(N))`, a tape implementation must actually enumerate N indices. An H+1 digit odometer, appending each fixed-width index, takes O(N(H+1)^2) transitions and O(N(H+1)) cells on sequential tapes; these are below N^3 and N^2 respectively for the present large H. It cannot charge such an N-item construction as O(H). Actual whole-field payload movement is separate from this control cost. Use delimited records and explicit tags for signs, lengths, IDs and owners; an integer is data, never a fixed-width machine register or one unit-cost word.

## v=430 installer and actual forest depth

Let A=134^430, let the minimum retained target rank be 15^430, and cap paid blocks at 12^430. The exact source contains rank-15 target labels and rank-56 paid labels. Consequently the first minimum and the maximum paid block are actually attained: the loop's ratio is `(5/4)^430`. Let G be its least integer with `(5/4)^(430G) > 2^H/(4A)`. Because A<2^(8*430) and `(5/4)^430<2^430`,

    G > floor((H-2-8*430)/430).

At the largest H this lower bound is `2381395348837209302317`, over 258 times this host's `sys.maxsize`. The old `G < 2^50` assertion is therefore false, not merely unsupported by a coarse new upper bound. Real path stacks, odometers and suspended frames must reside on tape; growing Python sequence lengths and recursion cannot implement this instance.

For the upper bound, `(5/4)^13 > 2^4` yields

    G+1 <= ceil(13H/(4*430)) + 2.

At largest H the right side is `7739534883720930232561`, with 73 binary digits. The exact powered source census gives

    18906^430 + 104904^430 + 23800^430 < 2^(18*430).

For H>=512*430, enumeration of every candidate, including rejects and split paid occurrences, gives `(W+P#)^G < N^[18(13/4+1/512)] < N^60`. The physical source's raw record bound `2^64*(v+1)*2^(28v)<N` also holds. The existing #8030 installed-band accounting bounds the remaining structural search and generation by N^380 transitions and its finite numeric expansion by N^960; the fixed program, scratch, generation and erasure are budgeted by J=N^1024. The H+1-digit constructor above is <N and fits the spare powers. This transfer of the old clock is conditional on the predecessor's written record enumeration and physical compiler accounting; the arithmetic guards do not establish those general claims independently. The exact candidate profiles use six J_i plus the fixed numerical J_M.

Using the candidate's updated control computation, the raw structural-node logarithm is 12973. Even after allowing `G+1` in the live source slots, their log is at most `19+2*12973+73 = 26038`, below the local allowance 53044 and the chosen q=65536. The earlier proof's numerical example using 50 bits for G is not valid at these heights. The independently computed program envelope reports `log2(max J)=1024*Hmax=1048576000000000000000000000`; summing the six binary programs and the numerical program is bounded by another three bits. The 2^513 setup in [#8042's installation proof](https://github.com/aliromman/integer-mult-bounds/blob/3d33cb0c8a523b66d91e8de8250b85d0a436eb35/research/retimed-native-multiplier/INSTALLATION.md) belongs to its separate unpowered calendar construction and does not price this powered epoch.

## Epoch cursor, variable data and quotient guards

Serialize records with lengths and nonnegative base-128 integers, as the reference does. A sequential implementation may store a suspended parent cursor as binary data. To resume, rewind the image, copy its saved offset into a counter, and advance one cell for every decremented step, explicitly charging the counter tests, writes and returns. For an image of L<=J cells, an elementary conservative bound for this operation is O(L log(L+1)) <= O(J^2), not a unit-cost seek. Descriptor lookup and updates use a second tape to scan and rewrite the delimited table; copying or scrubbing each record and returning the head is charged. `len` becomes a stored count maintained during construction, or a paid scan; no `Py_ssize_t` conversion is assumed. The reference's one-image-per-rank reuse is a finite-program bound, while each suspended invocation retains its own cursor and private payload owner. The predecessor's O(J^11)(1+C_previous) ordinary and O(J^12) outer fixed-work budgets are the stated place to charge these scans; arbitrary input payload transfers, zero fields, ownership and restoration retain their own bills. This paragraph is a lowering of these operations, not a proof that every operation of the physical caller is included in the inherited budget.

The old helper `quotient_entry_log` assumes eta=97/25000. This profile has eta=39/10000, so the correct sufficient width logarithm is

    Q(H) = ceil((2H+64)/(1-39/10000))
         = ceil(10000*(2H+64)/9961).

For every selected H, `(1-eta)Q >= 2H+64` and `Q<3H<8H`. At Hmax, Q is `2056018472040959742997756`. The hardcoded predecessor helper is smaller by `41280537927979756315`. The old helper is used by the predecessor's receipt, not by this profile's `ordinary_carrier.stage_body`; the candidate's last-tick checker computes Q separately using the actual eta. This prevents mistaking a bad proof threshold for a demonstrated runtime dispatch bug.

## Stopping parameter and explicit comparator charge

For the positive caller, g=1/D and D=10^21 are constants of this particular finite machine. Their common rational encodings, signed gate coefficients and denominator are stored as finite binary data. At this D, `kappa*D=3890115286594445000` and `ordinary*D=3890115286594445005`. The 54 strict margins, four functional margins and the positive paid margin in the pinned gate all have denominators dividing D^2, which has 140 bits. Their exact scaled numerators use at most 181 bits; the least margin is 1/(10D). The replay checks those properties.

The fixed gate can be evaluated by keeping a common D^2 denominator. Form products of the few base D-denominator parameters first, then use signed additions and exact fixed-denominator divisions; the other products are by fixed small rationals. No expression multiplies two separately formed D^2-denominator quantities. Even the 2^45-7^16 constant, after scaling by D^2, has fewer than 186 bits. This gives a concrete fixed straight-line evaluation with fewer than 10000 integer operations on at most 256-bit working values. Applying the inherited 2^20(b+1)^3 schoolbook bound, with rewinds and initialization, costs less than 2^60 tape transitions and fewer than 2^23 retained work cells. This charges **the fixed gate calculation**, not the input-dependent signed multiplication or its recovery.

In an active `Positive._run`, the original root has selected width h and the current width e satisfies 0<=e<=h. It stops when e<=M or e^D<=h. If the latter test runs, repeated squaring uses D's 70 bits and 29 one-bits: at most 69 squarings and 29 selected multiplications, 98 products total. The algorithm rejects as soon as its running value exceeds h; it caps each squared base at h+1. Before an early rejection every operand is <=h+1 and every actual, not-yet-capped product is <=(h+1)^2. It does not materialize e^D.

Let L=ceil(log2(h+2)). The predecessor's sequential schoolbook arithmetic estimate is 2^20(b+1)^3 transitions for b-bit operands and its elementary comparisons. Charging that conservatively to every one of the 98 products, their 2L+2-bit temporaries, comparisons, counter handling and cleanup gives at most `2^32*(L+2)^3` transitions and O(L+70) work cells for **one test**. With epsilon=10^-23 and x=h+2, calculus and ln 2>1/2 imply

    2^32 (L+2)^3 <= 2^277 x^epsilon.

Indeed `(1+log2 x)^3 / x^epsilon <= (1+6/epsilon)^3 < 2^240`, and `L+2 <= 3(1+log2 x)`. The checked strict gate minimum for this profile is 10^-22, so this exponent is one-tenth of that minimum. This shows a concrete possible allocation for the new per-test logarithms; it does not automatically pay other growing work or permit the same slack to be spent twice. The number of tests, positive recurrence, remaining finite list of logarithmic charges, tape movement and signed recovery still depend on the inherited estimates. [#8035's proof](https://github.com/Clear1nsight/integer-mult-bounds/blob/ea776471bf8ed143a0625cf2d7532f65d15eb5f9/research/p104-single-band-signed-margin/PROOF.md) states its stopping proof for every fixed integer D>=2; replacing D=10^17 by 10^21 increases the fixed bit-loop factor and changes the actual stopping condition, and the signed inequalities must be rechecked, as the last-tick receipt does.

## Replay and limits

From this package, `python3.12 -I -B verify.py price` reconstructs the pinned source privately and passes its path to `check_bridge.py` and `check_dispatch.py`. To call either helper directly, supply an already reconstructed source directory as its sole argument. The bridge test checks exact production-height integer inequalities without forming any 2^H, compares small stopping boundaries against both direct integer powering and the source comparator, exercises D=10^21 on finite inputs, constructs and counts 129 concrete rank tapes, and invokes the physical nested-epoch test. `BRIDGE.json` is the sealed receipt. The nested test used rank 323, 128 lanes, 1456 records and an 8481-byte image; one parent resumed at saved offset 654, with 271392 total bytes read and 271392 units of seek distance. These controls do not run the production epoch.

The separately produced `check_last_product.py` receipt uses `physical_product(LAST_TICK)` and passed with product -345550037539, 138 shuttles and 157248 H calls. It passes the requested profile to `Product`, but that product has `machine.total=32`: every H dispatch therefore uses the `total<=4096` local `RetainedProduct.h` branch. It does not execute the candidate's positive supplier or stopping parameter. Its finite staged receiver has rank 2. It is evidence about that small signed instance, not production-size execution.

`check_dispatch.py` additionally verifies the real `Product.h` forwards `(rank_log, denominator)=(1600000, 10^21)` to its supplier factory, with the factory and outer H body replaced by spies. It exercises the real `band_positive.Positive._run` stop branch at e=3, carrier 2: D=3 stops at h=27 and continues at h=26; D=10^21 continues at finite h=2^4096. It replaces `one_axis` with a recorder and stops before reaching the supplier. This improves branch-binding evidence but does not execute the production positive word or produce an astronomical stopped case. Retain the full five inherited premises and open all-size/compiler mapping when reporting the conditional numerical result.
