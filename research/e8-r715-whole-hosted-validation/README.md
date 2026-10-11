# Validation receipts

Linux Python 3.12.3 completed the default full verifier, including a fresh complete replay of the corrected #458 chain. macOS Python 3.11.15 completed every new R715 component with an explicitly reused, freshly completed full #458 parent whose manifest and source hashes match. The parent receipt is retained. The macOS receipt deliberately reports parent reuse, not a fresh complete parent run.

The entire final RESULT.json, independent global audit and target-label audit are byte-identical across platforms. Both release receipts bind the unchanged 32-file package manifest and source inventory. The complete 327-file upstream package inventory was rechecked after both runs. Exact reconstruction receipts from both systems and the 16 passing repository joint tests are included.

Early component-wrapper attempts stopped on a filename mismatch, the Spark 2 Boost include path and macOS Bash 3 empty-array behavior. Those wrapper issues were fixed before the frozen release runs. No failed operator witness is treated as a passing receipt. GitHub CI is separate and is not claimed here.
