# Activate focused CI

Copy `supplier-circuit-consolidation.yml` into `.github/workflows/` in a
workflow-authorized commit. It defines two local Python versions and one full
Linux hosted/native job. No secrets, write permissions or automatic merge are
required. It follows the repository's existing pinned checkout/setup actions.

The current connected GitHub OAuth token rejected an active-workflow push
because it lacks `workflow` scope. This template preserves a concrete CI setup
without requesting broader account access. Local native/hosted, relocation,
component, selected cold and binding checks passed; remote CI is not claimed.
