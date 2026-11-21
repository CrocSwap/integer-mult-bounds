"""Execute both signs on a rational Fourier column and a full signed product."""

from fractions import Fraction
from io import BytesIO
from math import prod
from multiplier import Product
from product_path import number, original_positions, put
from outer_schedule import first_mixing_layer


def main():
    # The diagnostic grid deliberately cannot satisfy the old sub-grid target.
    machine = Product((3, 5), 8, 72)
    denom = 1 << machine.P
    public = 1 << machine.p
    size = prod(machine.sides)
    cap = (4 * size * denom) ** 2
    true = list(original_positions(machine.sides, machine.widths))
    for sign in (False, True):
        data = BytesIO()
        for i in range(machine.total):
            put(data, (denom // 4 if i == 0 else 0, 0), machine.wide)
        machine.transform(data, opposite=sign)
        data.seek(0)
        errors = []
        for original in true:
            x, y = number(data, machine.wide), number(data, machine.wide)
            u = 4 * size * x - (denom if original else 0)
            v = 4 * size * y
            errors.append(u * u + v * v)
            if not original:
                assert abs(x) < 1 << (machine.P - machine.p)
                assert abs(y) < 1 << (machine.P - machine.p)
        worst = max(errors)
        assert 64 * public**2 * worst <= cap
        assert public**8 * worst > cap
        print(
            "opposite",
            sign,
            "grid",
            machine.P,
            "true plus hole outputs",
            len(errors),
            "exact squared error",
            str(Fraction(worst, cap)),
            "eighth-pass old-raw-fail",
            flush=True,
        )

    for k, bits in zip(machine.sides, machine.widths, strict=True):
        from product_path import fourier, SOURCES

        p = fourier()
        axis = p.fourier_axis(p.load_compiler(SOURCES), k, 1 << bits, -1, machine.P + 8)
        print(
            "true-side", k, "branching root and layer", first_mixing_layer(axis.layers), flush=True
        )
    value, coeffs = machine.multiply(-741503, 466013, coefficients=True)
    assert (
        value == -345550037539
        and coeffs[:5] == [11811, 10996, 4152, 868, 77]
        and not any(coeffs[5:])
    )
    print("signed product", value, "unsigned coefficients", coeffs[:5], flush=True)


if __name__ == "__main__":
    main()
