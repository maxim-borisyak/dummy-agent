#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

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

  def shutdown(self, agent, hard=False, wait=False):
    self.lock.acquire()
    try:
      self._shutdown(agent, hard, wait)
    finally:
      self.lock.release()

  def _shutdown(self, agent, hard=False, wait=False):
    agent = self.agents_by_name.pop(str(agent), None)
    if agent is None:
      return

    pipe = self.pipes.pop(agent, None)
    pipe.close()
    thread = self.threads.pop(agent, None)

    if hard:
      thread.join(0.5)
      if thread.isAlive():
        raise Exception('Non-stop thread!')
    elif wait:
      thread.join()

    self.info('Agent', agent, 'was stopped')

  def _direct_transfer(self, from_agent, to_agent, message):
    self.info('Transfer message', message, 'from', from_agent, 'to', to_agent)
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

  def shutdown_system(self, hard=True, wait=False):
    self.lock.acquire()
    try:
      pipes = self.pipes.items()

      for agent, pipe in pipes:
        self._shutdown(agent, hard, wait)

      self.pipes.clear()
      self.threads.clear()
      self.agents_by_name.clear()
    finally:
      self.lock.release()

