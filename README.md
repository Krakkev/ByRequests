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

max_retries (DEFAULT=3)
```python
#  Every request done by this session is going to be send 'max_retries' times for every proxy service unless a good response has been obtained
byrequest = ByRequest(max_retries=1)
print(byrequest.max_retries)
```

#### ByRequest Parameters
proxies (DEFAULT=[None, "crawlera", "scrapoxy", "luminati"])
```python
# 1st Option:   proxies=None
# Your requests done by this session are not going to use any kind of proxy service
byrequest = ByRequest(proxies=None)

# 2nd Option:   proxies="<Proxy Service>"
# Your requestsdone by this session  are going to use the proxy service that you specified
byrequest = ByRequest(proxies="Crawlera")

# 3rd Option:   proxies=[<Proxy Service>, <Proxy Service>]
# The requests done by this session are going to be send with the proxy services that you specified  in the order that they appear for 3 times (Default value for max_retries, unless it has been specified with the max_retries parameter) unless a good response's obtained before.
# * None represents the use of no proxies
byrequest = ByRequest(proxies=[None, "Crawlera", "Scrapoxy", "crawlera"])


# 4th Option:   proxies=[{<Proxy Service>: <max retries>}, {<Proxy Service>: <max retries>}]
# The requests done by this session are going to be send with the proxy services that you specified  in the order that they appear 'max_retries' times each proxy service until a good response is obtained.
# * None represents the use of no proxies
# ** This max_retries overrides the max_retries parameter
byrequest = ByRequest(proxies=[{None: 3}, {"luminati": 1}, "Scrapoxy", {"crawlera": "1"}])
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
#  Timeout parameter is the max time that a response will be waited before a timeout error showns for every request made with this session
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
