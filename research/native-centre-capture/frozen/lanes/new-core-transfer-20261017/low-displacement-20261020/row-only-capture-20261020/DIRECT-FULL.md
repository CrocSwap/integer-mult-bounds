# Direct FULL recipe

The native rank-nine kernel is, by its exact recipe definition, the
nine positive coordinate line gates. The canonical FULL frame is
the same circuit. Thus each of the sixteen new FULL calls can use
identity left and right maps.

The original generic compiler produced two nontrivial wrappers for
each such call. They compose with the native kernel to the same
operator. The new checker compares the two complete operators,
including global phase, and replays every complete bank word.
The selected, ordinary, source, and helper contracts do not change.

This separate refinement removes 32 nontrivial native side maps.
The complete side-map upper bound is now 3,008. The profile,
mass 1,808, scalar price 11,640, and 208 explicit boundary views
remain unchanged. The earlier frozen packet is preserved.

The native-review lane identified this direct-kernel refinement.
AI assistance was used.
