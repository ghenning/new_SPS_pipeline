#!/bin/bash -l 

#SBATCH -o /hercules/results/ghil/1720/20200809/logs/1720.err.%j 
#SBATCH -D ./ 
#SBATCH -J 1720 
#SBATCH --partition=long.q 
#SBATCH --nodes=1 
#SBATCH --cpus-per-task=8 
#SBATCH --mem=15360 
#SBATCH --time=40:00:00 

echo "NODE: "$HOSTNAME 
echo "Space on node:"
df -h 


DDl="300.0" 
DDh="400.0" 
step="0.0" 
downsamp="1" 
orig_fil="/hercules/results/ghil/1720/20200809/R3_20200809_1_merged_13732910_18310546.fil" 
tmpdir="/tmp/R3_20200809_1_merged_13732910_18310546" 
tmpfil=$tmpdir"/R3_20200809_1_merged_13732910_18310546.fil" 
result_dir="/hercules/results/ghil/1720/20200809/results/R3_20200809_1_merged_13732910_18310546" 
code_dir="/hercules/u/ghil/NEW_PIPE_TEST/new_SPS_pipeline/" 
prepdir=$tmpdir"/prepsub" 
f="R3_20200809_1_merged_13732910_18310546.fil" 
p="prepsub" 
s="subdir" 
spsplot=$prepdir"/R3_20200809_1_merged_13732910_18310546_singlepulse.ps" 

if [ ! -d "$tmpdir" ]; then 
	 mkdir $tmpdir 
fi 

rsync -v $orig_fil $tmpdir 

singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --dmstep $step --downsamp $downsamp 

echo "mv single pulse search plot to main dir" 
mv $spsplot $tmpdir 
echo "ls tmpdir" 
echo "###########" 
ls $tmpdir 
echo "###########" 
echo "rsync results back" 
rsync -r --exclude $f --exclude $p --exclude $s $tmpdir/ $result_dir 
echo "removing temp dir on tmp: "$tmpdir 
rm -rf $tmpdir 
echo "it's gone, byebye "$tmpdir 

echo "NODE: "$HOSTNAME 
echo "Space on node:"
df -h 
