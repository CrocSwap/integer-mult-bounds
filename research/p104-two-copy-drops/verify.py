from two_drops import run,need,HERE
import json
if __name__ == "__main__":
    need(run()==json.loads((HERE/"CERTIFICATE.json").read_text()),"complete certificate")
    print("PASS_P104_TWO_TERM_DROP")
