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
import wrap_cand_plot
import DDp
import struct

def process_one(FIL,DIR,DMLO,DMHI,DMSTEP,DOWNSAMP,SUB,PLTSUB,PLTDWN,MASK,ZAP):

    if SUB:
        # prepsubband stuff
        # run DDplan.py and get search parameters
        DDres,subb = DDp.create_DDplan(FIL,DIR,DMLO,DMHI,SUB)
        # ddplan.py does a stupid thing sometimes and writes
        # its output differently than usual
        # this is to fix that 
        # found out, it happens if you don't have the -s flag
        """if len(DDres==1) and int(DDres[0,-1])==0:
            lowDM = DDres[:,0]
            hiDM = DDres[:,1]
            dDM = DDres[:,2]
            downsamp = DDres[:,3]
            dsubDM = hiDM - lowDM
            numDMs = DDres[:,4]
            DMsCall = numDMs
            calls = np.ones(len(lowDM))
        else: """
        lowDM = DDres[:,0]
        hiDM = DDres[:,1]
        dDM = DDres[:,2]
        downsamp = DDres[:,3]
        dsubDM = DDres[:,4]
        numDMs = DDres[:,5]
        DMsCall = DDres[:,6]
        calls = DDres[:,7]
        numjob = len(lowDM)
    # no subbands
    elif int(np.ceil(DMSTEP))==0: 
            DDres,subb = DDp.create_DDplan(FIL,DIR,DMLO,DMHI,False)
            lowDM = DDres[:,0]
            hiDM = DDres[:,1]
            dDM = DDres[:,2]
            downsamp = DDres[:,3]
            print "lDM {}".format(lowDM)
            print "hDM {}".format(hiDM)
            print "dDM {}".format(dDM)
            print "downsamp {}".format(downsamp)
            # create DM and downsample lists
            DM = []
            DownSamp = []
            for i in range(np.shape(lowDM)[0]):
                dmtmp = np.arange(lowDM[i],hiDM[i],dDM[i])
                DM.extend(dmtmp)
                DownSamp.extend(np.ones(np.shape(dmtmp))*downsamp[i]) 
            DM = np.asarray(DM)
            DownSamp = np.asarray(DownSamp)
            ###DM = np.arange(DMLO,DMHI+.001,dDM)
    # manual DMstep
    else:
        # create DM list
        DM = np.arange(DMLO,DMHI+.001,DMSTEP)
        downsamp = DOWNSAMP
        DownSamp = np.ones(np.shape(DM))*DOWNSAMP

    # sub-directories 
    prepdir = os.path.join(DIR,"prepsub")
    if not os.path.exists(prepdir):
        try:
            subprocess.check_call(["mkdir",prepdir])
        except OSError as error:    
            print error
    if SUB:
        subdir = os.path.join(DIR,"subdir") # [later]
        if not os.path.exists(subdir):
            try:
                subprocess.check_call(["mkdir",subdir])
            except OSError as error:
                print error

    # basename of file
    clean_basename = os.path.splitext(os.path.basename(FIL))[0]
    clean_fullname = os.path.splitext(FIL)[0]
      
    if ZAP.lower() == 'cx':
        # standard zaps CX receiver, only FB0
        zappys = "0:5,"\
                "670:737,"\
                "768:808,"\
                "1019:1026,"\
                "1669:1817,"\
                "1840:1843"
        # cut the upper band
        #zappys = "0:2048,"\
                #"2209:2213,"\
                #"2718:2785,"\
                #"2816:2856,"\
                #"3067:3074,"\
                #"3717:3865,"\
                #"3888:3891"
        # no manual zapping
        zappys = "0:1"
        # standard zaps CX receiver
        zappys = "0:51,"\
                "1016:1031,"\
                "2037:2058,"\
                "2191:2232,"\
                "2713:2790,"\
                "2811:2861,"\
                "3062:3079,"\
                "3712:3870,"\
                "3882:3896"

        ## standard zaps cx receiver reverse test
        #zappys = "200:214,"\
        #        "226:384,"\
        #        "1017:1034,"\
        #        "1235:1285,"\
        #        "1306:1383,"\
        #        "1864:1905,"\
        #        "2038:2059,"\
        #        "3065:3080,"\
        #        "4045:4096"

    elif ZAP.lower() == 'seven':
        print "nothing here yet"
        print "someone can fill this in later..."
        zappys = "0:1"

    elif ZAP == None:
        zappys = "0:1"

    else:
        zappys = ZAP.replace("-",",")

    # prep RFIfind commands
    RFI_t = "2.0"
    RFI_o = "{}".format(clean_fullname)
    RFI_file = "{}".format(FIL)
    RFI_z = "{}".format(zappys)
    RFI_cf = "0.7"
    RFI_ts = "10"
    RFI_if = "0.3"

    if MASK==None:
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
    else:
        current_mask = MASK

    if SUB:
        # out parameter for prepsubband
        sub_out = os.path.join(subdir,clean_basename)
        sub_out_2 = os.path.join(prepdir,clean_basename)

        # dedisperse using prepsubband
        for ddplan in range(numjob):
            tmpLoDM = lowDM[ddplan]
            sub_dmstep = DMsCall[ddplan] * dDM[ddplan]
            for call in range(int(calls[ddplan])):
                lowDMprep = lowDM[ddplan] + call * sub_dmstep
                tmpsubdm = tmpLoDM + (call + .5) * sub_dmstep # wat? it works I guess 
                # got it, the .5 takes the central DM value of the DM values in call
                # and -sub and -subdm writes subbands at that DM
                #subprocess.check_call(["prepsubband",
                subprocess.check_call(["prepsubband",
                    FIL,
                    "-nobary",
                    "-sub","-subdm",str(tmpsubdm),
                    "-downsamp",str(int(downsamp[ddplan])),
                    "-nsub",str(subb),
                    "-mask",current_mask,
                    "-o",sub_out])
                tmpsubname = "{}_DM{}0.sub[0-9]*".format(clean_basename,tmpsubdm)
                tmpin = os.path.join(subdir,tmpsubname)
                # can't get subprocess to work for this, us os.system instead
                """subprocess.Popen(["prepsubband",
                    "-lodm",str(lowDMprep),
                    "-dmstep",str(dDM[ddplan]),
                    "-numdms",str(int(DMsCall[ddplan])),
                    "-downsamp",str(1),
                    "-nobary",
                    "-nsub",str(subb),
                    "-o",sub_out_2,
                    tmpin],
                    shell=True,
                    stdout=subprocess.PIPE) """
                os_sys_string = "prepsubband -lodm {} "\
                        "-dmstep {} "\
                        "-numdms {} "\
                        "-downsamp {} "\
                        "-nobary "\
                        "-nsub {} "\
                        "-o {} "\
                        "{}"\
                        .format(str(lowDMprep),str(dDM[ddplan]),str(int(DMsCall[ddplan])),str(1),str(subb),sub_out_2,tmpin)
                #print "command {}".format(os_sys_string)
                os.system(os_sys_string)
    else: 

        # dedisperse using prepdata
        for dm,downsamp in zip(DM,DownSamp):

            # out parameter for prepdata
            name_dm = "{}_DM{}".format(clean_basename,str(dm))
            prep_out = os.path.join(prepdir,name_dm)
        
            # prep prepdata commands
            PD_dm = "{}".format(str(dm))
            PD_o = "{}".format(prep_out)
            PD_m = "{}".format(current_mask)
            PD_file = "{}".format(FIL)
            PD_ds = "{}".format(int(downsamp))
            # run prepdata
            subprocess.check_call(["prepdata",
                "-nobary",
                "-o",PD_o,
                "-dm",PD_dm,
                "-mask",PD_m,
                "-downsamp",PD_ds,
                PD_file])

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
    #try:
        #file_to_waterfall, all_cands = giantsps(sp_files,prepdir,DIR)
    #except IndexError as error:
        #print error

    # find header param
    with open(FIL,'r') as F:
        head = header(F)
    tsamp = get_headparam(head,['tsamp'])[0]

    # write out waterfall candidates
    wf_file = waterfall_cands(file_to_waterfall,tsamp)
    if wf_file == 0:
        print "nothing good here, skipping plotting"
    #try:
        #wf_file = waterfall_cands(file_to_waterfall)
        #if wf_file == 0:
            #print "nothing good here, skipping plotting"
            #return
    #except UnboundLocalError as error:
        #print error

    # make plots    
    if wf_file != 0:
        plotter.plotstuff(all_cands,file_to_waterfall,wf_file)
    #try:
        #plotter.plotstuff(all_cands,file_to_waterfall,wf_file)
    #except ValueError as error:
        #print error

    # calculate modulation index
    m_i_file = 0
    if wf_file != 0:
        m_i_file = mod_index(FIL,current_mask,DIR,wf_file)
    #no_m_i = False
    #try:
        #m_i_file = mod_index(FIL,current_mask,DIR,wf_file)
    #except IOError as error:
        #print error
        #no_m_i = True
    
    if m_i_file != 0:
        wrap_cand_plot.plot_cands(FIL,current_mask,DIR,m_i_file,PLTSUB,PLTDWN)
    #if not no_m_i: 
        #try:
            #wrap_cand_plot.plot_cands(FIL,current_mask,DIR,m_i_file)
        #except ValueError as error:
            #print error

# header parameters
def header(afile):
    inread = ""
    while True:
        tmp = afile.read(1)
        inread = inread + tmp 
        flag = inread.find('HEADER_END')
        if flag != -1: 
            break
    return inread

def get_headparam(head, parlist):
    how2parse={
        'nchans': ('i',4),
        'tsamp': ('d',8),
        'foff': ('d',8),
        'fch1': ('d',8),
        'tstart': ('d',8),
        'ibeam': ('i',4),
        'nbits': ('i',4)
    }
    n = 0
    for i in parlist:
        i1 = head.find(i)
        i2 = i1 + len(i)
        nbytes = how2parse[i][1]
        cstr = how2parse[i][0]

        val = struct.unpack(cstr, head[i2:i2+nbytes])[0]
        parlist[n] = val
        n += 1
        return parlist


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

    # fix weird behaviour with one-liners
    if gsps.ndim==1:
        gsps = np.reshape(gsps,(1,len(gsps)))

    # sort the file by time
    if gsps.any():
        gsps = gsps[gsps[:,2].argsort()]
    else:
        gsps = np.zeros((1,5))

    # write to it
    np.savetxt(goodsps_sorted,gsps,fmt=formt,header=head)
    return goodsps_sorted, all_sps_sorted

# write highest SN cands to file
def waterfall_cands(FILE,sampsize):

    # load high SN cand file
    goodsps = np.loadtxt(FILE)
    if not goodsps.any():
        str2return = "No good single pulses"
        print "{}".format(str2return)
        return 0 
    # fix weird behaviour with one-liners
    if np.ndim(goodsps)==1:
        goodsps = np.reshape(goodsps,(1,len(goodsps)))

    # hardcoded time resolution
    #sampsize = 131e-6 

    # prep array
    wf_cands = np.zeros((1,5))
    
    # iterate through cands
    # finding the strongest SN cand
    # within a certain time period
    # now set to 1 sec
    elecounter = 0
    print "goodsps shape {}".format(np.shape(goodsps))
    while elecounter<len(goodsps):
        #timgrp, = np.where(abs(goodsps[elecounter:,2]-1.)<=goodsps[elecounter,2])
        timgrp, = np.where(abs(goodsps[elecounter:,2]-.001)<=goodsps[elecounter,2])
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

    # find header param
    with open(FIL,'r') as F:
        head = header(F)
    tsamp = get_headparam(head,['tsamp'])[0]

    # calculate modulation index for each candidate
    for cand in data:
        DM = cand[0]
        T = cand[3] # presto sample is sample/downsamp
        T = int(cand[2]/tsamp)
        W = cand[4]
        print "FIL {}{}MASK {}{}DM {}{}T {}{}W {}"\
            .format(FIL,'\n',MASK,'\n',DM,'\n',T,'\n',W)
        M = m_i.M_I(FIL,MASK,DM,T,W) 
        Sig = cand[1]
        Time = cand[2]
        str2file = "{:.1f}\t{:.2f}\t{:f}\t{:d}\t{:d}\t{:.2f}\n"\
                .format(DM,Sig,Time,int(T),int(W),M)
        with open(m_i_file,'a') as F:
            F.write(str2file)
    return m_i_file

if __name__ == "__main__":
    desc = """ Search for single pulses in a filterbank file.
        It processes only one file from a directory, as it is
        designed to work with the runshell.py wrapper for
        Slurm usage on clusters. It still is simple to use it without the
        wrapper. \n
        What is happening under the hood:\n
        Grabs one filterbank from directory. \n
        Runs RFIfind on data. \n
        Dedisperses data (prepdata or prepsubband depending on
        options used. \n
        Searches for single pulses using single_pulse_search.py. \n
        Returns files with high signal to noise, sorted in time,
        best candidates with a calculated modulation index,
        DM over time plot, colored version of the single_pulse_search.py
        plot, and dedispersed time series and dynamic spectra plots
        for the best candidates """
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
            help="Manually input DM step. Default uses DDplan.py DM steps")
    optional.add_argument('--downsamp',type=int, default=1,
            help="Manually input downsampling. Default is 1 with --dmstep, otherwise taken from DDplan.py")
    optional.add_argument('--subband',action='store_true',
            help="Use subbands with prepsubband (and DDplan.py)")
    optional.add_argument('--noRFIfind',action='store_true',
            help="Skip RFIfind, use with manual mask input from --mask [add later]") 
    optional.add_argument('--mask',type=str,
            help="Input an existing rfifind mask")
    optional.add_argument('--plotsub',type=int,
            help="Cand plot subbands, default 128",default=128)
    optional.add_argument('--plotdown',type=int,
            help="Cand plot downsamp, default = 8",default=8)
    optional.add_argument('--zaps',type=str,
            help="Manual zapping ('cx' for CX receiver, 'seven' for 7beam receiver, 'x:y-x:y-x:y' for manual zaps)")
    parser._action_groups.append(optional)
    args = parser.parse_args()

    # !!!!!!!!!!!!!! #
    # MISSING FEATURES
    # DOUBLE CHECK WHAT M_I IS LOOKING AT (WHERE In FILE)
    #   seems fine, but is crashing in some cases (crap holiday data)
    #   see if it happens to other data as well
    # MANUAL MASK
    # OPTION FLAG FOR ZAPPYS
    # !!!!!!!!!!!!!! #

    # Time process
    t_0 = time.time()

    # create DM list
    ##dms = np.arange(args.lodm,args.hidm+1,args.dmstep)

    # find filterbank file
    # should only contain one filterbank
    # as this assumes processing a single
    # filterbank per cluster node
    fils = os.path.join(args.dir,"*.fil")
    fils_glob = glob.glob(fils)
    fil = fils_glob[0]

    # process filterbank
    ##process_one(fil,args.dir,dms)
    process_one(fil,args.dir,args.lodm,args.hidm,args.dmstep,args.downsamp,args.subband,args.plotsub,args.plotdown,args.mask,args.zaps)

    # end message
    end_msg = "great success, all done!"
    print end_msg

    # Time process
    t_1 = time.time()
    # Total time processing 
    t_tot = t_1 - t_0
    print "This took {} seconds, mama mia!".format(t_tot)

