import scrapy
import json

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
        # print(response.text)
        rs = json.loads(response.text)
        homeworks = rs.get('homeworks')


        # {'homework_id': 243356, 'name': 'C语言基本输入输出实训', 'private_icon': True, 'status': ['已截止'], 'status_time': '评阅剩余时间：63 天 8 小时 18 分 ', 'time_status': 5, 'allow_late': False, 'author': '李志清', 'author_img': 'avatars/User/21310?t=1612439758', 'author_login': 'lizhiqing', 'created_at': '2021-03-01', 'upper_category_name': '第1章 C语言概述', 'position': 27, 'publish_immediately': False, 'end_immediately': False, 'commit_count': 96, 'uncommit_count': 0, 'all_count': 96, 'compelete_count': 96, 'shixun_identifier': '3aexl5my', 'shixun_status': 2, 'shixun_name': 'C语言基本输入输出实训', 'opening_time': None, 'is_enter_shixun': True, 'shixun_enter_status': 0}

        for homework in homeworks:
            # print(homework)
            all_count = homework.get('all_count')
            uncommit_count = homework.get('uncommit_count')
            commit_count = homework.get('commit_count')
            compelete_count = homework.get('compelete_count')
            print('#'*40)
            print(homework.get('name'))
            print(homework.get('status'))
            print(homework.get('status_time'))
            print("未开始:{0} 尝试中:{1} 已完成:{2}".format(uncommit_count, commit_count - compelete_count, compelete_count))
        
        # request: {"page":3,"limit":20,"order":"work_score","b_order":"desc","coursesId":"11157","categoryId":"275431"}
        # https://data.educoder.net/api/homework_commons/275431/works_list.json
        
        pass
