# Scrapy settings for redfin_sales project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# from shutil import which
# from webdriver_manager.chrome import ChromeDriverManager
BOT_NAME = 'redfin_sales'

SPIDER_MODULES = ['redfin_sales.spiders']
NEWSPIDER_MODULE = 'redfin_sales.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
LOG_LEVEL = "INFO"
