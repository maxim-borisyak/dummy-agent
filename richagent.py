#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

from agent import Agent, receive_method
from functial import *

class RichAgent(Agent):
  def __init__(self, *args, **kwargs):
    Agent.__init__(self, *args, **kwargs)

  @receive_method
  def defer(self, message):
    """
    The best way to defer a message is to send it to itself.
    Use it carefully with extra attention.
    """
    self.send(self, message)

  def become(self, *funcs):
    if len(funcs) != 0 and funcs[0] is not None:
      mixin_funcs = funcs + (self.mortal, self.ignore)
      Agent.become(self, *mixin_funcs)
    else:
      Agent.become(self, *funcs)

  @receive_method
  def ignore(self, message):
    pass

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