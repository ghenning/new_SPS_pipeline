import numpy as np
import struct

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
        'ibeam': ('i',4)
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

def M_I(FIL,MASK,DM,T,W):

    # read the header
    with open(FIL,'r') as F:
        head = header(F)
    
    # get tsamp and nchan of data
    tsamp = get_headparam(head,['tsamp'])[0]
    nchan = get_headparam(head,['nchans'])[0]

    # find start and duration of candidate
    start1 = T - int((.5 * W))

    # find start and duration of reference
    dur2 = int(.1/tsamp)
    start2 = T - int(.5 * dur2)

    # get median of ref frame
    ref_data = grab_data(FIL,start2,dur2,nchan)
    medi = np.median(np.ndarray.flatten(ref_data))

    # apply mask to cand
    mask = read_mask(MASK)

    # get cand data
    data = grab_data(FIL,start1,W,nchan)
    
    # replace zaps with median
    data[mask,:] = medi

    # scale cand data
    data /= medi
    data -= 1
    
    # calculate moments and modulation index
    one = np.sum(np.sum(data,1))
    two = np.sum(np.sum(data,1)**2)
    three = np.sum(np.sum(data,1)**3)
    four = np.sum(np.sum(data,1)**4)
    moments = np.array([one,two,three,four])/float(nchan)
    m_I = np.sqrt((moments[1] - moments[0]**2)/moments[0]**2)
    
    return m_I
