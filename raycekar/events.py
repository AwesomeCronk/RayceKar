import logging

from raycekar.util import loggingHandler


logger = logging.getLogger('rk.events')
logger.addHandler(loggingHandler)
logger.setLevel(logging.DEBUG)


events = []

class event:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback
        logger.debug('Created event "{}"'.format(self.name))

    def activate(self):
        if not self in events:
            logger.debug('Activating event "{}"'.format(self.name))
            events.append(self)

    def deactivate(self):
        if self in events:
            logger.debug('Deactivating event "{}"'.format(self.name))
            del(events[self])

    def fire(self, args=(), kwargs={}):
        logger.debug('Firing event "{}" (args={}, kwargs={})'.format(self.name, args, kwargs))
        self.callback(*args, **kwargs)

def getEventByName(name):
    for event in events:
        if event.name == name:
            return event
    return None
