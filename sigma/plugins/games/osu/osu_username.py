import discord
from .misc.profile_helper import get_osu_profile


async def osu_username(cmd, message, args):

    if not args:
        await message.channel.send(cmd.help())
        return

    if message.mentions: target = message.mentions[0]
    else: 
        embed = discord.Embed(color=0xDB0000, title='❗ Who?')
        await message.channel.send(None, embed=embed)
        return

    osu_profile = get_osu_profile(cmd, target)

    if not osu_profile:
        embed = discord.Embed(color=0xDB0000, title='❗ Strange... I never saw this user play osu')
        await message.channel.send(None, embed=embed)
        return

    embed = discord.Embed(color=0x00DB00, title=osu_profile['username'])
    await message.channel.send(None, embed=embed)
