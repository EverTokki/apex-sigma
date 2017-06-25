﻿import yaml
import arrow
import discord
from config import Prefix

in_use = False


def check_for_bot_prefixes(text):
    common_pfx = [Prefix, '!', '/', '\\', '~', '.', '>', '-', '_']
    prefixed = False
    for pfx in common_pfx:
        if text.startswith(pfx):
            prefixed = True
            break
    return prefixed


async def collectchain(cmd, message, args):
    global in_use
    if in_use:
        response = discord.Embed(color=0x696969, title='🛠 Currently in use. Try Again Later.')
        await message.channel.send(None, embed=response)
    else:
        if args:
            if message.mentions:
                target = message.mentions[0]
            else:
                target = discord.utils.find(lambda x: x.name.lower() == ' '.join(args).lower(), message.guild.members)
            if target:
                start_time = arrow.utcnow().timestamp
                if message.channel_mentions:
                    target_chn = message.channel_mentions[0]
                else:
                    target_chn = message.guild.default_channel
                collected = 0
                collection = []
                in_use = True
                ch_response = discord.Embed(color=0x66CC66,
                                            title='📖 Collecting... You will be sent a DM when I\'m done.')
                await message.channel.send(None, embed=ch_response)
                async for log in target_chn.history(limit=50000):
                    if log.author.id == target.id:
                        if log.content:
                            if log.content != '':
                                if len(log.content) > 3:
                                    if not check_for_bot_prefixes(log.content):
                                        if 'http' not in log.content and '```' not in log.content:
                                            content = log.content
                                            if log.mentions:
                                                for mention in log.mentions:
                                                    content = content.replace(mention.mention, mention.name)
                                            if log.channel_mentions:
                                                for mention in log.channel_mentions:
                                                    content = content.replace(mention.mention, mention.name)
                                            unallowed_chars = ['`', '\n', '\\', '\\n']
                                            for char in unallowed_chars:
                                                content = content.replace(char, '')
                                            if len(content) > 48:
                                                if not content.endswith(('.' or '?' or '!')):
                                                    content += '.'
                                            collection.append(content)
                                            collected += 1
                                            if collected >= 3000:
                                                break
                with open(f'chains/chain_{target.id}.yml', 'w', encoding='utf-8') as chain_file:
                    yaml.dump(collection, chain_file, default_flow_style=False)
                in_use = False
                dm_response = discord.Embed(color=0x66CC66, title=f'📖 {target.name}\'s chain is done!')
                dm_response.add_field(name='Amount Collected', value=f'```\n{collected}\n```')
                dm_response.add_field(name='Time Elapsed', value=f'```\n{arrow.utcnow().timestamp - start_time}\n```')
                await message.author.send(None, embed=dm_response)
                await message.channel.send(None, embed=dm_response)
                if message.author.id != target.id:
                    tgt_msg = discord.Embed(color=0x66CC66,
                                            title=f'📖 {message.author.name} has made a markov chain for you.')
                    await target.send(None, embed=tgt_msg)
