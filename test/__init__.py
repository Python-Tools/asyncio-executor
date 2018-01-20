import unittest
from concurrent.futures import as_completed
import aiohttp
import requests as rq
from asyncio_executor import AsyncioExecutor


async def httpget(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text("utf-8")
    return len(html)


def httpsync(url):
    req = rq.get(url)
    return len(req.text)


def setUpModule():
    print("setUp asyncio executor test")


def tearDownModule():
    print("tearUp asyncio executor test")


class TestAdd(unittest.TestCase):

    def setUp(self):
        print("setUp urls")
        self.urls = ["https://github.com/", "https://docs.aiohttp.org/"]

    def test_function_submit(self):
        with AsyncioExecutor() as executor:
            to_do = []
            for i in self.urls:
                job = executor.submit(httpsync, i)
                to_do.append(job)
            for future in as_completed(to_do):
                res = future.result()
                assert res > 2000

    def test_function_map(self):
        with AsyncioExecutor() as executor:
            result = []
            for i in executor.map(httpsync, self.urls):
                result.append(i)
        for i in result:
            assert i > 2000

    def test_coroutine_submit(self):
        with AsyncioExecutor() as executor:
            to_do = []
            for i in self.urls:
                job = executor.submit(httpget, i)
                to_do.append(job)
            for future in as_completed(to_do):
                res = future.result()
                assert res > 2000

    def test_coroutine_map(self):
        with AsyncioExecutor() as executor:
            result = []
            for i in executor.map(httpget, self.urls):
                result.append(i)
        for i in result:
            assert i > 2000


def func_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestAdd("test_function_submit"))
    suite.addTest(TestAdd("test_function_map"))
    return suite


def coroutine_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestAdd("test_coroutine_submit"))
    suite.addTest(TestAdd("test_coroutine_map"))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(func_suite())
    runner.run(coroutine_suite())
