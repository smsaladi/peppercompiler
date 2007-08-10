"""Wrapper for Vienna RNAfold."""
import os, tempfile

import RNAfold_grammar as gram

#Globals
#par_file = "/research/src/ViennaRNA-1.4/dna.par"
#RNAfold  = "/research/bin/RNAfold";
par_file = "dna.par"
RNAfold = "RNAfold"

### TODO: This is not the most efficient?
def tempfilename(*args, **keys):
  fd, filename = tempfile.mkstemp(*args, **keys)
  os.close(fd)
  return filename

BREAK = "NNNNN" # Fake sequence used for strand break
def DNAfold(seq, temp, pf=False):
  """Runs Vienna RNAfold on sequence 'seq' at temp 'temp' (with partition function calc if 'pf' is True)."""
  infilename  = tempfilename(prefix="rna_in")
  outfilename = tempfilename(prefix="rna_out")

  # Make dummy sequence which has our fake strand break (because RNAfold can't handle multistranded folding)
  dummy_seq = seq.replace("+", BREAK)

  # Write inputs
  infile = file(infilename, "w")
  infile.write("%s\n" % dummy_seq)
  infile.close()
  
  # Call RNAfold
  if pf:
    command = "%s -p -T %f -P %s < %s > %s" % (RNAfold, temp, par_file, infilename, outfilename)
  else:
    command = "%s -T %f -P %s < %s > %s" % (RNAfold, temp, par_file, infilename, outfilename)
  stat = os.system(command)
  if stat != 0:
    raise OSError, "RNAfold failed with status (%d)" % stat
  os.remove(infilename)
  
  # Read results
  struct, dG = gram.parseFile(outfilename)
  os.remove(outfilename)

  # Fix the structure to account for the fake strand breaking
  while BREAK in dummy_seq:
    n = dummy_seq.find(BREAK)
    dummy_seq = dummy_seq[:n] + "+" + dummy_seq[n+len(BREAK):]
    struct = struct[:n] + "+" + struct[n+len(BREAK):]
  assert seq == dummy_seq
  assert len(struct) == len(dummy_seq)
  
  return struct, dG
