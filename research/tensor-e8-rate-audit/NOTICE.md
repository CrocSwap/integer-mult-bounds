# Attribution and license

Prepared by Scott Woolsey Biggart (@swbiggart), with substantial OpenAI Codex
assistance in the mathematics, implementation, review and writing. No independent
human referee or formal proof is claimed. New material is under the repository's
Apache-2.0 license; see ../../LICENSE.

This audit depends on the paid tensor profile in Artus / @artuskg's PR647,
head 956bb581e7f97328e1b53baa5aca3d2490f2f607. That contribution credits OpenAI
Pro for the retained provider proof, Codex for its recovery and scrutiny,
and a separate Codex referee for its depth-one checker. The limit
28/(2739 log 3), the construction and all original count formulas belong to
that predecessor. Our additions are the independent general-depth accounting,
explicit finite-depth bounds and the center-copy correction expansion.
No predecessor implementation is imported by our checker.

Retain the precursor credits recorded in PR647: Jacob Sussman's E8 unit and
phase-frame/cover work; Chafik Boukhalfa's explicit programs; eumemic's batched
recursion; Ryan Shea's transfer work; and the P390/P401 and paired-cube lineage.
OpenAI's exact-Fourier source is part of PR647's transfer, which this audit
does not use or revalidate. See the immutable PR647 NOTICE.md and source hashes
in SOURCE.json for its complete provenance and retained notices.

The elementary atanh/logarithm and exponential bounds are classical. No
literature-priority claim is made for them, tensorization or moment methods.
