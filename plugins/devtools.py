# Light UserBot
# Copyright (C) 2021-2022 CodeWithTyagi
#
# This file is a part of < https://github.com/CodeWithTyagi/Light >
# Please read the GNU Affero General Public License in
# https://www.github.com/CodeWithTyagi/Light/blob/main/LICENSE

from . import get_help

__doc__ = get_help("help_devtools")

import inspect
import os
import sys
import traceback
from io import BytesIO, StringIO
from random import choice
from pathlib import Path
from pprint import pprint

from telethon.utils import get_display_name
from telethon.tl import functions
from yaml import safe_load

from LightUB import _ignore_eval
from . import *

try:
    import black  # Used for Formatting Eval Code.
except ImportError:
    black = None

try:
    from telegraph import upload_file as uf
except ImportError:
    uf = None


fn = functions


def osremove(*args):
    for _ in args:
        p = Path(_)
        if p.is_file():
            p.unlink()


@light_cmd(
    pattern="(sysinfo|neofetch)$",
)
async def _(e):
    xx = await e.eor(get_string("com_1"))
    x, y = await bash("neofetch|sed 's/\x1B\\[[0-9;\\?]*[a-zA-Z]//g' >> neo.txt")
    if y and y.endswith("NOT_FOUND"):
        return await xx.edit(f"Error: `{y}`")
    with open("neo.txt", "r") as neo:
        p = (neo.read()).replace("\n\n", "")
    haa = await Carbon(code=p, file_name="neofetch", backgroundColor=choice(ATRA_COL))
    await e.reply(file=haa)
    await xx.delete()
    os.remove("neo.txt")


@light_cmd(pattern="bash", fullsudo=True, only_devs=True)
async def _bash(event):
    carb = None
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
        if cmd.split()[0] in ["-c", "--carbon"]:
            cmd = cmd.split(maxsplit=1)[1]
            carb = True
    except IndexError:
        return await event.eor(get_string("devs_1"), time=10)
    xx = await event.eor(get_string("com_1"))
    reply_to_id = event.reply_to_msg_id or event.id
    stdout, stderr = await bash(cmd, run_code=1)
    OUT = f"**☞ BASH\n\n• COMMAND:**\n`{cmd}` \n\n"
    err, out = "", ""
    if stderr:
        err = f"**• ERROR:** \n`{stderr}`\n\n"
    if stdout:
        if (carb or udB.get_key("CARBON_ON_BASH")) and (
            event.is_private
            or event.chat.admin_rights
            or event.chat.creator
            or event.chat.default_banned_rights.embed_links
        ):
            li = await Carbon(
                code=stdout,
                file_name="bash",
                download=True,
                backgroundColor=choice(ATRA_COL),
            )
            url = f"https://graph.org{uf(li)[-1]}"
            OUT = f"[\xad]({url}){OUT}"
            out = "**• OUTPUT:**"
            os.remove(li)
        else:
            out = f"**• OUTPUT:**\n`{stdout}`"
    if not stderr and not stdout:
        out = "**• OUTPUT:**\n`Success`"
    OUT += err + out
    if len(OUT) > 4096:
        ultd = err + out
        with BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "bash.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb=LightConfig.thumb,
                allow_cache=False,
                caption=f"`{cmd}`" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )

            await xx.delete()
    else:
        await xx.edit(OUT, link_preview=bool(carb))


pp = pprint  # ignore: pylint
bot = light = light_bot


class u:
    ...


def _parse_eval(value=None):
    if not value:
        return value
    if hasattr(value, "stringify"):
        try:
            return value.stringify()
        except TypeError:
            pass
    elif isinstance(value, dict):
        try:
            return json_parser(value, indent=1)
        except BaseException:
            pass
    return str(value)


@light_cmd(pattern="eval", fullsudo=True, only_devs=True)
async def _eval(event):
    try:
        cmd = event.text.split(maxsplit=1)[1]
    except IndexError:
        return await event.eor(get_string("devs_2"), time=5)
    silent, gsource, xx = False, False, None
    spli = cmd.split()

    async def get_():
        try:
            cm = cmd.split(maxsplit=1)[1]
        except IndexError:
            await event.eor("->> Wrong Format <<-")
            cm = None
        return cm

    if spli[0] in ["-s", "--silent"]:
        await event.delete()
        silent = True
        cmd = await get_()
    elif spli[0] in ["-n", "-noedit"]:
        cmd = await get_()
        xx = await event.reply(get_string("com_1"))
    elif spli[0] in ["-gs", "--source"]:
        gsource = True
        cmd = await get_()
    if not cmd:
        return
    if not silent and not xx:
        xx = await event.eor(get_string("com_1"))
    if black:
        try:
            cmd = black.format_str(cmd, mode=black.Mode())
        except BaseException:
            # Consider it as Code Error, and move on to be shown ahead.
            pass
    reply_to_id = event.reply_to_msg_id or event
    if any(item in cmd for item in KEEP_SAFE().All) and (
        not (event.out or event.sender_id == light_bot.uid)
    ):
        warning = await event.forward_to(udB.get_key("LOG_CHANNEL"))
        await warning.reply(
            f"Malicious Activities suspected by {inline_mention(await event.get_sender())}"
        )
        if not os.getenv("IGNORE_WARNINGS", False):
            _ignore_eval.append(event.sender_id)
            return await xx.edit(
                "`Malicious Activities suspected⚠️!\nReported to owner. Aborted this request!`"
            )
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc, timeg = None, None, None, None
    tima = time.time()
    try:
        value = await aexec(cmd, event)
    except Exception:
        value = None
        exc = traceback.format_exc()
    tima = time.time() - tima
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if value and gsource:
        try:
            exc = inspect.getsource(value)
        except Exception:
            exc = traceback.format_exc()
    evaluation = exc or stderr or stdout or _parse_eval(value) or get_string("instu_4")
    if silent:
        if exc:
            msg = f"• <b>EVAL ERROR\n\n• CHAT:</b> <code>{get_display_name(event.chat)}</code> [<code>{event.chat_id}</code>]"
            msg += f"\n\n∆ <b>CODE:</b>\n<code>{cmd}</code>\n\n∆ <b>ERROR:</b>\n<code>{exc}</code>"
            log_chat = udB.get_key("LOG_CHANNEL")
            if len(msg) > 4000:
                with BytesIO(msg.encode()) as out_file:
                    out_file.name = "Eval-Error.txt"
                return await event.client.send_message(
                    log_chat, f"`{cmd}`", file=out_file
                )
            await event.client.send_message(log_chat, msg, parse_mode="html")
        return
    tmt = tima * 1000
    timef = time_formatter(tmt)
    timeform = timef if not timef == "0s" else f"{tmt:.3f}ms"
    final_output = "__►__ **EVAL** (__in {}__)\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
        timeform,
        cmd,
        evaluation,
    )
    if len(final_output) > 4096:
        final_output = evaluation
        with BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb=LightConfig.thumb,
                allow_cache=False,
                caption=f"```{cmd}```" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )
        return await xx.delete()
    await xx.edit(final_output)


def _stringify(text=None, *args, **kwargs):
    if text:
        u._ = text
        text = _parse_eval(text)
    return print(text, *args, **kwargs)


async def aexec(code, event):
    exec(
        (
            "async def __aexec(e, client): "
            + "\n print = p = _stringify"
            + "\n message = event = e"
            + "\n u.r = reply = rm = await event.get_reply_message()"
            + "\n chat = event.chat_id"
            + "\n u.lr = locals()"
        )
        + "".join(f"\n {l}" for l in code.split("\n"))
    )

    return await locals()["__aexec"](event, event.client)


DUMMY_CPP = """#include <iostream>
using namespace std;

int main(){
!code
}
"""


@light_cmd(pattern="cpp", only_devs=True, fullsudo=True)
async def docpp(e):
    match = e.text.split(" ", maxsplit=1)
    try:
        match = match[1]
    except IndexError:
        return await e.eor(get_string("devs_3"))
    msg = await e.eor(get_string("com_1"))
    if "main(" not in match:
        new_m = "".join(" " * 4 + i + "\n" for i in match.split("\n"))
        match = DUMMY_CPP.replace("!code", new_m)
    open("cpp-light.cpp", "w").write(match)
    m = await bash("g++ -o Cpplight cpp-light.cpp")
    o_cpp = f"• **Eval-Cpp**\n`{match}`"
    if m[1]:
        o_cpp += f"\n\n**• Error :**\n`{m[1]}`"
        if len(o_cpp) > 3000:
            osremove("cpp-light.cpp", "Cpplight")
            with BytesIO(str.encode(o_cpp)) as out_file:
                out_file.name = "error.txt"
                return await msg.reply(f"`{match}`", file=out_file)
        return await eor(msg, o_cpp)
    m = await bash("./Cpplight")
    if m[0] != "":
        o_cpp += f"\n\n**• Output :**\n`{m[0]}`"
    if m[1]:
        o_cpp += f"\n\n**• Error :**\n`{m[1]}`"
    if len(o_cpp) > 3000:
        with BytesIO(str.encode(o_cpp)) as out_file:
            out_file.name = "eval-cpp.txt"
            await msg.reply(f"`{match}`", file=out_file)
    else:
        await eor(msg, o_cpp)
    osremove("Cpplight", "cpp-light.cpp")


# for running C code with gcc (no dummy cpp)
@light_cmd(pattern="gcc", only_devs=True, fullsudo=True)
async def _gcc_compiler(e):
    try:
        match = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await e.eor(get_string("devs_3"))
    msg = await e.eor(get_string("com_1"))
    with open("light.c", "w+") as f:
        f.write(match)
    m = await bash("gcc light.c -o light-gcc.out")
    out = f"• **Eval-C**\n```{match}```"
    if m[1]:
        out += f"\n\n**• Error :**\n```{m[1]}```"
        osremove("light.c", "light-gcc.out")
        if len(out) > 4000:
            with BytesIO(str.encode(out)) as out_file:
                out_file.name = "compile-error-gcc.txt"
                return await msg.reply(f"```{match}```", file=out_file)
        return await eor(msg, out)
    m = await bash("./light-gcc.out")
    if m[0] != "":
        out += f"\n\n**• Output :**\n```{m[0]}```"
    if m[1]:
        out += f"\n\n**• Error :**\n```{m[1]}```"
    if len(out) > 4000:
        with BytesIO(str.encode(out)) as out_file:
            out_file.name = "gcc_output.txt"
            await msg.reply(f"```{match[:1023]}```", file=out_file)
    else:
        await msg.edit(out)
    osremove("light-gcc.out", "light.c")
