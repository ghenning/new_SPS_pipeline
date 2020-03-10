import numpy as np
import struct
import os

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

def grab_data(FILE,STARTSAMP,NUMSAMP,NCHAN,DTYPE=np.uint8,FIL=True):
    with open(FILE,'r') as F:
        if not FIL:
            headlen = 4096
            print "hi there, I'm assuming the DADA header is 4096 bits"
        else:
            print "hi there, I'm reading a filterbank header now"
            thehead = header(F)
            headlen = len(thehead)
        F.seek(headlen+NCHAN*STARTSAMP)
        data = np.fromfile(F,dtype=DTYPE,count=int(NCHAN*NUMSAMP))
        data = np.reshape(data,(-1,NCHAN)).T
    return data

def read_mask(MASK):
    with open(MASK,'r') as x:
        np.fromfile(x,dtype=np.float64,count=6)
        np.fromfile(x,dtype=np.int32,count=3)
        nzap = np.fromfile(x,dtype=np.int32,count=1)[0]
        mask_zap_chans = np.fromfile(x,dtype=np.int32,count=nzap)
    return mask_zap_chans

def dispdelay(DM,LOFREQ,HIFREQ):
    dconst = 4.15e+06
    delay = DM * dconst * (1.0 / LOFREQ**2 - 1.0 / HIFREQ**2) # in ms
    return delay

def DDdata(DATA,DM,FTOP,FCHAN,NCHAN,TSAMP,TO_USE):
    DD = np.zeros((int(NCHAN),int(TO_USE)))
    for chan in np.arange(int(NCHAN)):
        chandata = DATA[chan,:]
        chanfreq = FTOP - chan * FCHAN
        dmdelay = dispdelay(DM,chanfreq,FTOP) # in ms
        dmdelay_s = dmdelay * 1e-3 # in seconds 
        dmdelay_samp = int(np.round(dmdelay_s/TSAMP))
        DD[chan,:] = chandata[dmdelay_samp : dmdelay_samp + int(TO_USE)] 
    return DD

def M_I(FIL,MASK,DM,T,W):

    # read the header
    with open(FIL,'r') as F:
        head = header(F)
    
    # get tsamp and nchan of data
    tsamp = get_headparam(head,['tsamp'])[0]
    nchan = get_headparam(head,['nchans'])[0]

    # find top and bottom freqs of band
    hifreq = get_headparam(head,['fch1'])[0]
    chan_bw = get_headparam(head,['foff'])[0]
    lofreq = hifreq - (abs(chan_bw) * nchan)

    # find dispersion sweep of cand
    sweep = dispdelay(DM,lofreq,hifreq)  # in ms
    sweep_s = sweep * 1e-3 # in seconds
    sweep_samples = int(np.round(sweep_s/tsamp)) + W

    # find start and duration of candidate
    start1 = T - int((.5 * W))

    # find start and duration of reference
    # ref frame is sweep +- .05 seconds
    pad2 = int(.1/tsamp)
    dur2 = pad2 + sweep_samples
    start2 = T - int(.5 * (pad2 + W))

    # find out length of file, and see if we have reached the end
    data_size = os.path.getsize(FIL) - len(head)
    nbits = get_headparam(head,['nbits'])[0]
    bytes_per_spectrum = nchan * nbits / 8
    nspec = data_size / bytes_per_spectrum
    grab_data_end = start2 + dur2
    print "number of samples {}".format(nspec)
    print "grab data end {}".format(grab_data_end)
    if grab_data_end > nspec:
        print "reached the end of the file"
        return 999

    # get median of ref frame, get data
    ref_data_tmp = grab_data(FIL,start2,dur2,nchan)

    # dedisperse data
    samps_to_use = pad2 + W
    ref_data = DDdata(ref_data_tmp,DM,hifreq,abs(chan_bw),nchan,tsamp,samps_to_use)

    # read mask
    mask = read_mask(MASK)

    # mask data
    ref_data[mask,:] = 0

    # median of data, ignoring masked values
    #medi = np.median(np.ndarray.flatten(ref_data))
    medi = np.median(np.ndarray.flatten(ref_data[np.nonzero(ref_data)]))

    # get cand data
    data_tmp = grab_data(FIL,start1,sweep_samples,nchan)

    # dedisperse data
    data = DDdata(data_tmp,DM,hifreq,abs(chan_bw),nchan,tsamp,W)
    
    # replace zaps with median
    data[mask,:] = medi

    # scale cand data
    ##data /= medi # same_kind divide error
    data = data/medi
    data -= 1
    
    # calculate moments and modulation index
    one = np.sum(np.sum(data,1))
    two = np.sum(np.sum(data,1)**2)
    three = np.sum(np.sum(data,1)**3)
    four = np.sum(np.sum(data,1)**4)
    moments = np.array([one,two,three,four])/float(nchan)
    m_I = np.sqrt((moments[1] - moments[0]**2)/moments[0]**2)
    
    return m_I
