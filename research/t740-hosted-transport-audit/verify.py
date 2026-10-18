"""Run the independent literal-row transport audit. Nick Petalas, Apache-2.0."""

import json

from audit import audit, require
from sources import PACKAGE, load


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def verify(data):
    observed = audit(data)
    expected = {key: data["reference"][key] for key in observed}
    require(canonical(observed) == canonical(expected), "independent transport receipt")
    return {
        "status": "PASS_INDEPENDENT_T740_HOSTED_TRANSPORT",
        "method": "reverse last-touch barriers; exact ten-copy journal reconstruction",
        **observed,
    }


def main():
    result = verify(load())
    expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
    require(canonical(result) == canonical(expected), "committed audit receipt")
    print(
        json.dumps(
            {
                key: result[key]
                for key in ("status", "contexts", "hosted_rows", "journal_edits")
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
