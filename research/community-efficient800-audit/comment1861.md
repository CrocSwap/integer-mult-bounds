Review found a cache-dependent validation regression in `binary_phase_frames.basis` at head `54d7f5fd4ef6073b6399d1e6e73773f61fe4360a`:

```python
_basis_cached.cache_clear()
basis((1,))       # warms the cache
basis((1.0,))     # now returns (1,), bypassing the integer assertion
```

The baseline rejects `(1.0,)`, and your optimized implementation also rejects it with an empty cache. Validation inside the memoized function is skipped because these tuple keys compare equal. Please validate row types before lookup (or preserve element types in the key), add a warm-cache regression control, and refresh the affected source pins. Integer-input receipt equivalence remains useful; this hold concerns preserving verifier rejection behavior.
