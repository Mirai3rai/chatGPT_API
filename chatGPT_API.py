from hoshino import Service, priv, log
from hoshino.typing import CQEvent
import openai
from .textfilter.filter import DFAFilter
import asyncio
import os
import json

# 配置OpenAI的API密钥
openai.api_key = ""
openai.proxy = ""  # 格式类似：http://127.0.0.1:1080
user_session = dict()
block_groups = []

sv_help = """ 
你自己设置的前缀 + 你要说的话就能实现
[设置+屏蔽+开/关] 控制开关屏蔽，每次重启bot以后重新设置
[设置+本群状态] 查询本群是否被屏蔽
"""
sv = Service(
    name="chatGPT_API",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help  # 帮助说明
)


async def get_chat_response(prompt, setting='你是一个人工助手，负责帮助人回答他们的问题'):
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": setting},
            {"role": "user", "content": prompt}])
    return response


# 和谐模块
def beautifulworld(msg: str) -> str:
    w = ''
    infolist = msg.split('[')
    for i in infolist:
        if i:
            try:
                w = w + '[' + i.split(']')[0] + ']' + beautiful(i.split(']')[1])
            except:
                w = w + beautiful(i)
    return w


# 切换和谐词库
def beautiful(msg: str) -> str:
    beautiful_message = DFAFilter()
    beautiful_message.parse(os.path.join(os.path.dirname(__file__), 'textfilter/sensitive_words.txt'))
    msg = beautiful_message.filter(msg)
    return msg


@sv.on_fullmatch(('查设定'))
async def view_setting(bot, ev):
    uid = ev.user_id
    with open('./hoshino/modules/chatGPT_API/data.json', 'r') as f:
        setting_data = json.load(f)
    if str(uid) in setting_data:
        msg = setting_data[str(uid)]
        await bot.send(ev, "您当前的设定为:" + msg)
    else:
        await bot.send(ev, "您还没有自己的专属设定哦~", at_sender=True)


@sv.on_prefix(('设定触发词'), only_to_me=False)
async def chatGPT_method(bot, ev):
    uid = ev.user_id
    gid = ev.group_id
    name = ev.sender['nickname']
    msg = str(ev.message.extract_plain_text()).strip()
    with open('./hoshino/modules/chatGPT_API/data.json', 'r') as f:
        setting_data = json.load(f)
    try:
        if str(uid) in setting_data:
            resp = await get_chat_response(msg, setting_data[str(uid)])
        else:
            resp = await get_chat_response(msg)
        if gid in block_groups:
            flit_resp = beautiful(resp.choices[0].message.content)
        else:
            flit_resp = resp.choices[0].message.content
        await bot.send(ev, flit_resp, at_sender=True)
    except Exception as e:
        hoshino.logger.exception(e)
        await bot.send(ev, "出问题了，可以晚点再试试看捏~", at_sender=True)


@sv.on_prefix(('定制GPT'))
async def reset_setting(bot, ev):
    uid = ev['user_id']
    msg = str(ev.message.extract_plain_text()).strip()
    with open('./hoshino/modules/chatGPT_API/data.json', 'r') as f:
        setting_data = json.load(f)
    setting_data[str(uid)] = msg
    with open('./hoshino/modules/chatGPT_API/data.json', 'w') as f:
        json.dump(setting_data, f)
    await bot.send(ev, "写入完成~", at_sender=True)


@sv.on_prefix(('设置'))
async def block_set(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    is_su = priv.check_priv(ev, priv.SUPERUSER)
    args = ev.message.extract_plain_text().split()
    msg = ''
    if not is_su:
        msg = '需要超级用户权限'
    elif len(args) == 0:
        msg = '无效参数'
    elif args[0] == '屏蔽' and len(args) >= 2:
        global block_status
        if args[1] == '开' or args[1] == '启用':
            if gid in block_groups:
                msg = "开咯~"
                block_groups.remove(gid)
            else:
                msg = "一直开着呢"
        elif args[1] == '关' or args[1] == '禁用':
            if gid not in block_groups:
                msg = "关咯~"
                block_groups.append(gid)
            else:
                msg = "一直关着呢"
    elif args[0] == '本群状态':
        if gid in block_groups:
            msg = '本群没开屏蔽'
        else:
            msg = '本群已开启屏蔽'
    await bot.send(ev, msg)
