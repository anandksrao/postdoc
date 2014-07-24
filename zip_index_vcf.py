import glob
import subprocess
import re

files = glob.glob('/mnt/lustre/home/sonal.singhal1/ZF/phasing/family_approach/unrel_vcf/by_chr/*poly*')

for vcf in files:
	call = '~/bin/tabix-0.2.6/bgzip %s' % vcf
	chr = re.search('(chr[A-Z|0-9|\_|a-z]+)', vcf).group(1)
	# subprocess.call('echo \'%s\' | qsub -l h_vmem=1g -cwd -V -j y -N \'%s\'' % (call, 'zip_' + chr), shell=True)
	subprocess.call('echo \'~/bin/tabix-0.2.6/tabix -p vcf %s\' | qsub -l h_vmem=1g -cwd -V -j y -N \'%s\'' % (vcf, 'ind_' + chr), shell=True) 