# coding=utf-8
import requests
import scrapy
import csv
import re
import sys
from retrying import retry
reload(sys)
sys.setdefaultencoding('utf-8')

import time

class myspider(object):

    def remove_space(self,text):
        newtext=re.sub('\s+', '', text)
        return newtext

    def get_hire_href(self,company):
        html=requests.get(company,timeout=2)
        html.encoding='utf-8'
        html=html.text
        alist=scrapy.Selector(text=html).xpath('.//a')
        link=""
        for a in alist:
            # print a.xpath('string(.)').extract_first()
            if u'加入我们' in a.xpath('string(.)').extract_first():
                link= a.xpath('./@href').extract_first()
                if re.search('^http', link):
                    pass
                else:
                    link=company+link
            if u'招贤纳士' in a.xpath('string(.)').extract_first():
                    link= a.xpath('./@href').extract_first()
                    if re.search('^http', link):
                        pass
                    else:
                        link=company+link
            if u'诚聘' in a.xpath('string(.)').extract_first():
                    link= a.xpath('./@href').extract_first()
                    if re.search('^http', link):
                        pass
                    else:
                        link=company+link
        return link

    def extract_one_company(self,companyurl):
        html=requests.get(companyurl).text
        selector=scrapy.Selector(text=html)
        location=company=""
        href=False
        try:
            location=selector.xpath('.//span[@class="loca c-gray-aset"]')[0].xpath('string(.)').extract_first()
        except:
            pass
        try:
            baseinfo=selector.xpath('.//div[@class="des-more"]')[0].xpath('.//span')
            for each in baseinfo:
                info=each.xpath('string(.)').extract_first()
                match= re.search(u'公司全称：(.*?$)', info, re.S)
                if match:
                    company=match.group(1)
        except:
            pass
        try:
            href=selector.xpath('.//a[@class="weblink marl10"]/@href').extract_first()
        except:
            pass
        return {'loc':self.remove_space(location),'name':company,'link':href}

    @retry(stop_max_attempt_number=3)
    def extract_one_page(self,url):
        with open('result','a') as f:
            html=requests.get(url).text

            li=scrapy.Selector(text=html).xpath('.//ul[@class="list-main-icnset"]/li')
            for item in li:

                href=item.xpath('.//p[@class="title"]/a/@href').extract_first()
                product=item.xpath('.//.//p[@class="title"]')[0].xpath('string(.)').extract_first()

                info=self.extract_one_company(href)
                if info['link']:
                    hireurl=self.get_hire_href(info['link'])
                else:
                    hireurl=""
                profile=product,info['name'],info['loc'],hireurl
                print product,info['name'],info['loc'],hireurl,info['link']
                f.write(','.join(profile)+'\n')

if __name__ == '__main__':
    p=myspider()
    for page in range(1,150):
        url='http://www.itjuzi.com/company?scope=126&fund_needs=1&page={}'.format(page)
        print url
        try:
            p.extract_one_page(url)
        except:
            pass

