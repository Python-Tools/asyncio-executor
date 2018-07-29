import asyncio
import functools
import inspect
import threading
from concurrent import futures
from typing import (Union, Callable, Any, Optional)


def _loop_mgr(loop: asyncio.AbstractEventLoop)->None:
    """起一个线程执行事件循环的`run_forever`方法.
    
    [Start up a thread for running the eventloop's `run_forever` method.]

    当它被终止时会清理未完结的协程,但不会关闭事件循环
    [When it shutdown, all the coroutines will be closed.but the eventloop will not close.]

    Params:
        loop (asyncio.AbstractEventLoop) : - 事件循环[the eventloop]

    """
    if loop.is_closed():
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())


async def func_executor_coroutine(
        func: Any,
        loop: Optional[asyncio.AbstractEventLoop]=None)->Any:
    """将函数使用`loop.run_in_executor`包装成协程函数.

    [wrap `loop.run_in_executor` as a coroutine function.]

    Params:

        func (callable) : - 需要使用执行器执行的函数[the function who need the executor to run].

        loop (asyncio.AbstractEventLoop) : - 事件循环[the eventloop]

    Return:

        (Any): - 执行器的执行结果[the result the func retruned ran in the executor]
    """
    _loop = loop or asyncio.get_event_loop()
    return await _loop.run_in_executor(None, func)


class AsyncioExecutor(futures.Executor):
    """asyncio执行器,可以执行函数或者协程.

    [Asyncio executor who can execute the function or coroutine.]

    Attributes:

        _shutdown (bool): - 执行器是否终止
        [the executor shutdowned or not]

        _loop (asyncio.AbstractEventLoop): - 事件循环
        [the eventloop]

        _thread (threading.Thread): - 执行事件循环上任务的线程
        [the thread who runs the tasks in the eventloop]

        _func_executor (futures.Executor): - 如果使用执行器执行函数,那么默认使用什么执行器
        [which executor will be used by default if must run a function]

    """

    def __init__(self, *,
                 loop: Optional[asyncio.AbstractEventLoop]=None,
                 func_executor: Optional[futures.Executor]=None)->None:
        super().__init__()
        self._shutdown = False
        self._loop = loop or asyncio.get_event_loop()
        self._func_executor = func_executor or futures.ThreadPoolExecutor()
        self._loop.set_default_executor(func_executor)
        self._thread = threading.Thread(target=_loop_mgr,
                                        args=(self._loop,),
                                        daemon=True)
        self._thread.start()

    def submit(self,
               fn: Any,
               *args: Any, **kwargs: Any)->futures.Future:
        """提交任务.

        [submit a task.]
        
        会先检查执行器是否已经关闭或者执行器的事件循环是否还在运行. 如果不是则会抛出一个运行时异常
        [It will check if the excutor has already closed or the eventloop is not running. 
        If yes, will throw a RuntimeError exception.]

        Params:

            ``fn (Union[callable,coroutinefunction])``: - 要执行的函数或者协程函数
            [the function or coroutinefunction who need to execute]

            ``*args/**kwargs`` : - fn的参数
            [the function's params]

        Return:

            (concurrent.futures.Future) : - 丢进loop后的future对象,因为使用的是`run_coroutine_threadsafe`方法,因此返回的是一个线程安全的`concurrent.futures.Future`对象.
            [the instance of Future, because of using the method `run_coroutine_threadsafe`,it will return a instance of `concurrent.futures.Future` who is thread safe.]

        Raise:

            (RuntimeError) : - 当执行器是已经关闭或者执行器的事件循环不在运行时,会抛出运行时异常表明无法执行该操作.
            [when the excutor has already closed or the eventloop is not running.]

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
            return fu

        else:
            # 如果是其他可执行对象,那么就使用run_in_executor将可执行对象委托给执行器放入事件循环
            func = functools.partial(fn, *args, **kwargs)
            coro = func_executor_coroutine(func)
            fu = asyncio.run_coroutine_threadsafe(coro, self._loop)
            return fu

    def shutdown(self, wait: bool=True, timeout: int=None)->None:
        """关闭执行器

        [Close the executor.]

         Params:

            wait (bool): - 是否等待线程同步
            [if waitting for syncing the thread or not.]

            timeout (int): - wait为True时才有效果,设置join的等待时间
            [set the waitting time.it will take effect only when param `wait` is `True`.]]

        """
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._shutdown = True
        if wait:
            self._thread.join(timeout)
