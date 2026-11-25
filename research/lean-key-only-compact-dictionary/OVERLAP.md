# Bounded overlap and source-closure comparison

This is a comparison against the direct public predecessors and their exact source bytes, not an exhaustive search or a claim of global novelty.

- PR1831 (`542f914ca0e5df4026341d08c84385cb1a71cfdf`) provides the unchanged strict parsed-value syntax. This unit does not introduce another AST.
- PR1879 (`981afe759f7dd206188b1c1a62250c6425bcd76a`) provides strict indices, checked permutation/binary certificates, canonical encoding, AST interpretation and gather. Those exact modules remain imports; this unit adds complete byte-layout and ordered-key witness composition.
- PR1927 (`a5838afac3a2d69d802c2440cbfa7d160ca0b218`) provides actual owner/call/packed-column AST adapters. The strict named-column decoder is reused unchanged.
- PR1950 (`d5aa485468f31fbcac3758ee63284c07da426cde`) provides restricted factorization recovery and actual byte parsing. The operator class and parser equations are retained unchanged; no general invertibility or parser correctness theorem is added.
- PR1961 (`3bb423ee93c8d8707b7b521e88132e3dfb5799fc`) provides compact fragment equality and named-dictionary joins. This unit extends one-fragment checks to complete serialized-layout equality. Its ASCII module is not required by this import closure.
- PR1978 (`cfd9f916c2e3402cc1d65c63235f3f7241233b3c`) provides exact byte containment and same-artifact parsing. The new layout proof derives the selected containment from the complete ordered field list; the key-only layer then obtains all values from actual lookup rather than accepting supplied column values.

The three new sources have distinct module names and hashes from all twenty direct prerequisite sources. Import closure is twenty unchanged public sources plus three new sources, with no copied predecessor. This bounded comparison does not certify the absence of analogous unpublished or unrelated work.

All PR URLs use `https://github.com/CrocSwap/integer-mult-bounds/pull/<number>`; immutable repository paths and full source hashes are in the manifest.
