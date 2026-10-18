# Selected verifier digest maintenance

The PR2531 portability correction made `LEAN.read_text()` explicitly UTF-8. The selected record also pinned that verifier as a proof supplement; integration initially left its old hash in place. This checkpoint refreshes **only that hash**. The selected rational kappa, certificate, frozen source inventory, other proof digests and inherited assumptions are unchanged.

The exact script diff is checked against the frozen batch baseline. In an isolated export of the complete selected package roots and supporting files, the old record fails on precisely this digest; the corrected record passes all selected source-inventory and proof bindings. The PR2531 CLI regression also passes its cp1252 and mutated-recipe controls. See `combined-selected-tool-pin.json` and its bound log. This is not another full supplier cold replay or a new theorem.

Credit ywz65 for PR2531 and its encoding regression. The stale-pin integration bookkeeping correction is the maintainer's. The earlier mismatch receipt remains as historical evidence of the detected failure.
