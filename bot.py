import discord
import json
import os
import youtube_dl
from discord.ext import commands
import asyncio
from itertools import cycle

TOKEN = 'NDY1MDI2ODY0Mzk4NzI5MjI2.DjdfbQ.Hir6G8TI5kWAzGcoeouPLdZI9Hk'

client = commands.Bot(command_prefix = '`')
client.remove_command('help')
status = ['with Source Cade!', '`help']
os.chdir(r'C:\Users\OBSOLETE\Desktop\OBSOLETE\Obsolete Bot')
players = {}
queues = {}

def check_queue(id):
    if queues[id] != []:
        player = queues[id].pop(0)
        players[id] = player
        player.start()

async def change_status():
    await client.wait_until_ready()
    msgs = cycle(status)

    while not client.is_closed:
        current_status = next(msgs)
        await client.change_presence(game=discord.Game(name=current_status))
        await asyncio.sleep(5)

@client.event
async def on_member_join(member):
    with open('users.json', 'r')as f:
        users = json.load(f)

    await update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)

@client.event
async def on_message(message):
    with open('users.json', 'r')as f:
        users = json.load(f)

    await update_data(users, message.author)
    await add_experience(users, message.author, 5)
    await level_up(users, message.author, message.channel)

    with open('users.json', 'w') as f:
        json.dump(users, f)

async def update_data(users, user):
    if not user.id in users:
        users[user.id] = {}
        users[user.id]['experience'] = 0
        users[user.id]['level'] = 1

async def add_experience(users, user, exp):
    users[user.id]['experience'] += exp

async def level_up(users, user, channel):
    experience = users[user.id]['experience']
    lvl_start = users[user.id]['level']
    lvl_end = int(experience ** (1/4))

    if lvl_start < lvl_end:
        await client.send_message(channel, '{} has leveled up to level {}'.format(user.mention, lvl_end))
        users[user.id]['level'] = lvl_end                    

@client.event
async def on_ready():
   print('Obsolete is ready to rock!')

@client.event
async def on_message(message):
    print('A user has sent a message.')
    await client.process_commands(message)

@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()

@client.command(pass_context=True)
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url)
    players[server.id] = player
    player.start()

@client.command(pass_context=True)
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()

@client.command(pass_context=True)
async def stop(ctx):
    id = ctx.message.server.id
    players[id].stop()

@client.command(pass_context=True)
async def resume(ctx):
    id = ctx.message.server.id
    players[id].resume()

@client.command(pass_context=True)
async def queue(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))

    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]
    await client.say('Video queued.')

@client.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    await client.send_message(channel, '{} has added a reaction {} to the message: {}'.format(user.name, reaction.emoji, reaction.message.content))

@client.event
async def on_reaction_remove(reaction, user):
    channel = reaction.message.channel
    await client.send_message(channel, '{} has removed {} from the message: {}'.format(user.name, reaction.emoji, reaction.message.content))
@client.event
async def on_message_delete(message):
    author = message.author
    content = message.content
    channel = message.channel
    await client.send_message(channel, '{}: {}'.format(author, content))

@client.command()
async def ping():
    await client.say('Pong!')

@client.command()
async def echo(*args):
    output = ''
    for word in args:
        output += word
        output += ' '
    await client.say(output)

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, name='God')
    await client.add_roles(member, role)

@client.command(pass_context=True)
async def clear(ctx, amount=100):
    channel = ctx.message.channel
    messages = []
    async for message in client.logs_from(channel, limit=int(amount)):
        messages.append(message)
    await client.delete_messages(messages)
    await client.say('Messages deleted.')

@client.command()
async def botinfo():
    embed = discord.Embed(
        title = 'Bot Information',
        description = 'Hey there! I am Obsolete Bot created by my owner TSM_Obsolete. I am here to manage your Discord server and entertain people in it.',
        colour = discord.Colour.orange()
    )

    embed.set_footer(text='TSM_Obsolete#0962')
    embed.set_image(url='https://cdn.discordapp.com/attachments/465387709599580162/471313520164601857/epqQnheg.jpg')
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/465387709599580162/471314321159225364/discord-logo-39d3600a80352a05-512x512.png')
    embed.add_field(name='Made In', value = 'discord.py', inline=False)
    embed.add_field(name='Made By', value ='TSM_Obsolete#0962', inline=False)

    await client.say(embed=embed)

@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(
        description = 'Hi! Thanks for using me. Here is a list of my commands.',
        colour = discord.Colour.orange()
    )

    embed.set_author(name='Help')
    embed.add_field(name='🏓Ping', value='`ping', inline=True)
    embed.add_field(name='🆑Clear', value='`clear', inline=True)
    embed.add_field(name='🤖Bot Information', value='`botinfo', inline=True)
    embed.add_field(name='😀Echo', value='`echo', inline=False)
    await client.send_message(author, embed=embed)

client.loop.create_task(change_status())
client.run(TOKEN)
