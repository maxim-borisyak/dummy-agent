#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

from richagent import RichAgent
from functial import *
from threading import Event, Timer


class TestAgent(RichAgent):
  def __init__(self, scenario, *args, **kwargs):
    RichAgent.__init__(self, *args, **kwargs)

    self.__iterator = iter(scenario)
    self.__answers = list()
    self.__event = Event()
    self.__timeout = False
    self.__timer = None
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

  def timeout(self):
    self.__event.set()
    self.__timeout = True

  def get_answers(self, timeout=None):
    if timeout is not None:
      self.__timer = Timer(timeout, self.timeout)
      self.__timer.start()

    self.__event.wait()

    if self.__timeout:
      raise Exception('Timeout!')
    elif self.__timer is not None:
      self.__timer.cancel()

    return self.__answers

  def expect(self, matcher):
    def gen_receive(message):
      if matcher(message):
        self.__answers.append(message)
        self.__next()
      else:
        raise Exception('Bad incoming: %s' % str(message))

    return gen_receive