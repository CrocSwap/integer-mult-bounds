"""Check every complex output against the independent exact spectral transform."""

from check_periodic import ComplexMachine, spectral_quarters
from periodic import Job, Rule
from epoch_tape import Compiler as make_planner, run


def dense():
    n = 16
    rule = Rule(2, (2,), (1, 1))
    machine = ComplexMachine(rule, ((1, 1),))
    planner = make_planner(rule, 2)
    p = planner(n)
    assert p.forest and p.forest.layers
    lanes = [Job(i, tuple((k - i) % n for k in range(n))) for i in range(p.width)]
    for lane in lanes:
        machine.data[lane.owner] = machine.initial(lane.owner, n)
        machine.geometry[lane.owner] = n
    run(rule, n, lanes, machine, planner=planner)
    for i in range(p.width):
        real, imag, den = machine.data.pop(i)
        initial_a, initial_b, _ = machine.initial(i, n)
        expect_a, expect_b = spectral_quarters(initial_a, initial_b)
        assert den[0] >= n
        shift = den[0] - n
        assert all(x << shift == y for x, y in zip(expect_a, real, strict=True))
        assert all(x << shift == y for x, y in zip(expect_b, imag, strict=True))
    assert machine.frames > 0 and machine.leaves == p.leaves
    return n, p.width, machine.frames, p.width * (1 << n), machine.leaves


if __name__ == "__main__":
    print("dense Gaussian outputs against two WHTs", *dense())
