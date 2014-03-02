#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

import functools

partial = functools.partial

from pattern import MatchError
from pattern import case
from pattern import to_pattern

# Type patterns
from pattern import a_class
from pattern import a_str
from pattern import a_float
from pattern import an_int

# General patterns
from pattern import some
from pattern import otherwise
from pattern import constant

from match import match
from match import match_f
from match import case_f
from match import match_method
from match import case_method
from match import merge_matches
from match import to_match