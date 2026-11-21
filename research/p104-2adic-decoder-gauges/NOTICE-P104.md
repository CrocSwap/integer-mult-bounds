Apache-2.0 (see `LICENSE`). Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

The Lean closure contains, unchanged, the earlier P104 Lean library that the new modules import, including the
Bridge7761 modules that encode facts about PR #7761's graph (Clear1nsight), as shipped in our PR #7796 and carried by
our CERTKIT package. This package states and checks facts ABOUT those constructions and about decoder/network models;
it does not replace or endorse them. `data/frame/` holds the P104 label and frame lists (labels.txt, frames.txt) and the
list of 7-dimensional blocking sections (block.out) from which `FrameCert.lean` is generated.
The new Lean sources, the FrameCert generator and the checks are ours; toolchain and Mathlib pin are those of the earlier Lean packages.
