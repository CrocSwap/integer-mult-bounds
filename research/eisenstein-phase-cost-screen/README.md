# Eisenstein phase-path cost screen

**Outcome: certified necessary-condition screen — any Eisenstein-supplied
decoder that beats the selected complex supplier needs total copy cost
C <= 31 (bracket 31.0635… at s=7, window h=7); every *clean* support
alphabet costs exactly 40; the prize for any complex-only win is capped by
the selected assembly's bit side at kappa <= 0.001730427469823602 (+3.45%).**
No supplier was built and no kappa changed.

## Question

PR #831 reopened the F4/Eisenstein phase path: alternating F4 trace forms no
longer block phase compilation, because the alternating-compatible
quadratic-phase normal form handles nondegenerate alternating blocks. The
next question is economic: **if we build an Eisenstein supplier, does it beat
the current selected complex supplier?** This package answers the first half
of that question — the cost side — under the repo's inherited accounting.

## What was checked (all exact, standard library only)

1. **Geometry replay** (`research/eisenstein-clique-copy-bound/geometry.py`):
   240 roots of E8, order-three complex structure J, 40 nonorthogonal lines
   (degree 27), full flat census
   `{(0,0):1, (1,1):40, (2,2):240, (2,4):90, (3,5):360, (3,12):40, (4,40):1}`,
   every line-spanned flat nonsingular, and a 7-clique exists — so any
   pattern-legal decoder B satisfies B[Q,Q] = I_7 on a 7-clique, hence
   `rank_F2(B) >= 7` unconditionally (no reliance on the archived minrank-10
   SAT).

2. **Clean-class floor = 40.** Call an ordered flat pair (R, A) *clean* if
   every cross pair of distinct lines is orthogonal. For clean pairs the
   per-rectangle pairing-rank charge is exactly |R ∩ A|: the functionals
   x ↦ ⟨x, t⟩ − ⟨Jt, Jt·x⟩ for t ∈ R ∩ A are independent on X_R by positive
   definiteness of the real form and pairwise orthogonality of R ∩ A. The
   verifier checks this on **all 7033 clean ordered pairs** (tight everywhere,
   no census drift). Two independent sharp witnesses at total cost 40:
   - **Frame partition:** the 40 lines split into ten pairwise-orthogonal
     4-line frames, each spanning all of E8; the block-diagonal decoder is
     pattern-legal (F2 rank 10) and costs exactly 40.
   - **Star decomposition:** the canonical pattern
     B0 = (all-ones + orthogonality) mod 2 decomposes into 40 clean stars,
     each of cost exactly 1.

3. **Certified threshold screen.** For a supplier with window h and stage
   count s (odd), the format-limits skeleton (`skel.profile`, k=1,
   x = C/40 with v = 40 Eisenstein ports) gives a pressure whose root X must
   exceed the selected complex saving
   b = 67018507072324140917/40000000000000000000000. Because the copy slot
   enters the profile as mass s·x at cap h, the beat condition is **linear in
   C**, so the exact threshold is
   `C*(s,h) = 40·((s−1) − F_0(b)) / (s·(m/h)^b)` with m = 1 + s(h−1).
   The verifier certifies rational brackets on C*(s,h) for every h ∈ [7,40]
   and every odd s (interval arithmetic from `cert.py`, outward-rounded,
   ~1e-42 wide), confirms non-beat directly at each window's closure point,
   and closes the tail with an exact rational increment bound
   (binomial-series chord bound; exact partial sums to P = 200, exact
   quadratic minimum beyond; the closed-form slot masses are cross-checked
   against the engine at 25 points). Result:

   | window h | max integer threshold | argmax s | viable s range |
   |---|---|---|---|
   | 7  | 31 | 7 | 3..61 |
   | 8  | 30 | 7–15 | 3..49 |
   | 9  | 30 | 7–11 | 3..41 |
   | 10 | 29 | 7–11 | 3..35 |

   Larger windows only hurt (s=9 dies at h ≥ 24). So **any beating supplier
   needs C ≤ 31 at some s ≤ 61**, and with the minrank-10 window the bound
   sharpens to C ≤ 29 at s ≤ 35.

4. **Prize cap.** The selected assembly's bit side is
   X_bit = 0.001733427039589844 (PR #1094 audit, `bit_lower`), *above* the
   complex side b. Every screen argmax point clears X_bit, so any
   complex-only improvement is capped by the bit side:
   `kappa <= X_bit/(1+X_bit) = 1733427039589844234749/1001733427039589844234749
   = 0.001730427469823602`, i.e. **+3.45% over the selected record**
   0.001672660197076918 — the uniform prize regardless of how cheap the
   decoder is.

5. **Negative controls (4):** closed-form/direct cross-validation at eight
   boundary points; doubling b flips the argmax beat verdict; a tampered
   pattern changes the clean census; the naive consecutive-block partition is
   illegal (the frame witness needs orthogonality) and a star without its
   self-loop costs 0 (the star witness is not vacuously constant).

## What this proves and what it does not

**Proves (under the inherited accounting):** the old #620-style construction
(40 units) cannot improve kappa; any Eisenstein route that can must live in
the non-clean window C ∈ [22, 31] at s ≤ 61; and the entire prize is at most
+3.45%.

**Does not prove:** that a C ≤ 31 non-clean decoder exists; that the
quadratic-phase normal form compiles such a decoder's labels without extra
frames; or any new kappa. The screen is a necessary condition, not a
construction and not a general decoder-optimality theorem.

## Credit

Built on `research/format-limits/scripts/{skel,cert}.py` (PR #801 format
ceilings), `research/eisenstein-clique-copy-bound/geometry.py` (E8 root
geometry and pairing-rank machinery), and the selected-record provenance in
`research/community-frontier1094-audit/` (PR #1094). Related results: PR #798
(copy floor 22, all supports), PR #620 (40-unit construction), PR #831
(alternating-phase interface). See SOURCES.json for pinned hashes.

## Open next questions

- **Does a pattern-legal 40×40 F2-valued decoder exist with total copy cost
  C ≤ 31 whose support is not clean?** The screen shows the entire remaining
  upside of the Eisenstein phase route lives in this window (C ∈ [22,31] at
  s ≤ 61). Settling it either yields the first Eisenstein-supplied assembly
  (kappa up to the bit cap 0.001730427469823602) or closes the route under
  the current accounting. First step: enumerate minimal non-clean supports
  (a nonorthogonal pair read by a common rectangle) and certify their minimum
  copy cost with the same pairing-rank machinery. Not blocked.
- **Can the quadratic-phase normal form (PR #831) realize a candidate
  decoder's phase labels on nondegenerate alternating blocks at the frame
  level required by the assembly template?** PR #831 removed the interface
  obstruction at the trace-form level, but no one has checked that a concrete
  cheap decoder's labels compile without extra frames or adapters that would
  break the C ≤ 31 budget. First step: take the cheapest abstract decoder
  surviving the screen (if any) and run the f4-alternating-interface
  compilation on its labels, charging every added frame. Blocked by the
  non-clean window question.
