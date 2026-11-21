"""Check every transform direction, the extent guards, CRT and the public caller."""

from hashlib import sha256
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from multiply import finite_product, fourier, multiply, receiver
from short_product import MODULI, native_product, reference_product, transform


def require(check, message):
    if not check:
        raise ArithmeticError(message)


def check(library=None):
    for (prime, g), factors in zip(MODULI, ((2, 3, 5), (2, 3)), strict=True):
        residual = prime-1
        for f in factors:
            while residual % f == 0:
                residual //= f
        require(residual == 1 and pow(g, prime-1, prime) == 1, "Order certificate")
        for f in factors:
            from math import gcd
            require(gcd(pow(g, (prime-1)//f, prime)-1, prime) == 1, "Lucas witness")
        rng = Random(prime)
        for power in range(7):
            n = 1 << power
            samples = [rng.randrange(prime) for _ in range(n)]
            w = pow(g, (prime-1)//n, prime)
            expected = [sum(x * pow(w, i*k, prime) for i,x in enumerate(samples)) % prime
                        for k in range(n)]
            actual = samples.copy()
            transform(actual, prime, g, False)
            for k,v in enumerate(expected):
                reverse = int(format(k, "0"+str(max(1,power))+"b")[::-1], 2)
                require(actual[reverse] == v, "Forward orientation")
            transform(actual, prime, g, True)
            require(actual == samples, "Inverse orientation")
    engine = native_product(library) if library else reference_product
    rng = Random(358021)
    count = 0
    for n in (0, 1, 2, 3, 4, 9, 16, 31, 32, 33, 67, 84, 129):
        for m in (0, 1, 2, 3, 7, 9, 32, 89):
            a, b = rng.randbytes(n), rng.randbytes(m)
            result = engine(a,b)
            expected = int.from_bytes(a,"little") * int.from_bytes(b,"little")
            require(len(result)==n+m and int.from_bytes(result,"little")==expected,
                    "Packed multiplication")
            count += 1
    calls = []
    def observed(a,b):
        calls.append((len(a), len(b)))
        return engine(a,b)
    for n in (192, 193, 4095, 4096, 4097, 12289, 32768):
        limit = (1 << n)-1
        for a,b in ((limit,limit), (limit,-rng.getrandbits(n+4)), (1,limit), (0,limit)):
            require(multiply(a,b,observed)==a*b, "Public signed product")
    a, b = rng.getrandbits(32768), rng.getrandbits(32671)
    before = len(calls)
    require(finite_product(a,b,observed,max_transform=1024)==a*b, "Blocked recursion")
    require(len(calls)>before+1, "Blocked recursion did not call the transform")
    # The retained direct Fourier sign, normalization, router and carry are exercised here.
    machine = receiver()((3,5), 8, 136, source_root=Path(__file__).resolve().parents[2])
    for opposite in (False, True):
        tokens = (list(range(32)) if opposite else
                  [(i*(1<<127)-19, -i*(1<<125)+7) for i in range(32)])
        require(machine.crt(tokens, opposite) == fourier().Multiplier.crt(machine, tokens, opposite),
                "A genuine or padded CRT coordinate moved to the wrong row")
    result, coefficients = machine.multiply(741503,466013)
    require(result==345550037539 and coefficients[:5]==[11811,10996,4152,868,77]
            and not any(coefficients[5:]), "Fourier regression")
    print("packed_cases", count, "observed_transforms", len(calls))
    print("fourier", result, coefficients[:5], "full_H_calls", machine.transform.h_calls)
    require(machine.row_stats["late_packets"] > 0 and machine.row_stats["crt_calls"] == 5,
            "The real multiplication did not use the ternary groups")
    print("real_crt_calls",machine.row_stats)
    print("PASS_GENERAL_PRODUCT")


if __name__ == "__main__":
    check(sys.argv[1] if len(sys.argv)>1 else None)
