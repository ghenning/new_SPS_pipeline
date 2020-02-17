import argparse
import numpy as np

if __name__ == "__main__":
    desc = """ I'm a description """
    parser = argparse.ArgumentParser(description=desc)
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('--dir',
            help="Filterbank directory",required=True)
    required.add_argument('--lodm',type=float,
            help="Minimum DM for search",required=True)
    required.add_argument('--hidm',type=float,
            help="Maximum DM for search",required=True)
    optional.add_argument('--dmstep',type=float, default=0.0,
            help="Manually input DM step. Default uses DDplan.py DM steps [add later]")
    optional.add_argument('--subband',action='store_true',
            help="Use subbands with prepsubband (and DDplan.py)")
    optional.add_argument('--nomask',action='store_true',
            help="Skip RFIfind, use with manual mask input from --mask [add later]") 
    optional.add_argument('--mask',
            help="Manual mask input [add later]")
    parser._action_groups.append(optional)
    args = parser.parse_args()

    print args.dir
    print args.lodm
    print args.hidm
    print args.dmstep
    print args.subband
    print np.ceil(args.dmstep)

    if int(np.ceil(args.dmstep)) == 0:
        print "no dm step set, use ddplan"

