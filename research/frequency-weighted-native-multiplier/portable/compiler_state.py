"""Extract and bind the fields used by both physical native suppliers."""

from types import SimpleNamespace


def construct():
    from upstream import install

    install()
    from grades import numerical_recipe, numerical_source
    from installations import PROFILES
    from mixed_caller import instructions
    from raw_binary_stage import binary_recipe, binary_word
    from strong_binary import caller, fixed_binary_charts, graph

    layers = tuple(
        tuple(binary_recipe(h) for h in profile.rank_logs)
        + (numerical_recipe(profile.complex_log),)
        for profile in PROFILES.values()
    )
    atlas, *values = numerical_source()
    fields = vars(atlas).copy()
    iterator = fields.pop("instructions")
    closure = dict(
        zip(
            iterator.__code__.co_freevars,
            (cell.cell_contents for cell in iterator.__closure__),
            strict=True,
        )
    )
    assert closure.keys() == {"binds", "instructions", "offsets", "roots", "words"}
    assert closure["instructions"] is instructions
    for key in ("offsets", "roots", "words"):
        assert closure[key] is fields[key]
    return (
        layers,
        binary_word(),
        graph(),
        caller(),
        fixed_binary_charts(),
        fields,
        closure["binds"],
        values,
    )


def bind(fields):
    from mixed_caller import instructions

    layers, binary, graph, caller, charts, values, binds, rest = fields
    atlas = SimpleNamespace(**values)
    atlas.instructions = lambda: instructions(
        atlas.words, atlas.roots, binds, atlas.offsets
    )
    return layers, binary, graph, caller, charts, (atlas, *rest)
