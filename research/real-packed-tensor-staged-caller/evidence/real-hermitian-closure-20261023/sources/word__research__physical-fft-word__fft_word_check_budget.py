"""Exact finite controls for the all-size word and Gaussian arithmetic bills."""
from fractions import Fraction
import importlib.util
from fft_word_sources import active, require


def run():
    cases = 0
    for n in range(3, 8193):
        b = (n-1).bit_length()
        q = (n+b-1)//b
        ell = (2*q-1).bit_length()
        r, p = 1 << ell, 2*b+ell
        require(2*q <= r < 4*q and 2*q-2 < r and r*b >= 2*n, "complete padded digit geometry")
        require(q*((1 << b)-1)**2 < 1 << (p-1), "strict real coefficient headroom")
        require(r*(p+2) <= 40*n, "linear complete packet volume")
        require(r*(ell+1)*p*p <= 256*n*b*b, "FFT arithmetic inside n log-squared allowance")
        require(r*p**3 <= 512*n*b*b and p**3 <= 64*n*b*b, "unamortized twiddle and metadata setup")
        cases += 1
    path = active().ring_package / "ring_check_budget.py"
    spec = importlib.util.spec_from_file_location("fft_word_inherited_budget", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = module.run()
    phi = Fraction(source["fourier_power"])
    epsilon, rho, delta = Fraction(997, 1000), Fraction(2, 1000), Fraction(1, 10000)
    old_power = Fraction(8, 5)-rho
    gaussian_arithmetic = max(epsilon+delta, 1-rho+delta)
    require(old_power > phi and gaussian_arithmetic == Fraction(9981, 10000) < phi,
            "changed Gaussian scalar arithmetic feasibility")
    require(phi-gaussian_arithmetic == Fraction(17619697, 100000000000), "strict arithmetic margin")
    return {"finite_geometry_cases": cases, "packet_bound": "r*(p0+2)<=40*n",
            "full_word_time": "O(n*log2(n+2)^2)", "word_space": "O(n)",
            "old_gaussian_power": str(old_power), "new_gaussian_arithmetic_power": str(gaussian_arithmetic),
            "fourier_power": str(phi), "arithmetic_gap": str(phi-gaussian_arithmetic),
            "scope": "PROOF.md supplies the universal argument; Gaussian coefficient, layout and restoration work remains separate."}
