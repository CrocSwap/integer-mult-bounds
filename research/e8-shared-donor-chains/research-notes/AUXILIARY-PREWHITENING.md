# Full auxiliary prewhitening: sufficient construction

Let x be immutable source registers and z=(y,h) be targets and helpers. Suppose an explicitly emitted linear main circuit has block map

    (x,z) -> (x, N*x + T*z),

where every auxiliary-only elementary shear is invertible, and source additions are the only occurrences of x. Then T is the exact zero-X projection of that circuit. Emit its inverse by reversing and negating the projected elementary shears (including the centre scatter as explicit helper-to-target additions at its actual snapshot). This is a literal finite circuit, not an assumed inverse oracle. Starting with arbitrary x,z, the composed main after preconditioning is

    (x,z) -> (x, N*x + z).

If the target rows of N are the intended M, and helper rows are N_h, add -N_h*x at the common final frame. Every original helper is restored and targets gain M*x. If a helper row N_h[r] is zero, it needs no final repair. The inverse-transpose implementation yields the corresponding backward shear.

This strictly generalizes helper-only prewhitening: T may include target-to-helper as well as helper-to-target and target-to-target elementary gates. A candidate may therefore use target rows to uncompute a helper after its last influence on any target or retained total. Its clean helper row can become zero despite introducing target dirt: the full T inverse compensates that dirt explicitly.

Sufficient finite admission still requires: source registers truly immutable; clean target map unchanged; the zero-X projected centre operation actually a shear at its retained snapshot; actual same-frame gates; nested paid climbs; exact phases/endpoint conjugations; common initial scalar-only preconditioner implementation; finite coefficient/primitive bill; restored work; and correct global bank placement if a zero row is used to remove/fuse a child. The universal algebra above does not supply a paid improvement by itself.

Search gate: allow targets as donors for helper nullification after their last target influence; replay every clean source row, then both full dirty orientations using the explicit projected inverse. Charge all donor advances once, including shared advances across multiple sinks. Prefer free frame coincidences first, then amortized advances. Reject any positive histogram nomination failing full frame/column admission.
