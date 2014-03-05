#! /usr/bin/python
# Module: execution context
# Author: Maxim Borisyak, 2014

"""
  Not so effective realisation of basic operations over agent:
   - transfer messages,
   - launching new agent,
   - shutdown an agent,
   - some operations, like generation of default names.

  Each operation, like transfer, lock the only mutex,
  so, for example, you can not transfer two messages simultaneously.
  But, for Python threads, it is normal, because really
  there is only one execution flow.
"""

from executioncontext import ExecutionContext
from multiprocessing import Pipe
from threading import Thread, Lock

class AgentThread(Thread):
  def __init__(self, agent, pipe):
    Thread.__init__(self)
    self.pipe = pipe
    self.agent = agent

  def run(self):
    try:
      while True:
        message = self.pipe.recv()
        self.agent.incoming(message)
        self.agent.process()
    except EOFError:
      pass

class ThreadBasedExecutionContext(ExecutionContext):

  def generate_name(self):
    self.lock.acquire()
    name = 'agent' + str(self.name_counter)
    self.name_counter += 1
    self.lock.release()
    return name

  def get_parent(self):
    return self.guard.name

  def __init__(self, print_level = 2):

    self.name_counter = 0
    self.lock = Lock()
    self.threads = dict()
    self.pipes = dict()
    self.agents_by_name = dict()

    ExecutionContext.__init__(self, print_level)

  def lifecycle(self):
    pass

  def launch(self, agent):
    self.lock.acquire()
    try:
      pipe_parent, pipe_child = Pipe()
      new_agent_thread = AgentThread(agent, pipe_child)
      self.threads[agent] = new_agent_thread
      self.pipes[agent] = pipe_parent
      self.agents_by_name[str(agent)] = agent
      new_agent_thread.start()
      self.info('Agent', agent, 'was launched')
    finally:
      self.lock.release()

    return agent

  def shutdown_agent(self, agent, hard=False, wait=False):
    self.lock.acquire()
    try:
      self._shutdown_agent(agent, hard, wait)
    finally:
      self.lock.release()

  def _shutdown_agent(self, agent, hard=False, wait=False):
    agent = self.agents_by_name.pop(str(agent), None)
    if agent is None:
      return

    pipe = self.pipes.pop(agent, None)
    pipe.close()
    thread = self.threads.pop(agent, None)

    if hard:
      thread.join(1.0)
      if thread.isAlive():
        raise Exception('Non-stop thread!')
    elif wait:
      thread.join()

    self.info('Agent', agent, 'was stopped')

  def _direct_transfer(self, from_agent, to_agent, message):
    self.debug('Transfer message', message, 'from', from_agent, 'to', to_agent)
    if type(to_agent) is str or type(to_agent) is unicode:
      if self.agents_by_name.has_key(to_agent):
        _to_agent = self.agents_by_name[to_agent]
      else:
        self._direct_transfer(self.guard, from_agent, ('ERROR', 'Unknown address', message))
        return
    else:
      _to_agent = to_agent

    if self.pipes.has_key(_to_agent):
      self.pipes[_to_agent].send(message)
    else:
      self._direct_transfer(self.guard, from_agent, ('ERROR', 'Unknown address', message))

  def transfer(self, from_agent, to_agent, message):
    self.lock.acquire()
    try:
      self._direct_transfer(from_agent, to_agent, message)
    finally:
      self.lock.release()

  def shutdown(self, hard=True, wait=False):
    self.lock.acquire()
    try:
      pipes = self.pipes.items()

      for agent, pipe in pipes:
        self._shutdown_agent(agent, hard, wait)

      self.pipes.clear()
      self.threads.clear()
      self.agents_by_name.clear()
    finally:
      self.lock.release()

