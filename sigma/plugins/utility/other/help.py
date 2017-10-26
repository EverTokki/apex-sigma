import discord
from config import Prefix, MainServerURL
from sigma.core.command_alts import load_alternate_command_names
import os
import yaml

alts = load_alternate_command_names()


async def help(cmd, message, args):

    cmd.db.add_stats('HelpCount')
    
    if not args:
        directory = 'sigma/plugins'
        module_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file == 'plugin.yml':
                    file_path = (os.path.join(root, file))
                    with open(file_path) as plugin_file:
                        plugin_data = yaml.safe_load(plugin_file)
                        try:
                            category = plugin_data['categories'][0]
                            if category.title() not in module_list and category not in ['administration', 'special']:
                                module_list.append(category.title())
                        except:
                            pass

        help_out = discord.Embed(type='rich', title='❔Help❔', color=0x2cefe5)
        
        help_out.add_field(name=' Sickle\'s Module List', value='```yaml\n' + '\n'.join(module_list) + '\n```', inline=True)
        help_out.add_field(name='Please submit bugs, issues, or suggestions here.', value='[**LINK**](https://github.com/abraker95/apex-sigma/issues)', inline=True)
        help_out.add_field(name='Add me to your server!', value='[**LINK**](https://discordapp.com/oauth2/authorize?&client_id=290355925317976074&scope=bot&permissions=0)', inline=True)
        
        help_out.add_field(name='Sickle in its natural habitat', value='⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿\n'+'⠀⠀⠀⠀⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⣄ ⣠⠀⠀⠀⠀⠀⣿⣿⣿⣿\n'+'⠀⠀⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⣿⣿⣿⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿\n'+'⣿⠋⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⣿⣿⠋⠈⠀⠀⠀⠀⠀⠀⠀⠙⣿\n'+'⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈\n'+'⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠈', inline=True)
        help_out.set_footer(text=f'Use {Prefix}commands <module> to get a list of commands available in that module.\n Use {Prefix}help <command> to get a description about the command usage.')
        help_out.set_image(url='https://i.imgur.com/UOzJ31H.png')
        
        await message.channel.send(None, embed=help_out)
    
    else:
        qry = args[0].lower()
        if qry in alts:
            qry = alts[qry]

        try:
            help_out = discord.Embed(type='rich', title=':book: ' + qry.upper() + ' Help', color=0x1B6F5F)
            help_out.add_field(name='Command Usage Example and Information', value=cmd.bot.plugin_manager.commands[qry.lower()].help())
            await message.channel.send(None, embed=help_out)
        except:
            out_content = discord.Embed(type='rich', color=0x696969, title='🔍 No such command was found...')
            await message.channel.send(None, embed=out_content)
