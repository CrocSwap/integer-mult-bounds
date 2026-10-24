# Independent physical raw-dual derivation for PR4935

Exact upstream head: `64c9f99693c92fb370096fb43dbc58a085b30e36`.
The review uses only this source, #4929 head `361f5d4100640177d6a983dd2f336021c75bfd5e`, and an independently written interpreter. A candidate emitter is not imported.

Let R be the actual eight-by-112 observation matrix, K=R^T/4, and P equal K on selected rows 0,7,20,23,86,93,108,111 and zero elsewhere. Direct exact checks give RK=14I and RP=I. Thus A=I−KR and F=A+12PR agree with the frozen 4935 forward coefficient matrix, and F²=I. The source-mutating unit-transfer variant is excluded.

The #4929 physical raw-dual main endpoint is Xi=bar(F9)(xi−Σj Aji yj), and Yj=bar(Vj)yj. Every helper is autonomous. For each selected j:

1. Clear only the already owned C0, assigning its chart to the zero state at bar(Vj).
2. COPY the pure physical Yj into C0. Yj remains unchanged.
3. Apply Lj=bar(F9)bar(Vj)^*, a single rank-one Gaussian transport with its actual monomial factors and phase.
4. Scatter −12(PR)ji C0 into Xi at the common bar(F9) chart.
5. CLEAR C0. No arbitrary owner is erased or overwritten.

The endpoint is Xi=bar(F9)(xi−Σj Fji yj), Y unchanged, with every original helper output unchanged. This route is derived directly from pure physical Y; it is not obtained by treating COPY/CLEAR as an automatically transposable instruction.

All eight selected Y frames are rank8: 142,149,162,165,228,235,250,253. The exact Clifford lowering has rank1 for every lift. A separately written sparse Gaussian-integer gate interpreter checks all512 basis columns per lift, including the global phase of bar(Vj) followed by the compiled lift, against bar(F9):4,096 equalities. Wrong unconjugated lifts and reversed-adjoint lifts fail.

There are424 scatters, each selected source having53. Coefficients are8×−12,268×−6 and148×+6. The initial external summary208/208 was incorrect; this independent audit flagged the difference, and A independently caught and corrected its expectation before freezing any receipt. The coefficient word itself was generated from −12PR. The simple fixed-scalar primitive allowance is2,976 for these scatters; signs do not change that tariff. Add8COPY and16CLEAR, eight Gaussian child protocols and all literal monomial/routing/precision costs. A final bill of {1:2209,2:412,3:510,4:127,5:40} is consistent with the eight added H1 children, but the full emitted program still requires chronological replay.

This derivation establishes new lift phases and exact coefficient/ownership feasibility. The inherited #4929 full native event semantics and full source632 physical phase audit are separate premises. Normal and optimized derivation checks pass. No caller, decoder, finite compiler reserve, outer admission or κ improvement is claimed. Full frozen-candidate review follows separately.

Prepared for Chris R/Clear1nsight with substantial OpenAI Codex assistance. Credit Dugongue #4935/#4929, Rohan Arun #1931, Ali Romman #1862, Cinna Davis/1337isnot1337 #4694/#4698 and Cao Yifan/intqwq #4610/native round-three source; all retained notices apply.
