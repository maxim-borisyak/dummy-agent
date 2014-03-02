#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

from richagent import RichAgent
from functial import *
from threading import Event

class TestAgent(RichAgent):
  def __init__(self, scenario, *args, **kwargs):
    RichAgent.__init__(self, *args, **kwargs)

    self.__iterator = iter(scenario)
    self.__answers = list()
    self.__event = Event()
    self.__next()

  def __next(self):
    try:
      agent, msg, matcher = self.__iterator.next()
      self.send(agent, msg)
      if matcher is None:
        self.__next()
      else:
        self.become(self.expect(to_pattern(matcher)))
    except StopIteration:
      self.__event.set()

  def get_answers(self):
    self.__event.wait()
    return self.__answers

  def expect(self, matcher):
    def gen_receive(message):
      if matcher(message):
        self.__answers.append(message)
        self.__next()
      else:
        raise Exception('Bad incoming: %s' % str(message))

    return gen_receive