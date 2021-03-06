import numpy as np
import os

def create_script(LODM,HIDM,DIR,FIL,RES,CODE,JOB,LOG,Q,STEP,SUBBAND,DS,PLTSUB,PLTDWN,MASK,ZAP):
    with open("launch_me.sh",'w') as F:
        F.write("#!/bin/bash -l \n")
        F.write("\n")
        log_path = os.path.join(LOG,JOB + ".err.%j")
        F.write("#SBATCH -o {} \n".format(log_path))
        F.write("#SBATCH -D ./ \n")
        F.write("#SBATCH -J {} \n".format(JOB))
        if Q:
            F.write("#SBATCH --partition=long.q \n")
        else:
            F.write("#SBATCH --partition=short.q \n")
        F.write("#SBATCH --nodes=1 \n")
        F.write("#SBATCH --cpus-per-task=8 \n")
        #F.write("#SBATCH --ntasks=1 \n")
        #F.write("#SBATCH --ntasks-per-node=1 \n")
        F.write("#SBATCH --mem=15360 \n")
        if Q:
            F.write("#SBATCH --time=40:00:00 \n")
        else:
            F.write("#SBATCH --time=10:00:00 \n")
        F.write("\n") 
        F.write("echo \"NODE: \"$HOSTNAME \n")
        F.write("echo \"Space on node:\"\n")
        F.write("df -h \n")
        F.write("\n") 
        #F.write("module load singularity \n")
        F.write("\n") 
        F.write("DDl=\"{}\" \n".format(str(LODM)))
        F.write("DDh=\"{}\" \n".format(str(HIDM)))
        F.write("step=\"{}\" \n".format(str(STEP)))
        F.write("downsamp=\"{}\" \n".format(str(DS)))
        F.write("pltsub=\"{}\" \n".format(str(PLTSUB)))
        F.write("pltdwn=\"{}\" \n".format(str(PLTDWN)))
        F.write("mask=\"{}\" \n".format(str(MASK)))
        F.write("zaps=\"{}\" \n".format(str(ZAP)))
        ###filly = os.path.join(FILPATH,FIL + ".fil")
        F.write("orig_fil=\"{}\" \n".format(FIL))
        #F.write("orig_fil=\"" + FIL + ".fil\" \n")
        fil_no_ext = os.path.splitext(os.path.basename(FIL))[0]
        F.write("tmpdir=\"/tmp/{}\" \n".format(fil_no_ext))
        fil_base = os.path.basename(FIL)
        F.write("tmpfil=$tmpdir\"/{}\" \n".format(fil_base))
        F.write("result_dir=\"{}\" \n".format(RES))
        F.write("code_dir=\"{}\" \n".format(CODE))
        F.write("prepdir=$tmpdir\"/{}\" \n".format("prepsub"))
        F.write("f=\"{}\" \n".format(fil_base))
        F.write("p=\"{}\" \n".format("prepsub"))
        F.write("s=\"{}\" \n".format("subdir"))
        spsname = "{}_singlepulse.ps".format(fil_no_ext)
        F.write("spsplot=$prepdir\"/{}\" \n".format(spsname))
        F.write("\n")
        F.write("if [ ! -d \"$tmpdir\" ]; then \n")
        F.write("\t mkdir $tmpdir \n")
        F.write("fi \n")
        F.write("\n")
        F.write("rsync -v $orig_fil $tmpdir \n")
        F.write("\n")
        if MASK == None:
            if ZAP == None:
                if SUBBAND:
                    F.write("singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --subband --plotsub $pltsub --plotdown $pltdwn \n")
                else:
                    F.write("singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --dmstep $step --downsamp $downsamp --plotsub $pltsub --plotdown $pltdwn \n")
            else:
                if SUBBAND:
                    F.write("singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --subband --plotsub $pltsub --plotdown $pltdwn --zaps $zaps \n")
                else:
                    F.write("singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --dmstep $step --downsamp $downsamp --plotsub $pltsub --plotdown $pltdwn --zaps $zaps \n")
        else:
            if ZAP == None:
                if SUBBAND:
                    F.write("singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --subband --plotsub $pltsub --plotdown $pltdwn --mask $mask \n")
                else:
                    F.write("singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --dmstep $step --downsamp $downsamp --plotsub $pltsub --plotdown $pltdwn --mask $mask \n")
            else:
                if SUBBAND:
                    F.write("singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --subband --plotsub $pltsub --plotdown $pltdwn --zaps $zaps --mask $mask \n")
                else:
                    F.write("singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --dmstep $step --downsamp $downsamp --plotsub $pltsub --plotdown $pltdwn --zaps $zaps --mask $mask \n")
        F.write("\n")
        F.write("echo \"mv single pulse search plot to main dir\" \n")
        F.write("mv $spsplot $tmpdir \n")
        F.write("echo \"ls tmpdir\" \n")
        F.write("echo \"###########\" \n")
        F.write("ls $tmpdir \n")
        F.write("echo \"###########\" \n")
        F.write("echo \"rsync results back\" \n")
        F.write("rsync -r --exclude $f --exclude $p --exclude $s $tmpdir/ $result_dir \n")
        F.write("echo \"removing temp dir on tmp: \"$tmpdir \n")
        F.write("rm -rf $tmpdir \n")
        F.write("echo \"it's gone, byebye \"$tmpdir \n")
        F.write("\n")
        F.write("echo \"NODE: \"$HOSTNAME \n")
        F.write("echo \"Space on node:\"\n")
        F.write("df -h \n")


