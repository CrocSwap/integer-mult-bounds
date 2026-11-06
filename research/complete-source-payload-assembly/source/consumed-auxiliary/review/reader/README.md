Independent final payload reader, authored only

verify_payload_v1.py imports Python standard-library modules only. It never
imports or invokes the constructor, preparer, controls, archived modules,
compiler or scientific workload. No reader execution was performed by its author.

Stable parent-only CLI:
/usr/bin/python3.12 -I -S -B ABS/verify_payload_v1.py --inventory ABS/control/SOURCE-INVENTORY-v1.json --inventory-sha256 EXACT_SHA256 --output ABS/validation/final-readback
ABS is the existing outputs/s04-02-completion-20261105T2226Z directory, except
the script itself resides under review/reader. The guard supplies the exact
inventory SHA after freezing source, guard and reader; the inventory does not
include itself. The reader accepts only these fixed inventory/output paths.

Payload expectations come from original pinned role-map, selected manifest,
actual adoption receipt, adopted recipe gate and all71 detached manifests.
Constructor results and newly observed outputs supply no expected bytes.
Inventory closure explicitly covers all332 original source paths,71 manifests,
36 preparation pins and four original authority records. Every inventory row is
hashed and identified before and after the payload read.

Every original stage receives exact file/directory-set checks, directory0555 and
file0444 checks, no-follow opens, regular single-link files, full streamed size
and SHA checks, stable named/FD identities and global distinct file inodes. A
second whole71-root pass rescans the exact trees and checks retained complete
file/directory identities. It does not claim a second complete byte-hash pass.
Baseline/candidate expected same-path differences and distinct roots are retained.

Only the fresh fixed output directory and exclusive READBACK.json are written.
Evidence is bounded below64MiB, read back, mode0444 and fsynced; the new evidence
directory becomes0555. Payload/source roots are never written, repaired or
deleted. File descriptors are retired before one close attempt; local raw first
and ordered secondary errors remain retained through finalisation. JSON reports
do not preserve cross-process Python exception identity. Failed evidence output
or termination cannot establish acceptance and must remain a parent failure.

The outer guard owns the <=120second final-child limit inside the final180second
batch, CPU/AS/file/descriptor limits, capture and termination. The reader streams
1MiB chunks and keeps metadata plus bounded JSON buffers; at most192 known own
descriptors are admitted under the guard's256 limit. The reader-local source
custody is joined with all later completed guard postchecks by the independent
outcome reviewer. It cannot authenticate a future guard receipt before exit.

Source review and reader execution grants belong to the separate guard reviewer.
Original S04.02 credit remains zero until actual full reader and guard outcomes
are independently accepted. Complete physical costs remain OPEN_NOT_ZERO.
