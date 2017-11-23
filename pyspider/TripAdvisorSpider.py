#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-21 23:29:15
# Project: TripAdvisorSpider

from pyspider.libs.base_handler import *
import re
import pymongo


class Handler(BaseHandler):
    '''
    抓取www.tripadvisor.cn网站景点搜索结果页以及详情页信息
    '''
    crawl_config = {
    }

    page_start = 660  # 默认第一页从0开始
    page_step = 30  # 每一页递增30，即第2页是30
    next_url = None
    start_url = 'https://www.tripadvisor.cn/Search?ssrc=A&q=%E6%BE%B3%E5%A4%A7%E5%88%A9%E4%BA%9A&geo=&sid=09AB1DC3BE6ED9600006CDE422AFE8621511446534135&rf=0&actionType=updatePage&dist=undefined&o={}&ajax=search'.format(
        page_start)  # 起始url

    @every(minutes=24 * 60)  # @every(minutes=24*60, seconds=0) 这个设置是告诉scheduler（调度器）on_start方法每天执行一次。
    def on_start(self):  # def on_start(self) 方法是入口代码。当在web控制台点击run按钮时会执行此方法。
        # self.crawl(url, callback=self.index_page)这个方法是调用API生成一个新的爬取任务，这个任务被添加到待抓取队列。
        self.crawl(self.start_url, callback=self.index_page)

    @config(
        age=60)  # @config(age=10 * 24 * 60 * 60) 这个设置告诉scheduler（调度器）这个request（请求）过期时间是10天，10天内再遇到这个请求直接忽略。这个参数也可以在self.crawl(url, age=10*24*60*60) 和 crawl_config中设置。
    def index_page(self, response):
        # def index_page(self, response) 这个方法获取一个Response对象。 response.doc是pyquery对象的一个扩展方法。pyquery是一个类似于jQuery的对象选择器。
        for each in response.doc('a[href^="http"]').items():  # response.doc
            # 使用正则匹配详情页地址
            match = re.search(r"https://www.tripadvisor.cn/Attraction_Review-.*\.html", each.attr('href'))
            if match:  # 使用正则获取匹配的部分
                result = match.group()
                self.crawl(result, callback=self.detail_page)
        # 每页30个 自动获取下一页，通过选择器判断是否到达最后一页
        print("当前page_start为：%d 是否是最后一页： %s" % (
        self.page_start, response.doc("a.ui_button.pagination-next.primary").hasClass("disabled")))
        self.page_start += self.page_step
        if not response.doc("a.ui_button.pagination-next.primary").hasClass("disabled"):  # 不是最后一页
            self.next_url = 'https://www.tripadvisor.cn/Search?ssrc=A&q=%E6%BE%B3%E5%A4%A7%E5%88%A9%E4%BA%9A&geo=&sid=09AB1DC3BE6ED9600006CDE422AFE8621511446534135&rf=0&actionType=updatePage&dist=undefined&o={}&ajax=search'.format(
                self.page_start)
            self.crawl(self.next_url, callback=self.index_page)

    @config(priority=2)  # @config(priority=2) 这个是优先级设置。数字越小越先执行。
    def detail_page(self, response):
        # def detail_page(self, response)返回一个结果集对象。这个结果默认会被添加到resultdb数据库（如果启动时没有指定数据库默认调用sqlite数据库）。你也可以重写on_result(self,result)方法来指定保存位置。

        name = response.doc('#HEADING.heading_title').text()  # 景点名称
        ranking = response.doc('div > span > b > span').text()  # 景点排名
        location = response.doc('span.locality').text()  # 景点位置
        phone = response.doc('div > div.blEntry.phone > span:nth-child(2)').text()  # 景点电话
        bussinesstime = response.doc('div.section.hours > div > div:nth-child(2) > div').text()  # 景点营业时间
        rating = response.doc('span.overallRating').text()  # 景点评分

        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "name": name,
            "ranking": ranking,
            "rating": rating,
            "location": location,
            "phone": phone,
            "bussinesstime": bussinesstime
        }

    client = pymongo.MongoClient("localhost")
    db = client['TripAdvisor']  # 库名

    def on_result(self, result):  # 重写on_result(self,result)方法来指定保存位置。
        if result:
            self.save_to_mongo(result)

    def save_to_mongo(self, result):
        if self.db['Australia'].update({"url": result['url']}, {"$set": result}, True):  # 表名
            print('saved mongo success :', result)


