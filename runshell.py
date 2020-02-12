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
        launchmaker.create_script(args.lodm,args.hidm,args.dir,fil,fil_res,args.code,args.job,args.log,args.longQ,args.dmstep)

        # make it executable
        subprocess.check_call(["chmod","+x","launch_me.sh"])

        # send slurm job 
        subprocess.check_call(["sbatch","./launch_me.sh"])

if __name__ == "__main__":
    desc = """ I'm a description """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--dir',
            help="Directory to filterbanks")
    parser.add_argument('--code',
            help="Code directory")
    parser.add_argument('--job', default="1519",
            help="Job name. Default: 1519")
    parser.add_argument('--log', default="~/slurm_logs/",
            help="Path to slurm logs. Default: ~/slurm_logs/")
    parser.add_argument('--longQ', action="store_true",
            help="Send to long queue. Default: False")
    parser.add_argument('--lodm', type=int, default=500,
            help="Low DM of search. Default: 500")
    parser.add_argument('--hidm', type=int, default=600,
            help="High DM of search. Default: 600")
    parser.add_argument('--dmstep', type=int, default=2,
            help="DM step of search. Default: 2")
    args = parser.parse_args()

    # grab filterbanks
    files = grab_fils(args.dir)

    # send filterbanks to slurm factory
    process_files(files)


