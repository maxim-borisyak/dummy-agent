#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

from ..agent import GuardAgent

class ExecutionContext:

  guard = None
  DEBUG_LEVEL = 4
  INFO_LEVEL = 3
  WARNING_LEVEL = 2
  ERROR_LEVEL = 1

  def __init__(self, print_level = 1):
    self.print_level = print_level
    self.guard = GuardAgent(self)

  def launch(self, agent):
    raise NotImplementedError

  def generate_name(self):
    raise NotImplementedError

  def get_parent(self):
    return self.guard

  def shutdown_agent(self, agent):
    raise NotImplementedError

  def shutdown(self, hard=True, wait=False):
    raise NotImplementedError

  def initiate(self, agent, message):
    self.transfer(self.guard, agent, message)
    self.lifecycle()

  def lifecycle(self):
    raise NotImplementedError

  def warning(self, *args):
    if self.print_level >= ExecutionContext.WARNING_LEVEL:
      print '[WARNING] ', " ".join(map(str, args))

  def error(self, *args):
    if self.print_level >= ExecutionContext.ERROR_LEVEL:
      print '[ ERROR ] ', " ".join(map(str, args))

  def info(self, *args):
    if self.print_level >= ExecutionContext.INFO_LEVEL:
      print '[  INFO ] ' + " ".join(map(str, args))

  def debug(self, *args):
    if self.print_level >= ExecutionContext.DEBUG_LEVEL:
      print '[ DEBUG ] ' + " ".join(map(str, args))

  def transfer(self, from_agent, to_agent, message):
    raise NotImplementedError

  def spawn(self, constructor, parent=None, name=None):
    agent = constructor(self, parent, name)
    return str(agent)