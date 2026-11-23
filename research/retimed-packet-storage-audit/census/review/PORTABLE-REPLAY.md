# Location adapter for the frozen owner reviewer

The original independent checker is preserved unchanged as `review_check.py`,
SHA256 `9f585184774697db158efa313fe963f7cc2111d5fcf0dacf46d4f2ebedeac0ca`.
Its historical receipts and cross-review remain unchanged. Its original
workspace constants are not portable on their own.

`replay.py` authenticates those exact bytes, imports the checker without
executing its command-line guard, and replaces exactly three location globals:

| Global | Portable value | Purpose |
|---|---|---|
| `AUTHOR` | Parent directory of this review | Read this package's owner proof and source bindings |
| `RUNTIME` | Explicit `--runtime` | Read the freshly restored exact #8042 runtime |
| `HERE` | Explicit `--output` | Write receipts and temporary bootstrap data outside the committed package |

It then calls the unchanged `main()`. No theorem, constant, source pin,
comparison, finite domain, negative control or assertion is altered.
`BASE` is only used to initialize the replaced original locations; it has
no later mathematical use. The checker continues to record its unchanged
source hash and require the exact original owner-proof hash.

The completion review inspected every use of these globals before accepting
the adapter. A fresh offline restoration and all unchanged checks were run
through this wrapper. The enclosing `verify_supplements.py` executes that
portable route and requires the precise successful result marker.

```sh
python3 -B census/review/replay.py --runtime RESTORED_RUNTIME --output REVIEW_OUTPUT
```

Use the enclosing supplement driver for restoration without any preexisting
workspace. Its temporary byte-package copy also prevents the author byte
driver from overwriting committed evidence. The replay is verification, not
permission to change the selected result or its five retained assumptions.
