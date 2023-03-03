from hoshino import Service, priv, log, logger
from hoshino.typing import CQEvent
import openai
from .textfilter.filter import DFAFilter
import asyncio
import os
import json
from os.path import dirname, join
from nonebot import on_startup


curpath = dirname(__file__)
context_path = join(curpath, 'data/context.json')
settings_path = join(curpath, 'data/settings.json')
config_path = join(curpath, 'config.json')

TOKEN = ""
assert os.path.exists(config_path), "ChatGPT module needs a token!"
with open(config_path, "r", encoding="utf-8") as fp:
    config = json.load(fp)
    assert "TOKEN" in config, "ChatGPT module needs a token!"
    TOKEN = config["TOKEN"]


# @on_startup
# async def onStartup():
#     pass


def saveSettings(dic:dict) -> None:
    with open(settings_path, "w", encoding='utf=8') as fp:
        json.dump(dic, fp, ensure_ascii=False, indent=4)
        

def saveContext(dic:dict) -> None:
    with open(context_path, "w", encoding='utf=8') as fp:
        json.dump(dic, fp, ensure_ascii=False, indent=4)
        
        
def getSettings() -> dict:
    if not os.path.exists(settings_path):
        saveSettings({})
    with open(settings_path, "r", encoding='utf=8') as fp:
        return json.load(fp)


def getContext() -> dict:
    if not os.path.exists(context_path):
        saveContext({})
    with open(context_path, "r", encoding='utf=8') as fp:
        return json.load(fp)
    
        
openai.api_key = "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"  # 配置OpenAI的API密钥
# openai.proxy = ""  # 格式类似：http://127.0.0.1:1080

sv_help = """
#GPT <...>
GPT设定 你是<...>
GPT设定重置
""".strip()
sv = Service(
    name="chatGPT",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.SUPERUSER,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help  # 帮助说明
)


@sv.on_fullmatch(('GPT', 'gpt', "GPT帮助", "gpt帮助"), only_to_me=False)
async def send_help(bot, ev):
    await bot.send(ev, sv_help)


async def get_chat_response(prompt: str, setting: str = None, context: list = None) -> str:
    msg = []
    if setting is not None:
        msg.append({"role": "system", "content": setting})
    if context is not None:
        msg.append += context
    msg.append({"role": "user", "content": prompt})
    response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=msg)
    response = response.choices[0].message.content
    return response


def beautiful(msg: str) -> str:
    beautiful_message = DFAFilter()
    beautiful_message.parse(os.path.join(os.path.dirname(__file__), 'textfilter/sensitive_words.txt'))
    msg = beautiful_message.filter(msg)
    return msg


lck = asyncio.Lock()


async def _chatGPT_method(prompt: str, setting: str = None, context: list = None) -> str:
    if lck.locked():
        await asyncio.sleep(3)

    async with lck:
        try:
            resp = await get_chat_response(prompt, setting)
        except Exception as e:
            resp = f'Failed: {e}'
        else:
            pass  # resp = beautiful(resp)
        finally:
            return resp.strip()


@sv.on_prefix(('#GPT', '#gpt'), only_to_me=False)
async def chatGPT_method(bot, ev):
    uid = ev.user_id
    msg = str(ev.message.extract_plain_text()).strip()
    settings = getSettings()
    
    # print(settings.get(str(uid), None))
    ret = await _chatGPT_method(msg, settings.get(str(uid), None))
    await bot.send(ev, ret, at_sender=True)


@sv.on_prefix(('GPT定制', 'gpt定制', 'gpt设定', 'GPT设定'))
async def reset_setting(bot, ev):
    uid = str(ev.user_id)
    msg = str(ev.message.extract_plain_text()).strip()
    outp = []

    if len(msg) > 32:
        await bot.finish(ev, "太长力！")
    settings = getSettings()
    
    if len(msg) and msg != "重置":
        if uid in settings:
            outp.append(f'chat的原角色设定为：{settings[uid]}')
        settings[uid] = msg
        saveSettings(settings)
        outp.append(f'chat的现角色设定为：{msg}')
        outp.append(f'角色设定测试：{await _chatGPT_method("你是谁？", msg)}')
    else:
        if uid in settings:
            outp.append(f'chat的当前角色设定为：{settings[uid]}')
            if msg == "重置":
                settings.pop(uid)
                saveSettings(settings)
                outp.append(f'已重置为默认角色设定')
        else:
            outp.append(f'chat当前为默认角色设定')

    await bot.send(ev, "\n".join(outp), at_sender=True)
