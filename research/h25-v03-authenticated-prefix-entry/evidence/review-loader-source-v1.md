# Unit06 independent loader source findings, first draft

CHANGES REQUIRED. This freezes the first observed9950-byte predecessor_entry.py draft, SHA256 `d7512ffe6c9ee2b7a51b98672032fd14f50f5d47e193131873ea426a47f25cbd`, rather than accepting implementation from the design. The companion JSON preserves the exact first source bytes when still available as the unchanged prefix.

U6-L01, critical, lines159–175: observe_regular performs an unowned preliminary open/read/close. A read failure followed by close failure replaces the raw primary, leaves Owner usable, and does not retain partial buffers/FD or account the first read against the aggregate. Use one owned observation state machine with raw primary/secondary retention and terminal failure; observed digest remains an observation, not prior approval.

U6-L02, material, line45: kind membership in a tuple of types may invoke a foreign metaclass equality callback. Use type identity branches; author should serialize a fresh callback-count-zero control.

U6-L03, material, lines83–91/159–175: exact integer/range cap checks must precede comparisons and I/O at validator/observer boundaries. U6-L04, interface, lines73–76: paths must match original ASCII printable and64-component schema restrictions before installation/publication.

All findings were sent to parent and author before edits. Parent alone decides the single repair window; no repair authorization was inferred. The rest of the loader/preparer and fixture harness were not yet available. No original code or new tests/counterexamples/native/compiler/Popen/namespace/target work ran. Full C05/V03/runtime flags remain false and costs OPEN_NOT_ZERO.
