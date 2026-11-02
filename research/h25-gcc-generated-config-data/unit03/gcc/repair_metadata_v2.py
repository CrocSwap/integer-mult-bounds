"""Rebuild ar metadata from retained authenticated bytes; never decode again."""
import json
from datetime import datetime,timezone
from pathlib import Path
import configured_data_v1 as parse
import generated_config_v1 as generated

UNIT=Path(__file__).resolve().parents[1]
OUT=UNIT/"source-artifacts"
OLD_PAYLOAD_SHA="67e2d71f4affb83e458f226786e93361ec2cae3a3d19f9dd894d51d341ce61f7"
OLD_AR_SHA="1ea9badd67a4e768106c515d1cae504845df9d75bfd4b38a83c44bf282bbcfe3"


def write_new(path,value):
    if path.exists():raise parse.DataRefusal("refuse metadata repair overwrite")
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def main():
    raw=(OUT/generated.PACKAGE).read_bytes()
    if len(raw)!=1451870 or parse.digest(raw)!=generated.PACKAGE_SHA256:
        raise parse.DataRefusal("retained package identity changed")
    old_raw=(OUT/"PLUGIN-PAYLOAD-v1.json").read_bytes()
    old_ar_raw=(OUT/"PLUGIN-AR-MEMBERS-v1.json").read_bytes()
    if parse.digest(old_raw)!=OLD_PAYLOAD_SHA or parse.digest(old_ar_raw)!=OLD_AR_SHA:
        raise parse.DataRefusal("rejected report identity changed")
    old=json.loads(old_raw);old_ar=json.loads(old_ar_raw)
    old_identities={row["name"]:(row["bytes"],row["sha256"]) for row in old_ar}
    new=parse.strict_ar(raw)
    if [(row["offset"],row["data_offset"]) for row in new] != [(8,68),(72,132),(12374,12434)]:
        raise parse.DataRefusal("independently fixed actual package offsets differ")
    checked=[]
    for row in new:
        header=raw[row["offset"]:row["offset"]+60]
        body=raw[row["data_offset"]:row["data_offset"]+row["bytes"]]
        if header.hex()!=row["raw_header"] or header[58:]!=b"`\n":
            raise parse.DataRefusal("corrected header slice differs")
        identity=(len(body),parse.digest(body))
        if identity!=old_identities[row["name"]] or body!=row["data"]:
            raise parse.DataRefusal("corrected compressed slice identity differs")
        checked.append({"name":row["name"],"bytes":len(body),"sha256":parse.digest(body),
                        "offset":row["offset"],"data_offset":row["data_offset"],
                        "matches_preserved_v1_member_identity":True})
    for member in old["extracted_regular_members"]:
        path=Path(member["saved_path"])
        if path.is_symlink():raise parse.DataRefusal("retained regular header became alias")
        body=path.read_bytes()
        if len(body)!=member["bytes"] or parse.digest(body)!=member["sha256"]:
            raise parse.DataRefusal("retained member bytes changed")
    inventory=[{key:value for key,value in row.items() if key!="data"} for row in new]
    write_new(OUT/"PLUGIN-AR-MEMBERS-v2.json",inventory)
    repaired=dict(old)
    repaired["schema"]="unit03-plugin-payload-v2"
    repaired["metadata_repair"]={
        "observed_utc":datetime.now(timezone.utc).isoformat(),
        "rejected_v1_payload_report_sha256":OLD_PAYLOAD_SHA,"preserved_v1_ar_report_sha256":OLD_AR_SHA,
        "corrected_ar_inventory":inventory,"independent_compressed_slice_checks":checked,
        "package_sha256_unchanged":True,"regular_retained_member_hashes_rechecked":len(old["extracted_regular_members"]),
        "tar_inventory_disposition":"Carried forward unchanged from immutable v1 payload report and its decoder evidence; not decoded again and not a fresh decoding milestone",
        "fresh_tar_decoding":False,
        "rejected_code_defect":"strict_ar numeric-field loop shadowed header start; corrected with separate header_start and field_start/field_end",
        "generated_binding_defect":"caller supplied matching text could receive pinned-driver label; exact embedded and compiler-binding reports now independently pinned and label narrowed"}
    write_new(OUT/"PLUGIN-PAYLOAD-v2.json",repaired)
    frozen=UNIT.parent
    headers=generated.load_headers(OUT/"plugin-members")
    view=generated.construct_generated_config_view(headers,
        (frozen/"source-artifacts/gcc-13_13.3.0-6ubuntu2~24.04.1_amd64.changes").read_bytes(),
        (frozen/"source-artifacts/gcc-13_13.3.0-6ubuntu2~24.04.1_amd64.buildinfo").read_bytes(),
        (frozen/"evidence/EMBEDDED-CONFIGURATION-v1.json").read_bytes(),
        (frozen/"source-artifacts/BINARY-PACKAGE-CORRESPONDENCE-v1.json").read_bytes())
    write_new(UNIT/"gcc/GENERATED-CONFIGURATION-VIEW-v2.json",view)
    for name in ("PLUGIN-AR-MEMBERS-v2.json","PLUGIN-PAYLOAD-v2.json"):
        path=OUT/name;print(name,len(path.read_bytes()),parse.digest(path.read_bytes()))
    path=UNIT/"gcc/GENERATED-CONFIGURATION-VIEW-v2.json"
    print(path.name,len(path.read_bytes()),parse.digest(path.read_bytes()))


if __name__=="__main__":main()
