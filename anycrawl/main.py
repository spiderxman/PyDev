from scrapy import cmdline
#cmdline.execute("scrapy crawl aitaotuCrawler -s LOG_FILE=scrapy.log".split())
cmdline.execute("scrapy crawl cssmobanSpider -s JOBDIR=crawls/cssmobanSpider-1 -s LOG_FILE=scrapy.log".split())
