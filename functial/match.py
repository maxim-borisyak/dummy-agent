#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

from pattern import MatchError, to_pattern, case

def to_match(pattern, func):
  def gen_match(*args):
    if pattern(*args):
      return func(*args)
    else:
      raise MatchError(args)
  return gen_match

def to_pair_list(f_list):
  if type(f_list) is dict:
    return f_list.items()

  elif hasattr(f_list, '__iter__'):
    i = iter(f_list)
    pair_list = list()
    while True:
      try:
        pair_list.append((i.next(), i.next()))
      except StopIteration:
        return pair_list

def match(_f_list):
  f_list = [(to_pattern(p), f) for p, f in to_pair_list(_f_list)]

  def gen_match(*args):
    for pattern, func in f_list:
      if pattern(*args):
        return func(*args)

    raise MatchError(args)
  return gen_match

def merge_matches(func_list):
  assert all(map(callable, func_list))

  def merged_func(*args):
    for f in func_list:
      try:
        result = f(*args)
        return result
      except Exception:
        pass

    raise MatchError(args)
  return merged_func

def match_f(matcher):
  def decorator(f):
    def gen_f(*args):
      if matcher(*args):
        return f(*args)
      else:
        raise MatchError(args, matcher)
    return gen_f
  return decorator

def case_f(*args):
  return match_f(case(*args))

def match_method(matcher):

  def decorator(f):

    def gen_f(self, *args):
      if matcher(*args):
        return f(self, *args)
      else:
        raise MatchError(args, matcher)

    return gen_f

  return decorator

def case_method(*args):
  return match_method(case(*args))