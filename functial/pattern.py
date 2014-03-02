#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

class MatchError(Exception):
  def __init__(self, value, against=None):
    self.value = 'Match error: ' + str(value) +\
                 ((' against ' + str(against)) if against is not None else '')

  def __str__(self):
    return repr(self.value)

some = lambda _: True
otherwise = some

def constant(x):
  def f(y):
    return y == x
  return f

def an_int(x):
  return type(x) is int

def a_float(x):
  return type(x) is float

def a_str(x):
  return type(x) is str or type(x) is unicode

def a_class(t):
  def gen_an_t(x):
    return isinstance(x, t)
  return gen_an_t

def to_pattern(f_or_value):
  return f_or_value if callable(f_or_value) else constant(f_or_value)

def case(*args):
  f_args = [to_pattern(x) for x in args]

  def pattern(_message):
    message = [_message] if not hasattr(_message, '__iter__') else _message

    if len(f_args) != len(message):
      return False

    for pattern, message_part in zip(f_args, message):
      if not pattern(message_part):
        return False

    return True

  pattern.func_name = 'case' + str(args)

  return pattern