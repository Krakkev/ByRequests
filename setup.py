import setuptools


setuptools.setup(
    name = 'ByRequests',
    packages = ['ByRequests'], # this must be the same as the name above
    version = '0.1.5',
    description = 'Helper to use proxy services with Requests',
    author = 'Kevin B. Garcia Alonso',
    author_email = 'kevangy@hotmail.com',
    url = 'https://github.com/Krakkev/ByRequests', # use the URL to the github repo
    download_url = 'https://github.com/Krakkev/ByRequests/tarball/0.1.5', # I'll explain this in a second
    keywords = ['requests', 'request', 'proxy', 'proxies', 'beautifulsoap', 'xpath', 'GET', 'POST'],
    install_requires=[
        'beautifulsoup4>=4.6.0',
        'bs4>=0.0.1',
        'requests>=2.18.1',
        'urllib3>=1.21.1',
        'fake-useragent>=0.1.10'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),
)
