asyncio-executor
===============================

* version: 0.0.3

* status: dev

* author: hsz

* email: hsz1273327@gmail.com

Desc
--------------------------------

Asyncio executor for running coroutines. This code is from <https://gist.github.com/seglberg/0b4487b57b4fd425c56ad72aba9971be>


keywords:asyncio,executor


Feature
----------------------
* run coroutines asynchronously

Example
-------------------------------

* run coroutines by using `submit`


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



* run coroutines by using map

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


* run functions by using submit


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

* run functions by using map

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

* only support python 3.5+ 