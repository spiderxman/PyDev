from scrapy import cmdline
#cmdline.execute("scrapy crawl aitaotuCrawler -s LOG_FILE=scrapy.log".split())
cmdline.execute("scrapy crawl aitaotuSpider -s JOBDIR=crawls/aitaotuSpider-1 -s LOG_FILE=scrapy.log".split())
