"""Acquire both pinned predecessor data and new inert selections/notices."""
from pathlib import Path
import argparse,subprocess,sys,urllib.request
import companion as packet

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--new-from',type=Path);parser.add_argument('--base-from',type=Path);args=parser.parse_args()
    packet.verify_base_code()
    command=[sys.executable,str(packet.BASE_CODE/'acquire_inputs.py')]
    if args.base_from:command+=['--from-dir',str(args.base_from)]
    subprocess.run(command,env=packet.child_env(),check=True)
    for row in packet.source_pins()['files']:
        dest=packet.INPUTS/row['label']
        if dest.exists():raw=dest.read_bytes()
        elif args.new_from:raw=(args.new_from/row['label']).read_bytes()
        else:
            with urllib.request.urlopen(row['url'],timeout=60)as response:raw=response.read()
        packet.check_source_bytes(raw,row);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    packet.verify_sources();print('Verified predecessor source data and all new inert selection/provenance files.')
if __name__=='__main__':main()
