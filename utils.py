"""Useful classes and functions."""
from __future__ import division

import math
import os
import random
import re
import string
import tempfile

class ParseException(Exception): pass

def match(regex, line):
  """Match *entire* line to regex converting all spaces into '\s+' and allowing trailing spaces."""
  regex = regex.replace(" ", r"\s+")
  regex += r"\s*\Z"
  parse = re.match(regex, line)
  if parse:
    return parse.groups()
  else:
    raise ParseException("regex '%s' does not match line:\n%r" % (regex, line))

def search_file(filename, search_path):
  """Find a file with this name in search_path."""
  for dir in search_path:
    file_path = os.path.join(dir, filename)
    if os.path.isfile(file_path):
      return file_path
  
  return None


def error(text):
	"""Return a formatted error message."""
	red = "\033[31;1m"  # ASCI color code for bold red
	reset = "\033[m"    # ASCI color code for reset color
	return red + "ERROR: " + text + reset + "\n"

def mktemp(mode, *args, **keys):
  """Creates a temporary file. Returns the file and filename.
     Like tempfile.mkstemp except that it actually creates a file object."""
  fd, filename = tempfile.mkstemp(*args, **keys)
  file_ = os.fdopen(fd, mode)
  return file_, filename


def _dummy(*args, **kw):
  """A method not available function."""
  raise Exception, "methods not available"


class URandom(random.Random):
  """An actual random number generator (using urandom)"""
  def random(self):
    return self.getrandbits(64) / 2**64
  
  def getrandbits(self, nbits):
    """Get n random bits from urandom."""
    nbytes = int(math.ceil( nbits / 8. ))
    
    rand_bytes = os.urandom(nbytes)
    
    rand = 0
    for byte in rand_bytes:
      rand = rand*256 + ord(byte)
    
    return rand % 2**nbits
  
  def seed(self, *args, **keys):
    """There is no seed, there is no state."""
    pass
  
  setstate = getstate = _dummy

urandom = URandom() # Singleton urandom object


## Generic Objects
class ordered_dict(dict):
  """A standard dictionary that remembers the order you added items in.
     Only supports __setitem__, __iter__, keys, values, items and read-only ops."""
  def __init__(self):
    self.order = []
    dict.__init__(self)
  
  def get_index(self, index):
    return self[self.order[index]]
  
  def __setitem__(self, key, value):
    if key not in self:
      self.order.append(key)
    dict.__setitem__(self, key, value)
  def __iter__(self):
    for key in self.order:
      yield key
  def keys(self):
    return self.order
  def values(self):
    return [self[key] for key in self]
  def items(self):
    return [(key, self[key]) for key in self]
  
  def __delitem__(self, key):
    self.order.remove(key)
    dict.__delitem__(self, key)
  ### TODO-maybe: impliment clear, copy, iter*, ...
  clear = copy = iteritems = iterkeys = itervalues = pop \
        = popitem = update = fromkeys = _dummy

class default_ordered_dict(ordered_dict):
  """An ordered dictionary automatically defaults to a given value on unset key.
     With the call=True flag, the default will be assumed a function and called each time."""
  def __init__(self, default=None, call=False):
    self.default = default
    self.call = call
    ordered_dict.__init__(self)
  def __getitem__(self, key):
    if not self.call:
      return self.get(key, self.default)
    else:
      return self.get(key, self.default())

class ordered_set(set):
  """A standard set that remembers the order you added items in.
     Only supports add, update, __iter__ and read-only ops."""
  def __init__(self):
    self.order = []
    set.__init__(self)
  def add(self, value):
    if value not in self:
      self.order.append(value)
      set.add(self, value)
  def update(self, other):
    for value in other:
      self.add(value)
  def __iter__(self):
    for value in self.order:
      yield value
  
  ### TODO-maybe: impliment clear, copy, ...
  clear = copy = difference = difference_update = discard = intersection \
        = intersection_update = pop = remove = symmetric_difference \
        = symmetric_difference_update = union = _dummy

class PrintObject(object):
  """Generic default-printable object."""
  def __str__(self):
    attribs = ["%s=%r" % (name, value) for (name, value) in self.__dict__.items()]
    attribs = string.join(attribs, ", ")
    return "%s(%s)" % (self.__class__.__name__, attribs)
  __repr__ = __str__
