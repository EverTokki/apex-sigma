from .nodes.sortie_functions import generate_sortie_embed
import aiohttp
import json


async def wfsortie(cmd, message, args):
    sortie_url = 'https://deathsnacks.com/wf/data/sorties.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(sortie_url) as data:
            sortie_data = await data.read()
            sortie_data = json.loads(sortie_data)
    response = generate_sortie_embed(sortie_data)
    await message.channel.send(embed=response)
