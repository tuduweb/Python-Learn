import scrapy


class HomeworkSpider(scrapy.Spider):
    name = 'homework'
    allowed_domains = ['educoder.net']
    courseId = 11157
    start_urls = ['https://data.educoder.net/api/courses/'+str(courseId)+'/homework_commons.json?id='+str(courseId)+'&type=4'] # 更改成参数列表形式
    cookieStr = 'autologin_trustie=a68ab10e065ef847f63345cde07889b9485f****; _educoder_session=38a5f00fa48e8b20cf3235f6bbf4a9d6'

    def start_requests(self):
        cookies = {i.split('=')[0]: i.split('=')[1] for i in self.cookieStr.split('; ')}
        print(cookies)
        yield scrapy.Request(self.start_urls[0], cookies=cookies)

    def parse(self, response):
        print(response.text)
        pass
