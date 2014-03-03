#! /usr/bin/python
# Module: 
# Author: Maxim Borisyak, 2014

from executioncontext import ExecutionContext

class SeqExecutionContext(ExecutionContext):

  involved_agents = set()
  name_counter = 0

  def __init__(self):
    ExecutionContext.__init__(self)

  def launch(self, agent):
    return agent

  def generate_name(self):
    name = 'agent' + str(self.name_counter)
    self.name_counter += 1
    return name

  def lifecycle(self):
    while len(self.involved_agents) > 0:
      previous_involved = self.involved_agents.copy()
      self.involved_agents.clear()
      for agent in previous_involved:
        try:
          agent.process()
        except Exception as e:
          self.transfer(agent, self.guard, ('ERROR', agent, e))

    print '[Execution Context] Agent system finished.'


  def transfer(self, from_agent, to_agent, message):
    to_agent.incoming(message)
    self.involved_agents.add(to_agent)

  def shutdown_agent(self, agent):
    pass

  def shutdown(self, hard=True, wait=False):
    pass