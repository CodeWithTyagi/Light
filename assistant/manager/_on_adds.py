# Light UserBot
# Copyright (C) 2021-2022 CodeWithTyagi
#
# This file is a part of < https://github.com/CodeWithTyagi/Light >
# Please read the GNU Affero General Public License in
# https://www.github.com/CodeWithTyagi/Light/blob/main/LICENSE

from telethon import events

from . import *


@asst.on(events.ChatAction(func=lambda x: x.user_added))
async def dueha(e):
    user = await e.get_user()
    if not user.is_self:
        return
    sm = udB.get_key("ON_MNGR_ADD")
    if sm == "OFF":
        return
    if not sm:
        sm = "Thanks for Adding me :)"
    await e.reply(sm, link_preview=False)
