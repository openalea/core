# Observer test

from openalea.core.observer import *
import gc

class NotifyException(Exception):
    pass


destroyflag = False
notified = False
class mylistener(AbstractListener):

    def notify (self, *args):
        global notified 
        notified = True
        raise NotifyException()


    def __del__(self):
        global destroyflag
        destroyflag = True


    @lock_notify
    def process(self, obv):
        # obv is an observer
        obv.notify_listeners()




class myobserved(Observed):
    pass


# Normal notification
def test_notification():

    l = mylistener()
    o = myobserved()

    l.initialise(o)

    global notified 
    notified = False

    o.notify_listeners()
    assert notified == True
    
    

def test_destruction():

    l = mylistener()
    o = myobserved()

    l.initialise(o)

    # del listener
    del(l)
    gc.collect()
    global destroyflag
    assert destroyflag == True



# Test notification lock

def test_lock():

    l = mylistener()
    o = myobserved()

    l.initialise(o)


    try:
        l.process(o)
        assert True
    except NotifyException:
        assert False

