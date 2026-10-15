Task ID / proposed scope key: uniform-transfer-audit / ce7411fb7cf6f3460bfc
  chooser nonce 9d450e657d814dfba70c4f6537e46fac, track adversarial-audit, priority revision 4
  (first suggestion taken; no redraw needed — not on the excluded list)
Base commit; exact predecessor and dependency heads:
  origin/main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2 (read via imb-work2, read-only)
  predecessors: research/leaf-destination-transport (woklerx, n=1..32 census),
  research/single-register-interval-transport (cbethin, PR1416: h-1 <= max <= h+2),
  research/dirty-interval-coefficient-boundary (Arham Tahir, PR1374), PR628 compose (Chafik Boukhalfa),
  PR1085 prefix invariant (Hanson Sun); adjacent open PR2067 (adamgall, endpoint accumulation).
Concrete object and question:
  PR628 balanced reserved-depth dirty word, n factors, both orientations, free noncommutative algebra
  (contractive factors, max-register norm). One unit error at the destination of a completed leaf;
  worst transport E(n) to any later complete-leaf cut. Open: exact all-size E(n)
  ("between h-1 and h+2"; finite census suggests max(1,floor(log2 n))).
Scope status: refined. Reason: takes the predecessor's open all-size question; proves an all-size
  upper bound E(n) <= h = ceil(log2 n) (n>=2) and extends the exact finite census.
Existing restriction being changed: none; same domain as leaf-destination-transport.
Method; explicit parameter ranges: written induction (three lemmas + LCA case table);
  exact free-algebra checks of each lemma for n=1..64; independent census engine n=1..128.
Nearest overlapping PRs and why this adds something: PR1416 (h+2, any single register),
  leaf-destination-transport (finite n<=32), PR2067 (endpoint cut only, many errors). None proves
  an interior-cut destination bound below h+2.
Optimistic full cost budget; required observable improvement: no kappa; precision-constant
  improvement only (h+2 -> h for destination-supported single errors).
Success evidence; falsification test; time/compute cap: written proof + exact finite lemma checks
  + mutation controls; a census value above ceil(log2 n) would falsify. Cap 3 h, CAP=3G, <=2 workers.
Predecessor authors; intended artifact and reproduction command: see above;
  LOCAL-ONLY scratch package $S/expAE/ldt (census.py, chainform.py, lemmas.py, controls.py).
Limitation: first-step research_baseline.py not run — disk quota truncated the archive extraction.
