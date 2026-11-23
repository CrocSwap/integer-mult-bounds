"""Exact raw-H format adapter for a supplied normalized native layer.

Prepared for Jerry Chen / @CubeJerry with OpenAI assistance. Apache-2.0.
This diagnostic implements the format boundary, not the native layer itself.
Python allocation and optional domain validation are not physical tape costs.
"""
from dataclasses import dataclass
from typing import Callable, Sequence

Word = tuple[int, int]
NativeLayer = Callable[[list[Word], int, tuple[int, ...]], list[Word]]


@dataclass(frozen=True)
class Format:
    external_bits: int
    magnitude_exponent: int
    selected_bits: int

    def __post_init__(self):
        if any(type(x) is not int for x in (
                self.external_bits, self.magnitude_exponent, self.selected_bits)):
            raise ValueError("Integer format parameters are required")
        if self.external_bits < 1 or self.magnitude_exponent < 0 or self.selected_bits < 1:
            raise ValueError("Require P>=1, E>=0 and h>=1")

    @property
    def radius_shift(self):
        return self.magnitude_exponent+1

    @property
    def requested_bits(self):
        return self.external_bits+self.radius_shift+self.selected_bits

    @property
    def entrance_component_bits(self):
        return self.requested_bits+2

    @property
    def returned_raw_component_bits(self):
        return self.external_bits+self.magnitude_exponent+self.selected_bits+2

    @property
    def conditional_private_fractional_bits(self):
        return self.requested_bits+self.selected_bits

    @property
    def conditional_private_component_bits(self):
        return self.requested_bits+2*self.selected_bits+4

    @property
    def conditional_private_temporary_bits(self):
        return self.conditional_private_component_bits+26


def validate_strides(length: int, strides: tuple[int, ...]) -> None:
    if type(length) is not int or length < 2 or length & (length-1):
        raise ValueError("Require a complete power-of-two field")
    if not strides or len(set(strides)) != len(strides):
        raise ValueError("Require distinct selected strides")
    if any(type(s) is not int or s < 1 or s & (s-1) or 2*s > length for s in strides):
        raise ValueError("Each stride must select an actual address bit")


def validate_domain(field: Sequence[Word], fmt: Format) -> None:
    """Unpriced diagnostic check; the reference theorem supplies this premise."""
    radius_squared = 1 << (2*(fmt.external_bits+fmt.magnitude_exponent))
    for a, b in field:
        if type(a) is not int or type(b) is not int or a*a+b*b > radius_squared:
            raise ValueError("The complete field exceeds the radius contract")


def finish_c_endpoint(field: Sequence[Word], selected_bits: int) -> list[Word]:
    """Normalize a completed S_h C_h S_h endpoint on the private Q+h grid.

    This exact terminal macro requires the endpoint's divisibility/parity.
    Arbitrary values on the private grid are not admissible. Source credit:
    compiled-root-clifford-precision's 05-layers numerical wrapper.
    """
    if type(selected_bits) is not int or selected_bits < 1:
        raise ValueError("Require a positive selected width")
    k = selected_bits//2
    scale = 1 << k
    result = []
    for a, b in field:
        if a % scale or b % scale:
            raise ValueError("The C endpoint lacks its exact normalization divisor")
        a, b = a//scale, b//scale
        a, b = ((a, b), (b, -a), (-a, -b), (-b, a))[k % 4]
        if selected_bits % 2:
            real, imag = a+b, b-a
            if real % 2 or imag % 2:
                raise ValueError("The completed odd C endpoint lacks parity")
            a, b = real//2, imag//2
        result.append((a, b))
    return result


def adapt_raw_h(field: Sequence[Word], external_bits: int, magnitude_exponent: int,
                strides: tuple[int, ...], native: NativeLayer, *, check_domain=False) -> list[Word]:
    """Use a supplied exact-then-truncated H0 service and return raw-H integers.

    The service must compute Q_Q(H0) on the complete field and selected strides,
    retaining spectators. Its final truncation is toward zero componentwise.
    Its realization and resource bounds remain explicit external premises.
    """
    validate_strides(len(field), strides)
    fmt = Format(external_bits, magnitude_exponent, len(strides))
    if check_domain:
        validate_domain(field, fmt)
    lifted = [(a << fmt.selected_bits, b << fmt.selected_bits) for a, b in field]
    returned = native(lifted, fmt.requested_bits, strides)
    if len(returned) != len(field):
        raise ValueError("The supplied native service changed the complete field")
    # Rescaling by 2**(R+h) is exactly the Q -> P denominator-label change.
    # A second post-return integer shift would be incorrect.
    return returned
