﻿import aiohttp
import discord
from config import MashapeKey


async def ud(cmd, message, args):

    if not args:
        await message.channel.send(cmd.help())
        return

    if MashapeKey == '':
        embed = discord.Embed(color=0xDB0000)
        embed.add_field(name='API key MashapeKey not found.', value='Please ask the bot owner to add it.')
        await message.channel.send(None, embed=embed)
        return

    ud_input = ' '.join(args)
    url = "https://mashape-community-urban-dictionary.p.mashape.com/define?term=" + ud_input
    headers = {'X-Mashape-Key': MashapeKey, 'Accept': 'text/plain'}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as data:
            response = await data.json()
    
    result_type = str((response['result_type']))
    if result_type != 'exact': return
        
    definition = str((response['list'][0]['definition']))
    if len(definition) > 750:
        definition = definition[:750] + '...'
    
    example = str((response['list'][0]['example']))
    
    embed = discord.Embed(color=0x1abc9c, title='🥃 Urban Dictionary Definition For `' + ud_input + '`')
    embed.add_field(name='Definition', value='```\n' + definition + '\n```')
    embed.add_field(name='Usage Example', value='```\n' + example + '\n```')
    await message.channel.send(None, embed=embed)
