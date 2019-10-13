import asyncio
import discord
import json

from .misc.profile_helper import fetch_user_info


async def discord_osu_linker(ev):

    while True:
        await asyncio.sleep(30)

        for guild in ev.bot.guilds:
            members = [ member for member in guild.members if len(member.activities) != 0 ]
            for user in members:
                await asyncio.sleep(0.1)

                # Check whether user is already recorded
                if ev.db.get_osu_link(user.id) != None: continue
                if len(user.activities) == 0: continue

                # Extract user's osu username from activity if possible
                username = None
                for activity in user.activities:
                    if activity.name != 'osu!': continue
                    #if activity.application_id != 367827983903490050
                    if activity.large_image_text == None: continue
                    username = activity.large_image_text.split('(')[0].strip()

                # Fetch user info via osu api
                if username == None: continue
                user_info = fetch_user_info(username)

                # Because it returns a list of matches
                if len(user_info) < 1: continue
                user_info = user_info[0]

                # Make sure json data has the info we need
                if not 'user_id' in user_info:
                    ev.log.error('Was unable to fetch user info via osu api')
                    continue

                # Record the link
                ev.log.info(f'Linked {user.name} to osu! name {username}')
                ev.db.set_osu_link(user.id, user_info['user_id'], username)
        
