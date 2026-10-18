from scan import run,need,HERE
import json
if __name__ == "__main__":
    need(json.loads(json.dumps(run()))==json.loads((HERE/"CERTIFICATE.json").read_text()),"complete certificate")
    print("PASS_RANK6_REPRESENTATIVES")
