Apache-2.0. Prepared for Thomas DiFiore with OpenAI Codex assistance.

This package composes earlier community constructions and retains their mathematical assumptions. It claims the displayed finite composition and its checks, not original authorship of E8, the mutable-source k8 circuit, the endpoint technique, or the admission machinery.

* CrocSwap/integer-mult-bounds PR1018 (`research/gauge44-slots`) supplies the R480 k8 + seven-slot circuit, all native scalar/phase checkers, and strict global admission.
* PR1030, commit d71857cd0ae7824e935aac17327e4ec27f66322b, supplies the rank-seven endpoint-pair lead. Its U8 helpers 588/589 correspond to k8 helpers 574/575. The new composition also uses 572/573, 580/581, and 582/583, with all four reductions refitted together.
* `discovery/frame_model.py` adapts the complete frame model from PR864 (navinor / Claude), retained in the earlier local research run. The adaptation permits a new initial frame assignment after changing the scalar graph or endpoint constraints. It is nomination code; unchanged independent native checks decide admission.
* `research/k8-coordinated-owners` supplies the initial whole-owner map and coordinated complete-call search. Earlier owner machinery and dual prices originate with chafreaky, G44Pack, and jon314159; see that package's NOTICE.md.
* All analytic, compiler, boundary, common-label, hosting, and bit-supplier assumptions remain those of the upstream source chain.
