#!/bin/bash -l 

#SBATCH -o /herc/bla/log/1519.err.%j 
#SBATCH -D ./ 
#SBATCH -J 1519 
#SBATCH --partition=short.q 
#SBATCH --nodes=1 
#SBATCH --cpus-per-task=8 
#SBATCH --mem=15360 
#SBATCH --time=10:00:00 

echo "NODE: "$HOSTNAME 
echo "Space on node:"
df -h 


DDl="10" 
DDh="20" 
step="3" 
orig_fil="/hercules/results/ghil/1519/20200207/FRB1.fil" 
tmpdir="/tmp/FRB1" 
tmpfil=$tmpdir"/FRB1.fil" 
result_dir="/herc/bla/files/res/FRB1" 
code_dir="/herc/bla/code" 
prepdir=$tmpdir"/prepsub" 

if [ ! -d "$tmpdir" ]; then 
	 mkdir $tmpdir 
fi 

rsync -v $orig_fil $tmpdir 

singularity exec -B $code_dir:/work/ -B $tmpdir:/data/ /hercules/u/ghil/singularity/images/prestomod.simg python /work/main.py --dir /data/ --lodm $DDl --hidm $DDh --dmstep $step 

echo "rsync results back" 
rsync --exclude $tmpfil --exclude $prepdir $tmpdir/ $result_dir 
echo "removing temp dir on tmp: "$tmpdir 
rm -rf $tmpdir 
echo "it's gone, byebye "$tmpdir 

echo "NODE: "$HOSTNAME 
echo "Space on node:"
df -h 
