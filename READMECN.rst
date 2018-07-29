asyncio-executor
===============================

* version: 0.0.4

* status: dev

* author: hsz

* email: hsz1273327@gmail.com

Desc
--------------------------------

asyncio的执行器,满足`concurrent.futures.Executor`接口,这个实现参考了
<https://gist.github.com/seglberg/0b4487b57b4fd425c56ad72aba9971be>
这个执行器可以执行协程或者函数,其原理是创建一个线程用于执行事件循环,
而主线程则用于管理这个执行时间循环的子线程.

由于是多线程执行事件循环,因此实现的时候使用的是线程安全的
`run_coroutine_threadsafe`和`call_soon_threadsafe`来操作.


keywords:asyncio,executor


Feature
----------------------

* 使用python3.5后的原生协程执行异步任务
* 如果是函数则将函数包装为协程利用多线程/多进程执行器执行


Example
-------------------------------

* 使用`submit`接口提交协程任务


.. code:: python


    from concurrent.futures import as_completed
    import aiohttp
    from asyncio_executor import AsyncioExecutor

    async def httpget(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                html = await resp.text("utf-8")
        return len(html)

    with AsyncioExecutor() as executor:
        to_do = []
        urls = ["https://github.com/","https://docs.aiohttp.org/"]
        for i in urls:
            job = executor.submit(httpget,i)
            to_do.append(job)

        for future in as_completed(to_do):
            res = future.result()
            print(res)


* 使用`map`接口执行协程任务

.. code:: python


    from concurrent.futures import as_completed
    import aiohttp
    from asyncio_executor import AsyncioExecutor

    async def httpget(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                html = await resp.text("utf-8")
        return len(html)

    with AsyncioExecutor() as executor:
        result = []
        urls = ["https://github.com/", "https://docs.aiohttp.org/"]
        for i in executor.map(httpget, urls):
            result.append(i)

    print(result)


* 使用`submit`接口提交可执行对象任务


.. code:: python


    from concurrent.futures import as_completed
    import requests as rq
    from asyncio_executor import AsyncioExecutor

    def httpsync(url):
        req = rq.get(url)
        return len(req.text)

    with AsyncioExecutor() as executor:
        to_do = []
        urls = ["https://github.com/", "https://docs.aiohttp.org/"]
        for i in urls:
            job = executor.submit(httpsync, i)
            to_do.append(job)

        for future in as_completed(to_do):
            res = future.result()
            print(res)


* 使用`map`接口执行可执行对象任务

.. code:: python


    from concurrent.futures import as_completed
    import requests as rq
    from asyncio_executor import AsyncioExecutor

    def httpsync(url):
        req = rq.get(url)
        return len(req.text)

    with AsyncioExecutor() as executor:

        result = []
        urls = ["https://github.com/", "https://docs.aiohttp.org/"]
        for i in executor.map(httpsync, urls):
            result.append(i)
    print(result)


Install
--------------------------------

- ``python -m pip install asyncio-executor``



Limitations
------------------------------

* 要求python 3.6+