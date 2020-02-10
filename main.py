import matplotlib
matplotlib.use('Agg')
import numpy as np
import argparse
import subprocess
#import filterbank
#import waterfaller
#import rawdata
import os
#from momentmod02 import singleplus
import time
#import rrattrapmod
#import spssummarizer
#from plotmaster import plotstutt,gathersps2
#import newsps2
#import spsbreak

def process_one(FIL,DIR,DM):

    # sub-directories 
    prepdir = os.path.join(DIR,"prepsub")
    if not os.path.exists(prepdir):
        try:
            subprocess.check_call(["mkdir",res_dir])
        except OSError as error:    
            print error
    subdir = os.path.join(DIR,"subdir") # [later]

    # basename of file
    clean_name = os.path.splitext(os.path.basename(FIL))
      
    # standard zaps CX receiver
    zappys = "0:51,"\
            "1021:1026,"\
            "2042:2053,"\
            "2196:2227,"\
            "2718:2766,"\
            "2816:2856,"\
            "3067:3865,"\
            "3888:3891"

    # prep RFIfind commands
    RFI = "-time 2.0 -o {} {} " \
        "-zapchan {} -chanfrac 0.7 " \
        "-timesig 10 -intfrac 0.3".format(DIR,FIL,zappys)

    # run RFIfind
    subprocess.check_call(["rfifind",RFI])

    # save mask file path
    current_mask = os.path.join(DIR,BLA.mask) # FIX ME (how2get mask name)

    # dedisperse using prepdata
    for dm in DM:

        # out parameter for prepdata
        name_dm = "{}_DM{}".format(clean_name,str(dm))
        prep_out = os.path.join(prepdir,name_dm)
    
        PREP = "-nobary -dm {} "\
                "-o {} "\
                "-dm {} "\
                "-mask {} "\
                "{}"\
                .format(str(dm),prep_out,str(dm),current_mask,FIL)
        subprocess.check_call(["prepdata",PREP])

    # prepsubband [later]

    # prep single pulse search command
    all_dat = os.path.join(prepdir,"*.dat")
    SPS = "-t 7.0 -m 0.02 -b -p {}".format(all_dat)

    #single pulse search
    subprocess.check_call(["single_pulse_search.py",SPS]) 

    # grab all singlepulse files
    sp_files = sps_files(prepdir) 

    # go through single pulse files
    # find high SN cands
    # sort in time
    giantsps(sp_file,prepdir,DIR)

# find all .singlepulse files
def sps_files(DIR):

    # first all files in prepdata dir
    spdir_files = []
    for (dirpath,dirnames,filenames) in os.walk(DIR):
        spdir_files.extend(filenames)
    
    # all .singlepulse files
    dot = '.'
    sp_files = []
    for i in range(len(spdir_files)):
        tmpfilename = [dot.join(spdir_files[i].split(dot)[0:-1]),spdir_files[i].split(dot)[-1]]
        if (tmpfilename[-1]=='singlepulse'):
            sp_files.append(tmpfilename[0])

    return sp_files

# write high SN cands to file
def giantsps(SPFILES,PREPDIR,DIR,THRESH=8.0):
 
    # name file
    goodspsfile = os.path.join(DIR,"goodsps.txt")

    # write header to file
    with open(goodspsfile,'w') as F:
        headstring = "# DM \t Sigma \t Time(s) \t Sample \t Downfact \n"
        F.write(headstring) 

    for SP in SPFILES:

        # add extension
        SP_ext = os.path.join(SP + ".singlepulse")
        
        # check if file is empty
        full_SP = os.path.join(PREPDIR,SP_ext)
        if (os.stat(full_SP).st_size==0): continue

        # load singlepulse file
        spdata = np.loadtxt(full_SP)
        if not spdata.any(): continue

        # fix weird behaviour with one-liners
        if spdata.ndim==1:
            spdata = np.reshape(spdata,(1,len(spdata)))

        # go through each line and check for high SN
        for n in range(np.size(spdata,0)):
            with open(goodspsfile,'a') as F:
                if (spdata[n,1]>=THRESH):
                    DM = spdata[n,0]
                    Sig = spdata[n,1]
                    Tim = spdata[n,2]
                    Samp = spdata[n,3]
                    Downf = spdata[n,4]
                    str2file = "{:.1f}\t{:.2f}\t{:f}\t{:d}\t{:d}\n"\
                        .format(DM,Sig,Tim,Samp,Downf)

    # load the file created to sort
    gsps = np.loadtxt(goodspsfile) 

    # sort the file by time
    if gsps.any():
        gsps = gsps[gsps[:,2].argsort()]
    else:
        gsps = np.zeros((1,5))

    # new sorted file
    goodsps_sorted = os.path.join(DIR,"goodsps_sorted.txt")

    # write to it
    head = "DM \t Sigma \t Time(s) \t Sample \t Downfact"
    formt = "%.1f \t %.2f \t %f \t %d \t %d" # OLD WAY, FIX WITH STR.FORMAT
    np.savetxt(goodsps_sorted,gsps,fmt=formt,header=head)
        
    
if __name__ == "__main__":
    desc = """ I'm a description """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--dir',
            help="Filterbank directory")
    parser.add_argument('--outdir',
            help="Result directory [redundant?]")
    parser.add_argument('--lodm',type=int,
            help="Minimum DM for search")
    parser.add_argument('--hidm',type=int,
            help="Maximum DM for search")
    parser.add_argument('--dmstep',type=int, default=1,
            help="DM step")
    parser.add_argument('--nomask',action='store_true',
            help="Skip RFIfind [add later]") 
    parser.add_argument('--mask',
            help="Manual mask input [add later]")
    parser.add_argument('--subband',action='store_true',
            help="Use subbands (prepsubband) [add later+other options]")
    args = parser.parse_args()

    # RE-INCORPORATE DDPLAN FROM OLD PIPE AT SOME POINT

    # Time process
    t_0 = time.time()

    # create DM list
    dms = np.arange(args.lodm,args.hidm+1,args.dmstep)

    # ADD MISSING INPUT ERRORS

    # find filterbank file
    ## find me!!!

    # process filterbank
    ##process_one(fil,args.dir,dms)

    # ADD NEWSPS2.GULLFOSS FROM OLD PIPE
    
    # WHERE IS THE M_I CALC? NEWSPS2.PY
    #ADD AS SEPARATE MODULE POST-PROCESSING?

    # ADD PLOTTING. PLOTMASTER.PY

    # Time process
    t_1 = time.time()
    # Total time processing 
    t_tot = t_1 - t_0
    print "T {}".format(t_tot)
    print args.nomask
    print dms

