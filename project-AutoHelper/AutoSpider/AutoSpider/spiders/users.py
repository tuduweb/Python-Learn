import scrapy
import json
from AutoSpider.items import UserItem

class UsersSpider(scrapy.Spider):
    name = 'users'
    allowed_domains = ['learnerhub.net']
    custom_settings = {
        'ITEM_PIPELINES': {
            'AutoSpider.pipelines.UserPipeline': 300,
        },
    }
    #start_urls = ['https://learnerhub.net/']
    web_token = ''
    group_id = 189


    #该页面需要进行鉴权
    def start_requests(self):
        #https://api.learnerhub.net/v1/users/login
        return [scrapy.Request('https://api.learnerhub.net/v1/groups/%d/users?page=1' % self.group_id,
            meta={'cookiejar': 1}, callback=self.parse_userlist, headers={'Authorization': self.web_token})]

    def start_login(self):
        #登录操作,暂时忽略
        pass

    def parse_userlist(self, response):
        rs = json.loads(response.text)
        print(rs)

        # 边界处理有问题
        for user in rs.get('data'):
            user_item = UserItem()
            user_item['user_id'] = user.get('user').get('id')
            user_item['user_truename'] = user.get('join_condition_hash').get('姓名')
            user_item['user_schoolid'] = user.get('join_condition_hash').get('学号')

            user_item['created_at'] = user.get('created_at')
            user_item['updated_at'] = user.get('updated_at')

            yield user_item

        if rs.get('kaminari').get('next_page') is not None and rs.get('kaminari').get('next_page') > 0:
            yield scrapy.Request('https://api.learnerhub.net/v1/groups/%d/users?page=%d' % (self.group_id, rs.get('kaminari').get('next_page')),
            meta={'cookiejar': 1}, callback=self.parse_userlist, headers={'Authorization': self.web_token})
        pass



    def parse(self, response):
        pass
