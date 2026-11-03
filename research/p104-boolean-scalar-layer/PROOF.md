# Caller premises

Each record is a signed W-bit two's-complement integer, with 26<=W<=256. Each ADD source must be divisible by the coefficient denominator. Each SCALE by 2^-k requires k zero low bits. Each exact scalar endpoint has magnitude strictly below 2^(W-1). COPY has coefficient one and a zero owned destination. These are explicit premises, not conclusions from the Boolean gate count.

The source-bound checker proves all alignment premises with formal integer rows. Every public entrance and every fresh native output starts as 32 times its own atom. At each literal scalar event, every source coefficient divides exactly by the dyadic denominator. The complete changed-row stream is hashed. This proof covers arbitrary physical components on the declared coarse grid, since native outputs are allowed to be independent. The numerical range premise is the separate PR6499 contract; this package does not implement its native child.

# ADD and COPY

The unchanged PR3080 circuit preserves each source bit and returns all W-1 initially zero carry bits. It adds the declared signed sum of shifted source bits modulo 2^W. Exact source divisibility makes every right shift a signed exact division. Intermediate modular wrap is permitted; the signed final-range premise makes the modular result the unique exact integer endpoint. The source circuit's mathematical proof retains credit. Both signed-power and binary-power policies are generated and counted here.

COPY is W CNOTs from the source to a zero destination. Each output bit equals the source bit, and the source is unchanged. No carry or new constant register is needed.

# SCALE

A nonzero dyadic unit is +/-2^k. Rotate the target bits by k positions with a cycle decomposition. Each swap is exactly three CNOTs. For k>0, signed no-overflow implies that the high k bits moved into the low positions all equal the sign. XOR the retained sign into those low positions to clear them. The result is the exact left shift.

For k<0, source alignment gives zero low -k bits. XOR the sign into those low positions, then rotate right. These filled bits become the high sign-extension bits. The result is exact signed division. Both routines are literal reversible gates on all bit strings; their arithmetic interpretation uses the stated alignment and range domain.

For a negative coefficient, complement every target bit and add one modulo 2^W. The increment is the source adder specialized to the constant source value one. A zero constant control deletes a gate; a one control removes that control. The remaining gates use only target and carry wires. This proves zero constant backing and preserves clean carry return. The signed range premise gives exact negation. The independent bit-list interpreter checks the complete SCALE alphabet, including negative division and widths with different rotation cycles.

# Reset, storage and cost

The word has 31 INIT and 31 CLEAR events. Each is charged W bit reset requests. This is an explicit primitive boundary. This package does not prove that reset is reversible or implement it with a physical tape routine. In particular, it does not erase residual numerical error for free.

Every ADD and negative SCALE uses the same W-1 clean carry bank and returns it to zero before the next scalar operation. COPY and positive SCALE need no carry bank. Source and target records have no temporary arithmetic guard bits; modular intermediate arithmetic and the SCALE domain justify that statement. There is no constant data bank.

Gate counts come from the complete emitted templates and literal source occurrence counts. For complex dimension D, all scalar maps act independently on 2D real components, so counts multiply by 2D. Serial component execution can reuse one carry bank. This says nothing about its physical access cost or the separate native workspace. The compiler caps W at 256; arbitrary-width native/precision admission is not claimed. The source's recursive invoice and selected exponent are unchanged.
