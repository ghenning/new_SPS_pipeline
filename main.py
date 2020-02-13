import matplotlib
matplotlib.use('Agg')
import numpy as np
import argparse
import subprocess
import os
import glob
import time
import plotter
import m_i

def process_one(FIL,DIR,DM):

    # sub-directories 
    prepdir = os.path.join(DIR,"prepsub")
    if not os.path.exists(prepdir):
        try:
            subprocess.check_call(["mkdir",prepdir])
        except OSError as error:    
            print error
    subdir = os.path.join(DIR,"subdir") # [later]

    # basename of file
    clean_basename = os.path.splitext(os.path.basename(FIL))[0]
    clean_fullname = os.path.splitext(FIL)[0]
      
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
    RFI_t = "2.0"
    RFI_o = "{}".format(clean_fullname)
    RFI_file = "{}".format(FIL)
    RFI_z = "{}".format(zappys)
    RFI_cf = "0.7"
    RFI_ts = "10"
    RFI_if = "0.3"

    # run RFIfind
    subprocess.check_call(["rfifind",
        "-time",RFI_t,
        "-o",RFI_o,
        RFI_file,
        "-zapchan",RFI_z,
        "-chanfrac",RFI_cf,
        "-timesig",RFI_ts,
        "-intfrac",RFI_if])

    # save mask file path
    mask_path = os.path.join(DIR,"*.mask")
    current_mask = glob.glob(mask_path)[0]

    # dedisperse using prepdata
    for dm in DM:

        # out parameter for prepdata
        name_dm = "{}_DM{}".format(clean_basename,str(dm))
        prep_out = os.path.join(prepdir,name_dm)
    
        # prep prepdata commands
        PD_dm = "{}".format(str(dm))
        PD_o = "{}".format(prep_out)
        PD_m = "{}".format(current_mask)
        PD_file = "{}".format(FIL)

        # run prepdata
        subprocess.check_call(["prepdata",
            "-nobary",
            "-o",PD_o,
            "-dm",PD_dm,
            "-mask",PD_m,
            PD_file])

    # prepsubband [later]

    # prep single pulse search command
    all_dat = os.path.join(prepdir,"*.dat")
    thresh = 7.0
    m = 0.02
    SPS_t = "{}".format(thresh)
    SPS_m = "{}".format(m)
    SPS_files = "{}".format(all_dat) # [redundant]

    #single pulse search
    # can't use *.dat, need to iterate over files
    # glob .dat files
    all_dat_glob = glob.glob(all_dat)
    for dat in all_dat_glob:
        subprocess.check_call(["single_pulse_search.py",
            "-t",SPS_t,
            "-m",SPS_m,
            "-b",
            #"-p",
            dat]) 

    # grab all singlepulse files
    sp_files = sps_files(prepdir) 

    # go through single pulse files
    # find high SN cands
    # sort in time
    file_to_waterfall, all_cands = giantsps(sp_files,prepdir,DIR)

    # write out waterfall candidates
    wf_file = waterfall_cands(file_to_waterfall)

    # make plots    
    plotter.plotstuff(all_cands,file_to_waterfall,wf_file)

    # calculate modulation index
    mod_index(FIL,current_mask,DIR,wf_file)

# find all .singlepulse files
def sps_files(DIR):

    # all .singlepulse files in directory
    all_sp = os.path.join(DIR,"*.singlepulse")

    # glob the files
    all_sp_glob = glob.glob(all_sp)

    return all_sp_glob

# write high SN cands to file (and all cands to file as well)
def giantsps(SPFILES,PREPDIR,DIR,THRESH=8.0):
 
    # the header 
    head = "# DM \t Sigma \t Time(s) \t Sample \t Downfact"

    # format of files
    formt = "%.1f \t %.2f \t %f \t %d \t %d" # OLD WAY, FIX WITH STR.FORMAT

    # name files
    goodspsfile = os.path.join(DIR,"goodsps.txt")
    goodsps_sorted = os.path.join(DIR,"goodsps_sorted.txt")
    all_sps = os.path.join(DIR,"all_sps.txt")
    all_sps_sorted = os.path.join(DIR,"all_sps_sorted.txt")

    # write header to files
    with open(goodspsfile,'w') as F:
        F.write(head) 
        F.write("\n")
    with open(all_sps,'w') as F:
        F.write(head)
        F.write("\n")

    for SP in SPFILES:
        
        # check if file is empty
        if (os.stat(SP).st_size==0): continue

        # load singlepulse file
        spdata = np.loadtxt(SP)
        if not spdata.any(): continue

        # fix weird behaviour with one-liners
        if spdata.ndim==1:
            spdata = np.reshape(spdata,(1,len(spdata)))

        # go through each line and check for high SN
        # and write all to all_sps file
        for n in range(np.size(spdata,0)):
            DM = spdata[n,0]
            Sig = spdata[n,1]
            Tim = spdata[n,2]
            Samp = int(spdata[n,3])
            Downf = int(spdata[n,4])
            str2file = "{:.1f}\t{:.2f}\t{:f}\t{:d}\t{:d}\n"\
                .format(DM,Sig,Tim,Samp,Downf)
            with open(all_sps,'a') as F:
                F.write(str2file)
            if (Sig>=THRESH):
                with open(goodspsfile,'a') as F:
                    F.write(str2file)

    # load file created to sort (all sps)
    asps = np.loadtxt(all_sps)
    
    # sort the file by time
    if asps.any():
        asps = asps[asps[:,2].argsort()]
    else:
        asps = np.zeros((1,5))

    # write to file
    np.savetxt(all_sps_sorted,asps,fmt=formt,header=head)

    # load the file created to sort
    gsps = np.loadtxt(goodspsfile) 

    # sort the file by time
    if gsps.any():
        gsps = gsps[gsps[:,2].argsort()]
    else:
        gsps = np.zeros((1,5))

    # write to it
    np.savetxt(goodsps_sorted,gsps,fmt=formt,header=head)
    return goodsps_sorted, all_sps_sorted

# write highest SN cands to file
def waterfall_cands(FILE):

    # load high SN cand file
    goodsps = np.loadtxt(FILE)
    if not goodsps.any():
        str2return = "No good single pulses"
        print "{}".format(str2return)
        return 0 

    # hardcoded time resolution
    sampsize = 131e-6 

    # prep array
    wf_cands = np.zeros((1,5))
    
    # iterate through cands
    # finding the strongest SN cand
    # within a certain time period
    # now set to 1 sec
    elecounter = 0
    while elecounter<len(goodsps):
        timgrp, = np.where(abs(goodsps[elecounter:,2]-1.)<=goodsps[elecounter,2])
        timgrp += elecounter
        try:
            maxval, = np.where(goodsps[timgrp,1]==goodsps[timgrp,1].max())
        # in case of error, move 1 second ahead
        except ValueError:
            added_time = int(1/sampsize)
            elecounter += added_time
            continue
        maxval += elecounter
        wf_cands = np.append(wf_cands,goodsps[maxval],axis=0)
        elecounter = timgrp[-1] + 1 

    # create path to new file
    wf_file = os.path.join(os.path.dirname(FILE),"waterfall_cands.txt")
        
    # remove first line which is only zeros
    wf_cands = np.delete(wf_cands,0,0)

    # create header and format of file and save 
    head = "DM \t Sigma \t Time(s) \t Sample \t Downfact"
    formt = "%.1f \t %.2f \t %f \t %d \t %d" # OLD WAY, FIX WITH STR.FORMAT
    np.savetxt(wf_file,wf_cands,fmt=formt,header=head)

    return wf_file

def mod_index(FIL,MASK,DIR,CANDFILE):

    # load mod index cand file
    data = np.loadtxt(CANDFILE)
    if not data.any():
        str2return = "No modulation index cands"
        print "{}".format(str2return)
        return 0 

    # fix weird behaviour with one-liners
    if np.ndim(data)==1:
        data = np.reshape(data,(1,len(data)))

    # name file and write header
    m_i_file = os.path.join(DIR,"mod_index.txt")
    head = "# DM \t Sigma \t Time(s) \t Sample \t Downfact \t M_I"
    with open(m_i_file,'w') as F:
        F.write(head)
        F.write("\n")

    # calculate modulation index for each candidate
    for cand in data:
        DM = cand[0]
        T = cand[3]
        W = cand[4]
        M = m_i.M_I(FIL,MASK,DM,T,W) 
        Sig = cand[1]
        Time = cand[2]
        str2file = "{:.1f}\t{:.2f}\t{:f}\t{:d}\t{:d}\t{:.2f}\n"\
                .format(DM,Sig,Time,T,W,M)
        with open(m_i_file,'a') as F:
            F.write(str2file)
    
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

    # ADD MISSING INPUT ERRORS [later]
    # optional vs required args

    # find filterbank file
    # should only contain one filterbank
    # as this assumes processing a single
    # filterbank per cluster node
    fils = os.path.join(args.dir,"*.fil")
    fils_glob = glob.glob(fils)
    fil = fils_glob[0]

    # process filterbank
    process_one(fil,args.dir,dms)

    # ADD NEWSPS2.GULLFOSS FROM OLD PIPE
    
    # WHERE IS THE M_I CALC? NEWSPS2.PY
    #ADD AS SEPARATE MODULE POST-PROCESSING?

    # Time process
    t_1 = time.time()
    # Total time processing 
    t_tot = t_1 - t_0
    print "T {}".format(t_tot)

