import discord
import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup

from .misc.BBcodeProcessor.BBcodeProcessor import BBcodeProcessor
from .misc.BBcodeProcessor.DiscordBBcodeCompiler import DiscordBBcodeCompiler
from .misc.Forum.Structs.Topic import Topic

async def display_thread(cmd, channel, args):

    thread_id = get_thread_id(args[0])

    # Get the HTML page
    topic_url = 'https://osu.ppy.sh/community/forums/topics/' + thread_id
    async with aiohttp.ClientSession() as session:
        async with session.get(topic_url) as data:
            page = await data.text()

    if page.find("Page Missing") != -1 or page.find("You shouldn&#039;t be here.") != -1:
        await channel.send("Topic does not exist! Maybe you want to get by post instead? (>>get_post)")
        return

    root = BeautifulSoup(page, "lxml")
    topic = Topic(root, cmd.log)
    
    try:
        subforum_name       = topic.getSubforum()
        topic_name          = topic.getName()
        topic_poster_name   = topic.getCreator().getName()
        topic_poster_avatar = topic.getCreator().getAvatar()
        topic_poster_url    = topic.getCreator().getUrl()

        post          = topic.getPosts()[0]
        post_contents = post.getContents()
    except:
        await channel.send("Something went wrong! Contact one of the bot devs.")
        cmd.log.error("[ get_thread ] " + topic_url + " is no longer parsable :(")
        return

    # Sanitize data
    topic_name = topic_name.replace('\n', '').replace(']', '\]')

    # Compile embed contents
    post_contents = BBcodeProcessor().Process(post_contents).text
    posts = []

    # Topic Header
    embed = discord.Embed(type='rich', color=0x66CC66, title=subforum_name + ' > ' + topic_name)
    embed.url = topic_url
    embed.set_author(name=topic_poster_name, icon_url=topic_poster_avatar, url=topic_poster_url)
    posts.append(embed)

    DiscordBBcodeCompiler().Compile(post_contents, posts)

    # Post everything to discord
    for post in posts:
        #print(post.description)
        await channel.send(None, embed=post)
        await asyncio.sleep(1) # Delay so that the posts don't get shuffled later on


def get_thread_id(arg):
    token = 'https://osu.ppy.sh/community/forums/topics/'
    idx = arg.find(token)
    if idx != -1:
        beg = len(token)
        token = '?start='
        idx = arg.find(token)

        if idx != -1: return arg[beg:idx]
        else:         return arg[beg:]

    token = 'https://osu.ppy.sh/forum/t/'
    idx = arg.find(token)
    if idx != -1: return arg[len(token):]

    return arg


async def get_thread(cmd, message, args):
    args = [arg for arg in args if arg != '']

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    await display_thread(cmd, message.channel, args)

