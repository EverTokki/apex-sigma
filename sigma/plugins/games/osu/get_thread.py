import discord
import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup

async def display_thread(cmd, channel, args):

    thread_id = args[0]

    # Get the HTML page
    topic_url = 'https://osu.ppy.sh/community/forums/topics/' + thread_id
    async with aiohttp.ClientSession() as session:
        async with session.get(topic_url) as data:
            page = await data.text()

    if page.find("Page Missing") != -1 or page.find("You shouldn&#039;t be here.") != -1:
        await channel.send("Topic does not exist!")
        return

    root = BeautifulSoup(page, "lxml")

    try:
        # Get relevant sections of the HTML
        subforum_name  = root.find_all(class_='page-mode-link--is-active')
        topic_name     = root.find_all(class_='js-forum-topic-title--title')
        topic_contents = root.find_all(class_='forum-post') # TODO: Use bbcode class instead

        post_authors  = [entry.find_all(class_='forum-post__username js-usercard')[0] for entry in topic_contents]
        post_ath_urls = [[avtr.get('href') for avtr in entry.find_all(class_='forum-post__username js-usercard')][0] for entry in topic_contents]
        post_avatars  = [[avtr.get('style') for avtr in entry.find_all(class_='avatar avatar--forum')][0] for entry in topic_contents]
        post_dates    = [entry.find_all(class_='timeago')[0] for entry in topic_contents]
        post_contents = root.find_all(class_='bbcode')[0]

        # Extract data from HTML
        subforum_name = [name.text for name in subforum_name][0]
        topic_url     = [name['href'] for name in topic_name][0]
        topic_name    = [name.text for name in topic_name][0]
        post_authors  = [auth.text for auth in post_authors]
        post_avatars  = [re.findall('background-image: url\(\'(.*?)\'\);', avtr)[0] for avtr in post_avatars]
        post_dates    = [date.text for date in post_dates]

    except:
        await channel.send("Something went wrong! Contact one of the bot devs.")
        cmd.log.error("[ get_thread ] " + topic_url + " is no longer parsable :(")
        return


    # Sanitize data
    subforum_name = subforum_name.replace('\n', '')
    topic_name    = topic_name.replace('\n', '').replace(']', '\]')
    topic_url     = topic_url.replace(')', '\)')
    post_authors = [auth.replace('\n', '') for auth in post_authors]

    post_contents = ''.join(post_contents)
    root = BeautifulSoup(post_contents, "lxml")

    # Process data

    while True:
        try: # Bold text
            root.strong.insert_before("**")
            root.strong.insert_after("**")
            root.strong.unwrap()
        except: break

    while True:
        try: # Next lines
            root.br.insert_before("\n")
            root.br.unwrap()
        except: break

    while True:
        try: # List indicator; ignore
            root.ol.unwrap0()
        except: break

    while True:
        try: # Can't do centered text in discord well; ignore
            root.center.unwrap()
        except: break
   
    while True:
        try: # List bullets
            root.li.insert_before("\n    ● ")
            root.li.unwrap()
        except: break

    while True:
        try: # Youtube video; Consider making this its own post if it's possible to embed like pictures
            root.iframe.insert_before(root.iframe['src'])
            root.iframe.unwrap()
        except: break

    while True:
        try: # Italic text
            root.em.insert_before('*')
            root.em.insert_after('*')
            root.em.unwrap()
        except: break

    while True:
        try: # Spoiler box arrow
            root.select_one("i.fa.fa-chevron-down.bbcode-spoilerbox__arrow").insert_after('\n')
            root.select_one("i.fa.fa-chevron-down.bbcode-spoilerbox__arrow").unwrap()
        except: break

    while True:
        try: # Spoiler box open/close thingy
            root.select_one("div.bbcode-spoilerbox__body").insert_before(':\n ')
            root.select_one("div.bbcode-spoilerbox__body").insert_after('\n')
            root.select_one("div.bbcode-spoilerbox__body").unwrap()
        except: break

    while True:
        try: # Emojis
            emoji = root.select_one("img.smiley")
            if emoji['title'] == 'smile': emoji.insert_after(':smile:')
            if emoji['title'] == 'wink': emoji.insert_after(':wink:')
            if emoji['title'] == 'Grin': emoji.insert_after(':grin:')
            if emoji['title'] == 'cry': emoji.insert_after(':cry:')
            emoji.unwrap()
        except: break

    while True:
        try: # Images
            
            try: # For any missed emoji
                if root.img['class'] == ['smiley']: 
                    cmd.log.warning("[ get_thread ] Smiley not handled: " + root.img)
                    root.img.unwrap()
                    continue
            except: pass

            # Replace https with img so we can easily identify image links later on
            if root.img['data-normal']: root.img.insert_before(root.img['data-normal'].replace('https','img') + " ")
            elif root.img['src']:       root.img.insert_before(root.img['src'].replace('https','img') + " ")

            root.img.unwrap()
        except: break

    while True:
        try: # Add markdown for it to be a hyperlink
            try: root.a.insert_before('[' + root.a.text.replace(']', '\]') + ']' + '(' + root.a['href'].replace(')', '\)') + ')')
            except: pass

            root.a.clear()
            root.a.unwrap()
        except: break

    while True:
        try:
            root.select_one("div.well").unwrap()
        except: break

    # TODO: Consider doing user quotes in code blocks. Not sure how nested quotes will do though


    #print(root)

    post_contents = root.text
    links = [match.start() for match in re.finditer(re.escape("img://"), post_contents)]
    link_end = 0
    posts = []

    # Compile embed contents
    embed = discord.Embed(type='rich', color=0x66CC66, title=subforum_name + ' > ' + topic_name)
    embed.url = topic_url
    embed.set_author(name=post_authors[0], icon_url=post_avatars[0], url=post_ath_urls[0])
    posts.append(embed)
   
    for link in links:
        if len(post_contents[link_end:link].strip()) != 0:
            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.description += post_contents[link_end:link]
            posts.append(embed)

        # Images are their own post
        link_end = post_contents[link:].find(' ') + link
        embed = discord.Embed(type='rich', color=0x66CC66)
        embed.set_image(url=post_contents[link:link_end].replace('img','https'))
        posts.append(embed)

    embed = discord.Embed(type='rich', color=0x66CC66)
    if len(post_contents[link_end:len(post_contents)].strip()) != 0:
        embed.add_field(name='___________', value=post_contents[link_end:len(post_contents)], inline=False)
    embed.set_footer(text=post_dates[0])
    posts.append(embed)

    # Split up fields in embed contents that are too long
    for post in posts:
        if len(post.fields) <= 0: continue
        if len(post.fields[0].value) <= 1024: continue
        

        '''
        1) Find next link:
            Find "http"
            valid if:
                http_index - 1 = '[' and there is no '\' http_index - 2, 
                http_index - 2 = ')' and there is no '\' http_index - 3, 
                there is a '(' before http_index - 2 that doesn't have '\' before it, and
                there is a ']' after http_index - 1  that doesn't have '\' before it:
                    ???
            start_of_link index = '(' before http_index - 2
            end_of_link index = ']' after http_index - 1

        2) If start_of_link index > 1024:
                Add 0:1024 to new post
                Substr original 0:1024
                goto 1)
            Else If end_of_link index > 1024:
                If end_of_link - start_of_link > 1024: 
                    Uh Oh!
                Else: 
                    Add 0:start_of_link to new post
                    Substr original 0:start_of_link
                    goto 1)
            Else:
                goto 1)
        '''

        split_posts = []
        link_start = post.fields[0].value.find('http')
        if link_start > 4:
            valid_link_code = post.fields[0].value[link_start-1] == '(' and post.fields[0].value[link_start-2] == ']'
            if valid_link_code:
                link_end = post.fields[0].value[link_start:].find(')')

            

        split_posts = [post.fields[0].value[part:part+1024] for part in range(0, len(post.fields[0].value), 1024)]
        post.remove_field(0)
        for split in split_posts:
            post.add_field(name='___________', value=split, inline=False)


    # TODO: Post body now has bbcode class, so I can use that instead to get post contents
    # TODO: img tags now just have img with no attributes
    # TODO: forum links now are wrapped in "postlink" class

    # TODO: Make sure links are intact during the splitting process

    # TODO: Threads to fix:
    #   626754 - Error displaying post (due to change in HTML relating to forum links)
    #   626684 - Chopped off formatted link
    #   626705 - Random ** bold formatting markers
    #   626710 - Collapsed text spoiler shows
    #   626725 - Chopped off formatted link
    #   627136 - Formatting error with URL
    #   629614 - Token parser messes up link
    #   629936 - markdown formatting error

    for post in posts:
         await channel.send(None, embed=post)
         await asyncio.sleep(1) # Delay so that the posts don't get shuffled later on

    '''
    post_list = []
    new_lines = [match.start() for match in re.finditer(re.escape("\n"), post_contents)]

    prev_new_line = 0
    for new_line in new_lines:
        if new_line - prev_new_line > 900:
            post_list.append(post_contents[prev_new_line:new_line])
            prev_new_line = new_line

    post_contents = []
    for post in post_list:            
        if len(post) >= 1024: 
            post_contents.append(post[0:512])
            post_contents.append(post[512:len(post)])
        else: 
            post_contents.append(post)
    '''

async def get_thread(cmd, message, args):

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    await display_thread(cmd, message.channel, args)

