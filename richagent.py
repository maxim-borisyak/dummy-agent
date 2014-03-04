#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

from agent import Agent, receive_method
from functial import *

class RichAgent(Agent):
  def __init__(self, *args, **kwargs):
    self._activities = list()
    self._postponed_messages = list()
    Agent.__init__(self, *args, **kwargs)

  def add_activity(self, activity):
    self._activities.append(activity)

  def _process_activity(self, message):
    for activity in self._activities:
      try:
        result = activity(message)
        self._activities.remove(activity)
        return result
      except MatchError as e:
        raise e

  def process(self):
    Agent.process(self)

    postponed = self._postponed_messages[:]
    self._postponed_messages = list()
    for m in postponed:
      self._process_message(m)

  def _process_message(self, message):
    for activity in self._activities:
      try:
        result = activity(message)
        self._activities.remove(activity)
        return result
      except MatchError:
        pass

    Agent._process_message(self, message)

  @receive_method
  def postpone(self, message):
    self._postponed_messages.append(message)

  def become(self, *funcs):
    mixin_funcs = funcs + (self.mortal, self.ignore)
    Agent.become(self, *mixin_funcs)

  @receive_method
  def ignore(self, message):
    pass

  @receive_method
  def unexpected(self, message):
    raise Exception('Unexpected message', message)

  @case_method('KILL')
  def mortal(self):
    """
    After receiving a 'KILL' message agent starts ignore all
    incoming messages and ask the guard agent to kill itself, that
    causes closing the connection pipe and so stop of the thread.
    """
    self.become(self.ignore)
    self.shutdown()

  def shutdown(self):
    self.send(self.execution_context.guard, ('KILL', self.name))