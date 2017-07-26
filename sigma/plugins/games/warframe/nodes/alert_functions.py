import datetime
import aiohttp
import discord
import arrow


def parse_alert_data(alert_data):
    lines = alert_data.split('\n')
    out_list = []
    for line in lines[:-1]:
        spliced = line.split('|')
        rewards = spliced[9]
        reward_spliced = rewards.split(' - ')
        credit_reward = int(reward_spliced[0].replace(',', '').replace('cr', ''))
        if len(reward_spliced) > 1:
            item_reward = reward_spliced[1]
        else:
            item_reward = None
        data = {
            'id': spliced[0],
            'node': spliced[1],
            'planet': spliced[2],
            'type': spliced[3],
            'faction': spliced[4],
            'levels': {
                'low': spliced[5],
                'high': spliced[6]
            },
            'stamps': {
                'start': int(spliced[7]),
                'end': int(spliced[8])
            },
            'rewards': {
                'credits': credit_reward,
                'item': item_reward
            }
        }
        out_list.append(data)
    return out_list


async def get_alert_data(db):
    alert_url = 'https://deathsnacks.com/wf/data/alerts_raw.txt'
    async with aiohttp.ClientSession() as session:
        async with session.get(alert_url) as data:
            alert_data = await data.text()
            alert_data = parse_alert_data(alert_data)
    alert_out = None
    for alert in alert_data:
        event_id = alert['id']
        db_check = db.find_one('WarframeCache', {'EventID': event_id})
        if not db_check:
            db.insert_one('WarframeCache', {'EventID': event_id})
            alert_out = alert
            break
    triggers = []
    item_reward = alert_out['rewards']['item']
    if item_reward:
        triggers = item_reward.lower().split(' ')
    return alert_out, triggers


async def generate_alert_embed(data):
    from .image_grabber import grab_image
    timestamp_start = data['stamps']['start']
    timestamp_end = data['stamps']['end']
    duration_sec = timestamp_end - timestamp_start
    duration_tag = str(datetime.timedelta(seconds=duration_sec))
    event_datetime = arrow.get().utcfromtimestamp(timestamp_end).datetime
    response = discord.Embed(color=0xffcc66, timestamp=event_datetime)
    alert_desc = f'Type: {data["faction"]} {data["type"]}'
    alert_desc += f'\nLevels: {data["levels"]["low"]} - {data["levels"]["high"]}'
    alert_desc += f'\nLocation: {data["node"]} ({data["planet"]})'
    alert_desc += f'\nReward: {data["rewards"]["credits"]}cr'
    if data['rewards']['item']:
        try:
            reward_icon = await grab_image(data['rewards']['item'])
        except:
            reward_icon = 'http://i.imgur.com/99ennZD.png'
        alert_desc += f' + {data["rewards"]["item"]}'
    else:
        reward_icon = 'https://i.imgur.com/WeUJXIx.png'
    response.add_field(name=f'Warframe Alert', value=f'{alert_desc}')
    response.set_thumbnail(url=reward_icon)
    response.set_footer(icon_url='https://i.imgur.com/99ennZD.png', text=f'Duration: {duration_tag}')
    return response
