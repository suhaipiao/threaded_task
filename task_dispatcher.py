import os
import queue
import threading
import time

from task_scheduling_framework_package.task_scheduling_framework.utils import LogHelper


class TaskDispatcher:
    def __init__(self, max_workers: int = 1,
                 do_work_callback=lambda work_item: LogHelper.log_warn(title="Work Callback Not Set",
                                                                       content="you should set this as fn(work_item:Any)->(is_ok:bool,result:Any,is_error_put_back:bool)"),
                 check_new_work_callback=lambda: LogHelper.log_warn(title='Check New Work Callback Not Set',
                                                                    content="you should set this as fn()->(is_ok:bool,work_list:[])"),
                 reply_new_result_callback=lambda result_item: LogHelper.log_warn(
                     title='Reply New Result Callback Not Set',
                     content="you should set this as fn(result_item)->(is_ok:bool,is_error_put_back:bool)")):

        if max_workers is None:
            max_workers = min(16, (os.cpu_count() or 1) + 4)

        if max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")
        self._max_workers = max_workers
        self._do_work_callback = do_work_callback
        self._check_new_work_callback = check_new_work_callback
        self._reply_new_result_callback = reply_new_result_callback
        self._work_queue = queue.SimpleQueue()
        self._result_queue = queue.SimpleQueue()
        self._threads = set()
        self._is_stop = False
        self._is_stop_lock = threading.Lock()

    def _do_work(self):
        while not self._is_stop:
            if not self._work_queue.empty():
                # work_item = None
                try:
                    work_item = self._work_queue.get_nowait()
                    is_ok, result, is_error_put_back = self._do_work_callback(work_item)
                    if is_ok:
                        LogHelper.log_info(title='Task Success',
                                           content=f'Task {work_item} execute successful, put result to result queue...')
                        self._result_queue.put(result)
                    else:
                        if is_error_put_back:
                            LogHelper.log_warn(title='Task Failed Put Back',
                                               content=f'Task {work_item} execute failed, put back to task queue...')
                            self._work_queue.put(work_item)
                except queue.Empty as e:
                    LogHelper.log_warn(title='Worker Queue Empty', content='Waiting more task to do...')
                    time.sleep(3)
        LogHelper.log_info(title='Worker Thread Exited',
                           content=f'Worker thread {threading.current_thread().name} exited...OK')

    def _check_new_work(self):
        while not self._is_stop:
            if self._work_queue.qsize() < self._max_workers:
                try:
                    LogHelper.log_info(title='Check New Work', content='Checking new work...')
                    is_ok, work_list = self._check_new_work_callback()
                    if is_ok:
                        for w in work_list:
                            self._work_queue.put(w)
                except Exception as e:
                    LogHelper.log_error(title='Check New Work', content=f'Check new work failed: {e}')
                    time.sleep(5)

            else:
                time.sleep(2)
        LogHelper.log_info(title='Check New Work Thread Exited',
                           content=f'Check new work thread exited...OK')

    def _reply_new_result(self):
        while not self._is_stop:
            if not self._result_queue.empty():
                try:
                    result_item = self._result_queue.get_nowait()
                    is_ok, is_error_put_back = self._reply_new_result_callback(result_item)
                    if is_ok:
                        LogHelper.log_info(title='Reply Result Success',
                                           content=f'Reply 1 result success...OK')
                    else:
                        if is_error_put_back:
                            LogHelper.log_warn(title='Reply Result Failed Put Back',
                                               content=f'Reply 1 result failed, put back to result queue...')
                            self._result_queue.put(result_item)
                except queue.Empty as e:
                    LogHelper.log_warn(title='Result Queue Empty', content='Waiting task to do or finish...')
                    time.sleep(1)
                except Exception as ex:
                    LogHelper.log_error(title='Reply Result Error', content=f'Reply result failed: {ex}')
                    time.sleep(1)
            else:
                time.sleep(2)