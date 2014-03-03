#! /usr/bin/python
# Module: Agent
# Author: Maxim Borisyak, 2014

from functial import *

class Agent:
  parent = None
  children = set()
  execution_context = None

  _message_queue = set()

  _current_receive = None

  name = ''

  def __init__(self, execution_context, receive_function=None, parent=None, name=None):
    self.execution_context = execution_context
    self.parent = parent if parent is not None else self.execution_context.get_parent()

    name_prefix = str(self.parent)
    name_postfix = name if name is not None else self.execution_context.generate_name()
    self.name = name_prefix + '/' + name_postfix

    if callable(receive_function):
      self._current_receive = partial(receive_function, self)

    self.execution_context.launch(self)
    self.setup()

  def setup(self):
    pass

  def __str__(self):
    return self.name

  def __repr__(self):
    return self.name

  def become(self, *funcs):
    if len(funcs) == 0 or funcs[0] is None:
      self._current_receive = self.receive
    else:
      self._current_receive = merge_matches(funcs)

  def send(self, whom, message):
    self.execution_context.transfer(self, str(whom), message)

  def incoming(self, message):
    self._message_queue.add(message)

  # To override.
  def receive(self, message):
    pass

  def process(self):
    mq = self._message_queue.copy()
    self._message_queue.clear()
    for m in mq:
      try:
        self._current_receive(m)
      except Exception as e:
        self.send(self.execution_context.guard, ('ERROR', self.name, str(e)))

    if len(self._message_queue) > 0:
      return self.process()

  def spawn(self, receive_function):
    agent = self.execution_context.spawn(receive_function, self)
    self.children.add(agent)
    return agent

class GuardAgent(Agent):
  def __init__(self, execution_context):

    Agent.__init__(self, execution_context, None, '', 'system')

    self.become(match([
      case('ERROR', an_agent, some), self.receive_error,
      case('KILL', an_agent)       , self.receive_shutdown,
      otherwise                    , self.receive_otherwise
    ]))

  def receive_otherwise(self, message):
    self.execution_context.warning('Guard receives:', message)

  def receive_error(self, (_, agent, e)):
    self.execution_context.error(e, 'is caused by', agent)

  def receive_shutdown(self, (_, agent)):
    self.execution_context.shutdown_agent(agent, False, False)

def an_agent(x):
  return isinstance(x, Agent) or a_str(x)

def receive_method(m):
  return match_method(otherwise)(m)