import discord
import aiohttp

from sigma.core.ctrl_client import CtrlClient
from .ot_monitor_enums import OTMonitorEnum


async def handle_data(reply, message, logger):
    if not 'status' in reply:
        logger.error('Invalid data: ' + str(reply))
        await message.channel.send('Failed')
        return

    if reply['status'] == 0: 
        if 'msg' in reply:
            await message.channel.send(reply['msg'])
    else:                    
        await message.channel.send('Failed')


async def ot_monitor_about(cmd, message, args):

    data = {
        'bot'  : 'OTMonitorBot',
        'cmd'  : 'about',
        'args' : [ ]
    }

    success = await CtrlClient(cmd.log, 44444, handle_data).request(data, (message, cmd.log))
    if not success:
        await message.channel.send('Failed')