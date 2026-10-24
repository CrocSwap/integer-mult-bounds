"""Exact finite controls for the quantified proof and complete online invoice."""
from fractions import Fraction as Q
import importlib.util
from gaussian_sources import active, require


def run():
    exponential_cases = 0
    for P in range(1, 129):
        for F in range(1, 33):
            X = 4*F
            k = (8*(X+1)-1).bit_length()
            H = P+X+k+16
            c = (H-1).bit_length()
            R = P+4*X+4*k+2*c+64
            J, N = (R+3)//4+8, (R+2)//3+8
            require(R >= 115 and R < 5*H and 2*N <= R, "Gaussian range/Taylor parameter bounds")
            require(20*J+40 <= 7*R and Q(7*R+65, 32) <= Q(R, 4), "directed angle-width allowance")
            require(R*R+2 <= 32*H*H and 3*N >= R+24 and 4*J >= R+32,
                    "complete tails and squaring-width constants")
            require(k+2*X+7+2*c-R <= -P-2*X-3*k-57,
                    "strict absolute exponential interval margin")
            exponential_cases += 1
    guard_cases = 0
    for p in range(101, 4097):
        logarithm = (p+1).bit_length()
        G = 8*p+8*logarithm+32
        require(max(8*p+18+2*logarithm, 18+4*logarithm, 17+3*logarithm) <= G-12,
                "complete local/boundary stored-value guard")
        require(32768*p >= 8*p+2 and 32*p < 1 << (16*p), "weight positivity and locality margin")
        guard_cases += 1
    slot_cases = 0
    for n in range(1, 18):
        for a in range(1, 9):
            for b in range(1, 9):
                slot = a+b+(n-1).bit_length()+1
                bound = n*((1 << a)-1)*((1 << b)-1)
                require(bound < 1 << (slot-1) and 4*bound < 1 << (slot+2),
                        "strict four-product packing and signed accumulator headroom")
                slot_cases += 1
    path = active().ring_package / "ring_check_budget.py"
    spec = importlib.util.spec_from_file_location("gaussian_inherited_fourier_budget", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inherited = module.run()
    phi = Q(inherited["fourier_power"])
    epsilon, rho, delta = Q(997, 1000), Q(2, 1000), Q(1, 10000)
    arithmetic = max(epsilon+delta, 1-rho+delta)
    require(arithmetic == Q(9981, 10000) and phi-arithmetic == Q(17619697, 100000000000),
            "complete structured Gaussian arithmetic fits inherited Fourier allowance")
    return {"exponential_cases": exponential_cases, "guard_cases": guard_cases, "slot_cases": slot_cases,
            "online_word_calls": "20*n_interior+16*w^2*n_long_cells+2*n_boundary*(4*w+1)+2*m+2*n_target+2*n_core+32*n_long_cells",
            "online_time": "O((m+m*w^2/d+w^2)*p*log2(p+2)^2)",
            "online_space": "O((m+m*w^2/d+w^2)*p)", "setup": "polynomial(t,p), explicitly charged for an isolated window",
            "arithmetic_power": str(arithmetic), "fourier_power": str(phi), "gap": str(phi-arithmetic),
            "scope": "finite controls only; PROOF.md supplies quantified arguments and inherited premises"}
