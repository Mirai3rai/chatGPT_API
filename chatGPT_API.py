from hoshino import Service, priv, log, logger
from hoshino.typing import CQEvent
import openai
from .textfilter.filter import DFAFilter
import asyncio
import json
from os.path import dirname
from pathlib import Path
from datetime import datetime

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

curpath = Path(dirname(__file__))
data_path = curpath / "data"
data_path.mkdir(exist_ok=True)
context_path = data_path / "context.json"
settings_path = data_path / "settings.json"
config_path = curpath / "config.json"


assert config_path.exists(), "Please make a copy of [config.jon.example] and config your token"
with open(config_path, "r", encoding="utf-8") as fp:
    config = json.load(fp)
    assert config.get("token", "") != "", "ChatGPT module needs a token!"
    openai.api_key = config["token"]
    openai.proxy = config.get("proxy", "")

# from nonebot import on_startup
# @on_startup
# async def onStartup():
#     pass


def getNowtime() -> int:
    return int(datetime.timestamp(datetime.now()))


def saveSettings(dic: dict) -> None:
    with open(settings_path, "w", encoding='utf=8') as fp:
        json.dump(dic, fp, ensure_ascii=False, indent=4)


def saveContext(dic: dict) -> None:
    with open(context_path, "w", encoding='utf=8') as fp:
        json.dump(dic, fp, ensure_ascii=False, indent=4)


def getSettings() -> dict:
    if not settings_path.exists():
        saveSettings({})
    with open(settings_path, "r", encoding='utf=8') as fp:
        return json.load(fp)


def getContext() -> dict:
    if not context_path.exists():
        saveContext({})
    with open(context_path, "r", encoding='utf=8') as fp:
        return json.load(fp)


@sv.on_fullmatch(('GPT', 'gpt', "GPT帮助", "gpt帮助"), only_to_me=False)
async def sendHelp(bot, ev):
    await bot.send(ev, sv_help)


async def getChatResponse(prompt: str, setting: str = None, context: list = None) -> str:
    msg = []
    if setting is not None:
        msg.append({"role": "system", "content": setting})
    if context is not None:
        msg += context
    msg.append({"role": "user", "content": prompt})
    response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=msg)
    response = response.choices[0].message.content
    return response


def beautiful(msg: str) -> str:
    beautiful_message = DFAFilter()
    beautiful_message.parse(curpath / 'textfilter/sensitive_words.txt')
    return beautiful_message.filter(msg)


lck = asyncio.Lock()


async def _chatGptMethod(prompt: str, setting: str = None, context: list = None) -> str:
    if lck.locked():
        await asyncio.sleep(3)

    async with lck:
        try:
            resp = await getChatResponse(prompt, setting, context)
        except Exception as e:
            resp = f'Fail. {e}'
        finally:
            return resp.strip()


@sv.on_prefix(('#GPT', '#gpt'), only_to_me=False)
async def chatGptMethod(bot, ev):
    uid = str(ev.user_id)
    msg = str(ev.message.extract_plain_text()).strip()
    settings = getSettings()

    context = getContext()
    user_context = context[uid]["context"] if (getNowtime() - context.get(uid, {}).get("time", -1) <= 300) else None
    
    ret = await _chatGptMethod(msg, settings.get(uid, None), user_context)

    if "Fail." not in ret:
        context[uid] = {
            "context": [{"role": "user", "content": msg}, {"role": "assistant", "content": ret}],
            "time": getNowtime()
        }
        saveContext(context)

    await bot.send(ev, ret, at_sender=True)


@sv.on_prefix(('GPT定制', 'gpt定制', 'gpt设定', 'GPT设定'))
async def chatGptSetting(bot, ev):
    uid = str(ev.user_id)
    msg = str(ev.message.extract_plain_text()).strip()
    outp = []

    if len(msg) > 32:
        await bot.finish(ev, "太长力！")
    settings = getSettings()

    if len(msg) and msg not in ["重置", "清空"]:
        if uid in settings:
            outp.append(f'chat的原角色设定为：{settings[uid]}')
        settings[uid] = msg
        saveSettings(settings)
        outp.append(f'chat的现角色设定为：{msg}')
        # outp.append(f'角色设定测试：{await _chatGPT_method("你是谁？", msg)}')
    elif uid in settings:
        outp.append(f'chat的当前角色设定为：{settings[uid]}')
        if msg == "重置":
            settings.pop(uid)
            saveSettings(settings)
            outp.append('已重置为默认角色设定')
    else:
        outp.append('chat当前为默认角色设定')

    await bot.send(ev, "\n".join(outp), at_sender=True)
