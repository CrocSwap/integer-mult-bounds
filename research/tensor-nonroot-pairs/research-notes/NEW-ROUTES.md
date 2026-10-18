# Complex supplier research: partial response and centre lattice

Status: exact algebraic route, bounded finite screens; no new admitted kappa from these screens.

## A sufficient partial-response entrance construction

Let C_h be the exact dirty target-response column of helper h. Fix an entrance frame E and a set G of target coordinates whose compensation gates can legally be executed at E. Suppose a helper p and donor helpers d satisfy

    C_p - sum_d q_d C_d = r_p, with support(r_p) contained in G.

Begin p at E. Execute target[t] += -r_p[t] p at E, then donor[d] += -q_d p at E, then the original scalar word. Its dirty p coefficient is exactly r_p-r_p=0; all other columns are unchanged. Invert all added helper updates in the ordinary cleanup, restoring arbitrary helper inputs. Scalar signs and coefficients are rational, not approximate. Require E to lie in every involved helper's first frame; target compensation levels must satisfy their explicit schedule constraints. Disjoint donor/pivot classes compose without higher-order terms.

This suffices for a new physical provider once all endpoint labels, wrappers, common-frame gates and costs are supplied; it is not a claim that the current word admits a profitable selection.

Screen: every one of 511 nonzero lines, and all 14,851 distinct subspaces of the current first-frame family, were examined. Higher-rank cases yield 2,393 distinct eligible-helper/admissible-target configurations. No genuinely mixed residual relation arose: each selected dependent column either has zero full response or already has admissible support. This is an exact finite statement about the frozen word and this construction, not a universal impossibility theorem.

Reproduce: partial_kernel.py and partial_higher.py. Source: PR484 pinned 035845ce95f31d0a2dcfb42b8c8e13411271fa5f, with base scalar word recovered from the inherited kernel79 input by removing its documented 229-gate prefix. These scans do not reverify PR484's published certification.

## A sufficient centre-lattice scatter construction

The descending-chain restriction on served target labels can be relaxed without a second centre copy. After taking the existing private centre copy at its label F, choose an ordering E_1,...,E_k of the distinct served labels. Move the copy from label A to label B via H=A intersect B: apply the inverse child for A/H, followed by the forward child for B/H, scattering exactly at B into targets currently at B. Skip zero-rank steps. At the scalar copy/clear interface explicitly stated in PR484 PROOF.md sections2.1--2.2, clear the private copy by a charged array zero assignment after its last use. That event is h_C <- 0 at its current label; it is NOT reversible subtraction of the untouched centre source. The transposed linear implementation starts this scratch row at zero, reverses the walks while gathering, adds its final value into the source at F, and then discards/zeros the scratch row. If a consumer instead requires reversible erase by subtracting the original source, the copy must first return to label F and that entire return path must be charged; the free-terminal prices do not apply to that stricter interface.

The label invariant is h=T_label ell. Each transition is T_B T_A^{-1}; each addition has equal source/target labels. Products telescope, so this realizes the same logical scalar scatter for every input. It does not require A and B to be nested. Every step is between nested labels, so the existing per-edge factorization machinery applies separately, provided its full wrapper charge is retained.

The complete child bill for an A-to-B step is one inverse child of rank dim(A)-dim(H) and one forward child of rank dim(B)-dim(H). This is a new paid schedule, not a free frame change. Exact subset dynamic programming finds a minimum total-rank path through the finitely many labels, with a free terminal label ONLY under the destructive scalar clear interface above; moment optimization may prefer a different path and must be checked separately. Extra centre rank reduces global deficit and can erase any benefit of warming more helpers. No packing-only price may omit this bill.

Current mathematical scope: this is a sufficient construction at the same abstract child/copy interface as the inherited provider. It still needs an explicit chosen word and changed physical audit to support a numerical record claim.


Finite centre screens completed:
- 60 unrestricted target-chain assignments, evaluated by a native C++ exact shortest Hamiltonian path solver on the distinct served labels: 138--156 entering helpers; entrance rank342--364; extra centre rank192--198. Full results in LATTICE-CENTRE-SCREEN.json.
- Requiring the selected labels inside every relevant centre frame gave the same measured assignments, saved separately in LATTICE-CENTRE-INSIDE-SCREEN.json.
- Keeping gauge80-kernel42 fixed and excluding every existing kernel donor/pivot: 1,872 additional legal gauge/frame candidates; minimum extra centre rank3. LATTICE-EXTENSIONS.json includes each candidate and exact cost. This does not rule out a coordinated replacement of many existing choices.
- The native DP solver passes 42 independent exhaustive permutation controls on random symmetric cost matrices of orders1--7; each emitted path is independently checked. ROUTE-DP-CONTROLS.json.

The separate whole-family G148-K4 profile has an exact rational price b=1333854156208409/10^18, but remains packing/price only, without a newly completed physical provider audit. It is below the 0.0014 goal. No new final kappa is claimed.
