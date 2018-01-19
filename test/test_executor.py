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
        



with AsyncioExecutor() as executor:
    result = []
    urls = ["https://github.com/","https://docs.aiohttp.org/"]
    for i in executor.map(httpget,urls):
        result.append(i)
