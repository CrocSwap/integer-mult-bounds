# Exact substitution and retained checks

This contribution was produced by Nick Petalas. Apache-2.0.

For the default scientific command pinned in SOURCES.json, replacing
`verify.dot` and `extension_check.dot` by `replay.dot8` preserves the full
result and every rejection predicate. This is implementation equivalence,
not independent acceptance of the predecessor's mathematical conclusions.

The two source dot functions receive eight-coordinate integer or rational
vectors. In the primary these are roots, normals, simple vectors and rows of
an eight-dimensional rational inverse. In the extension they are the same
doubled coordinate vectors, inverse rows and explicit eight-coordinate
fixtures. Frozen constructors and dimension checks fix this domain. Floating
point and overloaded scalar protocols are excluded.

Put s_0=0 and s_(j+1)=s_j+a_j*b_j for j=0,...,7. The original generator/sum
computes s_8. The new expression has the same eight terms and left-associated
additions, starting with zero. Exact integer/Fraction arithmetic proves equality
by induction on j. The new length check succeeds on the admitted calls.
Substituting an equal pure function preserves callers' values, branches and
checks by induction over execution. No memoization, pruning, approximation or
fixture-dependent answer is introduced. The Cartan and Gaussian algebra
implementations are unchanged.

The adapter authenticates all ten scientific inputs before compiling the four
original source modules at their original file locations. Compilation bypasses
adjacent bytecode caches. Import order is geometry, algebra, extension, primary.
The original default main executes, including the original full RESULT.json
comparison, and must return zero. Existing module objects, path and argument
lists are restored on exit. Stable files during execution are assumed, as in
the original source-hash check. Lean source bytes are authenticated because
they occur in that receipt, but Lean is not executed.

Checked mode compares old and new results at all 5,096,623 substituted calls
in one complete execution. A separate 576-case set includes all 64 ordered
basis pairs and both orientations of 256 signed rational fixtures. Six wrong
lengths and one invalid mode reject. Ten physical source-byte mutations and
one missing file reject before compilation. A wrong-dot integration control
reaches the original root-norm failure and rejects the complete command.
These are nineteen controls. Module sentinels check namespace restoration.
Explicit exceptions retain checks under optimized Python.

Performance is a local observation. Five alternating fresh-process pairs time
the original default CLI and new default CLI, including startup and output
capture. Every run must return zero, print the original success line and have
empty stderr. Input authentication before and after timing checks stability.
The generated report records every command, time and failure. It is not a
portable runtime bound, mathematical theorem or CI performance threshold.
