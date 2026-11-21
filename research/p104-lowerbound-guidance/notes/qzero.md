# QZERO QZ (Nov 20, Opus; theory + exact + Lean). Own code qz1.py (exact checker, sympy), qz2.py (Lean generator). Data: caller_C1.json
(copy of cards/WILD/UNIMODEL/swarm/d3star/caller_C1.json, built by our D3STAR lane Nov 19). Lean: lean/decoder-duality/Nov15/CallerQZero.lean.
Why this differs: CALLERASM searched for a Q = 0 odd-target word and suspected a q-grading obstruction; nobody had checked the D3STAR
build C1 against CallerWord's Legal / the CALLERASM hypotheses, and nobody had asked what the q^4 = 1 layer can forbid.

## 0. Verdict: EXISTS. Minimal Q = 0. No q-grading obstruction exists beyond a parity law.
C1 (n = 4, k = 3, 69 expanded events: 3 type-B J records + ADD/SCALE/LAMBDA/IDLE_ONE, no QUERY, no odd IDLE) is Legal in CallerWord's sense
with targets q * prod_{mask} D (all exponents odd), masks {1,2},{1,2},{0,1,2},{0,1,2} (stages in call order).
[C exact, qz1.log] replay = target at q = 1, -1, i, -i with SYMBOLIC D (equivalent to Legal: Q(i)[q]/(q^4-1) = product of 4 copies of Q(i) by CRT);
WF ok; |Iota| = 6 = 2k (Q = 0) = n + 2 (tight); rank K = 2, rank G = 4, prod V = -I; stage K-block dets 2, -4, -5 (lambda != -1, a*b = -1/2, -2, -9/4);
degrees 2,2,3,3. So EVERY hypothesis of CallerAsm.word_hp_B holds: cHat(.99) = 107.9101 <= HP(3) = 115.4151.
[P Lean, CallerQZero] see section 4.

## 1. LIFT lemma [P] (why the q^4 layer is inert for host-carried signs)
Let w use only HOST and q-free events (ADD/SCALE/SWAP/IDLE sigma=0). Put c_-+ = (1 -+ i)/2 + (1 +- i)/2 q^2 (= LAMBDA(-+1)), u := q c_-.
Then c_+ c_- = 1 and c_-^2 = q^2, so u^2 = q^4 = 1. Wrapping every HOST(s,t,a,b) as LAMBDA t(-1), HOST, LAMBDA t(+1) gives
diag(c_+ q^-1 at t) M diag(q c_- at t) = HOST evaluated at q := u. Appending LAMBDA r(+1) (ex = 1) or LAMBDA r(-1) (ex = 3) turns u into
c_+ u = q, resp. c_- u = q^3. Hence lift(w) is Legal iff w's replay at q = +1 / -1 equals +-diag(D^mask) for symbolic D
(on u^2 = 1 use e_+- = (1 +- u)/2). Columns are unchanged (LAMBDA is q-even). C1 is exactly such a lift.
=> Q = 0 legality is the q = +-1, D-exact frame problem (CallerSGram + D-exactness); SPEC's q^4 = 1, i^2 = -1 adds no constraint.

## 2. PARITY [P] (the only q-grading law)
q -> -q is a ring automorphism; det of every event is invariant except IDLE with odd sigma (sign -1); QUERY r r with odd sigma is singular at
q = -1 (illegal); HOST det = 1 + ab - ab q^4 = 1. Target det = q^(sum ex) prod D. Hence  sum_r ex_r = #{IDLE events with odd sigma} (mod 2);
for odd targets  n = #IDLE_ODD (mod 2). QUERY thins carry no parity. Q = 0 => n even (consistent with n = 2k - 2). #7113: A n36, 0 IDLE_ODD; B n36, 4. ok.
Also n = 2 already works: the k = 2, n = 2 conjugacy construction (V1 ~ -V2^{-1}, traces 2+4ab equal, e.g. ab = 1, -2) gives a Q = 0 word in principle [P sketch, not built].

## 3. What it means for the caller results
- HP(k) / KASYM / CALLERASM word_hp are NOT vacuous: a real legal word meets all hypotheses at k = 3 (HP has no content at k = 3 vs the bar,
  but the branch is inhabited). CALLERASM caveat 4 is closed.
- Both branches are live: Q = 0 (HP(k); D3STAR builds; MID/FIX laws) and Q >= 1 (#7113 Q = 4; HQ/THINQ at e = 0; EXTRATHIN + LEAF-CHANNEL for e >= 1).
  The universal caller bar is max over branches; neither can be dropped.
- By LIFT, any Q = 0 design is realisable iff a q = +-1 D-exact frame exists: build attempts in the HP window (k = 5..13) only need the
  real (q = +-1) frame + D-exactness; no q = +-i bookkeeping.

## 4. Lean (CallerQZero.lean) -- see status line below
STATUS [P Lean, all rc=0 via runlean.sh, peak <= 2.96 GB; no sorry/native_decide/axioms; axioms of c1_legal, c1_nonvac, c1_hp = propext, Classical.choice, Quot.sound].
Files: Nov15/CallerQZeroD.lean (event list, 41 constant lemmas nu-form, 70 checkpoint matrices), CallerQZeroS0..S7 (69 step identities
evMat * ck_j = ck_{j+1} + (q^4-1)*A + (i^2+1)*B + (390 nu - 1)*C, ring-checked), CallerQZero.lean:
- c1_legal : Legal C1W (WF + endpoint identity over every comm Q-algebra with q^4 = 1, i^2 = -1).
- c1_nonvac : Legal ∧ odd targets ∧ |Iota| = 2*3 ∧ 4 + 2 = |Iota| ∧ all degrees >= 2;  c1J : JB C1W (type-B schema, pos 1/20/43).
- c1_hp (hlam) : cHat C1W <= HPr 3 via word_hp_B -- every hypothesis discharged in Lean except hlam (K-block dets 2,-4,-5 [C exact qz1.log]).
Not in Lean: LIFT and PARITY (paper proofs above); hlam for C1 (needs complex P1 inverses).
Next: (1) build Q = 0 words in the HP window k = 5..13 via LIFT (only q = +-1 D-exact frames needed); (2) Lean LIFT lemma (u = q c_-, u^2 = 1).
