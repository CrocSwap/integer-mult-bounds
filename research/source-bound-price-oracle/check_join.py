"""Replay an immutable oracle join; no scientific engine execution."""
from pathlib import Path
import argparse
import json
import oracle as o


def check(path):
    c = (path/"candidate.json").read_bytes()
    p = o.decode((path/"policy.json").read_bytes())
    a = {item.name: item.read_bytes() for item in (path/"artifacts").iterdir() if item.is_file()}
    result = o.evaluate(c, a, p)
    expected = o.decode((path/"result.json").read_bytes())
    if result != expected:
        raise o.ContractError("ORACLE_JOIN_OUTPUT_CHANGED")
    return {"label": result["label"], "funded_kappa": result["funded_kappa"],
            "scientific_payload_sha256": result["scientific_payload_sha256"],
            "immutable_artifact_count": len(a)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    print(json.dumps(check(parser.parse_args().path), indent=2))
