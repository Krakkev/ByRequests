import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import ast
import os
import logging
import random
from lxml import html
import time
import eventlet
from eventlet.timeout import Timeout

ua = UserAgent()



class ByRequest():

    def __init__(self, proxies=False, max_retries=False, cookies=False, fake_ua=True, headers=False, timeout=False,
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

        self.proxies_retries = {
            None: 3,
            "crawlera": 3,
            "scrapoxy": 3,
            "luminati": 3
        }
        self.timeout = 15
        self.extras = {}
        self.delay = [1, 3]
        self.max_retries = 3
        self.proxies_order = [None, "crawlera", "scrapoxy", "luminati"]
        self.headers = {}
        self.cookies = {}
        self.verify = True
        self.delay_after = [0, 1]
        self.stats = {
            None: {
                "Total": 0,
                "Successful": 0,
                "Failed": 0
            },
            "crawlera": {
                "Total": 0,
                "Successful": 0,
                "Failed": 0
            },
            "scrapoxy": {
                "Total": 0,
                "Successful": 0,
                "Failed": 0
            },
            "luminati": {
                "Total": 0,
                "Successful": 0,
                "Failed": 0
            }
        }
        if real_timeout:
            try:
                self.real_timeout = int(real_timeout)
            except:
                self.logger.error("Real timeout value should be an integer or None")
                self.real_timeout = None
        else:
            self.real_timeout = None

        if max_retries:
            self.logger.debug("Assigning max_retries...")
            try:
                self.max_retries = int(max_retries)
            except:
                self.logger.error("Max retires cannot be converted to integer")
            for proxy in self.proxies_retries:
                self.proxies_retries[proxy] = self.max_retries

        if proxies or proxies is None:
            self.logger.debug("Assigning proxies...")
            if isinstance(proxies, list):
                self.logger.debug("Assigning order of proxy servers...")
                proxy_order = []
                for proxy in proxies:
                    if isinstance(proxy, dict):
                        if len(proxy) == 1:
                            self.logger.debug("Assigning order and max retries of proxy servers...")
                            for p, retries in proxy.items():
                                if p in self.proxies_retries.keys() or (
                                        isinstance(p, str) and p.lower() in self.proxies_retries.keys()):
                                    try:
                                        if max_retries:
                                            self.logger.warning("Overriding max_retries for {}".format(p))
                                        if p == None:
                                            self.proxies_retries[p] = int(retries)
                                            proxy_order.append(p)
                                        else:
                                            self.proxies_retries[p.lower()] = int(retries)
                                            proxy_order.append(p.lower())
                                    except Exception as e:
                                        self.logger.warning("Error while assigning proxies")
                                        self.logger.error(e)
                                else:
                                    self.logger.error("{proxy} is not in the list of valid proxies".format(proxy=str(p)))
                        else:
                            self.logger.error("Poxy service dict should be of length 1")
                    elif proxy in self.proxies_retries.keys():
                        proxy_order.append(proxy)
                    elif isinstance(proxy, str) and proxy.lower() in self.proxies_retries.keys():
                        proxy_order.append(proxy.lower())
                self.proxies_order = proxy_order
            elif isinstance(proxies, str):
                self.logger.debug("Assigning single proxy server...")
                if proxies.lower() in self.proxies_order:
                    self.proxies_order = [proxies.lower()]
                else:
                    self.logger.error("{proxy} is not a valid proxy server".format(proxy=proxies))
            elif proxies is None:
                self.logger.debug("Assigning single proxy server...")
                self.proxies_order = [None]

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
                    self.headers["cookie"]=cookies
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


    def request(self, method, url, fake_ua=False, return_json=False, br_session=True,  **kwargs):
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
        if self.proxies_order:
            if br_session == True:
                headers_ = kwargs.pop("headers", self.headers)
                cookies_ = kwargs.pop("cookies", self.cookies)
                delay = kwargs.pop("delay", self.delay)
                delay_after = kwargs.pop("delay_after", self.delay_after)
                real_timeout = kwargs.pop("real_timeout", self.real_timeout)
            else:
                headers_ = kwargs.pop("headers", {})
                cookies_ = kwargs.pop("cookies", {})
                delay = kwargs.pop("delay", [0,1])
                delay_after = kwargs.pop("delay_after", [0,1])
                real_timeout = kwargs.pop("real_timeout", None)

            proxies_order = kwargs.pop("proxies_order", self.proxies_order)
            verify_ = kwargs.pop("verify", self.verify)
            timeout_ = kwargs.pop("timeout", self.timeout)
            proxies_ = kwargs.pop("proxies", False)
            if proxies_ == False:
                is_proxies_defined = False
            else:
                is_proxies_defined = True

            for proxy in proxies_order:
                self.logger.debug("Trying with Proxy server {proxy}...".format(proxy=proxy))
                for retry in range(1, kwargs.pop("max_retries", self.proxies_retries.get(proxy)) + 1):
                    self.logger.debug("Try #{retry}...".format(retry=retry))
                    self.stats[proxy]["Total"] += 1
                    try:
                        if not is_proxies_defined:
                            proxies_ = self.get_proxies(proxy)
                        if fake_ua:
                            headers_["User-Agent"] = ua.random
                        if retry == self.proxies_retries.get(proxy) and self.verify == False:
                            self.logger.warning("Trying with verify as False")
                            response = self.request_wrapper(real_timeout, method, url, headers=headers_, proxies=proxies_,
                                                        cookies=cookies_, verify=True, timeout=timeout_, **kwargs)
                        else:
                            self.logger.debug("Headers --->", str(headers_), "proxies --->", str(proxies_))
                            response = self.request_wrapper(real_timeout, method, url, headers=headers_, proxies=proxies_,
                                                        cookies=cookies_, verify=verify_, timeout=timeout_, **kwargs)
                        if response.status_code == 200:
                            self.stats[proxy]["Successful"] += 1
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
                                "[{proxy}] The Request #{retry} failed: {url}".format(proxy=proxy, retry=retry,
                                                                                      url=url))
                            time.sleep(random.randrange(delay[0], delay[1]))
                            self.stats[proxy]["Failed"] += 1
                            continue

                    except Exception as e:
                        self.logger.error(e)
                        self.logger.warning(
                            "[{proxy}] The Request #{retry} had an error: {url}".format(proxy=proxy, retry=retry, url=url))
                        time.sleep(random.randrange(delay[0], delay[1]))
                        self.stats[proxy]["Failed"] += 1
                        continue
                self.logger.warning("[{proxy}] Was not able to return a good response for {url}".format(proxy=proxy,
                                                                                url=url))
            self.logger.error("REQUEST ERROR {url}".format(url=url))
            return False
        else:
            self.logger.error("Proxies are not well defined")

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
                return BeautifulSoup(response.content, 'html.parser')
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
                tree = html.fromstring(response.content)
                return tree
            except Exception as e:
                self.logger.error("Error while parsing the xpath")
                self.logger.error(e)

        else:
            self.logger.error("Soup cannot be returned")

    def print_status(self, percentage=True):
        print("------------------------------------------------------------------------------")
        print("---                                Stats                                   ---")
        print("------------------------------------------------------------------------------")
        self.logger.info("---                                Stats                                   ---")
        total = 0
        total_succ = 0
        total_fail = 0
        for proxy, dict_ in self.stats.items():
            if dict_["Total"] > 0:
                total += dict_["Total"]
                total_succ += dict_["Successful"]
                total_fail += dict_["Failed"]
                if proxy == None:
                    proxies = "Without proxies: "
                else:
                    proxies = "Using {proxy}: ".format(proxy=proxy)
                if percentage:
                    tot = str(dict_["Total"])
                    succ = str((dict_["Successful"]/dict_["Total"])*100) + "%"
                    fail = str((dict_["Failed"]/dict_["Total"])*100) + "%"
                else:
                    tot = str(dict_["Total"])
                    succ = str(dict_["Successful"])
                    fail = str(dict_["Failed"]/dict_["Total"])
                self.logger.info("{proxies} \t {succ} Successful \t {fail} Failed \t {tot} Total tries".format(proxies=proxies, succ=succ, fail=fail, tot=tot))
                print("{proxies} \t {succ} Successful \t {fail} Failed \t {tot} Total tries".format(proxies=proxies, succ=succ, fail=fail, tot=tot))

    def get_proxies(self, server=None):
        """
        Method to get the proxies request parameter for different proxy services
        :param server: Name of the proxy service
        :return: dict of http methods and their corresponding proxy service
        """
        self.logger.debug("Getting proxies dict...")
        if server == None:
            self.logger.debug("Without proxies...")
            return {}
        if server == 'crawlera':
            self.logger.debug("Proxies from crawlera...")
            proxy_host = "proxy.crawlera.com"
            proxy_port = "8010"
            proxy_auth = "{}:".format(os.getenv('CRAWLERA', 'api_key'))  # Make sure to include ':' at the end
            proxies = {"https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
                       "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}
            self.logger.debug("Returning:" + str(proxies))
            return proxies
        if server == "scrapoxy":
            self.logger.debug("Proxies from scrapoxy...")
            proxy_host = "{}".format(os.getenv('SCRAPOXY', 'localhost'))
            proxy_port = "8888"
            proxies = {"https": "https://{}:{}/".format(proxy_host, proxy_port),
                       "http": "http://{}:{}/".format(proxy_host, proxy_port)}
            self.logger.debug("Returning:" + str(proxies))
            return proxies
        if server == "luminati":
            self.logger.debug("Proxies from luminati...")
            #luminati = http://lum-customer-{costumer}-zone-{zone}:{password}@zproxy.lum-superproxy.io:{port}#
            luminati = "{}".format(os.getenv('LUMINATI', 'localhost'))
            proxies = {"https": luminati,
                       "http": luminati}
            self.logger.debug("Returning:" + str(proxies))
            return proxies

