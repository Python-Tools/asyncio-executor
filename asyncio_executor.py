"""
协程执行器,起一个额外的线程执行事件循环,主线程则管理这个事件循环线程,
这个执行器不要用在协程中.

代码来自于<https://gist.github.com/seglberg/0b4487b57b4fd425c56ad72aba9971be>
"""
import asyncio
from concurrent import futures
import functools
import inspect
import threading


def _loop_mgr(loop: asyncio.AbstractEventLoop):
    """起一个线程执行事件循环.

    Params:
    loop (asyncio.AbstractEventLoop) : - 事件循环
    """
    if loop.is_closed():
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

    # 只有run_forever被中断才会进入这边收尾
    # 会收集来已经注册进来的任务然后把它们执行完
    # If we reach here, the loop was stopped.
    # We should gather any remaining tasks and finish them.
    pending = asyncio.Task.all_tasks(loop=loop)
    if pending:
        loop.run_until_complete(asyncio.gather(*pending))


class AsyncioExecutor(futures.Executor):
    """asyncio执行器,可以执行函数或者协程.

    Attributes:
    _shutdown (bool): - 执行器是否终止
    _loop (asyncio.AbstractEventLoop): - 事件循环
    _thread (threading.Thread): - 执行事件循环上任务的线程
    _func_executor (futures.Executor): - 如果使用执行器,那么默认使用什么执行器
    """

    def __init__(self, *,
                 loop: asyncio.AbstractEventLoop=None,
                 func_executor: futures.Executor=None):
        super().__init__()
        self._shutdown = False
        self._loop = loop or asyncio.get_event_loop()
        self._func_executor = func_executor or futures.ThreadPoolExecutor()
        self._loop.set_default_executor(func_executor)
        self._thread = threading.Thread(target=_loop_mgr,
                                        args=(self._loop,),
                                        daemon=True)
        self._thread.start()

    def submit(self, fn, *args, **kwargs):
        """提交任务.

        Params:

        fn (Union[callable,coroutinefunction]): - 要执行的函数或者协程函数
        *args/**kwargs : - fn的参数

        Return:

        (asyncio.Future) : - 丢进loop后的future对象
        """
        if self._shutdown:
            raise RuntimeError(
                'Cannot schedule new futures after shutdown')

        if not self._loop.is_running():
            raise RuntimeError(
                "Loop must be started before any function can "
                "be submitted")

        if inspect.iscoroutinefunction(fn):
            # 如果是协程对象,那么就使用run_coroutine_threadsafe将协程放入事件循环
            # `asyncio.run_coroutine_threadsafe`返回一个`concurrent.futures.Future`对象
            # 因此需要将其包装一下成为`asyncio.Future`对象
            coro = fn(*args, **kwargs)
            fu = asyncio.run_coroutine_threadsafe(coro, self._loop)
            # return futures.wrap_future(fu,loop=self._loop)
            return fu

        else:
            # 如果是其他可执行对象,那么就使用run_in_executor将可执行对象委托给执行器放入事件循环
            # 返回一个`asyncio.Future`对象
            #func = functools.partial(fn, *args, **kwargs)
            # return self._loop.run_in_executor(None, func)
            # return self._func_executor.submit(func)
            raise RuntimeError(
                "AsyncioExecutor can only run coroutine")

    def shutdown(self, wait=True):
        self._loop.stop()
        self._shutdown = True
        if wait:
            self._thread.join()
