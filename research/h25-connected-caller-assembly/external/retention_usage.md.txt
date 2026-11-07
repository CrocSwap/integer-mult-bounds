# Standalone evidence archive

This package contains raw SHA-256 blobs, complete run manifests, original inventory and these stdlib-only tools. Linux `renameat2(RENAME_NOREPLACE)` is required for publication. Preserve the externally recorded ROOT SHA-256: a package-local digest does not establish historical completeness.

The tree contract includes regular-file bytes, relative paths, empty directories and modes. Symlinks (including ancestors), special files, special permission bits, xattrs/ACLs and unsupported names are rejected. Every file must have owner-read permission; every directory, including the root, must have owner-read and owner-search permissions. Other ordinary permission bits are preserved exactly. Ownership/time/inode fields record original provenance; restoration creates independent new inodes. Keep every attempt directory and receipt, including STOP outcomes. Existing paths are never overwritten.

All command paths must be absolute, with existing ordinary parent directories and fresh external destinations/attempt directories. The destination parent must be owned by the caller, have mode 0700, and have no xattrs/ACLs; create a fresh private output container when needed. Commands print one bounded receipt; detailed inventories are files.

Original inventory (only when archiving original evidence):

    python3 oracle.py /absolute/source/runs /external/original-inventory.json

Creation (use the inventory SHA-256 returned above):

    python3 archive.py create --source /absolute/source/runs --inventory /external/original-inventory.json --inventory-sha256 INVENTORY_SHA256 --destination /external/new-package --attempt /external/new-create-attempt

Verification (ROOT_SHA256 comes from the separately retained create receipt):

    python3 archive.py verify --archive /external/new-package --root-sha256 ROOT_SHA256 --attempt /external/new-verify-attempt

Restoration into an absent external directory:

    python3 archive.py restore --archive /external/new-package --root-sha256 ROOT_SHA256 --destination /external/new-restored-runs --attempt /external/new-restore-attempt

Creation/restoration build a fresh hidden sibling stage beside the destination; START/RESULT record its path. Restoration verifies the whole package, copies every file with bounded reads, applies original modes, independently inventories the new tree, verifies the package again and checks unchanged staged metadata before a same-parent no-replace rename. This preserves readonly root modes through publication. Failed sibling stages remain retained at their recorded locations. The restored inventory remains in the attempt directory. The historical source path is provenance only and is not opened. No original/common store is needed; copy the entire package with ordinary independent file copies and preserve the expected ROOT digest to restore elsewhere. Do not use hardlinks to copy a package.

A completed scientific or resource run must write all original outputs and finalize every receipt before archival begins. Archive wall/CPU/RSS, verification reads and additional disk footprint belong to separate retention accounting. Original data is never deleted. `RESULT.json` with PASS is required for a completed operation; a package marker alone does not complete an interrupted create/restore. A failed attempt must be reviewed and reverified explicitly, without automatic retry.

Per-operation counters include START, successful metadata writes, partial writes with known return counts, oracle source reads and restored-inventory bytes. RESULT.json cannot meter its own final write/fsync/time; the parent records those through its encompassing wall clock and complete footprint. If RESULT writing fails during another failure, the original failure remains primary and the unclosed attempt is retained.
