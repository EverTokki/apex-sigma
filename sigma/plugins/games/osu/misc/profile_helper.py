import urllib
import json

from config import OSUAPIKey


def fetch_user_info(user):
    if len(OSUAPIKey) == 0:
        cmd.log.error('fetch_user_info requires osu api key!')
        return None

    param = []
    param.append('k=' + str(OSUAPIKey))
    param.append('u=' + str(user))

    url = 'https://osu.ppy.sh/api/get_user?'
    url += '&'.join(param)

    try: data = urllib.request.urlopen(url).read()
    except urllib.error.HTTPError: return None
    
    return json.loads(data.decode('utf-8'))


def get_osu_profile(cmd, user):
    # Check db if there is an associated discord id with osu user id
    osu_profile = cmd.db.get_osu_link(user.id)
    if osu_profile != None: return osu_profile

    # If there is not associated osu! user id with discord id, try to determine it
    # by seeing if the user is playing osu!. Their status has their osu! username in there
    if len(user.activities) == 0: return None

    username = None
    for activity in user.activities:
        if activity.name != 'osu!': continue
        #if activity.application_id != 367827983903490050
        username = activity.large_image_text.split('(')[0]

    # Try to use the osu api to retrieve user id
    if username == None: return None    
    user_info = fetch_user_info(username)

    if user_info == None: 
        cmd.log.error('Was unable to fetch user info via osu api')
        return None
    
    # Because it returns a list of matches
    if len(user_info) < 1: return None
    user_info = user_info[0]

    if not 'user_id' in user_info:
        cmd.log.error('Was unable to fetch user info via osu api')
        return None

    # Save osu id to db
    cmd.db.set_osu_link(user.id, user_info['user_id'], username)
    cmd.log.info(f'Linked {user.name} to osu! name {username}')

    return cmd.db.get_osu_link(user.id)