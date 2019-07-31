from sigma.core.ctrl_client import CtrlClient
from .forum_bot_handler import handle_data
from ..misc.profile_helper import get_osu_profile



async def forum_bot(cmd, message, args):

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    try:    bot, name = args[0].split('.')
    except: bot, name = 'Core', 'help'

    osu_profile = get_osu_profile(cmd, message.author)
    if osu_profile == None: osu_id = None
    else:                   osu_id = osu_profile['osu_id']

    data = {
        'bot'  : bot,
        'cmd'  : name,
        'args' : [],
        'key'  : osu_id
    }

    if len(args) > 1: 
        data['args'] = args[1:]

    success = await CtrlClient(cmd.log, 44444, handle_data).request(data, (message, cmd.log))
    if not success: await message.channel.send('Failed')