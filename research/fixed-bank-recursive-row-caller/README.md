# Fixed-bank recursive complete-row caller

This closes PR5134's recursive outer-port gap: its exact split/merge and
park/call/restore programs now run at arbitrary dyadic depth on nine physical
tapes. Parent source payloads are physically parked; one bit per ancestor on
a continuation tape replaces a host recursion stack. No descendant tape or
frame object is allocated.

For V=B*2^d input bits and a supplied positive unary B guide, the default
literal complement leaf gives T<=100Vd+264V+3 global transitions and retained
allocation <=K0+16V+32. Root SOURCE/GUIDE and arbitrary parking ancestors are
preserved; OUTPUT is distinct and owned; all work/continuation bodies are erased
and heads return. Alternate finite leaf programs retain explicit semantic,
trace-locality and resource premises. See PROOF.md for the all-depth induction
and complete invoice, distinct from finite verifier evidence.

Reproduce: `python3.12 -B scripts/research_package.py --package research/fixed-bank-recursive-row-caller`.
Finite checks use translated origins, all columns of a depth3 case, larger
dyadic trees and a distinct first-bit-coupled row leaf, actual wrong-return and cleanup mutations, and complete snapshots.
No Lean/kernel run, selected GL64 supplier, frontier change or new kappa.

## Open next questions

Supply an actual supplier leaf with its complete frame/resource contract,
and price the external binary-to-unary descriptor protocol. Nondyadic trees
need an explicit shape/continuation grammar; no automatic extension is claimed.

Credit commdata2338's recursive parking, original retained Lean push/pop
contributors, and JoyboyBrian's complete-row/Builder predecessor packages.
Exact files and notices remain unchanged; SOURCES.json records their pins.
New work: JoyboyBrian with substantial OpenAI Codex assistance, Apache-2.0.
