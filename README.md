# Dummy agent


Dummy Python realisation of multi-agent toolkit.
It is designed to be similar to Akka as much as it possible in simple way.

There are only two basic objects:

* execution context
* agent

## Execution context
Execution context is interface for the basic operations over agents:

* spawning an agent
* transfering messages
* stoping an agent
 
Also it provides guard agent, that receives all error- and kill-messages.

There are two realisations of execution context:

* sequential execution context (`SeqExecutionContext`)
* python-thread based one (`ThreadBasedExecutionContext`)
 
The first one call agent one by one until there are not any agents with unhandled messages.

The second one launches each agent on new thread. Communication is based on pipes. Also each operation in the context will lock the mutex, so there are no way to sending messages concurently. So it is `dummy-agent`.

## Agent

To define an agent you have to define it's receive function. The best way is to subclass `Agent` or `RichAgent` (the last one contains some extra functions).

Basic functions defined in `Agent` class:

* `send(whom, message)`
* `become(*receive_functions)`

There are some useful features provided in module `functional` to define receive function.

First of all, it is a little piece of pattern matching.
`case(*predicates_or_constants)` forms the predicate that matchs only defined types of messages. For example,
`case('REPLY', an_agent, a_str)` will match only 3-item tuples iff the first value equals to 'REPLY', the second value is a possible reference to agent (actually any string), the third one is some string.

You can form partial applyed function from the list `[predicate, function, predicate, function, ...]`.
Usually it looks like:
```python
receive = match([
  case('REPLY', an_agent, a_str), self.reply,
  case('INC', an_int), self.inc,
  case('GET', an_agent), self.get
])
```

or you can use `match_method(predicate)(method)` or `case_method(*predicates_or_constants)(method)` (as decorators) like:
```python
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
```

The `become` method automatically combines methods.

Each agent is addressed by name. Usually it is something like `/system/my-agent` (`/system` is the name of the guard agent).
