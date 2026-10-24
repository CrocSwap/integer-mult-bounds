# Conditional native Word RAM multiplication: κ = 0.0030201655

The informal sufficient assembly in [NATIVE-ASSEMBLY.md](NATIVE-ASSEMBLY.md), together with the explicitly retained predecessor algebraic and analytic proofs, gives packed n-bit multiplication in O(n / (log n)^κ) on a standard Word RAM with w = Θ(log n) and bounded-word MUL/DIV, for κ = 0.0030201655. It uses neither a TM simulator nor a TM multiplication subroutine. The word-width constant and eventual cutoff may be enormous.

This exceeds the displayed conditional Word RAM target 0.003020165 in PR #4541 by 0.0000000005. It does **not** improve the underlying p16 paid profile or critical root, establish a new TM bound, or claim that no previous cofinal family implies this numerical value. The contribution is a direct finite-word realization and complete cost assembly with weaker machine premises. The selected upstream frontier is unchanged.

Two essential mechanisms are combined here: (1) fused gauge-free Gaussian circuits with paid sublinear full-group metadata tables, bounded local microbox routing, and multi-limb offline coefficient construction; (2) global-precision native FFT record products and an explicit batched boundary solver, including both coupling directions and periodic closure. Direct native execution of the actual retained finite provider supplies the transform exponent. An unfused Gaussian loop or a local-log(record-size) word model would not establish this bound.

## Read and replay

Start with NATIVE-ASSEMBLY.md, NATIVE-PROVIDER-4535.md and RECORD-PRODUCT.md. The exact nine-row ledger has a minimum excess of 0.0000000000197983445 above κ. Run `python3 -I -O -B verify.py` from this directory, or `python3 -B scripts/research_package.py --package research/native-kappa-30201655` from the repository root. Python 3.12 and its standard library suffice; Windows, Linux and macOS use the same source. No GPU or Lean environment is required.

The verifier authenticates the complete package before loading component code. It checks the source critical majorant and finite absorption, all strict native cost inequalities, actual fixed-word arithmetic components and rejecting controls. These are finite component and rational-arithmetic checks, **not** a replay of the all-input asymptotic multiplication algorithm or a formal proof certificate.

## Retained proof boundary

The finite provider has fixed rank N = 2^(10^12), encoded symbolically and never materialized. Its actual all-column/all-fiber algebraic identity and critical majorant are retained source proofs, not inferred from sampled matrix entries. The analytic Gaussian/Poisson, fine-padding, accretive Toeplitz and integer recovery proofs are also retained. MODERN-SOURCE-MAP.json and 4535-BRIDGE-PINS.json bind the exact public source snapshots. Source snapshots preserve their notices. This package adds an informal native assembly and executable components; independent acceptance of the inherited mathematics remains a review obligation. No unknown gadget or fast-multiplication oracle is assumed.

## Overlap, precedents and credit

The final checkpoint fetched canonical main f626db5c3a3d781d8f7695038776c621651f75e1 and inspected the 30 most recently updated PRs through #4562. In particular #4535 supplies the critical-root input; #4538/#4541 supply earlier native components and packed TM transfer; #4554 supplies native Gaussian/FFT primitives. Newly visible #4556–#4562 are independent component audits, not a new exponent. Their existence is acknowledged; this package does not claim to have replayed all those submissions. #4540/#4549's controller results do not change the paid p16 profile used here. No exhaustive historical-priority claim is made.

The shared DAG/Lean tree was searched for Word RAM, sparse limbs and convolution. Problem 1.8/MpLimbs and sparse-axis precedents informed the representation, but no newly kernel-checked Lean theorem is claimed or required. Source-only catalog entries are not treated as proofs. The canonical DAG and active Lean sources are untouched.

Credit includes Cinna Davis and joint-helper contributors; Jacob Alan Sussman; zxv; Ryanson Jonathan; Dillon (#4532/#4535); Vlado Vojdanovski (#1673); the #1758 gauge-free authors; Chafik Boukhalfa (#1786) and Tim Trudgian; Jeremy Kothe; eumemic and icekylinx; Harvey and van der Hoeven; and all retained source owners. See the original notices and assembly credit for specific contributions. Prepared for Dugongue with substantial OpenAI Codex assistance from one lead and three reviewing/research agents. Apache-2.0 for new code; inherited notices remain applicable.

## Open next questions

Independent review should check the retained all-fiber compiler and analytic proofs at their actual caller. A practical full native multiplier and a useful cutoff remain unimplemented; see TASK.json for concrete review and engineering steps. These limitations do not convert finite checks into universal evidence.
