# Final 18-factor composition review

The final changed word SHA-256 is `afd6333e2613a373c1078653d62667ae44b40b8ccfd9c548858b499377401f6c`. Direct comparison against pinned PR470 confirms that B remains the only changed field. Every helper start/final frame and every geometry, ret, scatter, D, A and C field is identical. Consequently the sufficient whole-hosting substitution argument in SCHUR-COMPOSITION-REVIEW.md applies unchanged. The second rewrite is sequential, not asserted disjoint from the first 17.

Final local profile:

    {1:2393,2:1069,3:225,4:299,5:87,6:75,8:9}.

Total local delta from PR470:

    {1:-10,2:-1,3:-3,4:-18,5:15,6:3}.

The additional layer contributes `1 + 5^p - 2^p - 4^p < 0` for every 0<p<1. Indeed, strict decrease of the derivative of x^p gives `5^p-4^p < 2^p-1`; this is precisely the required inequality. Adding it to the previously proved strictly negative moment proves strict improvement over both the 17-factor word and the public baseline over the entire relevant exponent interval.

The exact 88-call global profile is

    {1:210840,2:97761,3:19800,4:29701,5:7656,
     6:8632,7:4320,8:792,50:1,56:612}.

Rank mass745536 and deficit3264 are unchanged. Source hashes and the independent structural/profile comparison are recorded in FINAL18-COMPOSITION-REVIEW.json. This review does not replace the changed-program native replay, prefix/coefficient growth invoice or outer47-constraint assembly. No additional hosting search was performed.
