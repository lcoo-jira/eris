import pykka

class TaskStatus(object):
    INIT = "init"
    STOPPED = "aborted"
    ABORTED = "aborted"
    FINISHED ="finished"

class BaseLoader(pykka.ThreadingActor):
    def __init(self, observer, openrc, inventory, **params):
        pass
