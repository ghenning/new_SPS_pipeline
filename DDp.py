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
 

def create_DDplan(FIL,DIR,LODM,HIDM):
    
    # read header
    with open(FIL,'r') as F:
        head = header(F)

    # file parameters
    nchan = get_headparam(head,['nchans'])[0]
    fchan = get_headparam(head,['foff'])[0]
    tsamp = get_headparam(head,['tsamp'])[0]
    ftop = get_headparam(head,['ftop'])[0]
    cfreq = ftop - (abs(fchan) * nchan * .5)
    bw = fchan * nchan

    # subbands
    subb = int(nchan/8)

    # DDplan text file
    DD_out = os.path.join(DIR,"DDPlan.txt")

    # run DDplan.py
    try:
        subprocess.check_call(["DDplan.py",
            "-l",str(int(DDLO)),
            "-d",str(int(DDHI)),
            "-n",str(int(nchan)),
            "-f",str(int(cfreq)),
            "-b",str(int(bw)),
            "-t",str(tsamp),
            "-r",str(0.1),
            "-o",DIR,
            ">",DD_out])
    except subprocess.CalledProcessError as err:
        print err

    # old DDplan reader, too lazy to improve
    f = open(DD_out,'r')
    lines = f.readlines()
    deleters = []
    DDresults = np.zeros([15,9])
    for i,line in enumerate(lines):
        if 'WorkFract' in line:
            DDstartpoint = i + 1

    for i,line in enumerate(lines[DDstartpoint:-1]):
        if not lines[DDstartpoint+i].split():
            break
        for j in range(len(lines[DDstartpoint].split())):
            DDresults[i,j] = float(lines[DDstartpoint+i].split()[j])

    for i,line in enumerate(DDresults):
        if not line.any():
            deleters.append(i)

    for x in reversed(deleters):
        DDresults = np.delete(DDresults,x,0)

    f.close()

    return DDresults,subb



