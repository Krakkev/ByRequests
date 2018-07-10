# ByRequests
Request class created to be used by the company ByPrice to simplify the use of proxy services, create sessions, use fake UserAgents, manage the number of requests, delays and some other stuff to make easier the web scraping process :)

#### Installation
```shell
$ pip install byrequests
```

#### ENVIROMENT VARIABLES
Export the enviroment variables of the proxy services that you are going to use
```bash
export CRAWLERA='<API KEY>' # example CRAWLERA='17659951987l54e3296e142da791145e'
export SCRAPOXY='<HOST>' # example SCRAPOXY='127.0.0.0'
export LUMINATI='<COMPLETE URL>'  # example LUMINATI='http://lum-customer-ByRequest-zone-global:dj58yk1a9wtd@zproxy.lum-superproxy.io:22225'
```

#### HOW TO DECLARE ByRequest SESSION
Basic usage without custom parameters
```python
from ByRequests.ByRequests import ByRequest

# Create session
byrequest = ByRequest()

# Get Request
response = byrequest.get("http:www.someurl.com")
print(response)

# Post Request obtaining json
response_json = byrequest.post("http:www.someurl.com", returning_json=True)
print(response_json)

# Parsing soup
soup = byrequest.soup("http:www.someurl.com")
print(soup)

# Parsing Xpath
xpath = byrequest.xpath("http:www.someurl.com")
print(xpath)
```


#### ByRequest Parameters
proxies (DEFAULT=None)
```python
# 1st Option:   proxies="proxy_server_host"
# Your requests done by this session are not going to use any kind of proxy service
byrequest = ByRequest(proxies="proxy_server_host")

# 2nd Option:   proxies={"http": "proxy_server_http_host", "https": "proxy_server_https_host"}
# Your requestsdone by this session  are going to use the proxy service that you specified
byrequest = ByRequest(proxies="Crawlera")
```

headers (DEFAULT={})
```python
#  Every request done by this session is going to be send the headers that you define here
# * If the fake_ua parameter is enable, the User-Agent defined here will be overrided
headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
byrequest = ByRequest(headers=headers)
print(byrequest.headers)
```

cookies (DEFAULT={})
```python
#  Every request done by this session is going to be send the cookies that you define here
# The cookies can be a Dict, a CookieJar or a String
cookies = {<cookie key>: <cookie value>}
byrequest = ByRequest(cookies=cookies)
print(byrequest.cookies)
```

fake_ua (DEFAULT=True)
```python
#  Enable or desable the use of fake useragent in the headers of the session with values True or False
# * This fake useragent will override the header's User-Agent
byrequest = ByRequest(fake_ua=True)
print(byrequest.headers)
```

timeout (DEFAULT=15)
```python
#  Timeout parameter is the max time that a request will wait for an answer before a timeout error shows for every request made with this session
byrequest = ByRequest(timeout=5)
print(byrequest.timeout)
```

real_timeout (DEFAULT=15)
```python	
#  Timeout parameter is the max time for the whole requests process could take before a timeout error shows for every request made with this session
byrequest = ByRequest(timeout=5)
print(byrequest.timeout)
```


delay (DEFAULT=[1, 3])
```python
#  delay parameter determines the range of random time that will be waited between a failed request and the next request during this session

# 1st Option:   list or tuple with the range of random seconds     delay=[1, 5] or delay=(1, 5)
# Between a failed request and the next req. will be waited a random time between 1 and 5 seconds
byrequest = ByRequest(delay=(1, 5))
print(byrequest.delay)

# 2nd Option:  max number of random seconds delay="5" or delay=5 or delay=[5] or delay=["5"]
# Between a failed request and the next req. will be waited a random time between 1 to  5 seconds
byrequest = ByRequest(delay=5)
print(byrequest.delay)
```

delay_after (DEFAULT=[0,1])
```python
#  delay_after parameter determines the range of random time that will be waited afet a good response is obtained

# 1st Option:   list or tuple with the range of random seconds     delay_after=[1, 5] or delay_after=(1, 5)
# After a good response is obtained a random time between 1 and 5 seconds will be waited
byrequest = ByRequest(delay_after=(1, 5))
print(byrequest.delay_after)

# 2nd Option:  max number of random seconds delay_after="5" or delay_after=5 or delay_after=[5] or delay_after=["5"]
# After a good response is obtained a random time between 1 and 5 seconds will be waited
byrequest = ByRequest(delay_after=(5))
print(byrequest.delay_after)
```

verify (DEFAULT=True)
```python
#  verify parameter is a boolean to indicate if the SSL verification will be enabled or not during the session
byrequest = ByRequest(verify=False)
print(byrequest.verify)
```

logger (DEFAULT=logging.getLogger(__name__))
```python
import logging
#  logger parameter allows you to send the log messages through your own customized logger
logger = logging.getLogger(<APP_NAME>)
byrequest = ByRequest(logger=logger)
```


#### Add Proxies
br = ByRequest()

br.add_proxy(host=None, attempts=1, order=False, name=None, http=None, https=None)
```python
# Declare a host if it is going to be used for http & https requests
br.add_proxy(host="server_host")


# Declare http and/or https parameters if they are distinct host
br.add_proxy(http="http_host", https="https_host")


# Declare the name of the proxies to track their stats
br.add_proxy("proxy_host", name="ProxyService 1")
byrequest.stats


# You can declare the order of execution of your proxies, otherwise it will be appended at the end (begins with 0)
# If you declare a proxy with a previously oder defined it will overwrite the previous one
# !!! The proxy with order 0 is the one declared when the class is defined !!!
br.add_proxy("proxy_host", name="ProxyService 1", order=0)


# You can define the number of attempts for each proxy service (DEFAULT=1)
br.add_proxy("proxy_host", name="ProxyService 1", attempts=5)
```


#### Attributes
```python
br = ByRequest(attempts=3)
br.add_proxy("proxy_host2", name="ProxyService 2", order=2, attempts=3)
br.add_proxy("proxy_host1", name="ProxyService 1", order=1, attempts=2)


# You can check the proxies defined in your class printing the proxies attribute
print(br.proxies)

# You can check how the stats of the requests  made by your ByRequest object printing the stats attribute
br.get("http://some_url.io")
print(br.stats)


br2 = ByRequest(attempts=3)
br2.get("http://some_url.io")

# You can check how the stats of the requests  made by all your ByRequest objects printing the stats attribute
print(br.stats_class)


#If you like to use pandas library, you can use pandas to load your stats and visualize them easily
import pandas as pd
stats = pd.DataFrame(br.stats)
stats_class = pd.DataFrame(br.stats_class) # Equal to  pd.DataFrame(br2.stats_class)

#!!! The stats sizes are an estimation that come from:  ( response_body + response_headers)  ONLY FROM THE SUCCESSFUL RESPONSES !!!

```