import asyncio
import discord
import json

from sigma.core.data_reciever import DataReciever
from dateutil.parser import parse


class DataHandler():
    
    CHECK_IN         = 0
    COINS_TRANSFER   = 1
    THREAD_TRANSFER  = 2
    NEW_ACCOUNT      = 3

    OT_GOVERNMENT = 0  # OT Government treasury
    OT_PALIAMENT  = 1  # One of OT Paliament members
    DENIZEN_NOBLE = 2  # Denizens who control majority of content in OT
    DENIZEN_HIGH  = 3  # Denizens who are known for at least something
    DENIZEN_REG   = 4  # Regular denizens who are not in significant positions
    NORM_USER     = 5  # Not an OT denizen, aka who?

    @staticmethod
    async def handle_data(data, ev):
        embed = None

        if data['type'] == DataHandler.COINS_TRANSFER:   embed = DataHandler.handle_coins_transfer(data)
        if data['type'] == DataHandler.THREAD_TRANSFER:  embed = DataHandler.handle_thread_transfer(data)
        if data['type'] == DataHandler.NEW_ACCOUNT:      embed = DataHandler.handle_new_account(data)
        if data['type'] == DataHandler.CHECK_IN:
            ev.log.info('OT economy checked in')
            return

        try:
            for server in ev.bot.guilds:
                for channel in server.channels:
                    if channel.name == 'ot-ledger':
                        await channel.send(embed=embed)
        except Exception as e:
            ev.log.error('Unable to send message to ot-ledger;\n' + str(data) + '\n' + str(e))


    @staticmethod
    def handle_coins_transfer(data):
        icon_from = DataHandler.icon_from(data['from_status'])
        icon_to   = DataHandler.icon_from(data['to_status'])

        return discord.Embed(color=0x1ABC9C, title=f':moneybag: {data["amount"]} coins', description=f'({icon_from}) {data["from"]} -> ({icon_to}) {data["to"]} ')


    @staticmethod
    def handle_thread_transfer(data):
        icon_from = DataHandler.icon_from(data['from_status'])
        icon_to   = DataHandler.icon_from(data['to_status'])

        return discord.Embed(color=0x1ABC9C, title=f'Thread ownership transfered!', description=f'({icon_from}) {data["from"]} -> ({icon_to}) {data["to"]} ')


    @staticmethod
    def handle_new_account(data):
        return discord.Embed(color=0x1ABC9C, title=f'New account: {data["username"]}', description=f'Starts with {data["coins"]} coins!')


    @staticmethod
    def translate_status_to_icon(status):
        if status == DataHandler.OT_GOVERNMENT: return ':classical_building:'
        if status == DataHandler.OT_PALIAMENT:  return ':scroll:'
        if status == DataHandler.DENIZEN_NOBLE: return ':small_blue_diamond:'
        return ''


async def ot_ledger(ev):

    data_reciever = DataReciever(55558, DataHandler.handle_data)
    while True:
        await asyncio.sleep(0.1)
        await data_reciever.read_data((ev,))
