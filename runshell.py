import subprocess
import os
import numpy as np
import launchmaker
import argparse
import glob

def grab_fils(DIR):

    # find filterbanks
    all_fils = os.path.join(DIR,"*.fil")

    # glob glob
    fils = glob.glob(all_fils)

    return fils

def process_files(FILES):

    # create results directory and subdirectory
    res_dir = os.path.join(os.path.dirname(FILES[0]),"results")
    if not os.path.exists(res_dir):
        try:
            subprocess.check_call(["mkdir",res_dir])
        except OSError as error:
            print error 

    # create log file
    for fil in FILES:

        # create result subdirectory for file
        fil_res = os.path.join(res_dir,os.path.splitext(os.path.basename(fil))[0])
        if not os.path.exists(fil_res):
            try:
                subprocess.check_call(["mkdir",fil_res])
            except OSError as error:
                print error

        # run launchmaker on each file
        launchmaker.create_script(args.lodm,args.hidm,args.dir,fil,fil_res,args.code,args.job,args.log,args.longQ,args.dmstep,args.subband,args.downsamp)

        # make it executable
        subprocess.check_call(["chmod","+x","launch_me.sh"])

        # send slurm job 
        subprocess.check_call(["sbatch","./launch_me.sh"])

if __name__ == "__main__":
    desc = """ Slurm wrapper for main.py. Reads in a directory
        of filterbanks and processes each one as a Slurm job. 
        To change job parameters, change launchmaker.py."""
    parser = argparse.ArgumentParser(description=desc)
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('--dir',
            help="Directory to filterbanks",required=True)
    required.add_argument('--code',
            help="Code directory",required=True)
    required.add_argument('--lodm', type=float,
            help="Low DM of search.",required=True)
    required.add_argument('--hidm', type=float,
            help="High DM of search.",required=True)
    optional.add_argument('--dmstep', type=float, default=0.0,
            help="DM step of search. Default uses DDplan.py for DM steps")
    optional.add_argument('--downsamp',type=int,default=1,
            help="Downsampling. Default is 1 with --dmstep, otherwise taken from DDplan.py")
    optional.add_argument('--job', default="1519",
            help="Job name. Default: 1519")
    optional.add_argument('--log', default="~/slurm_logs/",
            help="Path to slurm logs. Default: ~/slurm_logs/")
    optional.add_argument('--longQ', action="store_true",
            help="Send to long queue. Default: False")
    optional.add_argument("--subband",action='store_true',
            help="Use prepsubband with DDplan. Default: False")
    parser._action_groups.append(optional)
    args = parser.parse_args()

    # grab filterbanks
    files = grab_fils(args.dir)

    # create log directory
    if not os.path.exists(args.log):
        try:
            subprocess.check_call(["mkdir",args.log])
        except OSError as error:
            print error 

    # send filterbanks to slurm factory
    process_files(files)


