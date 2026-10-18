# Attribution and license

New formalization and verification package prepared for Gareth Davidson
(@bitplane), with substantial OpenAI Codex assistance in task selection,
proof development, implementation, validation, and documentation. No
independent human peer review is claimed. New files are Apache-2.0.

Alexander Schwartzman (@AlexS-scale), PR784, supplied the original analytic
scratch/call theorem, equality family, 50-factor example, and Python source
being formalized. This package claims a distinct kernel-checked proof and
bounded executable correspondence, not priority for those mathematical
statements. Consumed files and the complete original notice are vendored
unchanged; `SOURCES.json` records their exact source commit, SHA256, and Git
blob identities.

PR784 builds on androolloyd's PR673 multiway echo and Koroffstrogov's PR758
all-arity optimization. Related work includes Sagar Thakrar (@thakrarsagar),
PR730 ordered binary/ternary optimization; Ali Romman (@aliromman), PR744
strict-ternary census; and Chafik Boukhalfa (@chafreaky), PR628 dirty cyclic
inverse leaves. The original notice preserves credit for PR621 and further
mathematical sources. No predecessor code is edited.

The official Lean toolchain is an external reproducibility prerequisite;
no compiler or library binaries are redistributed in this package.
