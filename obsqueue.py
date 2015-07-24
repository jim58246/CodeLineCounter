"""
Observer queue class
"""
__author__ = 'jim'


import queue
import time


class ObsQueue:
    instance_count = 0
    the_instance = None

    def __init__(self, process_in_main_thread=False):
        """
        process_in_main_thread: if yes, put will not put the action in the queue but immediately execute the action.
          it can be adjusted dynamically.
          Due to this design, whenever there is a second thread, the GUI in main thread should keep user from
          any modification, it becomes a pure observer. Under this design, some thread synchronous problem will
          be avoid.
        """
        self._q = queue.Queue()
        self.process_in_main_thread = process_in_main_thread
        ObsQueue.the_instance = self
        ObsQueue.instance_count += 1
        if ObsQueue.instance_count > 1:
            raise RuntimeError('Class ObsQueue can have only one instance.')

    def wait_sync(self):
        """
        wait until all previous event handled. Can be used to synchronous an event.
        """
        self._q.join()

    def put(self, observer, *args, **kwargs):
        if self.process_in_main_thread:
            observer(*args, **kwargs)
        else:
            item_to_put = (observer, args, kwargs)
            self._q.put(item_to_put)

    def process(self, timeout=None, print_trace=False):
        """
        return time consumed.
        """
        start_time = time.perf_counter()
        while True:
            try:
                func, args, kwargs = self._q.get(block=False)
            except queue.Empty:
                break
            else:
                if print_trace:
                    print('call func "{}" with parameters {}, {}'.format(func, args, kwargs))
                func(*args, **kwargs)
                self._q.task_done()  # Put after func call. Because func is the task.
                if timeout:
                    if time.perf_counter() - start_time > timeout:
                        break

        return time.perf_counter() - start_time


if __name__ == '__main__':
    oq = ObsQueue()
    try:
        oq2 = ObsQueue()
    except RuntimeError as err:
        print(err)

    oq.put(lambda x: print(x), 1)
    oq.put(lambda x: print(x), x='hello')

    print('time consumed:', oq.process())
    oq.put(lambda: time.sleep(1))
    oq.put(lambda: print('should not be printed in main thread.'))
    oq.process(0.5)
    print(oq._q.qsize())

    import threading
    threading.Thread(target=oq.process, args=(), daemon=True).start()
    oq.wait_sync()
