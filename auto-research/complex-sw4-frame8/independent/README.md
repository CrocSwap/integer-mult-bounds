# Independent checks

`audit_local.py` is PR664's unchanged generator-free exact scalar/frame/cone checker. `price_profile.py` is its unchanged two-engine and 47-constraint outer cross-check. The portable driver runs both on the final SW4 word with eight B-frame coalescences and its strict global profile.

The independent literal-owner, actual-native-width and rational-moment checker is `../extras/check_owner_map.py`. It explicitly checks 504 helpers and 36,288 complete roles against the inherited geometry. It imports neither the constructor nor the two moment engines. `../extras/replay_owner_map.py` reconstructs the owner map from the integer certificate and tests nine mutations.

Original upstream review reports and numerical claims remain in the retained provenance files. This witness's fresh outputs are written to the requested output directory and collected in the companion validation package.
