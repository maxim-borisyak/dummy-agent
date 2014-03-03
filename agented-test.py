#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

import unittest

from agent import *
from testagent import *
from executioncontext import ThreadBasedExecutionContext

class PatternMatchingTestCase(unittest.TestCase):

  def test_case(self):
    even = lambda x: x % 2 == 0
    c1 = case(1, an_int, 'MATCH', even)

    self.assertTrue(c1((1, 2, 'MATCH', 2)))
    self.assertFalse(c1((1, 2, 'MATCH', 3)))
    self.assertFalse(c1((2, 2, 'MATCH', 2)))
    self.assertFalse(c1((2, 2, 'MATH', 2)))

  def test_match_function(self):
    even = lambda x: x % 2 == 0

    f = merge_matches([
      match_f(even)(lambda n: n / 2),
      case_f(an_int)(lambda n: n + 1),
      case_f(an_int)(lambda n: n * 10), # 'never' method
      case_f(a_str)(lambda s: s + '!'),
      case_f(a_float)(lambda z: z + 1.0),
    ])

    self.assertEqual(f(1), 2)
    self.assertEqual(f(2), 1)
    self.assertEqual(f(3), 4)
    self.assertEqual(f('sss'), 'sss!')
    self.assertEqual(f(1.0), 2.0)

  def test_match(self):
    from math import sqrt

    f = match([
      case('INC', an_int), lambda (_, x): x + 1,
      case('SQRT', a_float), lambda (_, d): sqrt(d),
      case(a_str), lambda s: s + '!!!',
      case('+', an_int, some), lambda (_, x, y): x + y,
      otherwise, lambda x: x
    ])

    self.assertEqual(f(('INC', 1)), 2)
    self.assertEqual(f(('SQRT', 4.0)), 2.0)
    self.assertEqual(f('SQRT'), 'SQRT!!!')
    self.assertEqual(f(('+', 1)), ('+', 1))
    self.assertEqual(f(('+', 1, 2)), 3)

class AgentSystemTestCase(unittest.TestCase):
  def setUp(self):
    self.system = ThreadBasedExecutionContext(ThreadBasedExecutionContext.INFO_LEVEL)

  def test_agent_system(self):
    ok = case('OK')
    answer = lambda x: case('ANSWER', constant(x))

    scenario = [
      ('/system/incrementer', ('SET', '/system/test', 1), ok),
      ('/system/incrementer', ('INC', '/system/test', 1), answer(2)),
      ('/system/incrementer', ('SET', '/system/test', 2), ok),
      ('/system/incrementer', ('INC', '/system/test', 5), answer(7))
    ]

    class Incrementer(RichAgent):
      __inc = 0

      @case_method('INC', an_agent, an_int)
      def receive_inc(self, (_, whom, x)):
        self.send(whom, ('ANSWER', x + self.__inc))

      @case_method('SET', an_agent, an_int)
      def receive_set(self, (_, whom, x)):
        self.__inc = x
        self.send(whom, ('OK', ))

      def setup(self):
        self.__inc = 0
        self.become(self.receive_inc, self.receive_set)

    try:
      Incrementer(execution_context=self.system, name='incrementer')
      answers = TestAgent(scenario=scenario, execution_context=self.system, name='test').get_answers()

      matcher = [ok, answer(2), ok, answer(7)]
      self.assertTrue(all([p(x) for x, p in zip(answers, matcher)]))
    finally:
      self.system.shutdown(True, False)
