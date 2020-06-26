#!/bin/bash -l 

#SBATCH -o /hercules/results/ghil/1620/20200619/logs/1620.err.%j 
#SBATCH -D ./ 
#SBATCH -J 1620 
#SBATCH --partition=long.q 
#SBATCH --nodes=1 
#SBATCH --cpus-per-task=8 
#SBATCH --mem=15360 
#SBATCH --time=40:00:00 

echo "NODE: "$HOSTNAME 
echo "Space on node:"
df -h 


DDl="460.0" 
DDh="660.0" 
step="0.0" 
downsamp="1" 
orig_fil="/hercules/results/ghil/1620/20200619/FRB121102_20200619_5_merged_4577636_9155272.fil" 
tmpdir="/tmp/FRB121102_20200619_5_merged_4577636_9155272" 
tmpfil=$tmpdir"/FRB121102_20200619_5_merged_4577636_9155272.fil" 
result_dir="/hercules/results/ghil/1620/20200619/results/FRB121102_20200619_5_merged_4577636_9155272" 
code_dir="/hercules/u/ghil/NEW_PIPE_TEST/new_SPS_pipeline/" 
prepdir=$tmpdir"/prepsub" 
f="FRB121102_20200619_5_merged_4577636_9155272.fil" 
p="prepsub" 
s="subdir" 
spsplot=$prepdir"/FRB121102_20200619_5_merged_4577636_9155272_singlepulse.ps" 

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
