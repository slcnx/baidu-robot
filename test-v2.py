import datetime
import random
import re
import threading
import time

import requests
from aiohttp import web
from lxml import etree

regex = re.compile('.{3,100}(吗|吧|啊|呢|还是|是什么|是不是).*$')
regex2 = re.compile('.{5,100}？$')
anser_questions = {}


class Config:
    ACTION_PUT = datetime.datetime.now()  # 避免因为重启程序太频繁
    # ACTION_PUT = None


proxypool_url = 'http://192.168.1.237:5555/random'

lock = threading.Lock()
user_agent_list = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
    "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]


async def get_group_name(group_id):
    # 192.168.1.222:5700/get_group_info?group_id=305929080
    resp = requests.get("http://192.168.1.222:5700/get_group_info?group_id={}".format(group_id))
    data = resp.json()
    resp.close()
    return data['data']['group_name']


async def parse(data) -> dict:
    group_id = data['group_id']
    group_name = await get_group_name(group_id)
    user_id = data['sender']['user_id']
    user_name = data['sender']['nickname']
    message = data['message']
    message_id = data['message_id']
    return {"group_id": group_id, "group_name": group_name, "user_id": user_id, "user_name": user_name,
            "message": message, "message_id": message_id}


def get_random_proxy():
    """
    get random proxy from proxypool
    :return: proxy
    """
    return requests.get(proxypool_url).text.strip()


def get_baidu_result(data,parent_threadname):
    while True:
        print('threading running requesting. {} get_baidu_result'.format(parent_threadname))
        BASE_URL = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&ch=2&bar=&wd={}"

        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'User-Agent': random.choice(user_agent_list),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://www.baidu.com/?tn=98010089_dg&ch=2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            # 'Cookie': 'delPer=0; BD_CK_SAM=1; PSINO=2; BIDUPSID=1347521F0C74BAEEEF9F37D36678F78B; PSTM=1626788452; BAIDUID=1347521F0C74BAEE606A2E6A8D9642EC:FG=1; H_PS_PSSID=34268_34099_33966_34222_33848_34072_34280_34106_26350; BDSVRTM=16'
        }

        proxies = {'http': 'http://' + get_random_proxy()}
        response = requests.get(BASE_URL.format(data['message']), headers=headers, proxies=proxies)

        root = etree.HTML(response.text)
        response.close()
        items = root.xpath('//div[contains(@class,"c-container")]/h3/a/@href')
        if items:
            time.sleep(6)
            result = random.choice(items)
            # 记录
            with open('send.log', 'a') as fb:
                fb.write(' send_group_msg: {group_id}  {result} \n'.format(group_id=data['group_id'],
                                                                           result=result))
            # 对应群
            send_group_msg(send_gid=data['group_id'], msg=result)
            break
        time.sleep(2)


def send_group_msg(send_gid, msg, answer="", gname=""):
    """
    :param send_gid: 发到哪个组
    :param msg:  回答的问题的答案
    :param answer: 回答的问题
    :param gname:  回答的问题所属组的名称
    :return:
    """
    resp = requests.get(
        "http://192.168.1.222:5700/send_msg?message_type=group&group_id={}&message={}".format(send_gid, """{}
        {} {}""".format(msg, gname, answer)))
    resp.close()


def handler(data, anser_questions, config: Config, send_timeout, group_timeout):
    # handler: {'group_id': 901304910, 'group_name': 'Kubernetes/K8S技术交流群Ⅱ', 'user_id': 525680379, 'user_name': '小红帽', 'message': '创建的pod做什么啊', 'message_id': 103950} -------------------------------
    # print('handler: {} ------------------------------- {}' .format(data,anser_questions))
    # 问问题, 相同用户，10分钟回复一次
    # 如果发过消息，5分钟后才可以发
    lock.acquire()

    print(threading.current_thread().name, id(Config), Config.ACTION_PUT, regex.search(data['message']),
          regex2.search(data['message']), data['message'], '======================')
    CURRENT_DATETIME = datetime.datetime.now()
    if Config.ACTION_PUT:
        print('{} {} exist'.format(threading.current_thread().name, Config.ACTION_PUT))
        if (CURRENT_DATETIME - Config.ACTION_PUT).seconds <= send_timeout:
            print('{} 当前时间比过去时间  {} - {} <= {}s'.format(threading.current_thread().name, CURRENT_DATETIME,
                                                        Config.ACTION_PUT, send_timeout))
            lock.release()
            return
        else:
            print('{} 当前时间比过去时间  {} - {} > {}s'.format(threading.current_thread().name, CURRENT_DATETIME,
                                                       Config.ACTION_PUT, send_timeout))

    if len(data['message']) <= 6:
        print('{} {} 消息长度小于6个字符'.format(threading.current_thread().name, data['message']))
        lock.release()
        return

    if regex.search(data['message']) or regex2.search(data['message']):
        old_time = anser_questions.get(data['group_id'])
        if not old_time:
            anser_questions[data['group_id']] = CURRENT_DATETIME - datetime.timedelta(minutes=10)
            old_time = CURRENT_DATETIME - datetime.timedelta(minutes=10)

        if (CURRENT_DATETIME - old_time).seconds >= group_timeout:
            print('{} {}  send message'.format(threading.current_thread().name, Config.ACTION_PUT, old_time))
            print(threading.current_thread().name, 'anser_questions', anser_questions,
                  '---------------------------------')
            anser_questions[data['group_id']] = CURRENT_DATETIME
            Config.ACTION_PUT = CURRENT_DATETIME
            print(threading.current_thread().name, '更新的结果.', Config.ACTION_PUT)
            print('{}  send, and 当前时间比过去时间 {} - {} > {}s'.format(threading.current_thread().name, CURRENT_DATETIME,
                                                                 old_time, group_timeout))
            threading.Thread(target=get_baidu_result,
                             args=(data,threading.current_thread().name)).start()
        else:
            print('{}   don\'t send, and 当前时间比过去时间 {} - {} < {}s'.format(threading.current_thread().name,
                                                                         CURRENT_DATETIME, old_time, group_timeout))

    lock.release()


# [b'POST / HTTP/1.1', b'Host: 192.168.1.222:9000', b'User-Agent: CQHttp/4.15.0', b'Content-Length: 399', b'Content-Type: application/json', b'X-Self-Id: 1062670898', b'Accept-Encoding: gzip', b'', b'{"interval":5000,"meta_event_type":"heartbeat","post_type":"meta_event","self_id":1062670898,"status":{"app_enabled":true,"app_good":true,"app_initialized":true,"good":true,"online":true,"plugins_good":null,"stat":{"packet_received":961,"packet_sent":686,"packet_lost":0,"message_received":243,"message_sent":0,"disconnect_times":0,"lost_times":0,"last_message_time":1626664808}},"time":1626664815}\n']
async def handle(request):
    data = await request.json()
    if data['post_type'] != "message":
        return web.Response(text='ok')

    """
    anonymous None
    font 0
    group_id 249358926
    message [CQ:image,file=97a48689fc4bee6cd24597b3ba39655d.image,url=https://gchat.qpic.cn/gchatpic_new/2833560177/4139358926-2812419531-97A48689FC4BEE6CD24597B3BA39655D/0?term=3]
    message_id 939628
    message_seq 939628
    message_type group
    post_type message
    raw_message [CQ:image,file=97a48689fc4bee6cd24597b3ba39655d.image]
    self_id 1062670898
    sender {'age': 0, 'area': '', 'card': '成都-苦逼运维程序员', 'level': '', 'nickname': '树先生', 'role': 'member', 'sex': 'unknown', 'title': '', 'user_id': 2833560177}
    sub_type normal
    time 1626665572
    user_id 2833560177
    """
    # print(data)
    result: dict = await parse(data)
    print()
    print("收到 {group_name}({group_id}) 内 {user_name}({user_id}) 的消息: {message}({message_id})".format(**result))
    print('当前值.', Config.ACTION_PUT)
    threading.Thread(target=handler, args=(result, anser_questions, Config, 10, 1800)).start()
    #   for k,v in data.items():
    #       print(k,v)
    #   print('===========')
    return web.Response(text='ok')


app = web.Application()
app.add_routes([web.post('/', handle)])

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=9000)
