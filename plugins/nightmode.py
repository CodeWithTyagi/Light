# Light UserBot
# Copyright (C) 2021-2022 CodeWithTyagi
#
# This file is a part of < https://github.com/CodeWithTyagi/Light >
# Please read the GNU Affero General Public License in
# https://www.github.com/CodeWithTyagi/Light/blob/main/LICENSE

"""
✘ Commands Available -

At Night it will turn off everyone permission to send message in  an all groups which you added via `{i}addnight`
And Turn On auto at morning

• `{i}addnm`
   Add NightMode
   To Add Group To Auto Night Mode.

• `{i}remnm`
   Remove NightMode
   To remove Group From Auto Night Mode

• `{i}listnm`
   List NightMode
   To Get All List of Groups where NightMode Active.

• `{i}nmtime <close hour> <close min> <open hour> <open min>`
   NightMode Time
   By Default Its close 00:00 , open 07:00
   Use 24hr format
   Ex- `nmtime 01 00 06 30`
"""

from . import LOGS

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
except ImportError:
    LOGS.error("nightmode: 'apscheduler' not Installed!")
    AsyncIOScheduler = None

from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights

from LightUB.dB.night_db import *

from . import get_string, udB, light_bot, light_cmd


@light_cmd(pattern="nmtime( (.*)|$)")
async def set_time(e):
    if not e.pattern_match.group(1).strip():
        return await e.eor(get_string("nightm_1"))
    try:
        ok = e.text.split(maxsplit=1)[1].split()
        if len(ok) != 4:
            return await e.eor(get_string("nightm_1"))
        tm = [int(x) for x in ok]
        udB.set_key("NIGHT_TIME", str(tm))
        await e.eor(get_string("nightm_2"))
    except BaseException:
        await e.eor(get_string("nightm_1"))


@light_cmd(pattern="addnm( (.*)|$)")
async def add_grp(e):
    pat = e.pattern_match.group(1).strip()
    if pat:
        try:
            add_night((await light_bot.get_entity(pat)).id)
            return await e.eor(f"Done, Added {pat} To Night Mode.")
        except BaseException:
            return await e.eor(get_string("nightm_5"), time=5)
    add_night(e.chat_id)
    await e.eor(get_string("nightm_3"))


@light_cmd(pattern="remnm( (.*)|$)")
async def rem_grp(e):
    pat = e.pattern_match.group(1).strip()
    if pat:
        try:
            rem_night((await light_bot.get_entity(pat)).id)
            return await e.eor(f"Done, Removed {pat} To Night Mode.")
        except BaseException:
            return await e.eor(get_string("nightm_5"), time=5)
    rem_night(e.chat_id)
    await e.eor(get_string("nightm_4"))


@light_cmd(pattern="listnm$")
async def rem_grp(e):
    chats = night_grps()
    name = "NightMode Groups Are-:\n\n"
    for x in chats:
        try:
            ok = await light_bot.get_entity(x)
            name += f"@{ok.username}" if ok.username else ok.title
        except BaseException:
            name += str(x)
    await e.eor(name)


async def open_grp():
    chats = night_grps()
    for chat in chats:
        try:
            await light_bot(
                EditChatDefaultBannedRightsRequest(
                    chat,
                    banned_rights=ChatBannedRights(
                        until_date=None,
                        send_messages=False,
                        send_media=False,
                        send_stickers=False,
                        send_gifs=False,
                        send_games=False,
                        send_inline=False,
                        send_polls=False,
                    ),
                )
            )
            await light_bot.send_message(chat, "**NightMode Off**\n\nGroup Opened 🥳.")
        except Exception as er:
            LOGS.info(er)


async def close_grp():
    chats = night_grps()
    h1, m1, h2, m2 = 0, 0, 7, 0
    if udB.get_key("NIGHT_TIME"):
        h1, m1, h2, m2 = eval(udB.get_key("NIGHT_TIME"))
    for chat in chats:
        try:
            await light_bot(
                EditChatDefaultBannedRightsRequest(
                    chat,
                    banned_rights=ChatBannedRights(
                        until_date=None,
                        send_messages=True,
                    ),
                )
            )
            await light_bot.send_message(
                chat, f"**NightMode : Group Closed**\n\nGroup Will Open At `{h2}:{m2}`"
            )
        except Exception as er:
            LOGS.info(er)


if AsyncIOScheduler and night_grps():
    try:
        h1, m1, h2, m2 = 0, 0, 7, 0
        if udB.get_key("NIGHT_TIME"):
            h1, m1, h2, m2 = eval(udB.get_key("NIGHT_TIME"))
        sch = AsyncIOScheduler()
        sch.add_job(close_grp, trigger="cron", hour=h1, minute=m1)
        sch.add_job(open_grp, trigger="cron", hour=h2, minute=m2)
        sch.start()
    except Exception as er:
        LOGS.info(er)
