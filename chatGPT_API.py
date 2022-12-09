from hoshino import Service, priv
from hoshino.typing import CQEvent
import openai
from .textfilter.filter import DFAFilter
import asyncio
import os

# 配置OpenAI的API密钥
openai.api_key = "你的API"
user_session = dict()

sv_help = """ 你自己设置的前缀 + 你要说的话就能实现
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


def get_chat_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        temperature=0.5,
    )["choices"][0]["text"]
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


@sv.on_prefix(('你的触发词'), only_to_me=False)
async def chatGPT_method(bot, ev):
    uid = ev.user_id
    gid = ev.group_id
    name = ev.sender['nickname']
    msg = str(ev.message.extract_plain_text()).strip()
    resp = await asyncio.get_event_loop().run_in_executor(None, get_chat_response, uid, msg)
    flit_resp = beautiful(resp)
    await bot.send(ev, flit_resp, at_sender=True)





