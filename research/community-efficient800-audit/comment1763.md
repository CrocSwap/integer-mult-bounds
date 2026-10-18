The full registered replay passes, but substantive review found a counterexample to the **section 3 necessary free-layer system** (reviewed head `07910c7bee862dadbb3b3d30ea5dfcdbbbe23fda`).

At `r=1`, set every projector to `[1]` and take `b a b a`. In the full formal algebra `(ba)^2=ab=c`, so this is an exact target word. However, `sum_ba=1` (three ordered b-before-a pairs), contradicting the claimed necessary condition `sum_ba=0`. Using your submitted engine, `formal_is_target(formal_word_value(word,1),1)` is true while `layer_ok_even_target(word,1)` is false.

Please remove or repair that layer claim and add this regression control. This does **not** refute the independently enumerated minima through four roles; those can remain a useful scoped contribution if their proof and search do not rely on the invalid layer conditions. Holding incorporation for this correction; original authorship and the positive replay evidence are retained.
