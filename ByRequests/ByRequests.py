import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import ast
import os
import logging
import random
from lxml import html

ua = UserAgent()
logger = logging.getLogger(__name__)


class ByRequest():
    proxies_retries = {
        None: 3,
        "crawlera": 3,
        "scrapoxy": 3,
        "luminati": 3
    }
    timeout = 15
    extras = {}
    delay = [1, 3]
    max_retries = 2
    proxies_order = [None, "crawlera", "scrapoxy", "luminati"]
    headers = {}
    cookies = {}
    verify = True
    delay_after = [0, 1]
    stats = {
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

    def __init__(self, proxies=False, max_retries=False, cookies=False, fake_ua=True, headers=False, timeout=False,
                 delay=False, delay_after=False, verify=True):
        """
        Create object with the initial parameters
        :param proxies:
            * list of proxy services in execution order ["1st proxy service", "2nd", "3rd", ...]
            * str of the only proxy service that will be used
            * dict of proxy services in priority order {
                                                 "1st proxy service" : <<number of tries>>,
                                                 "2nd proxy service" : <<number of tries>>,
                                                 ..} ** The number of tries will overwrite the max_retries param
            *** Use None to use no proxy server
        :param max_retries: integer of max number of retries by failed request for every proxy service
        :param cookies: RequestCookieJar or Dict with the cookies that will persist for the whole request session
        :param fake_ua: Boolean to indicate if a Fake User-Agent will be used for the whole request session
            ** This User-Agent will overwrite the one from the headers
        :param headers: Dict with the headers that will persist for the whole session
        :param timeout: Integer or String digit with the timeout for the request that will persist for the whole session
        :param delay:
            * list [min, max] of the range of random seconds of wait between a request failed and a new retry
            * tuple (min, max) of the range of random seconds of wait between a request failed and a new retry
            * int or string digit of the max seconds of wait after a request failed
        :param verify: Boolean to indicate if the SSL verification is enabled or not
        """
        if max_retries:
            logger.debug("Assigning max_retries...")
            try:
                self.max_retries = int(max_retries)
            except:
                logger.error("Max retires cannot be converted to integer")
            for proxy in self.proxies_retries:
                self.proxies_retries[proxy] = self.max_retries

        if proxies:
            logger.debug("Assigning proxies...")
            if isinstance(proxies, list):
                logger.debug("Assigning order of proxy servers...")
                proxy_order = []
                for proxy in proxies:
                    if proxy in self.proxies_retries.keys():
                        proxy_order.append(proxy)
                    elif isinstance(proxy, str) and proxy.lower() in self.proxies_retries.keys():
                        proxy_order.append(proxy.lower())
                self.proxies_order = proxy_order
            elif isinstance(proxies, str):
                logger.debug("Assigning single proxy server...")
                if proxies.lower() in self.proxies_order:
                    self.proxies_order = [proxies.lower()]
                else:
                    logger.error("{proxy} is not a valid proxy server".format(proxy=proxies))
            elif isinstance(proxies, dict):
                logger.debug("Assigning order and max retries of proxy servers...")
                proxies_retries_aux = {}
                for proxy, retries in proxies.items():
                    if proxy in self.proxies_retries.keys() or (
                            isinstance(proxy, str) and proxy.lower() in self.proxies_retries.keys()):
                        try:
                            proxies_retries_aux[proxy] = int(retries)
                        except Exception as e:
                            logger.warning("Error while assigning proxies")
                            logger.error(e)
                    else:
                        logger.error("{proxy} is not in the list of valid proxies".format(proxy=str(proxy)))
                if proxies_retries_aux:
                    self.proxies_retries = proxies_retries_aux
                    self.proxies_order = list(self.proxies_retries.keys())
                    if max_retries:
                        logger.warning("Overwriting max_retries")

        if headers:
            logger.debug("Assigning headers...")
            if isinstance(headers, dict):
                self.headers = headers
            elif isinstance(headers, str):
                try:
                    self.headers = ast.literal_eval(headers)
                except:
                    self.headers = {}
                    logger.error("Headers string cannot be converted to dict")
            else:
                logger.error("Headers are not valid")

        if fake_ua:
            logger.debug("Assigning fake User-Agent...")
            try:
                user_agent = ua.random
                self.headers['User-Agent'] = user_agent
            except Exception as e:
                logger.warning("The fake user agent cannot be added to headers")
                logger.error(e)

        if cookies:
            logger.debug("Assigning cookies...")
            if isinstance(cookies, requests.cookies.RequestsCookieJar) or isinstance(cookies, dict):
                self.cookies = cookies
            elif isinstance(cookies, str):
                try:
                    self.cookies = ast.literal_eval(cookies)
                except:
                    logger.error("Cookies string cannot be converted to dict")
            else:
                logger.error("Cookies are not valid")

        if timeout:
            logger.debug("Assigning timeout...")
            if isinstance(timeout, int):
                self.timeout = abs(timeout)
            else:
                try:
                    self.timeout = abs(int(timeout))
                except:
                    logger.error("Timeout cannot be converted to integer")

        if delay:
            logger.debug("Assigning delay...")
            if isinstance(delay, list) or isinstance(delay, tuple):
                if len(delay) == 2:
                    logger.debug("Assigning min & max seconds...")
                    try:
                        self.delay[0] = int(delay[0])
                        self.delay[1] = int(delay[1])
                    except:
                        logger.error("Delay values cannot converted to integers")
                elif len(delay) == 1:
                    try:
                        logger.debug("Assigning max seconds...")
                        self.delay[1] = int(delay[0])
                    except:
                        logger.error("Delay value cannot converted to integer")
                else:
                    logger.error("Delay should contain 1 or 2 integer values")
            else:
                try:
                    logger.debug("Assigning max seconds...")
                    self.delay[1] = int(delay)
                except:
                    logger.error("Delay value cannot be converted into integer")

        if delay_after:
            logger.debug("Assigning delay after request...")
            if isinstance(delay_after, list) or isinstance(delay_after, tuple):
                if len(delay) == 2:
                    logger.debug("Assigning min & max seconds...")
                    try:
                        self.delay_after[0] = int(delay_after[0])
                        self.delay_after[1] = int(delay_after[1])
                    except:
                        logger.error("Delay value values cannot converted to integers")
                elif len(delay) == 1:
                    try:
                        logger.debug("Assigning max seconds...")
                        self.delay_after[1] = int(delay_after[0])
                    except:
                        logger.error("Delay after value cannot converted to integer")
                else:
                    logger.error("Delay after should contain 1 or 2 integer values")
            else:
                try:
                    logger.debug("Assigning max seconds...")
                    self.delay_after[1] = int(delay)
                except:
                    logger.error("Delay after value cannot be converted into integer")

        if verify is not True:
            self.verify = verify


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
        logger.debug("Executing request...")
        if self.proxies_order:
            if br_session == True:
                headers_ = kwargs.pop("headers", self.headers)
                cookies_ = kwargs.pop("cookies", self.cookies)
                delay = kwargs.pop("delay", self.delay)
                delay_after = kwargs.pop("delay_after", self.delay_after)
            else:
                headers_ = kwargs.pop("headers", {})c
                cookies_ = kwargs.pop("cookies", {})
                delay = kwargs.pop("delay", [0,1])
                delay_after = kwargs.pop("delay_after", [0,1])

            proxies_order = kwargs.pop("proxies_order", self.proxies_order)
            verify_ = kwargs.pop("verify", self.verify)
            timeout_ = kwargs.pop("timeout", self.timeout)
            proxies_ = kwargs.pop("proxies", False)
            if proxies_ == False:
                is_proxies_defined = False
            else:
                is_proxies_defined = True

            for proxy in proxies_order:
                logger.debug("Trying with Proxy server {proxy}...".format(proxy=proxy))
                for retry in range(1, kwargs.pop("max_retries", self.proxies_retries.get(proxy)) + 1):
                    logger.debug("Try #{retry}...".format(retry=retry))
                    self.stats[proxy]["Total"] += 1
                    try:
                        if not is_proxies_defined:
                            proxies_ = self.get_proxies(proxy)
                        if fake_ua:
                            headers_["User-Agent"] = ua.random
                        if retry == self.proxies_retries.get(proxy) and self.verify == False:
                            logger.warning("Trying with verify as False")
                            response = requests.request(method, url, headers=headers_, proxies=proxies_,
                                                        cookies=cookies_, verify=True, timeout=timeout_, **kwargs)
                        else:
                            print("Headers --->", str(headers_), "proxies --->", str(proxies_))
                            response = requests.request(method, url, headers=headers_, proxies=proxies_,
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
                                    logger.error("Json cannot be obtained from request")
                                    return response

                        else:
                            logger.warning(
                                "[{proxy}] The Request #{retry} failed: {url}".format(proxy=proxy, retry=retry,
                                                                                      url=url))
                            time.sleep(random.randrange(delay[0], delay[1]))
                            self.stats[proxy]["Failed"] += 1
                            continue

                    except Exception as e:
                        logger.error(e)
                        logger.warning(
                            "[{proxy}] The Request #{retry} failed: {url}".format(proxy=proxy, retry=retry, url=url))
                        time.sleep(random.randrange(delay[0], delay[1]))
                        self.stats[proxy]["Failed"] += 1
                        continue
                logger.warning(
                    "[{proxy}] Was not able to return a good response for {url}".format(proxy=proxy, url=url))
            logger.error(
                "REQUEST ERROR {url}".format(url=url))
            return False
        else:
            logger.error("Proxies are not well defined")

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
        logger.debug("Getting soup...")
        response = self.get(url, **kwargs)
        if response:
            try:
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                logger.error("Error while parsing the soup")
                logger.error(e)

        else:
            logger.error("Soup cannot be returned")

    def xpath(self, url, **kwargs):
        """
        Method to parse the xpath tree from an specific url
        :param url: str of the url of the html
        :return: XpathTree
        """
        logger.debug("Getting xpath...")
        response = self.get(url, **kwargs)
        if response:
            try:
                tree = html.fromstring(response.content)
                return tree
            except Exception as e:
                logger.error("Error while parsing the xpath")
                logger.error(e)

        else:
            logger.error("Soup cannot be returned")

    def print_status(self, percentage=True):
        print("--------------------------")
        print("---        Stats       ---")
        print("--------------------------")
        total = 0
        total_succ = 0
        total_fail = 0
        for proxy, dict_ in self.status.items():
            if dict_["Total"] > 0:
                total += dict_["Total"]
                total_succ += dict_["Successful"]
                total_fail += dict_["Failed"]
                if proxy == None:
                    proxies = "Without proxies: "
                else:
                    proxies = "Using {} service: ".format("proxy")
                if percentage:
                    tot = str(dict_["Total"])
                    succ = str((dict_["Successful"]/tot)*100) + "%"
                    fail = str((dict_["Failed"]/tot)*100) + "%"
                else:
                    tot = str(dict_["Total"])
                    succ = str(dict_["Successful"])
                    fail = str(dict_["Failed"]/tot)
                print("{proxies} \t {succ} Succesful \t {fail} Failed \t {tot} Total tries".format(proxies=proxies, succ=succ, fail=fail, tot=tot))

    @staticmethod
    def get_proxies(server=None):
        """
        Method to get the proxies request parameter for different proxy services
        :param server: Name of the proxy service
        :return: dict of http methods and their corresponding proxy service
        """
        logger.debug("Getting proxies dict...")
        if server == None:
            logger.debug("Without proxies...")
            return {}
        if server == 'crawlera':
            logger.debug("Proxies from crawlera...")
            proxy_host = "proxy.crawlera.com"
            proxy_port = "8010"
            proxy_auth = "{}:".format(os.getenv('CRAWLERA', 'api_key'))  # Make sure to include ':' at the end
            proxies = {"https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
                       "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}
            logger.debug("Returning:" + str(proxies))
            return proxies
        if server == "scrapoxy":
            logger.debug("Proxies from scrapoy...")
            proxy_host = "{}".format(os.getenv('SCRAPOXY', 'localhost'))
            proxy_port = "8888"
            proxies = {"https": "https://{}:{}/".format(proxy_host, proxy_port),
                       "http": "http://{}:{}/".format(proxy_host, proxy_port)}
            logger.debug("Returning:" + str(proxies))
            return proxies
        if server == "luminati":
            logger.debug("Proxies from scrapoy...")
            #luminati = http://lum-customer-{costumer}-zone-{zone}:{password}@zproxy.lum-superproxy.io:{port}#
            luminati = "{}".format(os.getenv('LUMINATI', 'localhost'))
            proxies = {"https": luminati,
                       "http": luminati}
            logger.debug("Returning:" + str(proxies))
            return proxies

