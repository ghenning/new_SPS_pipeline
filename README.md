# Presto based single pulse seach pipeline

A heavily upgraded version of [the old one](https://github.com/ghenning/SPSpipe).

## Cluster usage

This pipeline is designed to operate on a Slurm based cluster.
runshell.py is a wrapper for main.py. Reads in filterbanks from
a directory and processes each one as a Slurm job. Returns
the standard single pulse search plot, along with customised
plots and candidate files. 

## "Local" use

The wrapper is not required, you can run main.py on a filterbank file
on a machine with Presto.

## Output files
* RFIfind mask
* Candidates sorted in time (and filtered)
* Modulation index of best candidates
* Single pulse search plot (original and colorised)
* DM over time plot
* Dedispersed time series and dynamic spectra of best candidates

