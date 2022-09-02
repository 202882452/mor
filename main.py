import random
from time import localtime
from datetime import date, datetime
import math
# from time import tzset
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import sys
import os


def yq(region, config_data):
    key = config_data["weather_key"]
    url = "https://geoapi.qweather.com/v2/city/lookup?key={}&location={}".format(key, region)
    r = get(url).json()
    if r["code"] == "200":
        city = r["location"][0]["adm2"]
        if region in ["台北", "高雄", "台中", "台湾"]:
            city = "台湾"
    else:
        city = ""
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36',
    }

    response = get('https://covid.myquark.cn/quark/covid/data?city={}'.format(city), headers=headers).json()
    if city in ["北京", "上海", "天津", "重庆", "香港", "澳门", "台湾"]:
        city_data = response["provinceData"]
    else:
        city_data = response["cityData"]
    try:
        sure_new_loc = "昨日新增：{}".format(city_data["sure_new_loc"])
        sure_new_hid = "昨日无症状：{}".format(city_data["sure_new_hid"])
        present = "现有确诊：{}".format(city_data["present"])
        danger = "中/高风险区：{}/{}".format(city_data["danger"]["1"], city_data["danger"]["2"])
        statistics_time = response["time"]
        yq_data = "{}疫情数据\n{}\n{}\n{}\n{}\n{}".format(city, sure_new_loc, sure_new_hid, present, danger, statistics_time)
    except TypeError:
        yq_data = ""
    return yq_data


def get_commemoration_day(today, commemoration_day):
    # 获取纪念日的日期格式
    commemoration_year = int(commemoration_day.split("-")[0])
    commemoration_month = int(commemoration_day.split("-")[1])
    commemoration_day = int(commemoration_day.split("-")[2])
    commemoration_date = date(commemoration_year, commemoration_month, commemoration_day)
    # 获取纪念日的日期差
    commemoration_days = str(today.__sub__(commemoration_date)).split(" ")[0]
    return commemoration_days


def get_commemoration_data(today, config_data):
    # 获取所有纪念日数据
    commemoration_days = {}
    for k, v in config_data.items():
        if k[0:13] == "commemoration":
            commemoration_days[k] = get_commemoration_day(today, v)
    return commemoration_days


def color(name, config):
    # 获取字体颜色，如没设置返回随机颜色
    try:
        if config[name] == "":
            color = get_color()
        else:
            color = config[name]
        return color
    except KeyError:
        color = get_color()
        return color


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  return weather['weather'], math.floor(weather['temp'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

def get_city():
  return (city)

client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature = get_weather()
data = {"city":{"value":city},"weather":{"value":wea},"temperature":{"value":temperature},"love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},"words":{"value":get_words(), "color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
