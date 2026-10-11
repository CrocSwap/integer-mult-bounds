# Copy-source lifetime

A copy block copies a source, reads the copy as needed, and discards the copy when it again agrees with the source. The source must stay unchanged during the block. Reversing the block then creates the copy from that same source at the reverse entry and undoes the intervening gates. A source need not be globally excluded from a basis rewrite whose operations occur outside the block.

Two selected helpers, streams 10233 and 10257, are sources of copy blocks. Both are kernel pivots. A square-zero donor += pivot basis shear never writes its pivot. The old blanket audit ban on selecting a COPY source was consequently stronger than necessary. The independent arbitrary-precision chronological checker verifies that no scalar gate writes the original source while any COPY/ERASE window is open, checks both endpoint frames and all temporary lifetimes, and requires all 24 windows to close. The actual full word is additionally checked on every arbitrary input column, forward and inverse.

This replaces a conservative syntactic exclusion with the precise sufficient lifetime condition. It does not remove a required check or infer correctness from matching histograms.
