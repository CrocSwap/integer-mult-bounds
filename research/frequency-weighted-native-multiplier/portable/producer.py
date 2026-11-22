"""Generate both finite native profiles and emit their fixed directory."""

import sys
from pathlib import Path

from compiler_state import construct
from source_image import write_image


def run():
    write_image("/sources", "/machine", "/weighted")
    sys.path.insert(0, "/machine")
    from tape_directory import dump

    state = construct()
    assert [[recipe.rank_log for recipe in layer] for layer in state[0]] == [
        [3000, 3080, 1024],
        [35327, 559011, 542350],
    ]
    with Path("/tmp/compiled.dag").open("wb") as dest:
        print("directory_records", dump(dest, state), flush=True)
