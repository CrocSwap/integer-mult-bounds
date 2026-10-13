# Fresh graded box-convolution validation

The frozen package passed from new output directories on macOS arm64 with
Python 3.11.15 and 3.14.8, and Linux aarch64 with Python 3.14.8. Complete CHECKS
and RESULT files are byte-identical on all three runs. COMPARISON.json binds
those files to the final package manifest. SOURCE-BYTE-AUDIT.json compares the
pinned upstream proof with its exact Git object.

All runs execute the 2,040 integer products, independent convolution oracles,
carry checks, weighted rational fixtures and five invalid arithmetic controls.
Four additional wrapper controls reject optimized Python, a missing input,
a changed source token and an unexpected file before output creation.

An earlier local package was rebuilt after replacing the optimized-Python guard
with an explicit RuntimeError; only the final-source runs are included here.
These receipts establish finite exact behavior and package integrity. They do
not establish a runtime bound, a new multiplication exponent or a Lean theorem.
