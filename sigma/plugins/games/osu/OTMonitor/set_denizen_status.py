import discord
import aiohttp

from sigma.core.ctrl_client import CtrlClient
from .ot_monitor_enums import OTMonitorEnum


async def handle_data(reply, message, logger):
    if not 'status' in reply:
        logger.error('Invalid data: ' + str(reply))
        await message.channel.send('Failed')
        return

    if reply['status'] == 0: await message.channel.send('Done')
    else:                    await message.channel.send('Failed')


async def set_denizen_status(cmd, message, args):

    if len(args) < 2:
        await message.channel.send(cmd.help())
        return

    username = args[0]
    status   = ' '.join(args[1:])

    data = {
        'bot'  : 'OTMonitorBot',
        'cmd'  : 'set_denizen_status',
        'args' : [ username, status ]
    }

    success = await CtrlClient(cmd.log, 44444, handle_data).request(data, (message, cmd.log))
    if not success:
        await message.channel.send('Failed')