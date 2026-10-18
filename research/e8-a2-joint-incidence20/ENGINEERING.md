# Verification and resource scope

Separate Before Serializing Shared State gives this session one package,
branch and cache. Only short Git metadata operations and semantic reservation
use the shared OS locks. Prove It Works requires the actual committed export
and Git-free replay, in addition to working-tree checks. Unslop governs prose.

Power of Ten inspection covers verify.py, crosscheck.py, test_controls.py and
the called geometry root_data/root_lines/frame_lines/solve/dot/canonical paths.
The historical geometry flat_capacity/chamber census is never called. Existing
root reconstruction is fixed at 120 roots, 112 live labels and 8 coordinates.

All new functions use structured control flow without recursion. Exits either
return or raise; file contexts and TemporaryDirectory release resources.
Inputs are at most 100,000 bytes each. Binary values have at most 9 bits and
collections at most 512 entries at the public algebra boundary. Plane inventory
has 1,120 entries; fiber inventory 3,360; each span at most 512 vectors. Model
polarization has 65,536 pairs, plane construction 7,140 pairs, plane evaluation
134,400 roots, and canonical census 2,667 subspaces. The separate extremal
check has 80,730 five-label subsets and at most that many distinct closures.
All CLI commands have a 120-second registered timeout. These are deterministic
bounds, not performance measurements.

Rule 3, fixed memory after initialization. Python necessarily allocates during
managed arithmetic and collection operations. This is a managed-runtime
deviation, bounded by the fixed inventories above, three fixed source rows,
one temporary control root and sequential commands. No unbounded input or
stream is accepted. Static inspection and the complete replay verify bounds.
A future larger domain must introduce explicit capacities before reuse.

Rule 8, dynamic loading. The one inherited geometry module is executed from
source bytes after checking its exact fixed path, input usage, Git blob and
SHA256. It cannot consult stale bytecode. This limited loading mechanism
preserves the repository's pinned module without copying or mutating it.
Controls reject changed bytes, usage changes and malformed inventories. Any
additional module needs a new explicit authenticated dependency.

Rule 9, indirect calls. The authenticated geometry module has the fixed called
functions named above. Controls use bounded local callbacks only to verify
expected exceptions; there is no registry, untrusted dispatch or callback
lifetime. File and subprocess-free verifier operations own their resources.

Internal require/check contracts remain active under optimized Python.
Boundary schema/range/hash errors raise ValueError. Return values of source
reads, reconstruction and receipt checks are consumed; write lengths are
checked. Source mutation controls exercise failure cleanup. New functions
stay within roughly 60 formatted lines; no shared mutable state is introduced.
Ruff E/F/I/B/UP checks, formatting, warnings-as-errors and source compilation
are run. No repository-wide static-analysis configuration is changed for this
isolated opt-in package. A proof-kernel check and unrelated historical suites
remain outside the stated validation.
