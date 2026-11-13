# Candidate endpoint-bounded width bridge for the literal C leaf

Status: root derivation plus finite corroboration; not yet independently reviewed.
Pin: Nick Petalas, CrocSwap/integer-mult-bounds#7468, head
8b0dd714d30e9c1574387587eb6418ae99ac34e1. Its sharp integral scale is credited
input. The C component row norms are known (#7211 and credited
#2772/#3089/#3091 lineage). The joint two-endpoint consequence and physical
application are investigated here, not the standalone known norm.

Write C=[[1+i,1-i],[1-i,1+i]]/2, F=C^(tensor f), and let |x|_c be the
largest absolute real or imaginary component. Suppose x and Fx are Gaussian
integral and |x|_c,|Fx|_c <= M. For any subset S of j axes, d=min(j,f-j),

    |C_S x|_c <= 2^ceil(d/2) M.

Proof: every coefficient of C^(tensor j) is a Gaussian unit times
(1+i)^j/2^j. For j=2t, each real output uses 2^j input real/imaginary
components with coefficient magnitude 2^-t. For j=2t+1, each uses 2*2^j
components with coefficient magnitude 2^-(t+1). The induced component norms
are 2^t and 2^(t+1); the inverse has the same norm. Apply the first bound to
x and the second to C_(S-complement)^(-1) Fx, and take the minimum.

Sharpness: choose d axes in S and d outside S. On those 2d axes put
z=2^ceil(d/2) times the all-zero-address impulse. On every other axis use
the tensor factor u=(1,1). Put x=C_S^(-1)z, y=C_(S-complement)z. The
nonzero components of x,y are Gaussian units for even d, and Gaussian
integers whose real/imaginary components are each +/-1 for odd d. Hence
both endpoints are integral with component norm one, Fx=y, and prefix z
attains the bound. Scale by integer M to attain it at M.

Put k=ceil(floor(f/2)/2)=floor((f+2)/4). Credited #7468 proves that
2^k C_S x is integral for every S. The bound above gives maximum scaled
component <=2^(2k) M, attained by a middle-cut witness. For symmetric
signed-w endpoint range [-(2^(w-1)-1),2^(w-1)-1], w>=2, every scaled
prefix fits symmetric signed width w+2k. This width is sharp uniformly:
choose the middle-cut witness with M=2^(w-1)-1; one fewer signed bit
cannot hold 2^(2k)M. Literal kernel numerator storage remains separate.

Monomial permutations and unit Gaussian phases preserve this norm and
integrality. The endpoint promise therefore passes through the selected
MOVE monomial factors. This does not implement scaling, widened headers,
layout conversion, exact unscaling or owner commit: that is the next task.
No recursive f^sigma tariff, selected caller admission, global assumption
discharge or new kappa is asserted. Direct leaf cost remains O(f V).
