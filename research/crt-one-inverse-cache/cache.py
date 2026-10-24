"""One-inversion setup for the fixed locally scaled CRT cache of PR4716."""

from dataclasses import dataclass
from math import prod
from typing import Callable


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def inverse_mod(value: int, modulus: int) -> int:
    return pow(value, -1, modulus)


@dataclass(frozen=True)
class Cache:
    moduli: tuple[int, ...]
    target: int
    product: int
    full_modulus: int
    unit: int
    unit_inverse: int
    coefficients: tuple[int, ...]
    weights: tuple[int, ...]
    target_inverse: int

    def evaluate(self, residues: tuple[int, ...]) -> tuple[bool, int, int]:
        """Evaluate the current vector; invalid padded coordinates disable it."""
        require(type(residues) is tuple and len(residues) == len(self.moduli),
                "one current residue per left modulus is required")
        require(all(type(value) is int and value >= 0 for value in residues),
                "current residues must be nonnegative integers")
        if any(value >= modulus for value, modulus in zip(residues, self.moduli)):
            return False, 0, 0
        integer = sum(value * weight for value, weight in zip(residues, self.weights))
        integer %= self.product
        return True, integer, integer * self.target_inverse % self.target


def prepare(moduli: tuple[int, ...], target: int, right_prefix: int = 1,
            inverse: Callable[[int, int], int] = inverse_mod) -> Cache:
    """Use one provider call, modulo target * product(moduli).

    The provider receives canonical arguments and must return a canonical
    inverse. One modular identity authenticates its result and simultaneously
    rejects noncoprime fixed data. No address or payload enters setup.
    """
    require(type(moduli) is tuple and len(moduli) >= 1,
            "a nonempty tuple of left moduli is required")
    require(all(type(value) is int and value >= 2 for value in moduli),
            "left moduli must be integers at least two")
    require(type(target) is int and target >= 2, "target must be at least two")
    require(type(right_prefix) is int and right_prefix >= 1,
            "right prefix must be a positive integer")
    require(callable(inverse), "inverse provider must be callable")
    product = prod(moduli)
    full_modulus = product * target
    cofactors = tuple(product // modulus for modulus in moduli)
    cofactor_sum = sum(cofactors) % product
    target_residue = (product % target) * (right_prefix % target) % target
    unit = (target * cofactor_sum + product * target_residue) % full_modulus
    unit_inverse = inverse(unit, full_modulus)
    require(type(unit_inverse) is int and 0 <= unit_inverse < full_modulus,
            "provider must return a canonical integer inverse")
    require(unit * unit_inverse % full_modulus == 1, "invalid inverse or fixed data")
    common = target * unit_inverse % product
    coefficients = tuple(common % modulus for modulus in moduli)
    target_inverse = product * (unit_inverse % target) % target
    weights = []
    prefix = 1
    for modulus, cofactor, coefficient in zip(moduli, cofactors, coefficients):
        require(cofactor * coefficient % modulus == 1, "cofactor inverse failed")
        weights.append(prefix * cofactor * coefficient % product)
        prefix *= modulus
    require(target_residue * target_inverse % target == 1,
            "target inverse failed")
    return Cache(moduli, target, product, full_modulus, unit, unit_inverse,
                 coefficients, tuple(weights), target_inverse)
