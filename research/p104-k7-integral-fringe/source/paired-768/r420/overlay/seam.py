"""Update the frozen Round 415 stage controls for the sharper period price."""

from hashlib import sha256
from pathlib import Path

SOURCE_SHA256 = "57a4f8807833a512760466dcb18a477a9d04112af4e1cf945ac0efd88a330662"


def patch_stage_checks(peer: Path) -> None:
    path = peer / "check_stage_seam.py"
    original = path.read_bytes()
    if sha256(original).hexdigest() != SOURCE_SHA256:
        raise ValueError("The exact Round 415 prepared stage checker is required")

    replacements = (
        (
            "    GAUSSIAN=Q(1039776,2**23)    # five-shortcut word debit",
            """    PRIOR_GAUSSIAN=Q(1039776,2**23)
    GAUSSIAN=Q(1039701,2**23)  # sharper four-aligned period bound
    PRIOR_KAPPA=Q(".003900857269150")""",
        ),
        (
            '    assert TERMINAL.kappa==Q(".003900857269150")',
            '    assert TERMINAL.kappa==Q(".003900857312000")',
        ),
        (
            """    def gaussian_upper(h):
        return GAUSSIAN_C-GAUSSIAN/h""",
            """    def gaussian_upper(h,debit=GAUSSIAN):
        return GAUSSIAN_C-debit/h""",
        ),
        (
            """    assert TERMINAL.kappa>old_crossing
    assert TERMINAL.kappa+GRID>=gaussian_upper(TERMINAL.complex_log)-5*STOP""",
            """    assert TERMINAL.kappa>old_crossing
    prior_positive_crossing=gaussian_upper(TERMINAL.complex_log,PRIOR_GAUSSIAN)-5*STOP
    assert PRIOR_KAPPA<prior_positive_crossing<=PRIOR_KAPPA+GRID
    assert TERMINAL.kappa>prior_positive_crossing
    assert TERMINAL.kappa+GRID>=gaussian_upper(TERMINAL.complex_log)-5*STOP""",
        ),
        (
            """    def require_funding(proposed,gaussian,*,debit=ORDINARY,kappa=TERMINAL.kappa):
        threshold=kappa+5*STOP
        if ordinary_upper(proposed,debit)<=threshold or gaussian_upper(gaussian)<=threshold:""",
            """    def require_funding(proposed,gaussian,*,debit=ORDINARY,kappa=TERMINAL.kappa,gaussian_debit=GAUSSIAN):
        threshold=kappa+5*STOP
        if ordinary_upper(proposed,debit)<=threshold or gaussian_upper(gaussian,gaussian_debit)<=threshold:""",
        ),
        (
            "        require_funding(proposed,gaussian,debit=OLD_ORDINARY,kappa=OLD_KAPPA)",
            """        require_funding(proposed,gaussian,debit=OLD_ORDINARY,kappa=OLD_KAPPA,
                        gaussian_debit=PRIOR_GAUSSIAN)""",
        ),
        (
            """        rejected(lambda:require_funding(ranks,TERMINAL.complex_log-1),"gaussian-height-minus-one"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,kappa=TERMINAL.kappa+GRID),""",
            """        rejected(lambda:require_funding(ranks,TERMINAL.complex_log-1),"gaussian-height-minus-one"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,gaussian_debit=PRIOR_GAUSSIAN),
                 "prior-gaussian-debit-at-new-rate"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,kappa=TERMINAL.kappa+GRID),""",
        ),
    )
    source = original.decode("utf-8")
    for before, after in replacements:
        if source.count(before) != 1:
            raise ValueError("A stage-check source anchor was missing or repeated")
        source = source.replace(before, after, 1)
    compile(source, str(path), "exec")
    path.write_text(source, encoding="utf-8")
