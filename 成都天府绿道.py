
"""
脚本: 成都天府绿道小程序自动任务脚本
变量名：TFLD
变量格式：wxa_session_id#uid#w_open_id
多账号之间用&分隔

"""




import os

import json

import random

import requests

import urllib.parse

import time

from datetime import datetime


# WxPusher配置
WX_TOKEN = os.getenv('WX_PUSHER_APP_TOKEN', '')  # WxPusher的appToken
WX_UID = os.getenv('WX_PUSHER_UID', '')  # WxPusher的UID

# 哆啦A梦表情包
DORAEMON_EMOJI = {
    'happy': '(｡•ᴗ•｡)❤',
    'sad': '(｡•́︿•̀｡)',
    'surprised': '(⊙_⊙)？',
    'love': '(♡˙︶˙♡)',
    'cute': '(◕‿◕✿)',
    'error': '(╥﹏╥)',
    'sleep': '(￣▽￣)~*',
    'magic': '✨(◕‿◕)✨'
}



# 评论内容列表

comment_list = [

    "真是太棒了", 

    "很有意义啊", 

    "绿道很漂亮", 

    "期待更多活动", 

    "下次一定参加"

]



def send_wxpusher(title, content):
    """使用WxPusher发送通知"""
    if not WX_TOKEN:
        print(f"😅 哎呀，WxPusher的口袋还没准备好呢~ {DORAEMON_EMOJI['sad']}")
        return
    
    if not WX_UID:
        print(f"😅 哎呀，还没告诉我要发给谁呢~ {DORAEMON_EMOJI['sad']}")
        return
    
    url = "http://wxpusher.zjiecode.com/api/send/message"
    data = {
        "appToken": WX_TOKEN,
        "content": f"『哆啦A梦的绿道日记』\n\n{content}\n\n🎀 今天也要开心哦~ {DORAEMON_EMOJI['happy']}",
        "contentType": 1,
        "topicIds": [],
        "uids": [WX_UID],
        "url": ""
    }
    
    try:
        response = requests.post(url, json=data)
        if response.json().get('code') == 1000:
            print(f"✉️ 哆啦A梦已经把消息传送到你的口袋啦~ {DORAEMON_EMOJI['magic']}")
        else:
            print(f"😿 消息传送遇到了一点小问题：{response.json().get('msg')} {DORAEMON_EMOJI['sad']}")
    except Exception as e:
        print(f"❌ 糟糕，消息传送时出错了：{str(e)} {DORAEMON_EMOJI['error']}")

def get_env_configs():
    """从环境变量获取配置信息"""
    # 获取环境变量
    env_str = os.getenv('cdtf', '')
    if not env_str:
        print(f"😅 未设置环境变量cdtf {DORAEMON_EMOJI['surprised']}")
        return []

    

    configs = []

    # 分割多账号配置
    accounts = env_str.split('&')

    

    for i, account in enumerate(accounts, 1):

        parts = account.strip().split('#')

        if len(parts) == 3:

            configs.append({

                'wxa_session_id': parts[0],

                'uid': parts[1],

                'w_open_id': parts[2],

                'index': i  # 添加账号索引

            })

        else:

            print(f"账号{i}格式错误，应为wxa_session_id#uid#w_open_id")

    

    return configs



def get_headers(config):

    """获取请求头"""

    wxa_session_id = config.get('wxa_session_id', '')

    uid = config.get('uid', '')

    w_open_id = config.get('w_open_id', '')

    

    headers = {

        'Host': 'app-cdc.tfgreenroad.com',

        'apptype': 'miniprogram',

        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2540316) XWEB/13623',

        'content-type': 'application/x-www-form-urlencoded',

        'wxa_session_id': wxa_session_id,

        'uid': uid,

        'accept': '*/*',

        'accept-encoding': 'gzip, deflate, br',

        'cookie': f'w_uid={uid}; w_open_id={w_open_id};'

    }

    return headers



def get_current_points(headers):

    """获取当前积分"""

    url = 'https://app-cdc.tfgreenroad.com/vip/member/v1/api/myPoints?tradeType=2'

    

    try:

        payload = {}

        if payload:

            headers['Content-Length'] = str(len(json.dumps(payload)))

            response = requests.get(url, headers=headers, json=payload)

        else:

            # 删除Content-Length头

            if 'Content-Length' in headers:

                del headers['Content-Length']

            response = requests.get(url, headers=headers)

        

        result = response.json()

        if result.get('ret') == 0:

            points_num = result.get('data', {}).get('pointsNum', 0)

            expire_num = result.get('data', {}).get('expireNum', 0)

            expire_date = result.get('data', {}).get('expireDate', '')

            print(f"当前积分余额{points_num}")

            return {

                'status': True, 

                'points_num': points_num,

                'expire_num': expire_num,

                'expire_date': expire_date

            }

        else:

            print(f"获取积分失败: {result.get('msg')}")

            return {'status': False}

    except Exception as e:

        print(f"获取积分异常: {e}")

        return {'status': False}



def get_daily_points(headers):

    """获取今日获得的积分"""

    url = 'https://app-cdc.tfgreenroad.com/vip/points/v1/api/sign/rule'

    

    try:

        if 'Content-Length' in headers:

            del headers['Content-Length']

        

        response = requests.get(url, headers=headers)

        result = response.json()

        

        if result.get('ret') == 0:

            daily_points = result.get('data', {}).get('points', 0)

            return {'status': True, 'daily_points': daily_points}

        else:

            print(f"获取今日积分失败: {result.get('msg')}")

            return {'status': False}

    except Exception as e:

        print(f"获取今日积分异常: {e}")

        return {'status': False}



def do_sign(headers):

    """执行签到"""

    url = 'https://app-cdc.tfgreenroad.com/vip/points/v1/api/sign'

    

    try:

        payload = {}

        headers['Content-Length'] = str(len(json.dumps(payload)))

        response = requests.post(url, headers=headers, json=payload)

        result = response.json()

        

        if result.get('ret') == 0:

            sign_days = result.get('data', {}).get('days', 0)

            sign_reward = result.get('data', {}).get('value', 0)

            

            # 判断是否触发抽奖

            draw_result = result.get('data', {}).get('drawResult')

            if draw_result:

                # 抽奖情况

                name = draw_result.get('name')

                if name:

                    print(f"签到成功，周期内签到{sign_days}天，获得积分{sign_reward}，抽到奖品{name}")

                else:

                    print(f"签到成功，周期内签到{sign_days}天，获得积分{sign_reward}，抽奖什么都没有抽到")

            else:

                # 普通签到情况

                print(f"签到成功，周期内签到{sign_days}天，获得积分{sign_reward}")

            

            # print(f"签到响应: {json.dumps(result, ensure_ascii=False)}")

            return True

        else:

            print(f"签到失败: {result.get('msg')}")

            return False

    except Exception as e:

        print(f"签到异常: {e}")

        return False



def get_article_list(headers):

    """获取文章列表"""

    url = 'https://app-cdc.tfgreenroad.com/appserver/v1/mustPlay/list?pageSize=10&pageIndex=1&scenicId=1&contentType='

    

    try:

        if 'Content-Length' in headers:

            del headers['Content-Length']

        response = requests.get(url, headers=headers)

        result = response.json()

        

        if result.get('ret') == 0:

            articles = []

            must_play_list = result.get('data', {}).get('mustPlayList', [])

            

            # 获取前3篇文章

            count = min(3, len(must_play_list))

            for i in range(count):

                article = must_play_list[i]

                articles.append({

                    'contentId': article.get('contentId', ''),

                    'name': article.get('name', '')

                })

            

            # 打印文章列表

            print("即将使用3篇文章进行分享和评论：")

            for i, article in enumerate(articles, 1):

                print(f"{i}.{article['name']}")

            

            return articles

        else:

            print(f"获取文章列表失败: {result.get('msg')}")

            return []

    except Exception as e:

        print(f"获取文章列表异常: {e}")

        return []



def share_article(headers, article):

    """分享文章"""

    url = 'https://app-cdc.tfgreenroad.com/vip/points/v1/api/inner/benefits/order/share/submit'

    

    try:

        # 构建表单数据

        payload = {

            'orginId': article['contentId']

        }

        form_data = urllib.parse.urlencode(payload)

        headers['Content-Length'] = str(len(form_data))

        

        response = requests.post(url, headers=headers, data=form_data)

        result = response.json()

        

        if result.get('ret') == 0:

            print(f"文章【{article['name']}】分享成功")

            return True

        else:

            print(f"文章【{article['name']}】分享失败: {result.get('msg')}")

            return False

    except Exception as e:

        print(f"文章【{article['name']}】分享异常: {e}")

        return False



def comment_article(headers, article):

    """评论文章"""

    url = 'https://app-cdc.tfgreenroad.com/appserver/v1/comment/addComment'

    

    try:

        # 随机选择一条评论

        comment = random.choice(comment_list)

        

        # 构建请求数据 - 直接使用原始值，不预先编码

        data = {

            'cid': article['contentId'],

            'type': 'travel_notes',

            'uid': headers['uid'],

            'ctitle': article['name'],

            'content': comment,

            'image': '',

            'parent_id': '',

            'source_type': 'wxapp'

        }

        

        # 使用urlencode自动处理编码

        payload = urllib.parse.urlencode(data)

        headers['Content-Length'] = str(len(payload))

        

        response = requests.post(url, headers=headers, data=payload)

        result = response.json()

        

        if result.get('ret') == 0:

            print(f"文章【{article['name']}】评论成功")

            return True

        else:

            print(f"文章【{article['name']}】评论失败: {result.get('msg')}")

            return False

    except Exception as e:

        print(f"文章【{article['name']}】评论异常: {e}")

        return False



def cycling_login(headers):

    """登录骑行专区活动"""

    url = 'https://app-cdc.tfgreenroad.com/cycling/credit/login'

    

    try:

        payload = {}

        headers['Content-Length'] = str(len(json.dumps(payload)))

        response = requests.post(url, headers=headers, json=payload)

        result = response.json()

        

        if result.get('ret') == 0:

            value = result.get('data', {}).get('value', 0)

            print(f"骑行专区签到成功，获得{value}积分")

            return True

        else:

            print(f"骑行专区签到失败: {result.get('msg')}")

            return False

    except Exception as e:

        print(f"骑行专区签到异常: {e}")

        return False



def cycling_share(headers):

    """分享骑行专区文章"""

    url = 'https://app-cdc.tfgreenroad.com/cycling/credit/share'

    

    try:

        payload = {}

        headers['Content-Length'] = str(len(json.dumps(payload)))

        response = requests.post(url, headers=headers, json=payload)

        result = response.json()

        

        if result.get('ret') == 0:

            value = result.get('data', {}).get('value', 0)

            print(f"骑行专区文章分享成功，获得{value}积分")

            return True

        else:

            print(f"骑行专区文章分享失败: {result.get('msg')}")

            return False

    except Exception as e:

        print(f"骑行专区文章分享异常: {e}")

        return False



def camping_login(headers):

    """露营专区签到"""

    url = 'https://app-cdc.tfgreenroad.com/camping/user/login'

    

    try:

        payload = {}

        headers['Content-Length'] = str(len(json.dumps(payload)))

        response = requests.post(url, headers=headers, json=payload)

        result = response.json()

        

        if result.get('ret') == 0:

            value = result.get('data', {}).get('value', 0)

            print(f"露营专区签到成功，获得{value}积分")

            return True

        else:

            print(f"露营专区签到失败: {result.get('msg')}")

            return False

    except Exception as e:

        print(f"露营专区签到异常: {e}")

        return False



def process_account(config):
    """处理单个账号"""
    account_index = config.get('index', 0)
    print(f"\n🌟 第{account_index}个口袋开始执行任务啦~ {DORAEMON_EMOJI['happy']}\n")

    # 构建请求头
    headers = get_headers(config)

    # 获取初始积分
    points_info = get_current_points(headers)
    if not points_info.get('status'):
        print(f"😢 第{account_index}个口袋好像有点问题，Token可能失效了呢 {DORAEMON_EMOJI['sad']}")
        return

    # 执行签到
    print(f"🎯 让我们先来签个到吧~ {DORAEMON_EMOJI['cute']}")
    do_sign(headers)
    
    # 获取文章列表并执行分享和评论
    print(f"\n📚 让我找找有趣的文章... {DORAEMON_EMOJI['magic']}")
    articles = get_article_list(headers)

    if articles:
        # 执行文章分享
        print(f"\n🌟 一起来分享这些精彩内容吧~ {DORAEMON_EMOJI['love']}")
        for article in articles:
            share_article(headers, article)
        
        # 执行文章评论
        print(f"\n💭 写下我的小感想... {DORAEMON_EMOJI['happy']}")
        for article in articles:
            comment_article(headers, article)

    # 执行骑行专区签到
    print(f"\n🚲 骑行专区也要打个卡~ {DORAEMON_EMOJI['cute']}")
    cycling_login(headers)
    
    # 执行骑行专区分享
    print(f"\n🎈 分享骑行的快乐时光！{DORAEMON_EMOJI['happy']}")
    cycling_share(headers)
    
    # 执行露营专区签到
    print(f"\n⛺ 去露营专区看看~ {DORAEMON_EMOJI['magic']}")
    camping_login(headers)

    # 获取今日获得的积分
    print(f"\n🎁 让我数数今天获得了多少积分~ {DORAEMON_EMOJI['cute']}")
    daily_points_info = get_daily_points(headers)
    
    # 获取最新积分
    print(f"\n💰 来看看最新的积分余额... {DORAEMON_EMOJI['magic']}")
    new_points_info = get_current_points(headers)

    if daily_points_info.get('status') and new_points_info.get('status'):
        daily_points = daily_points_info.get('daily_points', 0)
        new_points = new_points_info.get('points_num', 0)
        expire_num = new_points_info.get('expire_num', 0)
        expire_date = new_points_info.get('expire_date', '')
        
        # 准备推送内容
        push_content = f"📱 第{account_index}个口袋:\n"
        push_content += f"✨ 今日收获：{daily_points}积分\n"
        push_content += f"💝 当前积分：{new_points}\n"
        
        # 添加积分兑换提醒
        if new_points >= 1990:
            push_content += f"🎉 恭喜！当前积分已经可以兑换商品啦~\n"
            print(f"\n🎊 太棒了！积分已经可以兑换商品了哦~ {DORAEMON_EMOJI['love']}")
        
        # 添加积分过期提醒
        if expire_num > 0:
            push_content += f"⚠️ 温馨提醒：有{expire_num}积分将在{expire_date}过期哦~"
        
        # 发送推送
        send_wxpusher("任务完成", push_content)
        
        print(f"\n🌈 第{account_index}个口袋今天的任务完成啦！{DORAEMON_EMOJI['happy']}")
        print(f"✨ 今日获得了{daily_points}积分，现在共有{new_points}积分啦~")
        if expire_num > 0:
            print(f"📢 温馨提醒：有{expire_num}积分将在{expire_date}过期，要记得使用哦~ {DORAEMON_EMOJI['surprised']}")

    print(f"\n======账号{account_index}执行完成======")



def main():
    print(f"\n🎵 叮叮当，口袋打开啦！{DORAEMON_EMOJI['magic']}")
    print(f"======天府绿道签到任务开始 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}======")

    

    # 获取配置

    configs = get_env_configs()

    if not configs:

        print("未获取到有效配置，退出脚本")

        return

    

    print(f"共获取到{len(configs)}个账号")

    

    # 处理每个账号

    for i, config in enumerate(configs):

        process_account(config)

        

        # 如果不是最后一个账号，则随机延迟3-5秒

        if i < len(configs) - 1:

            delay_time = random.randint(3, 5)

            print(f"\n随机延迟{delay_time}秒后处理下一个账号...")

            time.sleep(delay_time)

    

    print(f"\n======天府绿道签到任务结束 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}======")



if __name__ == "__main__":

    main()