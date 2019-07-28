import asyncio
import discord
import json

from sigma.core.data_reciever import DataReciever
from dateutil.parser import parse


class DataHandler():
    
    POST_MILESTONE   = 0
    THREAD_MILESTONE = 1
    NEW_FOREIGNER    = 2
    USER_RENAME      = 3
    NEW_DENIZEN      = 4
    CHECK            = 5

    @staticmethod
    async def handle_data(data, ev):
        embed = None

        if data['type'] == DataHandler.POST_MILESTONE:   embed = DataHandler.handle_post_milestone(data)
        if data['type'] == DataHandler.THREAD_MILESTONE: embed = DataHandler.handle_thread_milestone(data)
        if data['type'] == DataHandler.NEW_FOREIGNER:    embed = DataHandler.handle_new_foreigner(data)
        if data['type'] == DataHandler.POST_MILESTONE:   embed = DataHandler.handle_post_milestone(data)
        if data['type'] == DataHandler.USER_RENAME:      embed = DataHandler.handle_user_rename(data)
        if data['type'] == DataHandler.NEW_DENIZEN:      embed = DataHandler.handle_new_denizen(data)
        if data['type'] == DataHandler.CHECK:
            ev.log.info('OT monitor checked in')
            return

        try:
            for server in ev.bot.guilds:
                for channel in server.channels:
                    if channel.name == 'ot-feed':
                        await channel.send(embed=embed)
        except Exception as e:
            ev.log.error('Unable to send message to ot-feed;\n' + str(data) + '\n' + str(e))


    @staticmethod
    def handle_post_milestone(data):
        return discord.Embed(color=0x1ABC9C, title=f'{data["username"]} now has {data["count"]} posts in OT!')


    @staticmethod
    def handle_thread_milestone(data):
        return discord.Embed(color=0x1ABC9C, title=f'{data["username"]} now has {data["count"]} threads in OT!')


    @staticmethod
    def handle_new_foreigner(data):
        return discord.Embed(color=0x1ABC9C, title=f'Welcome a new foreigner in OT: {data["username"]}!')


    @staticmethod
    def handle_user_rename(data):
        return discord.Embed(color=0x1ABC9C, title=f'{data["username_old"]} renamed themselves to {data["username_new"]}!')


    @staticmethod
    def handle_new_denizen(data):
        return discord.Embed(color=0x1ABC9C, title=f'{data["username"]} is now an OT Denizen!')


async def ot_monitor(ev):

    data_reciever = DataReciever(55556, DataHandler.handle_data)
    while True:
        await asyncio.sleep(0.1)
        await data_reciever.read_data((ev,))
