# Independent integer-interval audit of shear-orbit rounding

This separately implemented exact checker corroborates Sricharan Vagvala / @theon199's PR1631 sharp finite-orbit allowance and provides a reusable oracle for arbitrary rational offsets and asymmetric integer windows. It imports no predecessor executable. The predecessor's original half-grid theorem remains credited to it; this is an independent audit and a small explicit domain extension, not a new supplier.

## Exact statement and proof

Measure the output grid in units of one. Let rho=p/d with d>0 and p integral, and consider v_k=(k rho,rho), L<=k<=U for integers L<=U. A shear-equivariant orbit is determined by the integer seed q(v_0)=(a,b), even when 0 lies outside the tested window. Its error is (a+k(b-rho),b-rho). The exact minimum radius is an integer multiple z/d.

For a proposed z>=0, set t=db-p. A feasible integer seed exists exactly when there is an integer b with |t|<=z and, when U>L, |t|(U-L)<=2z, for which the interval

    max(ceil((-z-Lt)/d), ceil((-z-Ut)/d))
      <= a <=
    min(floor((z-Lt)/d), floor((z-Ut)/d))

contains an integer. Necessity follows from the two endpoints and the vertical coordinate. Sufficiency follows because the first-coordinate error is affine in k and its maximum absolute value on the interval is at an endpoint. The interval bounds already are integers. The second bound on t only accelerates enumeration; it follows by subtracting the endpoint inequalities. This gives a finite feasibility test, and monotonicity in z permits exact binary search. The seed a=b=0 supplies a finite initial upper bound. No floating-point optimization is used.

At rho=1/2,L=0 this independently reproduces PR1631's delta*max(1/2,K/4+dist(K/4,Z)). The general oracle does not assume that formula. The verifier checks 1001 half-grid horizons, 2268 rational windows (d=2..9, p=1..d-1, L=-4..4, U=L..6) against a separate full chronological integer-box enumeration, and 10152 chronological positions. The box is complete because the trivial incumbent bounds b and the entrance error bounds a. A window beginning at 10^12+3 and ending at 10^12+987 has optimum 493/3 for rho=1/3, attained by (333333333498,0). The large-window certificate checks both feasibility and rejection of the immediately smaller radius without scanning that orbit.

Three controls retain the transverse error at a zero-length orbit, reject a noninteger seed shortcut, and require both endpoints. These test mathematical assumptions, not only format. The all-horizon obstruction and sharp half-grid theorem are predecessor results; finite tests here are not a proof by enumeration of all circuits.

## Reproduce and scope

    python3.12 scripts/research_package.py --package research/shear-orbit-interval-audit

Python standard library, read-only, explicit checks remain enabled under -O. Exact Git blobs and SHA256 hashes pin the unchanged predecessor README in EXTERNAL-SOURCES.json and local base provenance in SOURCES.json. No pending package code is imported. OVERLAP.json records the complete 535-PR /517-Discussion metadata snapshot and deliberate overlap.

This is a single prescribed orbit contract, not a globally compatible rounder, precision optimum, native tariff, complete cold replay, or multiplication theorem. The selected frontier is unchanged.

## Open next questions

Can an actual bounded caller domain be represented by finitely many such windows with one compatible seed function? First derive its reachable orbit classes and compatibility constraints. The missing piece is the caller's source-bound reachability and precision contract; separate per-orbit optima need not assemble into a global rounder.

## Credit

Sricharan Vagvala / @theon199, PR1631, supplies the sharp half-grid proof and interface audit. Sagar Thakrar / PR1537 supplies the exact carried reader, with Ross Richardson / PR1287 and the retained PR1227/889/1203 lineage. Their exact arithmetic construction is not refuted. New interval oracle and independent audit prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0; no independent human or formal proof-assistant review.
