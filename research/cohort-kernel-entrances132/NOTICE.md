# Attribution and scope

New response-kernel rewrite, native checks and packaging prepared with substantial OpenAI Codex assistance. No personal byline is added.

Based on CrocSwap/integer-mult-bounds PR249 at commit 96495746c786d6d0339dbb38c7f553d4af3f88ed. The original sources and license notices are preserved in vendor/pr249-source.zip; see vendor/UPSTREAM-NOTICE.md for upstream contributors and mechanisms. Those historical public credits are retained.

New code is distributed under Apache-2.0 (LICENSE). The vendored nlohmann JSON single header retains its own MIT license and attribution. Boost is an external build dependency, under the Boost Software License. Existing third-party files retain their original terms.

This is a finite construction with exact checks, conditional on retained public all-size interfaces. It is not a Lean/kernel certificate or an unconditional integer-multiplication theorem.
