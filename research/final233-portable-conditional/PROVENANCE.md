# Source and packaging

The retained scientific Python files under src/ are byte-identical copies of the earlier candidate-specific portable package. DATA-MANIFEST.json records every materialized input's original path, byte count and SHA-256. Identical data bytes are stored once. The #7334 archive is sourced externally at its pinned public commit and checked before materialization.

This package changes the packaging and entry point. It does not change upstream scientific engines or relax their checks. The earlier untrimmed artifact is retained outside this submission. Historical execution receipts remain author evidence; they are not reruns of this compact wrapper. Attribution and inherited license obligations are retained in NOTICE, LICENSE and the materialized source files.
