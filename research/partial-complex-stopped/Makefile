.PHONY: verify verify-sources
.DEFAULT_GOAL := verify

verify:
	python3 verify_package.py

# Both external checkouts are immutable, source-hashed predecessor snapshots.
verify-sources: verify
	python3 rebuild_bit.py --source-root "$(SWAPNIL_SOURCE)"
	python3 schedule/verify.py --source-root "$(PR104_SOURCE)" --assembly-inputs inputs
