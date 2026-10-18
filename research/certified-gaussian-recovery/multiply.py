#!/usr/bin/env python3
"""Run the certified Gaussian caller on two integers (decimal or 0x hexadecimal)."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from gaussian import GaussianLine
from pipeline import multiply,uniform_certificate
from intervals import need


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('left',type=lambda x:int(x,0))
    parser.add_argument('right',type=lambda x:int(x,0))
    parser.add_argument('--input-bits',type=int,help='declared input width, including leading zeros')
    args=parser.parse_args()
    lines=[GaussianLine(s,t,5) for s,t in ((5,8),(7,16),(13,32))]
    uniform=uniform_certificate(lines,64)
    width=args.input_bits or max(1,args.left.bit_length(),args.right.bit_length())
    need(width<=uniform['max_input_bits'],'supported certified input width is at most 14592 bits')
    result,receipt=multiply(args.left,args.right,lines,64,input_bits=width)
    print(json.dumps({'product_hex':hex(result),'output_bits':receipt['output_bits'],
                      'declared_input_bits':width,'certificate_error_lt':'2^-49',
                      'gaussian_line_executions':receipt['gaussian_line_executions'],
                      'precision':256,'interval_precision':448},indent=2))


if __name__=='__main__':main()
