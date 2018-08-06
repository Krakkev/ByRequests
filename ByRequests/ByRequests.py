import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import ast
import logging
import random
from lxml import html
import time
import eventlet
from eventlet.timeout import Timeout

ua = UserAgent()


class ByRequest():
    stats_class = {}

    def __init__(self, proxies=None, attempts=1, cookies=False, fake_ua=True, headers=False, timeout=False,
                 delay=False, delay_after=False, verify=True, logger=False, real_timeout=None):

        """
        Create object with the initial parameters
        :param proxies:
            * list of proxy services in execution order ["1st proxy service", "2nd", "3rd", ...]
            * str of the only proxy service that will be used
            * list of dicts of proxy services in priority order[
                                                 {"1st proxy service" : <<number of tries>>},
                                                 {"2nd proxy service" : <<number of tries>>},
                                                 ..]** The number of tries will override the max_retries param
            *** Use None to use no proxy server
        :param max_retries: integer of max number of retries by failed request for every proxy service
        :param cookies: RequestCookieJar or Dict or Str with the cookies that will persist for the whole request session
        :param fake_ua: Boolean to indicate if a Fake User-Agent will be used for the whole request session
            ** This User-Agent will override the one from the headers
        :param headers: Dict with the headers that will persist for the whole session
        :param timeout: Integer or String digit with the timeout for the request that will persist for the whole session
        :param real_timeout: Integer or String digit with the timeout of the whole requests process
        :param delay:
            * list [min, max] of the range of random seconds of wait between a request failed and a new retry
            * tuple (min, max) of the range of random seconds of wait between a request failed and a new retry
            * int or string digit of the max seconds of wait after a request failed
        :param verify: Boolean to indicate if the SSL verification is enabled or not
        :param logger: LoggingVariable with the logger configuration
        """
        if logger is not False:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.proxies = {}
        self.timeout = 15
        self.extras = {}
        self.delay = [0, 1]
        self.headers = {}
        self.cookies = {}
        self.verify = True
        self.delay_after = [0, 1]
        self.stats = {}

        if proxies:
            if isinstance(proxies, str):
                self.add_proxy(host=proxies, attempts=attempts)
            elif isinstance(proxies, dict):
                if proxies.get("http") and proxies.get("https"):
                    self.add_proxy(http=proxies.get("http"), https=proxies.get("https"), attempts=attempts)
                elif proxies.get("http"):
                    self.add_proxy(http=proxies.get("http"), attempts=attempts)
                    self.logger.warning("proxy host for http was not defined")
                elif proxies.get("https"):
                    self.add_proxy(https=proxies.get("https"), attempts=attempts)
                    self.logger.warning("proxy host for https was not defined")
                else:
                    self.logger.warning("proxy host for http and https were not defined")
        else:
            self.add_proxy(host=proxies, attempts=attempts)

        if real_timeout:
            try:
                self.real_timeout = int(real_timeout)
            except:
                self.logger.error("Real timeout value should be an integer or None")
                self.real_timeout = None
        else:
            self.real_timeout = None

        if headers:
            self.logger.debug("Assigning headers...")
            if isinstance(headers, dict):
                self.headers = headers
            elif isinstance(headers, str):
                try:
                    self.headers = ast.literal_eval(headers)
                except:
                    self.headers = {}
                    self.logger.error("Headers string cannot be converted to dict")
            else:
                self.logger.error("Headers are not valid")

        if fake_ua:
            self.logger.debug("Assigning fake User-Agent...")
            try:
                user_agent = ua.random
                self.headers['User-Agent'] = user_agent
            except Exception as e:
                self.logger.warning("The fake user agent cannot be added to headers")
                self.logger.error(e)

        if cookies:
            self.logger.debug("Assigning cookies...")
            if isinstance(cookies, requests.cookies.RequestsCookieJar) or isinstance(cookies, dict):
                self.cookies = cookies
            elif isinstance(cookies, str):
                if cookies[0] == "{" and cookies[-1] == "}":
                    try:
                        self.cookies = ast.literal_eval(cookies)
                    except:
                        self.logger.error("Cookies string cannot be converted to dict")
                else:
                    self.headers["cookie"] = cookies
            else:
                self.logger.error("Cookies are not valid")

        if timeout:
            self.logger.debug("Assigning timeout...")
            if isinstance(timeout, int):
                self.timeout = abs(timeout)
            else:
                try:
                    self.timeout = abs(int(timeout))
                except:
                    self.logger.error("Timeout cannot be converted to integer")

        if delay:
            self.logger.debug("Assigning delay...")
            if isinstance(delay, list) or isinstance(delay, tuple):
                if len(delay) == 2:
                    self.logger.debug("Assigning min & max seconds...")
                    try:
                        if int(delay[0]) < int(delay[1]):
                            self.delay[0] = int(delay[0])
                            self.delay[1] = int(delay[1])
                        else:
                            self.logger.error("delay[1] value should be higher than delay[0]")
                    except:
                        self.logger.error("Delay values cannot converted to integers")
                elif len(delay) == 1:
                    try:
                        self.logger.debug("Assigning max seconds...")
                        if int(delay[0]) > 1:
                            self.delay[1] = int(delay[0])
                        else:
                            self.logger.error("delay[0] value should be higher than 1")
                    except:
                        self.logger.error("Delay value cannot converted to integer")
                else:
                    self.logger.error("Delay should contain 1 or 2 integer values")
            else:
                try:
                    self.logger.debug("Assigning max seconds...")
                    if int(delay) > 1:
                        self.delay[1] = int(delay)
                    else:
                        self.logger.error("Delay value should be higher than 1")
                except:
                    self.logger.error("Delay value cannot be converted into integer")

        if delay_after:
            self.logger.debug("Assigning delay after request...")
            if isinstance(delay_after, list) or isinstance(delay_after, tuple):
                if len(delay_after) == 2:
                    self.logger.debug("Assigning min & max seconds...")
                    try:
                        if int(delay_after[0]) < int(delay_after[1]):
                            self.delay_after[0] = int(delay_after[0])
                            self.delay_after[1] = int(delay_after[1])
                        else:
                            self.logger.error("delay_after[1] value should be higher than delay_afer[0]")

                    except:
                        self.logger.error("Delay value values cannot converted to integers")
                elif len(delay_after) == 1:
                    try:
                        self.logger.debug("Assigning max seconds...")
                        if int(delay_after[0]) > 0:
                            self.delay_after[1] = int(delay_after[0])
                        else:
                            self.logger.error("delay[0] value should be higher than 0")
                    except:
                        self.logger.error("Delay after value cannot converted to integer")
                else:
                    self.logger.error("Delay after should contain 1 or 2 integer values")
            else:
                try:
                    self.logger.debug("Assigning max seconds...")
                    if int(delay_after) > 0:
                        self.delay_after[1] = int(delay_after)
                    else:
                        self.logger.error("Delay value should be higher than 0")
                except:
                    self.logger.error("Delay after value cannot be converted into integer")

        if verify is not True:
            self.verify = verify

    def add_proxy(self, host=None, attempts=1, order=False, name=None, http=None, https=None):
        if name and isinstance(name, str):
            proxy_name = name
        elif host and isinstance(host, str):
            proxy_name = host
        elif http and https and isinstance(http, str) and isinstance(https, str):
            if http == https:
                proxy_name = http
            else:
                proxy_name = "http: " + http + " - https: " + https
        elif http and isinstance(http, str):
            proxy_name = "http: " + http

        elif https and isinstance(https, str):
            proxy_name = "https: " + https

        else:
            proxy_name = "Without proxy"

        try:
            attempts = abs(int(attempts))
        except:
            self.logger.error("attempts argument should be an positive integer")

        if order is False:
            index = len(self.proxies)
        else:
            try:
                index = abs(int(order))
            except:
                self.logger.error("order argument should be an positive integer")
                index = len(self.proxies)

        if host:
            if self.proxies.get(index):
                self.proxies[index].update({
                    "http": host,
                    "https": host,
                    "attempts": attempts,
                    "name": proxy_name
                })
            else:
                self.proxies[index] = {
                    "http": host,
                    "https": host,
                    "attempts": attempts,
                    "name": proxy_name
                }
        else:
            self.proxies[index] = {
                "attempts": attempts,
                "name": proxy_name
            }

        if http and isinstance(http, str):
            self.proxies[index].update({
                "http": http
            })

        if https and isinstance(https, str):
            self.proxies[index].update({
                "https": https
            })

        if not self.stats.get(proxy_name):
            self.stats[proxy_name] = {
                "Total": 0,
                "Successful": 0,
                "Failed": 0,
                "AVG Size (Bytes)": 0,
                "Total Size (Bytes)": 0
            }

        if not self.stats_class.get(proxy_name):
            self.stats_class[proxy_name] = {
                "Total": 0,
                "Successful": 0,
                "Failed": 0,
                "AVG Size (Bytes)": 0,
                "Total Size (Bytes)": 0
            }

    def request_wrapper(self, real_timeout, *args, **kwargs):
        if real_timeout:
            eventlet.monkey_patch()
            with Timeout(real_timeout, False):
                try:
                    response = requests.request(*args, **kwargs)
                    return response
                except Timeout as t:
                    self.logger.error("Real timeout {} secs".format(str(real_timeout)))
                    response = requests.models.Response()
                    response.status_code = 504
                    return response
        else:
            return requests.request(*args, **kwargs)

    def request(self, method, url, fake_ua=False, return_json=False, br_session=True, **kwargs):
        """
        Method to create a http request
        :param method: str "GET" or "POST" to indicate the request method
        :param url: str of the url that will be requested
        :param fake_ua: boolean to indicate if a Fake UserAgent will be send on the headers
        :param return_json: Boolean to indicate if the response will be a json
        :param br_session: Boolean to indicate if the parameters of the session will be used or not
        :param kwargs: Extra parameters that can be used for requests.request
        :return: request or json depending on the return_json param.
        """
        self.logger.debug("Executing request...")


        if br_session == True:
            headers_ = kwargs.pop("headers", self.headers)
            cookies_ = kwargs.pop("cookies", self.cookies)
            delay = kwargs.pop("delay", self.delay)
            delay_after = kwargs.pop("delay_after", self.delay_after)
            real_timeout = kwargs.pop("real_timeout", self.real_timeout)
        else:
            headers_ = kwargs.pop("headers", {})
            cookies_ = kwargs.pop("cookies", {})
            delay = kwargs.pop("delay", [0, 1])
            delay_after = kwargs.pop("delay_after", [0, 1])
            real_timeout = kwargs.pop("real_timeout", None)

        verify_ = kwargs.pop("verify", self.verify)
        timeout_ = kwargs.pop("timeout", self.timeout)
        indexes = list(self.proxies.keys())
        indexes.sort()

        for index in indexes:
            proxy = self.proxies.get(index)
            self.logger.debug("Trying with Proxy server {proxy}...".format(proxy=proxy.get("name")))
            for retry in range(1, proxy.get("attempts") + 1):
                self.logger.debug("{proxy} attempt #{retry}...".format(proxy=proxy.get("name"), retry=retry))
                self.stats[proxy.get("name")]["Total"] += 1
                self.stats_class[proxy.get("name")]["Total"] += 1
                try:
                    proxies_ = {}
                    if proxy.get("http"):
                        proxies_["http"] = proxy.get("http")
                    if proxy.get("https"):
                        proxies_["https"] = proxy.get("https")

                    if fake_ua:
                        headers_["User-Agent"] = ua.random

                    self.logger.debug(
                        "Headers: " + str(headers_) + "      Proxies: " + str(proxies_) + "     Cookies:" + str(
                            cookies_), )
                    response = self.request_wrapper(real_timeout, method, url, headers=headers_, proxies=proxies_,
                                                    cookies=cookies_, verify=verify_, timeout=timeout_, **kwargs)

                    if response.status_code == 200:
                        self.stats[proxy.get("name")]["Successful"] += 1
                        self.stats_class[proxy.get("name")]["Successful"] += 1
                        size = (len(response.content) + len(str(response.headers)))
                        self.stats[proxy.get("name")]["Total Size (Bytes)"] += size
                        self.stats_class[proxy.get("name")]["Total Size (Bytes)"] += size
                        self.stats[proxy.get("name")]["AVG Size (Bytes)"] = self.stats[proxy.get("name")]["Total Size (Bytes)"]/self.stats[proxy.get("name")]["Successful"]
                        self.stats_class[proxy.get("name")]["AVG Size (Bytes)"] = self.stats_class[proxy.get("name")]["Total Size (Bytes)"]/self.stats_class[proxy.get("name")]["Successful"]
                        time.sleep(random.randrange(delay_after[0], delay_after[1]))
                        if not return_json:
                            return response
                        else:
                            try:
                                return response.json()
                            except:
                                self.logger.error("Json cannot be obtained from request")
                                return response

                    else:
                        self.logger.warning(
                            "[{proxy}] The Request #{retry} failed: {url}".format(proxy=proxy.get("name"), retry=retry,
                                                                                  url=url))
                        time.sleep(random.randrange(delay[0], delay[1]))
                        self.stats[proxy.get("name")]["Failed"] += 1
                        self.stats_class[proxy.get("name")]["Failed"] += 1
                        continue

                except Exception as e:
                    self.logger.error(e)
                    self.logger.warning(
                        "[{proxy}] The Request #{retry} had an error: {url}".format(proxy=proxy.get("name"), retry=retry,
                                                                                    url=url))
                    time.sleep(random.randrange(delay[0], delay[1]))
                    self.stats[proxy.get("name")]["Failed"] += 1
                    self.stats_class[proxy.get("name")]["Failed"] += 1
                    continue
            self.logger.warning("[{proxy}] Was not able to return a good response for {url}".format(proxy=proxy.get("name"),
                                                                                                    url=url))
        self.logger.error("REQUEST ERROR {url}".format(url=url))
        return False

    def post(self, url, fake_ua=False, return_json=False, br_session=True, **kwargs):
        """
        Method to call request wiht POST as a method
        :param url: str of the url that will be requested
        :param fake_ua: boolean to indicate if a Fake UserAgent will be send on the headers
        :param return_json: Boolean to indicate if the response will be a json
        :param br_session: Boolean to indicate if the parameters of the session will be used or not
        :param kwargs: Extra parameters that can be used for requests.request
        :return: request or json depending on the return_json param.
        """
        return self.request('POST', url, return_json=return_json, fake_ua=fake_ua, br_session=br_session, **kwargs)

    def get(self, url, fake_ua=False, return_json=False, br_session=True, **kwargs):
        """
        Method to call request wiht GET as a method
        :param url: str of the url that will be requested
        :param fake_ua: boolean to indicate if a Fake UserAgent will be send on the headers
        :param return_json: Boolean to indicate if the response will be a json
        :param br_session: Boolean to indicate if the parameters of the session will be used or not
        :param kwargs: Extra parameters that can be used for requests.request
        :return: request or json depending on the return_json param.
        """
        return self.request('GET', url, return_json=return_json, fake_ua=fake_ua, br_session=br_session, **kwargs)

    def soup(self, url, **kwargs):
        """
        Method to parse the soup from an specific url
        :param url: str of the url of the html
        :return: BeautifulSoup
        """
        self.logger.debug("Getting soup...")
        response = self.get(url, **kwargs)
        if response:
            try:
                try:
                    content = response.content.decode('utf-8')
                except Exception as e:
                    content = response.content
                return BeautifulSoup(content, 'html.parser')
            except Exception as e:
                self.logger.error("Error while parsing the soup")
                self.logger.error(e)

        else:
            self.logger.error("Soup cannot be returned")

    def xpath(self, url, **kwargs):
        """
        Method to parse the xpath tree from an specific url
        :param url: str of the url of the html
        :return: XpathTree
        """
        self.logger.debug("Getting xpath...")
        response = self.get(url, **kwargs)
        if response:
            try:
                try:
                    content = response.content.decode('utf-8')
                except Exception as e:
                    content = response.content
                tree = html.fromstring(content)
                return tree
            except Exception as e:
                self.logger.error("Error while parsing the xpath")
                self.logger.error(e)

        else:
            self.logger.error("Soup cannot be returned")
