# ByRequests
Request class created to be used by the company ByPrice to simplify the use of proxy services, create sessions, use fake UserAgents, manage the number of requests, delays and some other stuff to make easier the web scraping process :)

#### Installation
```shell
$ pip install byrequests
```

#### ENVIROMENT VARIABLES
Export the enviroment variables of the proxy services that you are going to use
```bash
export CRAWLERA='<API KEY>'
export SCRAPOXY='<HOST>'
export LUMINATI='<COMPLETE URL>'
```

#### HOW TO USE
Basic usage without custom parameters
```python
from ByRequests.ByRequests import ByRequest

# Create session
byrequest = ByRequest()

# Get Request
response = byrequest.get("http:www.someurl.com")

# Post Request obtaining json
response_json = byrequest.post("http:www.someurl.com", returning_json=True)

# Parsing soup
soup = byrequest.soup("http:www.someurl.com")

# Parsing Xpath
xpath = byrequest.xpath("http:www.someurl.com")
```

#### ByRequest Parameters
proxies
```python
# 1st Option:   proxies=None
# Your requests are not going to use any kind of proxy service
byrequest = ByRequest(proxies=None)

# 2nd Option:   proxies="<Proxy Service>"
# Your requests are going to use the proxy service that you specified
byrequest = ByRequest(proxies="Crawlera")

# 3rd Option:   proxies="<Proxy Service>"
# Your requests are going to use the proxy service that you specified
byrequest = ByRequest(proxies="Crawlera")

# 4th Option:   proxies=[<Proxy Service>, <Proxy Service>]
# The requests are going to be send with the proxy services that you specified  in the order that they appear for 3 times (Default value for max_retries, unless it has been specified with the max_retries parameter) unless a good response's obtained before.
# * None represents the use of no proxies
byrequest = ByRequest(proxies=[None, "Crawlera", "Scrapoxy", "crawlera"])


# 5th Option:   proxies={<Proxy Service>: <max retries>, <Proxy Service>: <max retries>}
# The requests are going to be send with the proxy services that you specified  in the order that they appear 'max_retries' times each proxy service until a good response is obtained.
# * None represents the use of no proxies
byrequest = ByRequest(proxies={None: 3, "luminati": 1, "Scrapoxy":"2", "crawlera": "1"])

```



