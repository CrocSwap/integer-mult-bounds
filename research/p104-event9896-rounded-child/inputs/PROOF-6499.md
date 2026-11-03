# Scalar grid

Use units h for each physical real component. Each public entrance and each completed native return is an integer in these units. Assign a fresh formal integer atom to each such return. A MOVE replaces its destination's grid row by this fresh atom. INIT and CLEAR set their rows to zero. COPY, SCALE and ADD act on the exact rational rows with their literal coefficients. This model permits every possible returned grid value and therefore covers the actual native outputs.

The checker computes all changed rows. Every coefficient denominator divides 32. A second interpreter stores integer coefficient rows in units 1/32 and checks every division before it is performed. Both rows agree at every event. The explicit row with denominator 32 gives a scalar basis assignment for which the four-bit grid fails. This is sharp only when the native grid returns are independent.

Induction now proves records.py. Initially each record is 32 times its input integer. Each native return has the same form. At each scalar instruction, its exact source multiple is on the fine grid: for an ADD this follows because both the old and new destination are on that grid, and their difference is the source multiple. The integer division therefore has no remainder. COPY and SCALE satisfy the same assertion directly. No scalar round occurs.

# Complete error and range

Retain the source unitary native charts and common-frame scalar semantics. Conjugate each physical native defect into the common chart. This preserves its Hilbert norm. Give each initial quantization error and each completed native defect its own symbol. MOVE adds a fresh error symbol; it does not replace the prior error row. Scalar instructions act with their signed coefficients, and owned reset removes only its current row. Thus the exact error at each cut is a signed sum of these defects. The l1 row norm bounds its Hilbert norm by the triangle inequality.

The complete forward calculation gives prefix norm 2764 and final public norm 1323/2. A separate reverse calculation agrees on every final row. Initial-error coefficients at the endpoint are derived from the checked complete endpoint map, including the extra source term in each active target. No input quantization error is omitted.

There are 2^(n+1) real components per field. Nearest rounding on spacing h gives field error at most `h*2^((n-1)/2)`. With `h=B*2^-(t+10+floor(n/2))`, this is at most `B*2^-(t+10)` for every n>=0. Consequently the final error is at most `(1323/2048)*B*2^-t`. The complete prefix error is at most `(2764/1024)*B*2^-t`. The ideal norm is at most 850 B, so the sum is less than 1024 B for all t>=0.

This argument covers exact native maps followed by coordinate rounding. A numerical child must instead establish the same bound for its entire completed error, including its internal work. No such child is implemented here. Exact owned reset and COPY are retained operations; this proof does not turn destructive reset into reversible erasure.

# Finite records

Stored components are multiples of `B*2^-(p+5)` and have magnitude less than 1024 B. Their integer codes therefore have magnitude less than `2^(p+15)`, so p+16 signed bits suffice. All scalar numerators have absolute value at most 16 and denominators at most 16. A separate product temporary, exact division, and destination addition have magnitude below 32 times the stored bound. The conservative p+21 signed temporary width covers them.

The Python executor uses arbitrary-precision integers to check the specified fixed-width algorithm. The proof supplies a bound for valid numerical executions; the arbitrary-return algebra fixtures test exactness and do not claim that their unconstrained returns satisfy the numerical norm contract. A physical implementation still needs finite records, bit operations, addresses, caller conversion and cleanup charges. The checked source paid/target invoice is unchanged.
