# Attribution and license

Prepared at Martin Rivera's request with substantial assistance from
OpenAI Codex. The AI assistant selected and implemented the optimization,
wrote the equivalence argument and tests, ran the measurements, and
prepared the handoff. No independent human review or official OpenAI
endorsement is claimed. New work is under this repository's Apache-2.0
license; see the root `LICENSE` and `NOTICE`.

Douglas R. Colkitt's historical joint rational-frame audit, rational
elimination, paired-network tools and proof supply the entire reference
workload. The repository attributes that original work to Douglas Colkitt
with OpenAI Codex assistance. Relevant original code commit:
`6e564879f51ae16f23d392e9e196c605f36d90df`.

The repository already uses modular rational-rank lower bounds in
`scripts/audit_stage_pair.py`. The present contribution adds an opt-in
*exact full-rank fast path with fallback* to a different historical audit;
it does not claim to invent modular rank computation.

Concurrent related work inspected, but not imported or used as a code
dependency:

* **amanforindia, PR #367**, head
  `522285db971642c2d744cc8d45f2a5ade3a55e19`: integer exact rank and
  canonical row-space acceleration for PR364. The present method and
  historical full-certificate workload differ.
* **davidgovea, PR #700**, head
  `dee275599160965d77324c9ab635bc00ad5f702d`: independent PR468 modular
  rank/parity audit. This work makes no PR468 or parity claim and does
  not assume that rank modulo 101 always equals rational rank.
* PR #707, #709, #721 and #736 address Gram prefixes, R420 geometry
  caching, reconciliation archive memory, and cyclic-inverse zero updates,
  respectively. Their work motivated avoiding those overlapping tasks.

The current accepted construction context is Chafik Boukhalfa's #626 on
Jeremy Kothe's #622/#623, with eumemic's #543 and the broader lineage
preserved in `certificates/selected-result.json` and
`docs/research/community-k492-review.md`. This package changes none of
their supplier sources, constructions, review status or attribution.

The original OpenAI #109 source remains pinned at
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`; `upstream/` is unchanged.
