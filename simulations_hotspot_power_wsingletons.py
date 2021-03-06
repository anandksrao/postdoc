import numpy as np
import re
import sys
from itertools import izip
import subprocess
import random

def simulate(out_dir, seq_size, theta, nsam, eq_freq, mut_rates, rho, diffs, hotspot_lengths, ix):
	
	hotspot_file = '%shotspot_rho%s_%s.txt' % (out_dir, rho, ix)
	hotspot_f = open(hotspot_file, 'w')
	num_hotspots = len(diffs) * len(hotspot_lengths)
	starts = np.linspace(0+20e3,seq_size-20e3,num_hotspots)
	for i, diff in enumerate(diffs):
		for j, length in enumerate(hotspot_lengths):
			spot_start = starts[j + i * len(hotspot_lengths)]
			spot_end = spot_start + length
			hotspot_f.write('%.4f\t%.4f\t%.5f\n' % (spot_start / float(seq_size), spot_end / float(seq_size), diff))
	hotspot_f.close()	

	haplo_file = '%shaplo_rho%s_%s.fa' % (out_dir, rho, ix)
	anc_file = '%sancallele_rho%s_%s.txt' % (out_dir, rho, ix)
	haplo_f = open(haplo_file, 'w')
	anc_f = open(anc_file, 'w')

	macs = subprocess.Popen('~/bin/macs/macs %s %s -t %s -r %s -R %s | ~/bin/macs/msformatter' % (nsam, seq_size, theta, rho, hotspot_file), shell=True, stdout=subprocess.PIPE)

	positions = []
	haplo = []

	for l in macs.stdout:
		if re.match('^positions:', l):
			positions = [float(match) for match in re.findall('([\d\.e-]+)', l)]
		haplo.append(l.rstrip())			

	haplo = haplo[(len(haplo) - nsam):len(haplo)]
	for ix, hap in enumerate(haplo):
		haplo[ix] = list(hap)

	positions_changed = []
	for ix, pos in enumerate(positions):
		pos = int(round(pos * seq_size)) - 1 
		if pos < 0:
			pos = 0
		if pos > (seq_size - 1):
			pos = seq_size - 1
		positions_changed.append(pos)
	
	del positions
	
	bases = []
	for base, freq in eq_freq.items():
		bases += [base] * int(freq * 1000)
	seq = []
	for x in range(int(seq_size)):
		seq.append(random.choice(bases))

	mutations = {}
	
	for pos in positions_changed:
		anc = seq[pos]
		ran_num = random.random()
		for base, prob in mut_rates[anc].items():
			ran_num = ran_num - prob
			if ran_num < 0:
				mut = base
				nuc = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
				prob = [0.02, 0.02, 0.02, 0.02]
				prob[nuc[mut]] = 0.94
				anc_f.write('%s %s\n' % (pos, ' '.join('%.2f' % i for i in prob)))
				mutations[pos] = [anc, mut]
				break
	anc_f.close()

	for ind, ind_hap in enumerate(haplo):
		tmp_seq = seq[:]
		for hap_ix, bp in enumerate(ind_hap):
			if bp == '1':
				tmp_seq[positions_changed[hap_ix]] = mutations[positions_changed[hap_ix]][1]
		haplo_f.write('>haplo%s\n' % ind)
		for seq_i in xrange(0, len(tmp_seq), 60):
			haplo_f.write('%s\n' % ''.join(tmp_seq[seq_i:seq_i+60]))
	haplo_f.close()


def main():
	out_dir = '/mnt/gluster/home/sonal.singhal1/ZF/analysis/hotspot_simulations_wsingletons/'
	# sim MB
	seq_size = 1000000
	# num replicates to simulate
	num_sim = 1
	# num_sim = 1
	# hotspot / coldspot difference, > 1
	diffs = [2, 3, 5, 10, 50, 100]
	# diffs = [10]
	# mean rho values
	rhos = [0.0001, 0.001, 0.01, 0.1, 1.0, 2.5]
	# rhos = [0.0001]
	# hotspot length
	hotspot_lengths = [1000, 2000]
	# hotspot_lengths = [1000]
	# theta (per bp!)
	theta = 0.0135
	# number of haplotypes to sample
	nsam = 38
	# A, C, T, G
	eq_freq = {'A': 0.303,'C': 0.197, 'G': 0.305, 'T': 0.195}
	# mutation rates, modified from mutation matrix
	mut_rates = {'A': {'C': 0.191, 'G': 0.591, 'T': 0.218},
                     'C': {'A': 0.206, 'G': 0.135, 'T': 0.659},
                     'G': {'A': 0.659, 'C': 0.135, 'T': 0.206},
                     'T': {'A': 0.215, 'C': 0.600, 'G': 0.185}}
	
	for rho in rhos:
		for ix in range(num_sim):
			simulate(out_dir, seq_size, theta, nsam, eq_freq, mut_rates, rho, diffs, hotspot_lengths, ix)
	

if __name__ == "__main__":
    main()

