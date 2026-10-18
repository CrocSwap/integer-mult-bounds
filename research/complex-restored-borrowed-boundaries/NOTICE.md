# Attribution and substantial AI assistance

New contribution by **Ross Richardson**, with substantial **OpenAI Codex**
assistance in research, proof, code, validation and packaging, under the
repository's Apache-2.0 license. No independent human review is claimed.

The Python search, C++ search, exact witnesses and boundary recognizer are
adapted from Ross Richardson / OpenAI Codex **PR1145**, at
`fd4d5ffc448361297e717aa30eafed578caf8e61`. SOURCES.json records the original
file digests. Changes add a fixed dirty donor in each dimension, extend the
C++ state to 128 bits, accelerate row permutation without reducing coverage,
and add the unbounded-donor reduction proof and controls. The two mathematical
implementations remain separate; no new claim of having authored both from
scratch in this run is made.

Credit the actual historical swap construction to **ToikY, PR969**, head
`d1ee3f46a6167ea54913e070af3161c71a99e1f2`, in the retained
`research/complex-swap-runs-seed37` package. Its own notice credits a separate
Codex worker for independent checking. PR1145 called it PR971 in prose; this
contribution corrects its own attribution while leaving frozen material intact.

Credit **woklerx, PR1095**, for the adjacent monomial-prefix/disposable-workspace
optimum; no code or claimed broader theorem from that PR is imported. Credit
**Sagar Thakrar, PR696**, for the primitive lowering, **faw01, PR839**, for the
known-zero work principle, **Jeremy Kothe, PR622**, for the K492 words, and
**Chafik Boukhalfa, PR626**, for the historical CK/JP8 composition. Preserve the
icekylinx scalar/factory lineage and DreamingOfClouds, eumemic, Rohan Arun and
other contributor notices in the unchanged source packages.

Rohan Arun's PR1094 packing, Jeremy Kothe's cumulative k8/slot work, Hao Yan's
controller and the selected review are current context only. Their numerical
claims are not recomputed or replaced here. Elementary permutation identities
and the standard modular quotient argument are not claimed as new.
