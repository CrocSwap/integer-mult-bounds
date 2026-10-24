# Machine-derived allocation routes

Source-only inspection, not new Lean certification. Exact source declarations consulted:

- Mathproof/Meta/Problem18RecursiveWorkspaceChain20261002.lean: program, cost, run, code_uniform. The run theorem keeps one physical reservation and preserves array lengths through an arbitrarily long sequence of verified calls.
- Mathproof/Meta/Problem18P34Subfield20261003NRecursiveWorkspaceRestore.lean: run. The entire reserved concrete memory image is restored, not merely a candidate-local prefix; restoration itself has an explicit cost.
- Mathproof/Meta/Problem18ConcreteSelectedChildContinuation20261002.lean: program, cost, run. Composes a concrete selected continuation with a disjoint-reservation precondition and additive counted cost.
- Mathproof/Meta/Problem18P351PolynomialWorkspaceFrameClose20261003.lean: gcd_ws_safe, quotient_ws_safe. Workspace-base ABI registers are excluded from scalarWrites.

## Sufficient adaptation

Treat each complete arbitrary-dirt cover invocation as a continuation that preserves the caller's reserved arrays outside its exact endpoint. A finite schedule is sufficient only when each pending child receives its full intended factor exactly once, every borrowed physical family is restored before its next data/bridge touch, distinct simultaneously interpreted local registers have distinct full owners, and all remaining children are explicitly charged. Composition then follows from equality of endpoints and per-replica event projection; neither shared workspace nor a different dispatch order introduces a free mathematical operation. This is an applicability theorem, not by itself a kappa improvement.

## Bounded new screens

1. Paid register spills for shorter K=3 controllers: rejected before expensive search. Current provider demands 7*4900=34300 helper-rank units per replica, while initial plus final pending children supply only26880. Shortage7420 already exceeds total positive rank deficit216. Any implementation must pay missing residual transformations and restore its full reserve. No private-reserve or LIVE increase is silently assumed.
2. Finite steady-state amortization at T=16: exact integer allocations for offsets6 and12 both reproduce twice the T=8 histogram and the same nominal b=0.0013744413363825925, with zero solver gap. No improvement claimed.
3. K=5,T=8,offset6: bounded feasible candidate b=0.0013680017192500558, worse than current. Solver reached time limit with tiny nonzero gap; this is not a universal no-gain theorem.

These screens use actual coordinated-rank2 local paid profile and widths (18 rank7,104 rank8,438 rank9), complete paid remainders, and finite fixed T. They do not merely score local savings. Literal owner matching and full scalar invoice would still be required for a positive nominee; no negative nominee was promoted.

## Public507 composition and literal owner witness

The new PR507 partial-own factory combines constructively with our previous coordinated rank-two gauge collapse. Kernel lane reconstructed its exact local word. The changed local profile is {1:2493,2:208,3:516,4:88,5:298,6:68,7:1,8:17}; widths are 18 rank7,146 rank8,396 rank9. Our complete offset6 allocation has nominal b=0.0013910579397602985 with every remainder paid. Its literal owner witness passes all40320 role assignments,72 calls,560 distinct helpers per call. Files RANK2-PARTIAL-O6.json and RANK2-PARTIAL-OWNERS.json.gz bind the construction. This is a positive composed supplier nomination; it still needs fresh emitted full orthogonal maps, scalar prefix and outer assembly. Its gain does not establish that three entirely new machine concepts improved the exponent.

## Repeated-axis modulo-four gate

The proposed sufficient algebraic extension tracks multiplicity of each pending coordinate modulo4: C squared equals translation X, so an even repeated factor can be compensated explicitly without another recursive Fourier call. Overlapping factors must still obey actual owner lifetime, full-family injection and scalar routing. For a rank-r pending bin hosting roles with total width s, a best-case leftover has size r-s if s<=r, otherwise parity(r-s). The latter is an optimistic capacity relaxation: every loss of odd coverage reduces the actual rank deficit and cannot be hidden as a free bank.

Native integer screens allowing aggregate width excess0,1,2,4 and16 per pending bin all selected the same disjoint pattern optimum, nominal b=0.001391135951042288, zero reported integer-solver gap. No overlap selected; therefore no positive candidate promoted from this bounded route. This is not a proof that every possible modulo-four physical compiler is unhelpful. It is a cheap full-profile gate with all repeated-rank loss charged.

## New kernel-92 candidate

Kernel lane supplied exact source-based variants after broadening availability at concrete instruction boundaries. Full controller pricing ranks them as follows: kernel-partial-base with 92 pivots, b approximately 0.0013934624979634045; latefirst-partial-base with 89 pivots, b approximately 0.0013927996101125715; snapshot-even, b approximately 0.0013926403309490465; snapshot-both, b approximately 0.0013914512506201793. All are floating nominations, not outer assembled kappa values.

The selected 92-pivot local profile is {1:2539,2:160,3:530,4:88,5:298,6:68,7:1,8:17}, with 18 width-7,154 width-8 and388 width-9 helpers. Selected plan KERNEL92-FOCUS-O6.json has SHA256 7a30db32ad8fc54bd5e7060febf4f8ff7747b8287c057ae926efc736e2b9f800. KERNEL92-OWNERS.json.gz has SHA256 9c6bd9793db16d599d3c7f9493350d2359681d19eb170ec7239e8d568090e745. Literal matching passes all40320 helper roles,72 invocations and560 distinct helper families per invocation. The emitted full physical maps and prefix invoice remain parent/independent-auditor responsibilities.

The complete selected paid histogram is {1:182808,2:11520,3:41233,4:6336,5:25173,6:4896,7:195,8:1224,16:1,32:1,39:1,48:766}. Live stock7680, ambient73, rank deficit2496, maximum child48.

An optimistic static stock allocation gives b approximately 0.0013943119744464494, but its fixed optimal patterns were infeasible under tested offset4,6,8,12 schedules with eight replicas and offset6 with sixteen replicas. That stronger number is not a delivered candidate. The limited failure is retained as a concrete search result, not a universal scheduling barrier.
