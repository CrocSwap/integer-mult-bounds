# Executable bounds and inspection

The retained artifact is one standard-library Python file. `compile_frames`
is its public computational entry; the other matrix routines are internal to
that entry or the fixed no-argument replay. The compiler validates both inputs,
matching dimensions, exact rational types, coefficient sizes and orthogonality.
Unsupported inputs fail with ValueError. Boolean and floating-point entries
are rejected. Every mathematical check uses an explicit exception and remains
active under optimized Python.

There is no recursion. Compiler dimension is at most eight, reduction has at
most eight iterations, and each iteration strictly decreases the independently
checked displacement rank. There are at most 25 emitted instructions. Compiler
matrix loops have at most eight iterations per dimension. Product outputs have
at most 4,096 numerator/denominator bits. Reflection construction and elimination
between those checks use a finite number of exact operations on bounded-size
matrices; no claim of a practical public worst-case runtime is made.

The replay has 2,921 fixed program fixtures, at most eight active-plus-dirty
complex coordinates, real matrices at most 16-by-16, at most 25 instructions per
fixture, and at most 16 elimination pivots. Its nonreal word corpus has exactly
1+5+25+125+625 words, each of at most four steps. All other loops range over
these finite dimensions, the 12 control cases, or the package's source files.
The receipt inventories only package-local regular files. The replay writes
nothing and owns no network connection, subprocess, random generator or lock.

Power of Ten rule 3 deviation: CPython and Fraction allocate during operation.
The fixed corpus, dimension limits and input/product bit guards bound live
matrices; one program endpoint is retained at a time. There is no service loop,
external state or retained history of the census. A native fixed-allocation
implementation is a separate obligation. Python has no pointer arithmetic or
preprocessor; the artifact uses direct named calls, no dynamic evaluation,
code generation or callback dispatch. Ordinary exception propagation is the
failure path. No shared repository implementation is changed.

Functions are below 60 physical lines. The compiler checks nonzero normals,
rational basis inverses, strict rank progress, exact termination and the tariff.
The separate interpreter verifies full endpoint matrices, every prefix bound,
returned dirty coordinates and an independent antilinear-rank calculation.
Warning-strict normal and optimized runs, AST syntax/function-size inspection
and tabnanny are the local diagnostics. No static type checker, native compiler
or formal proof kernel is claimed. Registered replay repeats both strict modes.
