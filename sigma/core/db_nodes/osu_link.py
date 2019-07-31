collection_name = 'osu_link'


def set_osu_link(db, discord_id, user_id, username):  
    collection = db[collection_name]

    # Update
    query = { '_id' : int(discord_id) }
    data  = { 'osu_id' : int(user_id), 'username' : username }
    collection.update_one(query, { "$set" : data }, upsert=True)


def get_osu_link(db, discord_id):
    # Request
    collection = db[collection_name]

    query  = { '_id' : int(discord_id) }
    cursor = collection.find_one(query)

    # Process
    if not cursor: link = None
    else:          link = { 'osu_id' : cursor['osu_id'], 'username' : cursor['username'] } 

    if cursor: del cursor
    return link