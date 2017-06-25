import discord
from sigma.core.permission import check_admin
from .nodes.permission_data import get_all_perms


async def enablemodule(cmd, message, args):
    if args:
        if not check_admin(message.author, message.channel):
            response = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
        else:
            mdl_name = args[0].lower()
            if mdl_name in cmd.bot.module_list:
                perms = get_all_perms(cmd.db, message)
                disabled_modules = perms['DisabledModules']
                if mdl_name in disabled_modules:
                    disabled_modules.remove(mdl_name)
                    perms.update({'DisabledModules': disabled_modules})
                    cmd.db.update_one('Permissions', {'ServerID': message.guild.id}, {'$set': perms})
                    response = discord.Embed(color=0x66CC66, title=f'✅ `{mdl_name.upper()}` enabled.')
                else:
                    response = discord.Embed(color=0xFF9900, title='⚠ Module Not Disabled')
            else:
                response = discord.Embed(color=0x696969, title='🔍 Module Not Found')
        await message.channel.send(embed=response)
