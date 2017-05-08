import random
import asyncio
import arrow
import discord

slot_back_data = {}


async def spin_slots(cmd, message, bet_amt, symbols, min_spins=4, max_spins=8, spin_cycle_timeout=1):

    # Cooldown Check
    not_on_cd = True
    current_time = arrow.utcnow().timestamp

    if message.author.id in slot_back_data:
        cd_timestamp = slot_back_data[message.author.id]
        if cd_timestamp + 20 > current_time: not_on_cd = False
        else: not_on_cd = True

    # Spinnage
    if not_on_cd:
        player_points = cmd.db.get_points(message.server, message.author)
        if player_points < bet_amt:
            embed = discord.Embed(color=0xDB0000, title=':exclamation: Not Enough Points')
            await cmd.bot.send_message(message.channel, None, embed=embed)
            return

        cmd.db.add_stats('SlotsCount')

        embed_colors = [0x990000, 0x0066FF, 0x009900, 0xff9900, 0xCC33FF, 0x990033]
        slot_embed = discord.Embed(color=random.choice(embed_colors))
        slot_back_data.update({message.author.id: current_time})

        rand_done = 0

        res_1 = random.choice(symbols)
        res_2 = random.choice(symbols)
        res_3 = random.choice(symbols)
        res_4 = random.choice(symbols)
        res_5 = random.choice(symbols)
        res_6 = random.choice(symbols)
        res_7 = random.choice(symbols)
        res_8 = random.choice(symbols)
        res_9 = random.choice(symbols)

        slot_view = ':pause_button: ' + res_4 + ' ' + res_5 + ' ' + res_6 + ' :pause_button:'
        slot_view += '\n:arrow_forward: ' + res_1 + ' ' + res_2 + ' ' + res_3 + ' :arrow_backward:'
        slot_view += '\n:pause_button: ' + res_7 + ' ' + res_8 + ' ' + res_9 + ' :pause_button:'
        slot_embed.add_field(name='🎰 Slots are spinning...', value=slot_view)
        slot_spinner = await cmd.bot.send_message(message.channel, None, embed=slot_embed)

        spin_amt = random.randint(min_spins, max_spins)
        while rand_done < spin_amt:
            await asyncio.sleep(spin_cycle_timeout)
            rand_done += 1
            res_7 = res_1
            res_8 = res_2
            res_9 = res_3
            res_1 = res_4
            res_2 = res_5
            res_3 = res_6
            res_4 = random.choice(symbols)
            res_5 = random.choice(symbols)
            res_6 = random.choice(symbols)

            slot_view = ':pause_button: ' + res_4 + ' ' + res_5 + ' ' + res_6 + ' :pause_button:'
            slot_view += '\n:arrow_forward: ' + res_1 + ' ' + res_2 + ' ' + res_3 + ' :arrow_backward:'
            slot_view += '\n:pause_button: ' + res_7 + ' ' + res_8 + ' ' + res_9 + ' :pause_button:'
            slot_embed.set_field_at(0, name='🎰 Slots are spinning...', value=slot_view)
            await cmd.bot.edit_message(slot_spinner, None, embed=slot_embed)

        # Result Response
        subtext = ''
        if res_1 == res_2 == res_3:
            win = True
            pts = bet_amt * 1   # TODO: This needs to be multiplied by emoji worth
        else:
            win = False
            pts = 0

        if win:
            cmd.db.add_points(message.server, message.author, pts)
            slot_embed.set_field_at(0, name=':gem: You Won!', value=slot_view)
            slot_embed.set_footer(text='You won ' + str(pts) + ' points.')
            await cmd.bot.edit_message(slot_spinner, None, embed=slot_embed)
        else:
            cmd.db.take_points(message.server, message.author, bet_amt)
            slot_embed.set_field_at(0, name=':bomb: You Lost...', value=slot_view)
            slot_embed.set_footer(text='You lost the ' + str(bet_amt) + ' points that you bet.')
            await cmd.bot.edit_message(slot_spinner, None, embed=slot_embed)
    else:
        cd_timestamp = slot_back_data[message.author.id]
        current_time = arrow.utcnow().timestamp
        timeout_amt = cd_timestamp + 20 - current_time

        embed = discord.Embed(color=0xDB0000, title=':exclamation: You can\'t spin for another ' + str(timeout_amt) + ' seconds!')
        await cmd.bot.send_message(message.channel, None, embed=embed)
        return
