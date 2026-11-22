# What the chart-510 rewrite can save

Write \(t=1-\kappa\). A nested MOVE of rank \(r\ge1\) carries one normalized field and costs \(r^t\) in the raw BIT moment. A cocharted ADD takes the XOR of two fields. The source has 630 public inputs, comprising 222 main fields and 408 helpers. All instruction numbers below are zero-based. The literal graph was supplied by Ali Romman. [Pinned #8027 source](https://github.com/aliromman/integer-mult-bounds/blob/fb9b6a7b0d27da1cf98430893a3016bf811e2aa4/research/p104-live-relative-gain/BINARY-CANDIDATE.json.gz)

## 1. Five MOVEs are optimal on arbitrary inputs with the original exterior traffic

The native block brings a field \(a\) from chart 330 and a field \(b\) from chart 331 into chart 510. It sends \(b,a\) separately to chart 1 and \(a+b\) to chart 328. The three rank-six charts 330, 331 and 328 have different projectors. Charts 510 and 1 have dimensions seven and eight. All five MOVEs have rank one. The actual first readers of the three exports occur at 29578, 29847 and 11021 respectively.

Allow the five sends to move in time, permit new nested projectors and grant every chart all its previously observed exterior fields for free. Keep the other paid packets' original normalized contents and the three outputs due at their first readers. The minimum cost for this class is five whenever \(0<t\le1\) and \(6^t>5\).

For the lower bound, let \(L\) be the sum of the integer MOVE ranks. Concavity gives \(\sum r^t\ge L^t\), so any contender costing at most five has \(L\le5\). At the final chart-1 deadline, \(a,b\) have quotient rank two over the pooled exterior information on the high side of each of the dimension cuts \(6\mid7\) and \(7\mid8\). These are exact ranks of the literal input coefficient matrices. They charge two upward unit crossings on each cut. Chart 328 also needs an incoming field by its parity reader. The early history check proves that its parity cannot come from the stock of any one rank-six sender combined with all rank-seven and higher exterior stocks. It follows that both upward sends out of rank six must stop at the same rank-seven parity sender. They cannot take a direct two-rank shortcut. The remaining three units go from that sender to the sum recipient and to the two chart-1 readers.

The rational image and kernel computation leaves only the original three neighbors of chart 510 as the possible terminals for an optimum. In particular, among all 16,110 pairs of original rank-six donors, only \((330,331)\) could supply the parity at a new, initially empty hub. Their image sum and kernel intersection determine the original projector at chart 510 uniquely. The precise historical spaces, the treatment of the previously delivered parity and the checks for all existing hubs are in the detailed proof. [Timed cut and geometry](HISTORY.md) · [Replayed ranks](HISTORY.json)

## 2. A cheaper word and its exact domain

Use the chart-1 values in the nine- and twenty-three-term lists in the checker to build the two export owners directly at chart 1. Keep the original parity route to 328. This replaces six original instructions with two INITs and 32 ADDs. The new word has 2,801 MOVEs, including 1,346 of rank one. The original counts are 2,803 and 1,348. Both words execute all 3,433 private clears at the same charts. [Literal rewrite and reverse replay](verify_rewrite.py)

Let \(M\) be the native public map and \(M'\) the changed one. At the two replaced exports, let \(r_a,r_b\) be the difference between the original form and the new local readout. Both residuals involve only grade-eight helpers. Their supports have 29 and 18 coordinates and overlap in one. Let \(s_a,s_b\) be the two public output columns reached by a unit error in the respective readouts. Their supports are disjoint and have sizes 12 and 7. If \(R\) has rows \(r_a,r_b\) and \(S\) has columns \(s_a,s_b\), full forward propagation gives

\[
M' = M+SR.
\]

The reverse instruction interpreter checks the transpose on every one of the 630 dual coordinates. Both \(R\) and \(S\) have rank two. Hence \(M'x=Mx\) **if and only if** \(Rx=0\). This is a codimension-two subspace, with arbitrary main inputs. Setting the 46 listed helpers to zero suffices, and correlated nonzero helper fields are also allowed whenever both XORs vanish. [Exact forms and signatures](REWRITE.json)

There is also a full-map rank defect. The original \(M\) is an involution, and direct pairing gives \(RM^{-1}S=I_2\). Therefore \(M'M^{-1}S=0\). Conversely if \(M'x=0\), then \(x=M^{-1}SRx\). The two columns of \(M^{-1}S\) are therefore a basis for the entire kernel of \(M'\). Its rank is 628. On the single input with helper 266 set, output 92 is wrong. On the input with only helper 254 set, output 63 is wrong. The two explicit collisions with zero also exclude any final decoder using only the changed public outputs. [Witnesses](REWRITE.json)

This loss composes in the actual 36-call order. Restrict to fields constant in their addresses, so all native chart permutations act identically. The retained adapter assigns a distinct helper bank to each LOCAL clock. Its original helper block is the identity. The changed block is \(I+S_hR\), where \(S_h\) is the helper part of \(S\), and \(RS_h=I_2\). Its rank is 406 and its outputs depend only on its own helper bank. With all helper inputs zero, the 4,218 root inputs still have an invertible root-to-root map. The full binary matrix on constants is thus block triangular. Applying the rewrite at **any** \(m\) of the 36 calls gives rank

\[
4,218+(36-m)408+m(406)=18,906-2m.
\]

For all 36 calls this gives 18,834, a loss of 72 independent directions. The claim concerns arbitrary independently supplied root and helper fields on this restriction. Individual zero-filled locations of a powered physical word have additional premises. [Independent constant-field check](constant_caller.py) · [Pinned helper-owner binding](https://github.com/aliromman/integer-mult-bounds/blob/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers/strong_binary.py#L97)

## 3. Independent instances can be priced together

Consider an abstract fixed schedule with two distinct dimension-six source projectors \(U,V\), an initially empty dimension-six parity recipient \(C\) distinct from both, and a dimension-eight recipient \(W\). At \(U,V\) place independent strings \(A,B\) of \(m\) symbols from the same finite field. Require \(A+B\) at \(C\) and both strings at \(W\). A MOVE carries one symbol and has the rank-difference tariff. Allow free local deterministic coding, unlimited retention and any new nested projectors. Every other initial value is fixed independently of the inputs. Assume \(9/10\le t\le1\).

**Theorem.** Every such protocol costs at least \(5m\), for every positive integer \(m\). If a dimension-seven hub is nested above all three dimension-six terminals and below \(W\), \(m\) copies of the native five-MOVE routing attain equality. In particular, pooling clean independent copies cannot buy a discount. This theorem and the single-invocation historical cut in §1 have different side-information hypotheses.

**Proof.** For a MOVE \(e\) of rank \(r_e\), let \(c_e\) count the upward cuts \(6\mid7\) and \(7\mid8\) it crosses, plus one if it arrives at \(C\). A MOVE into \(C\) crosses neither cut upward, so \(0\le c_e\le\min(r_e,2)\). At each cut the upper side must learn \(2m\) symbols. At \(C\), at least \(m\) arrivals are needed to determine its parity. Thus \(\sum c_e=5m+u+v+w\), where \(u,v,w\) are the respective nonnegative excess counts over \(2m,2m,m\).

Call a MOVE exceptional if \(r_e>c_e\), and let \(b\) count these MOVEs. Give every vertex the transcript \(Z\) of these \(b\) symbols in advance for the purpose of a lower bound. Among the other MOVEs, a jump of rank two must be a direct \(6\to8\) transmission. Let \(n\) count these direct jumps. Every other such MOVE has rank one and is of the form \(6\to7,\ 7\to8,\ 7\to C\), or \(5\to C\).

Fix \(B\) and give a simulator \(Z\) and all nonexceptional messages \(U\to7\). It can reproduce the knowledge at every dimension-seven vertex and at \(C\), in chronological order. Dimension-five vertices have only information in \(Z\). A dimension-six vertex other than \(U,V,C\) also has only that information. Messages from \(V\) are determined by \(B,Z\). Feedback from \(C\) is already known to the simulator, and a direct jump to dimension eight has no nonexceptional path back. As \(A+B\) recovers \(A\) when \(B\) is given, counting the possible transcripts forces at least \(m-b\) nonexceptional sends \(U\to7\). Exchanging the sources gives at least \(m-b\) sends \(V\to7\). The total number of upward crossings of \(6\mid7\) is \(2m+u\), so \(n\le u+2b\). This argument permits nonlinear encoders and feedback on a public input-independent schedule.

Put \(\delta=2-2^t\). The difference between total price and total credits is \(\sum_{\rm exceptional}(r_e^t-c_e)-\delta n\). Since \(2^{9/10}>7/4\) and \(3^{9/10}>5/2\), every exceptional term exceeds \(2\delta\). This follows from \(c_e=0\) for \(r_e=1\), \(c_e\le1\) for \(r_e=2\), and \(c_e\le2\) for \(r_e\ge3\). Substituting the bound on \(n\) gives

\[
\sum_e r_e^t-5m
\ \ge\ (1-\delta)u+v+w
+\sum_{\rm exceptional}(r_e^t-c_e-2\delta)\ \ge\ 0 .
\]

At equality all excesses vanish, there are no exceptional MOVEs and \(n=0\). Every charged MOVE then has rank one. The common-hub construction proves sharpness for the stated geometry. ∎

## 4. Consequences at the trial exponent

At \(\kappa=0.00389046\) the full original raw BIT word has about 0.132405116497 more paid than productive moment. In the particular hypothetical substitution of two paid rank-one occurrences by one rank-two occurrence, each substitution saves \(2-2^{1-\kappa}\). The least integer number needed is 25. With 24 the raw margin is already negative. With 25 the checked 268-factor supplier price, the six ordinary stage bills, the 48-call positive price and all 58 signed gates pass their numerical inequalities. These calculations assume the stated actual new histogram and compatible ownership and resource bounds. They give a price for a future construction. [Directed arithmetic](PRICE.json)

For the two displayed local readout variants, 46 and 90 zero coordinates are sufficient activation conditions. An integer transport additionally bounds a precisely defined pricing rule in which a retained productive tuple witnessing all the specified support hits requires a full-rank paid tuple. The certificate covers all finite powers and both alternatives at any selected coordinate. Its upper endpoint is \(0.003890115286594461129996943\). Exact linear cancellation among surviving nonzero fields is a different possible activation condition. [Guard theorem and certificate scope](GUARDS.md)
