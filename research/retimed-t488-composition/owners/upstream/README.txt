T488 combines the retained T37, T8, and T16 source chronologies, in that order, with eight copies and the authenticated staged provider.
Finite verification: OWNER_SOURCE_REPO=REPO python3 -I -B verify_owner.py --price-dir PARENT_PACKAGE
Optional deterministic literal reconstruction: OWNER_SOURCE_REPO=REPO python3 -I -B portable_expand.py --out FRESH_DIR
Independent literal audit requires OWNER_SOURCE_REPO, OWNER_LITERAL_DIR, OWNER_NATIVE_DIR (checked-base and checked-extra canonical tables), and OWNER_AUDIT_OUTPUT.
The finite verifier calls the parent exact price checker on the reconstructed profile. Neither finite verification nor stored owner evidence is full admission. No optimization is used.
T8 and T16 original Git provenance is retained in their PROVENANCE files; T37 source construction is authenticated by SOURCE-PINS and the source context.
