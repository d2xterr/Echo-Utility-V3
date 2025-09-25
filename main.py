import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import asyncio
import aiohttp
import datetime
import os
from typing import Optional
import mcstatus  
import io
import threading


TOKEN = 'BOT_TOKEN' 
MC_SERVER_IP = 'play.echo-smp.net'
MC_SERVER_PORT = 19132
REPORT_CHANNEL_ID = 1355859940819992626
TICKET_CATEGORY_ID = 1351291616375209996
COUNCIL_ROLE_ID = 1367958497584480256  
TEAM_ROLE_ID = 1351291476193181726  
STATUS_IMAGE_1 = 'https://cdn.discordapp.com/attachments/1353079900134834280/1358467893725106326/EN_Icon.png'
STATUS_IMAGE_2 = 'https://cdn.discordapp.com/attachments/1353079900134834280/1358467893725106326/EN_Icon.png'
BANNER_IMAGE = 'https://media.discordapp.net/attachments/1353079900134834280/1358467860883833022/Echo_Network2.png'
LOA_CHANNEL_ID = 1389767774280351864
APPLICATIONS_CHANNEL_ID = 1353441083895320811
STAFF_MOVEMENT_CHANNEL_ID = 1389767774280351864
STAFF_REPORTS_CHANNEL_ID = 1389767774280351864


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

def is_council():
    """
    Check if a user has the council role.
    Returns a predicate function that can be used as a command check.
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        try:
            if not interaction.guild:
                print("No guild found in interaction")
                return False
                
            council_role = interaction.guild.get_role(COUNCIL_ROLE_ID)
            if not council_role:
                print(f"Council role not found with ID: {COUNCIL_ROLE_ID}")
                return False
                
            has_role = council_role in interaction.user.roles
            if not has_role:
                print(f"User {interaction.user.name} does not have council role")
                await interaction.response.send_message("You need the Council role to use this command!", ephemeral=True)
            return has_role
            
        except Exception as e:
            print(f"Error in is_council check: {e}")
            return False
            
    return app_commands.check(predicate)


DATA_FILE = 'ticket_data.json'
REPORT_DATA_FILE = 'report_data.json'
TICKET_COUNTS_FILE = 'ticket_counts.json'
WARNINGS_FILE = 'warnings.json'  
REPORT_COUNTS_FILE = 'report_counts.json'


TICKET_BANNER_1 = "https://media.discordapp.net/attachments/1353079900134834280/1358467860883833022/Echo_Network2.png" 
TICKET_BANNER_2 = "https://cdn.discordapp.com/attachments/1353079900134834280/1358467893725106326/EN_Icon.png"  


SUPPORT_CATEGORY_ID = 1351607210936897547  
MEDIA_CATEGORY_ID = 1354459512517558364  
REPORTS_CATEGORY_ID = 1351604012608131193 
APPEALS_CATEGORY_ID = 1351291632871538728 
TICKET_LOGS_CHANNEL_ID = 1351604371925762168 
TRIAL_ROLE_ID = 1352661651198967819 
HELPER_ROLE_ID = 1351291474297356338 
MOD_ROLE_ID = 1351291471931904163 
TICKET_ADMIN_ROLE_ID = 1351625171076907048  
EVIDENCE_CHANNEL_ID = 1366446077389307945  
MEDIA_ROLE_ID = 1351291477250146435
LIVE_ANNOUNCEMENT_CHANNEL_ID = 1381980073695121539
COMMUNITY_ROLE_ID = 1351291478336602193
DISCUSSION_CHANNEL_ID = 1382337513259270208
CHAT_CHANNEL_ID = 1351291663074725899

AFK_DATA_FILE = 'afk_data.json'

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'tickets': {},
            'closed_tickets': {}
        }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_report_data():
    try:
        with open(REPORT_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'pending_reports': {}}

def save_report_data(data):
    with open(REPORT_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_ticket_counts():
    try:
        with open(TICKET_COUNTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'user_ticket_counts': {}}

def save_ticket_counts(data):
    with open(TICKET_COUNTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_warnings():
    try:
        with open(WARNINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'warnings': {}}

def save_warnings(data):
    with open(WARNINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_report_counts():
    try:
        with open(REPORT_COUNTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'user_report_counts': {}}

def save_report_counts(data):
    with open(REPORT_COUNTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def has_staff_permissions(user):
    staff_roles = [TRIAL_ROLE_ID, HELPER_ROLE_ID, MOD_ROLE_ID, TICKET_ADMIN_ROLE_ID]
    return any(role.id in staff_roles for role in user.roles)

def has_ticket_admin_permissions(user):
    return any(role.id == TICKET_ADMIN_ROLE_ID for role in user.roles)

def get_category_for_ticket_type(ticket_type):
    category_mapping = {
        "Support Tickets": SUPPORT_CATEGORY_ID,
        "Media Applications": MEDIA_CATEGORY_ID,
        "Player Reports": REPORTS_CATEGORY_ID,
        "Appeals": APPEALS_CATEGORY_ID
    }
    return category_mapping.get(ticket_type, SUPPORT_CATEGORY_ID)

async def get_minecraft_head_url(username):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{username}') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    uuid = data['id']
                    return f'https://minotar.net/avatar/{uuid}/64'
                else:
                    return 'https://minotar.net/avatar/steve/64'
    except:
        return 'https://minotar.net/avatar/steve/64'

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Select a ticket type...",
        options=[
            discord.SelectOption(
                label="Support Tickets",
                description="General help and questions",
                emoji="🎫"
            ),
            discord.SelectOption(
                label="Media Applications",
                description="Apply for content creator",
                emoji="📱"
            ),
            discord.SelectOption(
                label="Player Reports",
                description="Report rule violations",
                emoji="📊"
            ),
            discord.SelectOption(
                label="Appeals",
                description="Submit a ban/mute appeal",
                emoji="⚖️"
            )
        ]
    )
    async def ticket_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_modal(TicketModal(select.values[0]))

class TicketModal(discord.ui.Modal):
    def __init__(self, ticket_type):
        super().__init__(title=f"Create {ticket_type}")
        self.ticket_type = ticket_type
        
        self.username = discord.ui.TextInput(
            label="Minecraft Username",
            placeholder="Enter your Minecraft username...",
            required=True,
            max_length=16
        )
        
        self.proof = discord.ui.TextInput(
            label="Proof/Evidence",
            placeholder="Provide proof or evidence (links, descriptions, etc.)",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.username)
        self.add_item(self.proof)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        category_id = get_category_for_ticket_type(self.ticket_type)
        category = guild.get_channel(category_id)
        
        if not category:
            await interaction.response.send_message("Error: Ticket category not found! Please contact an administrator.", ephemeral=True)
            return
        
        channel_name = f"{self.ticket_type.lower().replace(' ', '-')}-{interaction.user.name}"
        
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.get_role(TRIAL_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.get_role(HELPER_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.get_role(MOD_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.get_role(TICKET_ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        head_url = await get_minecraft_head_url(self.username.value)
        
        embed = discord.Embed(
            title=f"🎫 {self.ticket_type}",
            color=0x5865F2,
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url=head_url)
        embed.add_field(name="👤 Minecraft Username", value=self.username.value, inline=True)
        embed.add_field(name="🆔 Discord User", value=interaction.user.mention, inline=True)
        embed.add_field(name="📝 Proof/Evidence", value=self.proof.value, inline=False)
        embed.add_field(name="⏰ Ticket Created", value=f"<t:{int(datetime.datetime.now().timestamp())}:R>", inline=True)
        embed.add_field(name="📂 Category", value=category.name, inline=True)
        embed.set_footer(text="Please be patient and provide clear information in your ticket.")
        
        claim_view = ClaimView()
        
        await ticket_channel.send(f"{interaction.user.mention}", embed=embed, view=claim_view)
        
        data = load_data()
        data['tickets'][str(ticket_channel.id)] = {
            'user_id': interaction.user.id,
            'username': self.username.value,
            'type': self.ticket_type,
            'category': category.name,
            'created_at': datetime.datetime.now().isoformat(),
            'last_activity': datetime.datetime.now().isoformat(),
            'claimed_by': None,
            'warning_sent': False
        }
        save_data(data)
        
        await interaction.response.send_message(f"Ticket created! {ticket_channel.mention}", ephemeral=True)

class ClaimView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.green, emoji="✋")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_staff_permissions(interaction.user):
            await interaction.response.send_message("You don't have permission to claim tickets!", ephemeral=True)
            return
        
        data = load_data()
        channel_id = str(interaction.channel.id)
        
        if channel_id not in data['tickets']:

            data['tickets'][channel_id] = {
                'user_id': interaction.channel.topic.split('|')[0] if interaction.channel.topic else None,
                'username': 'Unknown',
                'type': interaction.channel.category.name if interaction.channel.category else 'Unknown',
                'category': interaction.channel.category.name if interaction.channel.category else 'Unknown',
                'created_at': datetime.datetime.now().isoformat(),
                'last_activity': datetime.datetime.now().isoformat(),
                'claimed_by': None,
                'warning_sent': False
            }
            save_data(data)
        
        if data['tickets'][channel_id]['claimed_by']:
            if has_ticket_admin_permissions(interaction.user):
                claimer = interaction.guild.get_member(data['tickets'][channel_id]['claimed_by'])
                claimer_mention = claimer.mention if claimer else "Unknown User"
                await interaction.response.send_message(f"This ticket is already claimed by {claimer_mention}", ephemeral=True)
            else:
                await interaction.response.send_message("This ticket is already claimed!", ephemeral=True)
            return
        
        data['tickets'][channel_id]['claimed_by'] = interaction.user.id
        data['tickets'][channel_id]['last_activity'] = datetime.datetime.now().isoformat()  
        save_data(data)
        
        ticket_data = data['tickets'][channel_id]
        ticket_creator = interaction.guild.get_member(ticket_data['user_id'])
        claimer = interaction.guild.get_member(interaction.user.id)
        
        await interaction.channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await interaction.channel.set_permissions(interaction.guild.get_role(TRIAL_ROLE_ID), read_messages=False, send_messages=False)
        await interaction.channel.set_permissions(interaction.guild.get_role(HELPER_ROLE_ID), read_messages=False, send_messages=False)
        await interaction.channel.set_permissions(interaction.guild.get_role(MOD_ROLE_ID), read_messages=False, send_messages=False)
        
        await interaction.channel.set_permissions(interaction.guild.get_role(TICKET_ADMIN_ROLE_ID), read_messages=True, send_messages=True)
        if ticket_creator:
            await interaction.channel.set_permissions(ticket_creator, read_messages=True, send_messages=True)
        if claimer:
            await interaction.channel.set_permissions(claimer, read_messages=True, send_messages=True)
        
        embed = discord.Embed(
            title="🎫 Ticket Claimed",
            description=f"This ticket has been claimed by {interaction.user.mention}\nOnly ticket admins, the ticket creator, and the claimer can now see this ticket.",
            color=0x00ff00
        )
        
        if not has_ticket_admin_permissions(interaction.user):
            button.disabled = True
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_staff_permissions(interaction.user):
            await interaction.response.send_message("You don't have permission to close tickets!", ephemeral=True)
            return

        data = load_data()
        channel_id = str(interaction.channel.id)
        
        if channel_id not in data['tickets']:
            await interaction.response.send_message("This ticket doesn't exist in the database!", ephemeral=True)
            return

        messages = []
        async for message in interaction.channel.history(limit=None, oldest_first=True):
            messages.append(f"{message.author.name}: {message.content}")
        
        transcript = "\n".join(messages)
        
        ticket_data = data['tickets'][channel_id]
        ticket_counts = load_ticket_counts()
        
        if ticket_data.get('claimed_by'):
            closer_id = str(ticket_data['claimed_by'])
            if closer_id not in ticket_counts['user_ticket_counts']:
                ticket_counts['user_ticket_counts'][closer_id] = 0
            ticket_counts['user_ticket_counts'][closer_id] += 1
            save_ticket_counts(ticket_counts)
        else:
            closer_id = str(interaction.user.id)
            if closer_id not in ticket_counts['user_ticket_counts']:
                ticket_counts['user_ticket_counts'][closer_id] = 0
            ticket_counts['user_ticket_counts'][closer_id] += 1
            save_ticket_counts(ticket_counts)

        logs_channel = bot.get_channel(TICKET_LOGS_CHANNEL_ID)
        if logs_channel:
            log_embed = discord.Embed(
                title="🎫 Ticket Closed",
                color=0xff0000,
                timestamp=datetime.datetime.now()
            )
            log_embed.add_field(name="Ticket Type", value=interaction.channel.category.name, inline=True)
            log_embed.add_field(name="Category", value=interaction.channel.category.name, inline=True)
            log_embed.add_field(name="Closed By", value=interaction.user.mention, inline=True)
            log_embed.add_field(name="Channel", value=interaction.channel.name, inline=True)
            
            transcript_file = discord.File(
                io.StringIO(transcript),
                filename=f"transcript-{interaction.channel.name}.txt"
            )
            await logs_channel.send(embed=log_embed, file=transcript_file)
        
        await interaction.response.send_message("Ticket will be deleted in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="Unclaim Ticket", style=discord.ButtonStyle.gray, emoji="🔄")
    async def unclaim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_ticket_admin_permissions(interaction.user):
            await interaction.response.send_message("You don't have permission to unclaim tickets!", ephemeral=True)
            return
        
        data = load_data()
        channel_id = str(interaction.channel.id)
        
        if channel_id not in data['tickets']:
            await interaction.response.send_message("This ticket doesn't exist in the database!", ephemeral=True)
            return
        
        if not data['tickets'][channel_id]['claimed_by']:
            await interaction.response.send_message("This ticket is not claimed!", ephemeral=True)
            return
        
        data['tickets'][channel_id]['claimed_by'] = None
        data['tickets'][channel_id]['last_activity'] = datetime.datetime.now().isoformat()
        save_data(data)
        
        ticket_data = data['tickets'][channel_id]
        ticket_creator = interaction.guild.get_member(ticket_data['user_id'])
        
        await interaction.channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await interaction.channel.set_permissions(interaction.guild.get_role(TRIAL_ROLE_ID), read_messages=True, send_messages=True)
        await interaction.channel.set_permissions(interaction.guild.get_role(HELPER_ROLE_ID), read_messages=True, send_messages=True)
        await interaction.channel.set_permissions(interaction.guild.get_role(MOD_ROLE_ID), read_messages=True, send_messages=True)
        await interaction.channel.set_permissions(interaction.guild.get_role(TICKET_ADMIN_ROLE_ID), read_messages=True, send_messages=True)
        
        if ticket_creator:
            await interaction.channel.set_permissions(ticket_creator, read_messages=True, send_messages=True)
        
        embed = discord.Embed(
            title="🎫 Ticket Unclaimed",
            description=f"This ticket has been unclaimed by {interaction.user.mention}\nAll team members can now see this ticket again.",
            color=0xffff00
        )
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=embed)

@tasks.loop(seconds=10)
async def update_server_status():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.mcsrvstat.us/3/{MC_SERVER_IP}') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('online', False):
                        embed = discord.Embed(
                            title="🟢 Server Online",
                            color=0x00ff00,
                            timestamp=datetime.datetime.now()
                        )
                        
                        players = data.get('players', {})
                        online = players.get('online', 0)
                        max_players = players.get('max', 0)
                        version = data.get('version', 'Unknown')
                        
                        embed.add_field(name="Players Online", value=f"{online}/{max_players}", inline=True)
                        embed.add_field(name="Version", value=version, inline=True)
                        embed.add_field(name="Server IP", value=MC_SERVER_IP, inline=True)
                        embed.add_field(name="Port", value=str(MC_SERVER_PORT), inline=True)
                        embed.set_thumbnail(url=STATUS_IMAGE_1)
                        embed.set_image(url=BANNER_IMAGE)
                        
                        bot.server_status_embed = embed
                        print(f"Server status updated: Online - {online}/{max_players} players")
                        
                        await bot.change_presence(
                            activity=discord.Activity(
                                type=discord.ActivityType.playing,
                                name=f"👥 {online}/{max_players}"
                            )
                        )
                        return
                    
        embed = discord.Embed(
            title="🔴 Server Offline",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Server IP", value=MC_SERVER_IP, inline=True)
        embed.add_field(name="Port", value=str(MC_SERVER_PORT), inline=True)
        embed.set_thumbnail(url=STATUS_IMAGE_1)
        embed.set_image(url=BANNER_IMAGE)
        
        bot.server_status_embed = embed
        
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="🔴 Offline"
            )
        )
        
    except Exception as e:
        print(f"Error checking server status: {e}")
        embed = discord.Embed(
            title="🔴 Server Offline",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Server IP", value=MC_SERVER_IP, inline=True)
        embed.add_field(name="Port", value=str(MC_SERVER_PORT), inline=True)
        embed.set_thumbnail(url=STATUS_IMAGE_1)
        embed.set_image(url=BANNER_IMAGE)
        
        bot.server_status_embed = embed
        
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="🔴 Offline"
            )
        )

@bot.tree.command(name="status", description="Check the current server status")
async def server_status(interaction: discord.Interaction):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.mcsrvstat.us/3/{MC_SERVER_IP}') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('online', False):
                        embed = discord.Embed(
                            title="🟢 Server Online",
                            color=0x00ff00,
                            timestamp=datetime.datetime.now()
                        )
                        
                        players = data.get('players', {})
                        online = players.get('online', 0)
                        max_players = players.get('max', 0)
                        version = data.get('version', 'Unknown')
                        
                        embed.add_field(name="Players Online", value=f"{online}/{max_players}", inline=True)
                        embed.add_field(name="Version", value=version, inline=True)
                        embed.add_field(name="Server IP", value=MC_SERVER_IP, inline=True)
                        embed.add_field(name="Port", value=str(MC_SERVER_PORT), inline=True)
                        embed.set_thumbnail(url=STATUS_IMAGE_1)
                        embed.set_image(url=BANNER_IMAGE)
                    else:
                        embed = discord.Embed(
                            title="🔴 Server Offline",
                            color=0xff0000,
                            timestamp=datetime.datetime.now()
                        )
                        embed.add_field(name="Server IP", value=MC_SERVER_IP, inline=True)
                        embed.add_field(name="Port", value=str(MC_SERVER_PORT), inline=True)
                        embed.set_thumbnail(url=STATUS_IMAGE_1)
                        embed.set_image(url=BANNER_IMAGE)
                    
                    await interaction.response.send_message(embed=embed)
                    return
                    
    except Exception as e:
        print(f"Error in status command: {e}")
        embed = discord.Embed(
            title="🔴 Server Offline",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Server IP", value=MC_SERVER_IP, inline=True)
        embed.add_field(name="Port", value=str(MC_SERVER_PORT), inline=True)
        embed.set_thumbnail(url=STATUS_IMAGE_1)
        embed.set_image(url=BANNER_IMAGE)
        
        await interaction.response.send_message(embed=embed)

def load_temp_roles():
    """
    Load temporary roles data from temp_roles.json.
    Creates the file with default structure if it doesn't exist or is invalid.
    """
    try:
        with open('temp_roles.json', 'r') as f:
            content = f.read()
            if not content.strip():
                return {'temp_roles': {}}
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        default_data = {'temp_roles': {}}
        with open('temp_roles.json', 'w') as f:
            json.dump(default_data, f, indent=2)
        return default_data

def save_temp_roles(data):
    """
    Save temporary roles data to temp_roles.json.
    """
    try:
        with open('temp_roles.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving temp_roles.json: {e}")

@bot.tree.command(name="setup_tickets", description="Setup the ticket system")
@app_commands.describe(channel="Channel to send the ticket embed to")
async def setup_tickets(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎫 Echo Network Ticket System",
        description="Need assistance? Open a ticket using the dropdown below!\n\n"
                   "• **Support Tickets** - General help and questions\n"
                   "• **Media Applications** - Apply for content creator\n"
                   "• **Player Reports** - Report rule violations\n"
                   "• **Appeals** - Submit a ban/mute appeal\n\n"
                   "**Before opening a Media Application ticket, make sure you have hit the requirements!**\n"
                   "Check your requirements by going to <#1351291667088408587> and using `/media`\n\n"
                   "Please be patient and provide clear information in your ticket.",
        color=0x5865F2
    )
    
    embed.set_image(url=TICKET_BANNER_1)
    embed.set_thumbnail(url=TICKET_BANNER_2)
    
    embed.set_footer(text="Echo Network Support • Tickets are monitored 24/7")
    
    view = TicketView()
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"Ticket system setup in {channel.mention}!", ephemeral=True)

def has_team_permissions(member: discord.Member) -> bool:
    return any(role.id == TEAM_ROLE_ID for role in member.roles)

@bot.tree.command(name="close", description="Close the current ticket")
async def close_ticket(interaction: discord.Interaction):
 
    valid_categories = [SUPPORT_CATEGORY_ID, MEDIA_CATEGORY_ID, REPORTS_CATEGORY_ID, APPEALS_CATEGORY_ID]
    if not interaction.channel.category or interaction.channel.category.id not in valid_categories:
        await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
        return
    
    if not has_staff_permissions(interaction.user):
        await interaction.response.send_message("You don't have permission to close tickets!", ephemeral=True)
        return
    
    data = load_data()
    channel_id = str(interaction.channel.id)
    
    if channel_id not in data['tickets']:
        data['tickets'][channel_id] = {
            'user_id': interaction.channel.topic.split('|')[0] if interaction.channel.topic else None,
            'username': 'Unknown',
            'type': interaction.channel.category.name if interaction.channel.category else 'Unknown',
            'category': interaction.channel.category.name if interaction.channel.category else 'Unknown',
            'created_at': datetime.datetime.now().isoformat(),
            'last_activity': datetime.datetime.now().isoformat(),
            'claimed_by': None,
            'warning_sent': False
        }
        save_data(data)

    messages = []
    async for message in interaction.channel.history(limit=None, oldest_first=True):
        messages.append(f"{message.author.name}: {message.content}")
    
    transcript = "\n".join(messages)
    
    ticket_data = data['tickets'][channel_id]
    ticket_counts = load_ticket_counts()
    
    if ticket_data.get('claimed_by'):
        closer_id = str(ticket_data['claimed_by'])
        if closer_id not in ticket_counts['user_ticket_counts']:
            ticket_counts['user_ticket_counts'][closer_id] = 0
        ticket_counts['user_ticket_counts'][closer_id] += 1
        save_ticket_counts(ticket_counts)
    else:
        closer_id = str(interaction.user.id)
        if closer_id not in ticket_counts['user_ticket_counts']:
            ticket_counts['user_ticket_counts'][closer_id] = 0
        ticket_counts['user_ticket_counts'][closer_id] += 1
        save_ticket_counts(ticket_counts)

    logs_channel = bot.get_channel(TICKET_LOGS_CHANNEL_ID)
    if logs_channel:
        log_embed = discord.Embed(
            title="🎫 Ticket Closed",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        log_embed.add_field(name="Ticket Type", value=interaction.channel.category.name, inline=True)
        log_embed.add_field(name="Category", value=interaction.channel.category.name, inline=True)
        log_embed.add_field(name="Closed By", value=interaction.user.mention, inline=True)
        log_embed.add_field(name="Channel", value=interaction.channel.name, inline=True)
        
        transcript_file = discord.File(
            io.StringIO(transcript),
            filename=f"transcript-{interaction.channel.name}.txt"
        )
        await logs_channel.send(embed=log_embed, file=transcript_file)
    
    await interaction.response.send_message("Ticket will be deleted in 5 seconds...")
    await asyncio.sleep(5)
    await interaction.channel.delete()

@bot.tree.command(name="ticket_check", description="Check how many tickets you have closed")
async def ticket_check(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    target_user = user or interaction.user
    ticket_counts = load_ticket_counts()
    
    count = ticket_counts['user_ticket_counts'].get(str(target_user.id), 0)
    
    embed = discord.Embed(
        title="📊 Ticket Statistics",
        description=f"{target_user.mention} has closed **{count}** tickets",
        color=0x5865F2
    )
    embed.set_thumbnail(url=target_user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="report_check", description="Check how many reports you have submitted")
async def report_check(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    target_user = user or interaction.user
    report_counts = load_report_counts()
    count = report_counts['user_report_counts'].get(str(target_user.id), 0)
    embed = discord.Embed(
        title="📊 Report Statistics",
        description=f"{target_user.mention} has submitted **{count}** reports",
        color=0xff0000
    )
    embed.set_thumbnail(url=target_user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="store", description="Get the link to Echo Network's store")
async def store_command(interaction: discord.Interaction):
    if not any(role.id == COMMUNITY_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("You need the Community role to use this command!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🛒 Echo Network Store",
        description="Visit our store to purchase ranks, items, and more!",
        color=0x5865F2,
        url="https://store.echo-smp.net/"
    )
    embed.add_field(
        name="🔗 Store Link", 
        value="[Click here to visit the store](https://store.echo-smp.net/)", 
        inline=False
    )
    embed.set_footer(text="Support Echo Network by shopping at our store!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="media", description="View media requirements for Echo Network")
async def media_command(interaction: discord.Interaction):
    if not any(role.id == COMMUNITY_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("You need the Community role to use this command!", ephemeral=True)
        return

    embed = discord.Embed(
        title="📱 Media Requirements",
        description="Here are the requirements to apply for a media position at Echo Network:",
        color=0x5865F2
    )
    
    embed.add_field(
        name="📱 TikTok",
        value="• **5k views**\n• **TikTok Live:** 15 average viewers",
        inline=True
    )
    
    embed.add_field(
        name="📺 YouTube", 
        value="• **3k views**\n• **Live:** 10 average viewers",
        inline=True
    )
    
    embed.add_field(
        name="🎮 Twitch",
        value="• **10 views**",
        inline=True
    )
    
    embed.add_field(
        name="📝 How to Apply",
        value="Create a **Media Applications** ticket using the ticket system to apply for a media position!",
        inline=False
    )
    
    embed.set_footer(text="Echo Network Media Team")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="report", description="Report a player")
@app_commands.describe(
    username="The Minecraft username of the player to report",
    duration="How long they should be punished for",
    reason="The reason for the report"
)
async def create_report(interaction: discord.Interaction, username: str, duration: str, reason: str):
    if interaction.channel.id != REPORT_CHANNEL_ID:
        await interaction.response.send_message("This command can only be used in the report channel!", ephemeral=True)
        return
    
    report_data = load_report_data()
    user_id = str(interaction.user.id)
    

    if has_team_permissions(interaction.user):
        evidence_channel = bot.get_channel(EVIDENCE_CHANNEL_ID)
        if evidence_channel:
            async for message in evidence_channel.history(limit=1):
                if message.attachments:
                    for attachment in message.attachments:
                        if any(attachment.content_type.startswith(media_type) for media_type in ['image/', 'video/']):
                            evidence = attachment.url
                            break
                elif message.content.startswith(('http://', 'https://', 'medal.tv/')):
                    evidence = message.content
                else:
                    evidence = "No evidence found"
                break
    else:
        if user_id not in report_data['pending_reports']:
            await interaction.response.send_message("No pending evidence found! Please upload evidence to the evidence channel first.", ephemeral=True)
            return
        evidence = report_data['pending_reports'][user_id]
    
    head_url = await get_minecraft_head_url(username)
    
    embed = discord.Embed(
        title="📊 Player Report",
        color=0xff0000,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Reported Player", value=username, inline=True)
    embed.add_field(name="Duration", value=duration, inline=True)
    embed.add_field(name="Reported By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    
    if evidence.startswith(('http://', 'https://', 'medal.tv/')):
        embed.add_field(name="Evidence", value=evidence, inline=False)
    else:
        embed.add_field(name="Evidence", value="[Click here to view evidence]({})".format(evidence), inline=False)
    
    embed.set_thumbnail(url=head_url)
    embed.set_footer(text="Report submitted for review")
    
    await interaction.response.send_message(embed=embed)
    
    report_counts = load_report_counts()
    user_id = str(interaction.user.id)
    
    if user_id not in report_counts['user_report_counts']:
        report_counts['user_report_counts'][user_id] = 0
    
    report_counts['user_report_counts'][user_id] += 1
    save_report_counts(report_counts)
    
    if not has_team_permissions(interaction.user):
        del report_data['pending_reports'][user_id]
        save_report_data(report_data)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.channel.id == EVIDENCE_CHANNEL_ID:
        report_data = load_report_data()
        user_id = str(message.author.id)
        
        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.content_type.startswith(media_type) for media_type in ['image/', 'video/']):
                    report_data['pending_reports'][user_id] = attachment.url
                    await message.add_reaction('✅')
                    await message.channel.send(f"{message.author.mention} Evidence received! You can now use the /report command.", delete_after=10)
                    break
        elif message.content.startswith(('http://', 'https://', 'medal.tv/')):
            report_data['pending_reports'][user_id] = message.content
            await message.add_reaction('✅')
            await message.channel.send(f"{message.author.mention} Evidence link received! You can now use the /report command.", delete_after=10)
        
        save_report_data(report_data)
    
    afk_data = load_afk_data()
    
    excluded_channels = [
        DISCUSSION_CHANNEL_ID,  # Discussion channel
        CHAT_CHANNEL_ID,        # Chat channel
        APPLICATIONS_CHANNEL_ID,  # Applications channel
        LOA_CHANNEL_ID,         # LOA channel
        STAFF_MOVEMENT_CHANNEL_ID,  # Staff movement channel
        LIVE_ANNOUNCEMENT_CHANNEL_ID,  # Live announcement channel
        EVIDENCE_CHANNEL_ID,    # Evidence channel
    ]
    
    if str(message.author.id) in afk_data['afk_users'] and message.channel.id not in excluded_channels:
        try:
            data = afk_data['afk_users'][str(message.author.id)]
            await message.author.edit(nick=data['original_nickname'])
            del afk_data['afk_users'][str(message.author.id)]
            save_afk_data(afk_data)
            
            embed = discord.Embed(
                title="✅ Welcome Back!",
                description=f"{message.author.mention} is no longer AFK",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            await message.channel.send(embed=embed)
        except:
            pass
    
    for mention in message.mentions:
        user_id = str(mention.id)
        if user_id in afk_data['afk_users']:
            data = afk_data['afk_users'][user_id]
            end_time = datetime.datetime.fromisoformat(data['end_time'])
            time_remaining = end_time - datetime.datetime.now()
            
            if time_remaining.total_seconds() > 0:
                embed = discord.Embed(
                    title="⏸️ User is AFK",
                    description=f"{mention.mention} is currently AFK",
                    color=0xffff00,
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="Reason", value=data['reason'], inline=True)
                embed.add_field(name="Time Remaining", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
                embed.set_thumbnail(url=mention.display_avatar.url)
                
                await message.channel.send(embed=embed, delete_after=10)
    
    await bot.process_commands(message)

@bot.tree.command(name="ticket_stats", description="View ticket statistics (Admin only)")
async def ticket_stats(interaction: discord.Interaction):
    if not has_ticket_admin_permissions(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return
    
    data = load_data()
    ticket_counts = load_ticket_counts()
    
    active_tickets = len(data['tickets'])
    closed_tickets = len(data['closed_tickets'])
    total_tickets = active_tickets + closed_tickets
    

    categories = {}
    for ticket in data['tickets'].values():
        category = ticket.get('category', 'Unknown')
        categories[category] = categories.get(category, 0) + 1
    
    embed = discord.Embed(
        title="📊 Server Ticket Statistics",
        color=0x5865F2,
        timestamp=datetime.datetime.now()
    )
    
    embed.add_field(name="🎫 Active Tickets", value=str(active_tickets), inline=True)
    embed.add_field(name="✅ Closed Tickets", value=str(closed_tickets), inline=True)
    embed.add_field(name="📈 Total Tickets", value=str(total_tickets), inline=True)
    
    if categories:
        category_text = "\n".join([f"• {cat}: {count}" for cat, count in categories.items()])
        embed.add_field(name="📂 Active by Category", value=category_text, inline=False)
    
  
    top_closers = sorted(ticket_counts['user_ticket_counts'].items(), 
                        key=lambda x: x[1], reverse=True)[:5]
    if top_closers:
        closer_text = ""
        for user_id, count in top_closers:
            user = bot.get_user(int(user_id))
            name = user.display_name if user else "Unknown User"
            closer_text += f"• {name}: {count}\n"
        embed.add_field(name="🏆 Top Ticket Closers", value=closer_text, inline=False)
    
    embed.set_footer(text="Ticket system statistics")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="warn", description="Warn a user")
@is_council()
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    """
    Warn a user and keep track of their warnings.
    If a user reaches 5 warnings, their roles will be stripped.
    """
    await interaction.response.defer()
    
    warnings_data = load_warnings()
    user_id = str(user.id)
    
    if user_id not in warnings_data['warnings']:
        warnings_data['warnings'][user_id] = []
    
    warning = {
        'reason': reason,
        'warned_by': interaction.user.id,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    warnings_data['warnings'][user_id].append(warning)
    save_warnings(warnings_data)
    
    warning_count = len(warnings_data['warnings'][user_id])
    
    embed = discord.Embed(
        title="⚠️ User Warned",
        color=0xff4444,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Warned By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Warning Count", value=f"{warning_count}/5", inline=True)
    
    if warning_count >= 5:
        try:
            await user.edit(roles=[])
            embed.add_field(name="⚠️ Action Taken", value="All roles have been stripped due to reaching 5 warnings.", inline=False)
        except:
            embed.add_field(name="⚠️ Error", value="Failed to strip roles. Please do this manually.", inline=False)
    
    await interaction.followup.send(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title="⚠️ You have been warned",
            description=f"You have received a warning in {interaction.guild.name}",
            color=0xff4444,
            timestamp=datetime.datetime.now()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.add_field(name="Warning Count", value=f"{warning_count}/5", inline=True)
        if warning_count >= 5:
            dm_embed.add_field(name="⚠️ Action Taken", value="All your roles have been stripped due to reaching 5 warnings.", inline=False)
        await user.send(embed=dm_embed)
    except:
        pass

@bot.tree.command(name="warnings", description="Check warnings for a user")
async def warnings(interaction: discord.Interaction, user: discord.Member):
    if not (has_council_permissions(interaction.user) or has_team_permissions(interaction.user)):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    warnings_data = load_warnings()
    user_id = str(user.id)
    
    if user_id not in warnings_data['warnings'] or not warnings_data['warnings'][user_id]:
        await interaction.followup.send(f"{user.mention} has no warnings.", ephemeral=True)
        return
    
    warnings = warnings_data['warnings'][user_id]
    
    embed = discord.Embed(
        title=f"⚠️ Warnings for {user.name}",
        color=0xff4444,
        timestamp=datetime.datetime.now()
    )
    
    for i, warning in enumerate(warnings, 1):
        warned_by = interaction.guild.get_member(warning['warned_by'])
        warned_by_mention = warned_by.mention if warned_by else "Unknown User"
        timestamp = datetime.datetime.fromisoformat(warning['timestamp'])
        
        embed.add_field(
            name=f"Warning #{i}",
            value=f"Reason: {warning['reason']}\nWarned by: {warned_by_mention}\nTime: <t:{int(timestamp.timestamp())}:R>",
            inline=False
        )
    
    embed.set_footer(text=f"Total Warnings: {len(warnings)}/5")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="setup", description="Setup the ticket panel")
@is_council()
async def setup(interaction: discord.Interaction):
    if not interaction.channel:
        return
    
    embed = discord.Embed(
        title="🎫 Echo Network Support",
        description="Click the button below to create a support ticket",
        color=0x00ff00
    )
    embed.set_image(url=BANNER_IMAGE)
    embed.set_thumbnail(url=STATUS_IMAGE_1)
    
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Ticket panel has been set up!", ephemeral=True)

def get_minecraft_head(username: str) -> str:
    """Get a high-quality Minecraft head image URL"""
    return f"https://mc-heads.net/avatar/{username}/100.png"  

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        
 
        guild = bot.get_guild(interaction.guild.id)
        if guild:
            live_channel = guild.get_channel(interaction.guild.id)
            if live_channel:

                media_role = guild.get_role(MEDIA_ROLE_ID)
                if media_role:
       
                    for command in bot.tree.get_commands():
                        if command.name in ['live', 'end_live']:
                            await command.set_permissions(media_role, send_messages=True)
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="🔄 Checking..."
        )
    )
    
    update_server_status.start()
    check_temp_roles.start()
    update_leaderboards.start()
    check_afk_status.start()
    check_echo_roles.start()

def has_council_permissions(member: discord.Member) -> bool:
    return any(role.id == COUNCIL_ROLE_ID for role in member.roles)

@bot.tree.command(name="add_ticket", description="Add tickets to a user's count (Council only)")
@app_commands.describe(
    user="The user to add tickets to",
    ticket_type="Number of tickets to add"
)
async def add_ticket(interaction: discord.Interaction, user: discord.Member, ticket_type: int):
    if not has_council_permissions(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return

    if ticket_type < 1:
        await interaction.response.send_message("Please enter a number greater than 0!", ephemeral=True)
        return

    ticket_counts = load_ticket_counts()
    user_id = str(user.id)
    
    if user_id not in ticket_counts['user_ticket_counts']:
        ticket_counts['user_ticket_counts'][user_id] = 0
    
    ticket_counts['user_ticket_counts'][user_id] += ticket_type
    save_ticket_counts(ticket_counts)
    
    embed = discord.Embed(
        title="✅ Tickets Added",
        color=0x00ff00,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Tickets Added", value=str(ticket_type), inline=True)
    embed.add_field(name="New Ticket Count", value=str(ticket_counts['user_ticket_counts'][user_id]), inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title="📝 Tickets Added",
            description=f"{ticket_type} ticket(s) have been added to your count by {interaction.user.mention}",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        dm_embed.add_field(name="Tickets Added", value=str(ticket_type), inline=True)
        dm_embed.add_field(name="Your Total Tickets", value=str(ticket_counts['user_ticket_counts'][user_id]), inline=True)
        await user.send(embed=dm_embed)
    except:
        pass

@bot.tree.command(name="remove_ticket", description="Remove tickets from a user's count (Council only)")
@app_commands.describe(
    user="The user to remove tickets from",
    amount="Number of tickets to remove"
)
async def remove_ticket(interaction: discord.Interaction, user: discord.Member, amount: int):
    if not has_council_permissions(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return

    if amount < 1:
        await interaction.response.send_message("Please enter a number greater than 0!", ephemeral=True)
        return

    ticket_counts = load_ticket_counts()
    user_id = str(user.id)
    
    if user_id not in ticket_counts['user_ticket_counts'] or ticket_counts['user_ticket_counts'][user_id] <= 0:
        await interaction.response.send_message("This user has no tickets to remove!", ephemeral=True)
        return
    
    amount = min(amount, ticket_counts['user_ticket_counts'][user_id])
    ticket_counts['user_ticket_counts'][user_id] -= amount
    save_ticket_counts(ticket_counts)
    
    embed = discord.Embed(
        title="✅ Tickets Removed",
        color=0x00ff00,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Tickets Removed", value=str(amount), inline=True)
    embed.add_field(name="New Ticket Count", value=str(ticket_counts['user_ticket_counts'][user_id]), inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title="📝 Tickets Removed",
            description=f"{amount} ticket(s) have been removed from your count by {interaction.user.mention}",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        dm_embed.add_field(name="Tickets Removed", value=str(amount), inline=True)
        dm_embed.add_field(name="Your Total Tickets", value=str(ticket_counts['user_ticket_counts'][user_id]), inline=True)
        await user.send(embed=dm_embed)
    except:
        pass

@bot.tree.command(name="temprole", description="Give a role to a user temporarily")
@app_commands.describe(
    user="The user to give the role to",
    role="The role to give",
    duration="Duration (e.g., 1h, 30m, 1d)"
)
@is_council()
async def temprole(interaction: discord.Interaction, user: discord.Member, role: discord.Role, duration: str):
    if not has_team_permissions(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return

    try:
        duration_seconds = 0
        if duration.endswith('h'):
            duration_seconds = int(duration[:-1]) * 3600
        elif duration.endswith('m'):
            duration_seconds = int(duration[:-1]) * 60
        elif duration.endswith('d'):
            duration_seconds = int(duration[:-1]) * 86400
        else:
            await interaction.response.send_message("Invalid duration format! Use h for hours, m for minutes, or d for days.", ephemeral=True)
            return

        await user.add_roles(role)
        
        temp_roles = load_temp_roles()
        temp_roles['temp_roles'][str(user.id)] = {
            'role_id': role.id,
            'end_time': (datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)).isoformat(),
            'added_by': interaction.user.id
        }
        save_temp_roles(temp_roles)
        
        embed = discord.Embed(
            title="⏱️ Temporary Role Added",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Role", value=role.mention, inline=True)
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.add_field(name="Added By", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title="⏱️ Temporary Role Added",
                description=f"You have been given the role {role.mention} in {interaction.guild.name}",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Duration", value=duration, inline=True)
            dm_embed.add_field(name="Added By", value=interaction.user.mention, inline=True)
            await user.send(embed=dm_embed)
        except:
            pass

        await asyncio.sleep(duration_seconds)
        
        if role in user.roles:
            await user.remove_roles(role)
            
            temp_roles = load_temp_roles()
            if str(user.id) in temp_roles['temp_roles']:
                del temp_roles['temp_roles'][str(user.id)]
                save_temp_roles(temp_roles)
            
            try:
                remove_embed = discord.Embed(
                    title="⏱️ Temporary Role Removed",
                    description=f"Your temporary role {role.mention} in {interaction.guild.name} has expired",
                    color=0xff0000,
                    timestamp=datetime.datetime.now()
                )
                await user.send(embed=remove_embed)
            except:
                pass
            
            log_embed = discord.Embed(
                title="⏱️ Temporary Role Expired",
                color=0xff0000,
                timestamp=datetime.datetime.now()
            )
            log_embed.add_field(name="User", value=user.mention, inline=True)
            log_embed.add_field(name="Role", value=role.mention, inline=True)
            log_embed.add_field(name="Duration", value=duration, inline=True)
            log_embed.add_field(name="Added By", value=interaction.user.mention, inline=True)
            
            await interaction.channel.send(embed=log_embed)
            
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@tasks.loop(minutes=1)
async def check_temp_roles():
    """
    Background task to check and remove expired temporary roles.
    Runs every minute to check for roles that need to be removed.
    """
    try:
        temp_roles = load_temp_roles()
        current_time = datetime.datetime.now()
        
        for user_id, data in list(temp_roles['temp_roles'].items()):
            try:
                end_time = datetime.datetime.fromisoformat(data['end_time'])
                if current_time >= end_time:
                    guild = bot.guilds[0] if bot.guilds else None
                    if guild:
                        user = guild.get_member(int(user_id))
                        role = guild.get_role(data['role_id'])
                        if user and role and role in user.roles:
                            await user.remove_roles(role)
                            del temp_roles['temp_roles'][user_id]
                            save_temp_roles(temp_roles)
            except Exception as e:
                print(f"Error processing temp role for user {user_id}: {e}")
                continue
    except Exception as e:
        print(f"Error in check_temp_roles task: {e}")

@bot.tree.command(name="rename", description="Rename the current ticket")
@app_commands.describe(
    new_name="The new name for the ticket (without the prefix)"
)
async def rename_ticket(interaction: discord.Interaction, new_name: str):
 
    valid_categories = [SUPPORT_CATEGORY_ID, MEDIA_CATEGORY_ID, REPORTS_CATEGORY_ID, APPEALS_CATEGORY_ID]
    if not interaction.channel.category or interaction.channel.category.id not in valid_categories:
        await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
        return
    
    if not has_team_permissions(interaction.user):
        await interaction.response.send_message("You don't have permission to rename tickets!", ephemeral=True)
        return
    
    try:
        data = load_data()
        channel_id = str(interaction.channel.id)
        
        if channel_id not in data['tickets']:
            await interaction.response.send_message("This ticket doesn't exist in the database!", ephemeral=True)
            return
        
        ticket_data = data['tickets'][channel_id]
        old_name = interaction.channel.name
        
    
        category_prefixes = {
            SUPPORT_CATEGORY_ID: "support-",
            MEDIA_CATEGORY_ID: "media-",
            REPORTS_CATEGORY_ID: "reports-",
            APPEALS_CATEGORY_ID: "appeals-"
        }
        current_prefix = category_prefixes.get(interaction.channel.category.id, "ticket-")
        
       
        new_channel_name = f"{current_prefix}{new_name}"
        
        await interaction.channel.edit(name=new_channel_name)
        
        embed = discord.Embed(
            title="📝 Ticket Renamed",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Old Name", value=old_name, inline=True)
        embed.add_field(name="New Name", value=new_channel_name, inline=True)
        embed.add_field(name="Renamed By", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while renaming the ticket: {str(e)}", ephemeral=True)

@bot.tree.command(name="add_user", description="Add a user to the current ticket")
@app_commands.describe(
    user="The user to add to the ticket"
)
async def add_user(interaction: discord.Interaction, user: discord.Member):
    valid_categories = [SUPPORT_CATEGORY_ID, MEDIA_CATEGORY_ID, REPORTS_CATEGORY_ID, APPEALS_CATEGORY_ID]
    if not interaction.channel.category or interaction.channel.category.id not in valid_categories:
        await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
        return
    
    if not has_staff_permissions(interaction.user):
        await interaction.response.send_message("You don't have permission to add users to tickets!", ephemeral=True)
        return
    
    try:
        await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
        
        embed = discord.Embed(
            title="👥 User Added to Ticket",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User Added", value=user.mention, inline=True)
        embed.add_field(name="Added By", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title="🎫 Added to Ticket",
                description=f"You have been added to a ticket in {interaction.guild.name}",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Ticket Channel", value=interaction.channel.mention, inline=True)
            dm_embed.add_field(name="Added By", value=interaction.user.mention, inline=True)
            await user.send(embed=dm_embed)
        except:
            pass
        
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while adding the user: {str(e)}", ephemeral=True)

@bot.tree.command(name="live", description="Announce that you're going live")
@app_commands.describe(
    platform="The platform you're streaming on",
    url="Your live stream URL",
    title="The title of your stream"
)
@app_commands.checks.has_role(MEDIA_ROLE_ID)
async def announce_live(interaction: discord.Interaction, platform: str, url: str, title: str):
    if interaction.channel.id != LIVE_ANNOUNCEMENT_CHANNEL_ID:
        await interaction.response.send_message(f"This command can only be used in <#{LIVE_ANNOUNCEMENT_CHANNEL_ID}>!", ephemeral=True)
        return

    if not url.startswith(('https://', 'http://')):
        await interaction.response.send_message("Please provide a valid URL!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎥 Live Stream Started",
        description=f"{interaction.user.name} is now live on {platform}!",
        color=0x00ff00,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Platform", value=platform, inline=True)
    embed.add_field(name="Streamer", value=interaction.user.name, inline=True)
    embed.add_field(name="Title", value=title, inline=False)
    embed.add_field(name="Watch Now", value=f"[Click here to watch]({url})", inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text="Live Stream")

    message = await interaction.channel.send(embed=embed)
    
    await interaction.response.send_message("Live announcement has been posted!", ephemeral=True)

    try:
        while True:
            await asyncio.sleep(300)
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            end_embed = discord.Embed(
                                title="🎥 Live Stream Ended",
                                description=f"{interaction.user.name}'s stream on {platform} has ended.",
                                color=0xff0000,
                                timestamp=datetime.datetime.now()
                            )
                            end_embed.add_field(name="Platform", value=platform, inline=True)
                            end_embed.add_field(name="Streamer", value=interaction.user.name, inline=True)
                            end_embed.add_field(name="Title", value=title, inline=False)
                            end_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                            end_embed.set_footer(text="Stream Ended")
                            
                            await message.edit(embed=end_embed)
                            break
            except:
                end_embed = discord.Embed(
                    title="🎥 Live Stream Ended",
                    description=f"{interaction.user.name}'s stream on {platform} has ended.",
                    color=0xff0000,
                    timestamp=datetime.datetime.now()
                )
                end_embed.add_field(name="Platform", value=platform, inline=True)
                end_embed.add_field(name="Streamer", value=interaction.user.name, inline=True)
                end_embed.add_field(name="Title", value=title, inline=False)
                end_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                end_embed.set_footer(text="Stream Ended")
                
                await message.edit(embed=end_embed)
                break
    except Exception as e:
        print(f"Error in live stream monitoring: {e}")

@bot.tree.command(name="end_live", description="End your live stream announcement")
@app_commands.checks.has_role(MEDIA_ROLE_ID)
async def end_live(interaction: discord.Interaction):
    if interaction.channel.id != LIVE_ANNOUNCEMENT_CHANNEL_ID:
        await interaction.response.send_message(f"This command can only be used in <#{LIVE_ANNOUNCEMENT_CHANNEL_ID}>!", ephemeral=True)
        return

    async for message in interaction.channel.history(limit=100):
        if message.author == bot.user and message.embeds:
            embed = message.embeds[0]
            if embed.title == "🎥 Live Stream Started" and interaction.user.name in embed.description:
                end_embed = discord.Embed(
                    title="🎥 Live Stream Ended",
                    description=f"{interaction.user.name}'s stream has ended.",
                    color=0xff0000,
                    timestamp=datetime.datetime.now()
                )
                end_embed.add_field(name="Platform", value=embed.fields[0].value, inline=True)
                end_embed.add_field(name="Streamer", value=interaction.user.name, inline=True)
                end_embed.add_field(name="Title", value=embed.fields[2].value, inline=False)
                end_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                end_embed.set_footer(text="Stream Ended")
                
                await message.edit(embed=end_embed)
                await interaction.response.send_message("Live stream has been marked as ended!", ephemeral=True)
                return

    await interaction.response.send_message("No active live stream found for you!", ephemeral=True)

@bot.event
async def on_guild_join(guild):
    try:
        await bot.tree.sync(guild=guild)
        print(f"Synced commands for guild: {guild.name}")
    except Exception as e:
        print(f"Failed to sync commands for guild {guild.name}: {e}")

@bot.event
async def on_guild_available(guild):
    try:
        await bot.tree.sync(guild=guild)
        print(f"Synced commands for guild: {guild.name}")
    except Exception as e:
        print(f"Failed to sync commands for guild {guild.name}: {e}")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("You need the Media role to use this command!", ephemeral=True)
    else:
        print(f"Error: {error}")

class LOAView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def accept_loa(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_council_permissions(interaction.user):
            await interaction.response.send_message("You don't have permission to accept LOA requests!", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.color = 0x00ff00
        embed.title = "✅ LOA Request Accepted"
        embed.add_field(name="Accepted By", value=interaction.user.mention, inline=True)
        
        await interaction.message.edit(embed=embed, view=None)
        
        try:
            user = await bot.fetch_user(self.user_id)
            member = interaction.guild.get_member(self.user_id)
            if member:
                original_nickname = member.display_name
                new_nickname = f"{member.name}[LOA]"
                try:
                    await member.edit(nick=new_nickname)
                except:
                    pass
            
            dm_embed = discord.Embed(
                title="✅ LOA Request Accepted",
                description="Your Leave of Absence request has been accepted.",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Accepted By", value=interaction.user.mention, inline=True)
            await user.send(embed=dm_embed)
        except:
            pass

        await interaction.response.send_message("LOA request has been accepted!", ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, emoji="❌")
    async def deny_loa(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_council_permissions(interaction.user):
            await interaction.response.send_message("You don't have permission to deny LOA requests!", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.color = 0xff0000
        embed.title = "❌ LOA Request Denied"
        embed.add_field(name="Denied By", value=interaction.user.mention, inline=True)
        
        await interaction.message.edit(embed=embed, view=None)
        
        try:
            user = await bot.fetch_user(self.user_id)
            dm_embed = discord.Embed(
                title="❌ LOA Request Denied",
                description="Your Leave of Absence request has been denied.",
                color=0xff0000,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Denied By", value=interaction.user.mention, inline=True)
            await user.send(embed=dm_embed)
        except:
            pass

        await interaction.response.send_message("LOA request has been denied!", ephemeral=True)

@bot.tree.command(name="loa", description="Request a Leave of Absence")
@app_commands.describe(
    reason="The reason for your leave of absence",
    duration="How long you will be gone (e.g., 1 week, 2 months)"
)
async def request_loa(interaction: discord.Interaction, reason: str, duration: str):
    if not has_team_permissions(interaction.user):
        await interaction.response.send_message("You need to be a team member to request a Leave of Absence!", ephemeral=True)
        return

    loa_channel = bot.get_channel(LOA_CHANNEL_ID)
    if not loa_channel:
        await interaction.response.send_message("Error: LOA channel not found!", ephemeral=True)
        return

    embed = discord.Embed(
        title="⏸️ Leave of Absence Request",
        color=0xffff00,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Requested By", value=interaction.user.mention, inline=True)
    embed.add_field(name="Duration", value=duration, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text="Waiting for council approval")

    view = LOAView(interaction.user.id)
    await loa_channel.send(embed=embed, view=view)
    
    await interaction.response.send_message("Your LOA request has been submitted and is pending approval!", ephemeral=True)

@bot.tree.command(name="r", description="Add or remove a role from a user")
@app_commands.describe(
    user="The user to manage roles for",
    role="The role to add or remove"
)
@is_council()
async def manage_role(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message("I cannot manage roles that are higher than or equal to my highest role!", ephemeral=True)
        return

    staff_movement_channel = interaction.guild.get_channel(STAFF_MOVEMENT_CHANNEL_ID)
    arrow_emoji = ":BlueArrow:"
    role_names = {
        COMMUNITY_ROLE_ID: "Community",
        HELPER_ROLE_ID: "Helper",
        MOD_ROLE_ID: "Mod",
        TICKET_ADMIN_ROLE_ID: "Management"
    }
    role_icons = {
        COMMUNITY_ROLE_ID: ":Community:",
        HELPER_ROLE_ID: ":staffblue:",
        MOD_ROLE_ID: ":staffgreen:",
        TICKET_ADMIN_ROLE_ID: ":Management:"
    }
    staff_role_ids = [COMMUNITY_ROLE_ID, HELPER_ROLE_ID, MOD_ROLE_ID, TICKET_ADMIN_ROLE_ID]
    username = user.name
    user_mention = user.mention

    def get_highest_staff_role(member, exclude_role_id=None):
        roles = [r for r in member.roles if r.id in staff_role_ids and (exclude_role_id is None or r.id != exclude_role_id)]
        if not roles:
            return None
        priority = {TICKET_ADMIN_ROLE_ID: 4, MOD_ROLE_ID: 3, HELPER_ROLE_ID: 2, COMMUNITY_ROLE_ID: 1}
        roles.sort(key=lambda r: priority.get(r.id, 0), reverse=True)
        return roles[0]

    if role in user.roles:
        old_role_name = role_names.get(role.id, role.name)
        icon = role_icons.get(role.id, "")
        await user.remove_roles(role)
        new_highest = get_highest_staff_role(user)
        new_role_name = role_names.get(new_highest.id, new_highest.name) if new_highest else "None"
        # if staff_movement_channel:
        #     await staff_movement_channel.send(f"{user_mention} {old_role_name} {arrow_emoji} {new_role_name} {icon}")
        action = "removed from"
        color = 0xff0000
    else:
        old_highest = get_highest_staff_role(user)
        old_role_name = role_names.get(old_highest.id, old_highest.name) if old_highest else "None"
        icon = role_icons.get(role.id, "")
        await user.add_roles(role)
        new_role_name = role_names.get(role.id, role.name)
        # if staff_movement_channel:
        #     await staff_movement_channel.send(f"{user_mention} {old_role_name} {arrow_emoji} {new_role_name} {icon}")
        action = "added to"
        color = 0x00ff00
    embed = discord.Embed(
        title="Role Management",
        color=color,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Role", value=role.name, inline=True)
    embed.add_field(name="Action", value=f"Role {action} user", inline=True)
    embed.add_field(name="Modified By", value=interaction.user.mention, inline=True)
    await interaction.response.send_message(embed=embed)
    try:
        dm_embed = discord.Embed(
            title="Role Update",
            description=f"The role {role.name} has been {action} you in {interaction.guild.name}",
            color=color,
            timestamp=datetime.datetime.now()
        )
        dm_embed.add_field(name="Modified By", value=interaction.user.mention, inline=True)
        await user.send(embed=dm_embed)
    except:
        pass

class ApplicationResponseView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def accept_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_council_permissions(interaction.user):
            await interaction.response.send_message("You don't have permission to accept applications!", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.color = 0x00ff00
        embed.title = "✅ Application Accepted"
        embed.add_field(name="Accepted By", value=interaction.user.mention, inline=True)
        
        await interaction.message.edit(embed=embed, view=None)
        
        try:
            user = await bot.fetch_user(self.user_id)
            dm_embed = discord.Embed(
                title="✅ Application Accepted",
                description="Your staff application has been accepted! Please open a ticket to continue the process.",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Accepted By", value=interaction.user.mention, inline=True)
            await user.send(embed=dm_embed)
        except:
            pass

        await interaction.response.send_message("Application has been accepted!", ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, emoji="❌")
    async def deny_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_council_permissions(interaction.user):
            await interaction.response.send_message("You don't have permission to deny applications!", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.color = 0xff0000
        embed.title = "❌ Application Denied"
        embed.add_field(name="Denied By", value=interaction.user.mention, inline=True)
        
        await interaction.message.edit(embed=embed, view=None)
        
        try:
            user = await bot.fetch_user(self.user_id)
            dm_embed = discord.Embed(
                title="❌ Application Denied",
                description="Your staff application has been denied. You can reapply in 14 days.",
                color=0xff0000,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Denied By", value=interaction.user.mention, inline=True)
            await user.send(embed=dm_embed)
        except:
            pass

        await interaction.response.send_message("Application has been denied!", ephemeral=True)

class StaffApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apply for Staff", style=discord.ButtonStyle.green, emoji="📝")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message("I'll send you the application questions in a direct message!", ephemeral=True)
            
            try:
                questions = [
                    ("Minecraft Username", "What is your Minecraft username?"),
                    ("Discord Username", "What is your Discord username?"),
                    ("Age", "How old are you?"),
                    ("Timezone", "What is your timezone?"),
                    ("Experience", "What skills or qualities do you bring to the team?\nHow familiar are you with Echo SMP and its rules?\nHave you ever been staff on a Minecraft server before?"),
                    ("Team Choice", "Are you applying for the Community Team (Discord Moderation) or In-Game Team (Minecraft Moderation)?"),
                    ("Moderation", "How would you handle a player breaking the rules for the first time?\nWhat would you do if two players were having a heated argument?\nHow do you handle criticism or negative feedback from other players?"),
                    ("Availability", "Are you willing to help with tickets, reports, and assisting players when needed?\nHow many hours per week can you dedicate to the team?\nAre you comfortable enforcing rules fairly, even if it involves friends?"),
                    ("Final Questions", "Why do you want to be part of the Echo SMP Team?\nAre you a staff member on any other server?\nAnything else to know?")
                ]
                
                answers = {}
                
                for field, question in questions:
                    embed = discord.Embed(
                        title=f"Question {len(answers) + 1}/{len(questions)}",
                        description=question,
                        color=0x5865F2
                    )
                    await interaction.user.send(embed=embed)
                    
                    def check(m):
                        return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)
                    
                    try:
                        msg = await bot.wait_for('message', check=check, timeout=3600.0)
                        answers[field] = msg.content
                    except asyncio.TimeoutError:
                        await interaction.user.send("You took too long to respond. Please start over by clicking the apply button again.")
                        return
                
                applications_channel = bot.get_channel(APPLICATIONS_CHANNEL_ID)
                if not applications_channel:
                    await interaction.user.send("Error: Applications channel not found!")
                    return

                embed = discord.Embed(
                    title="📝 New Staff Application",
                    color=0x5865F2,
                    timestamp=datetime.datetime.now()
                )
                
                embed.add_field(name="1️⃣ Basic Information", value=f"**Minecraft Username:** {answers['Minecraft Username']}\n**Discord Username:** {answers['Discord Username']}\n**Age:** {answers['Age']}\n**Timezone:** {answers['Timezone']}", inline=False)
                embed.add_field(name="2️⃣ Experience & Skills", value=answers['Experience'], inline=False)
                embed.add_field(name="Team Choice", value=answers['Team Choice'], inline=False)
                embed.add_field(name="3️⃣ Moderation & Responsibilities", value=answers['Moderation'], inline=False)
                embed.add_field(name="4️⃣ Availability & Commitment", value=answers['Availability'], inline=False)
                embed.add_field(name="5️⃣ Final Questions", value=answers['Final Questions'], inline=False)
                
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
                embed.set_footer(text=f"Application ID: {interaction.id}")
                
                view = ApplicationResponseView(interaction.user.id)
                await applications_channel.send(embed=embed, view=view)
                await interaction.user.send("Your application has been submitted successfully! The staff team will review it soon.")
                
            except discord.Forbidden:
                await interaction.followup.send("I couldn't send you a direct message. Please make sure your DMs are open!", ephemeral=True)
                
        except Exception as e:
            print(f"Error in button click: {e}")
            await interaction.response.send_message("An error occurred. Please try again.", ephemeral=True)

@bot.tree.command(name="setup_staff_applications", description="Setup the staff applications system")
@app_commands.describe(channel="Channel to send the application embed to")
@is_council()
async def setup_staff_applications(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        embed = discord.Embed(
            title="📝 Echo Network Staff Applications",
            description="Interested in joining our staff team? Click the button below to apply!\n\n"
                       "**Requirements:**\n"
                       "• Must be 14 years or older\n"
                       "• Active on both Discord and Minecraft\n"
                       "• Good communication skills\n"
                       "• Fair and unbiased\n"
                       "• Willing to help others\n\n"
                       "**Available Positions:**\n"
                       "• Community Team (Discord Moderation)\n"
                       "• In-Game Team (Minecraft Moderation)",
            color=0x5865F2
        )
        
        embed.set_image(url=BANNER_IMAGE)
        embed.set_thumbnail(url=STATUS_IMAGE_1)
        embed.set_footer(text="Echo Network Staff Team")
        
        view = StaffApplicationView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Staff applications system setup in {channel.mention}!", ephemeral=True)
    except Exception as e:
        print(f"Error in setup: {e}")
        await interaction.response.send_message("An error occurred while setting up the applications system.", ephemeral=True)

@bot.tree.command(name="remove_user", description="Remove a user from the current ticket")
@app_commands.describe(
    user="The user to remove from the ticket"
)
async def remove_user(interaction: discord.Interaction, user: discord.Member):
    valid_categories = [SUPPORT_CATEGORY_ID, MEDIA_CATEGORY_ID, REPORTS_CATEGORY_ID, APPEALS_CATEGORY_ID]
    if not interaction.channel.category or interaction.channel.category.id not in valid_categories:
        await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
        return
    
    if not has_ticket_admin_permissions(interaction.user):
        await interaction.response.send_message("You need ticket admin permissions to use this command!", ephemeral=True)
        return
    
    try:
        data = load_data()
        channel_id = str(interaction.channel.id)
        
        if channel_id not in data['tickets']:
            await interaction.response.send_message("This ticket doesn't exist in the database!", ephemeral=True)
            return
        
        ticket_data = data['tickets'][channel_id]
        
        if str(user.id) == str(ticket_data['user_id']):
            await interaction.response.send_message("You cannot remove the ticket creator!", ephemeral=True)
            return
        
        await interaction.channel.set_permissions(user, read_messages=False, send_messages=False)
        
        embed = discord.Embed(
            title="👥 User Removed from Ticket",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User Removed", value=user.mention, inline=True)
        embed.add_field(name="Removed By", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title="🎫 Removed from Ticket",
                description=f"You have been removed from a ticket in {interaction.guild.name}",
                color=0xff0000,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Ticket Channel", value=interaction.channel.mention, inline=True)
            dm_embed.add_field(name="Removed By", value=interaction.user.mention, inline=True)
            await user.send(embed=dm_embed)
        except:
            pass
        
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while removing the user: {str(e)}", ephemeral=True)

@bot.tree.command(name="kick", description="Kick a user from the server")
@is_council()
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    """
    Kick a user from the server.
    Only council members can use this command.
    """
    await interaction.response.defer()
    
    if user.top_role >= interaction.user.top_role:
        await interaction.followup.send("You cannot kick someone with a higher or equal role!", ephemeral=True)
        return
    
    if user == interaction.user:
        await interaction.followup.send("You cannot kick yourself!", ephemeral=True)
        return
    
    try:
        await user.kick(reason=f"Kicked by {interaction.user.name}: {reason}")
        
        embed = discord.Embed(
            title="👢 User Kicked",
            color=0xff8800,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Kicked By", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title="👢 You have been kicked",
                description=f"You have been kicked from **{interaction.guild.name}**",
                color=0xff8800,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Server", value=interaction.guild.name, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Kicked By", value=f"{interaction.user.name} ({interaction.user.id})", inline=True)
            dm_embed.add_field(name="Date", value=f"<t:{int(datetime.datetime.now().timestamp())}:F>", inline=True)
            dm_embed.set_footer(text="You can rejoin the server if you have an invite link")
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            print(f"Could not send DM to {user.name} - DMs are closed")
        except Exception as e:
            print(f"Error sending DM to {user.name}: {e}")
            
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to kick this user!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An error occurred while kicking the user: {str(e)}", ephemeral=True)

@bot.tree.command(name="ban", description="Ban a user from the server")
@is_council()
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided", delete_message_days: int = 1):
    """
    Ban a user from the server.
    Only council members can use this command.
    """
    await interaction.response.defer()
    
    if user.top_role >= interaction.user.top_role:
        await interaction.followup.send("You cannot ban someone with a higher or equal role!", ephemeral=True)
        return
    
    if user == interaction.user:
        await interaction.followup.send("You cannot ban yourself!", ephemeral=True)
        return
    
    if delete_message_days < 0 or delete_message_days > 7:
        await interaction.followup.send("Delete message days must be between 0 and 7!", ephemeral=True)
        return
    
    try:
        await user.ban(reason=f"Banned by {interaction.user.name}: {reason}", delete_message_days=delete_message_days)
        
        embed = discord.Embed(
            title="🔨 User Banned",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Banned By", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Delete Messages", value=f"{delete_message_days} days", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title="🔨 You have been banned",
                description=f"You have been **permanently banned** from **{interaction.guild.name}**",
                color=0xff0000,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Server", value=interaction.guild.name, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Banned By", value=f"{interaction.user.name} ({interaction.user.id})", inline=True)
            dm_embed.add_field(name="Date", value=f"<t:{int(datetime.datetime.now().timestamp())}:F>", inline=True)
            dm_embed.add_field(name="Message Deletion", value=f"{delete_message_days} days of messages deleted", inline=True)
            dm_embed.set_footer(text="This ban is permanent. Contact staff if you believe this was a mistake.")
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            print(f"Could not send DM to {user.name} - DMs are closed")
        except Exception as e:
            print(f"Error sending DM to {user.name}: {e}")
            
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to ban this user!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An error occurred while banning the user: {str(e)}", ephemeral=True)

@bot.tree.command(name="timeout", description="Timeout a user")
async def timeout(interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
    await interaction.response.defer()
    if user.top_role >= interaction.user.top_role:
        await interaction.followup.send("You cannot timeout someone with a higher or equal role!", ephemeral=True)
        return
    if user == interaction.user:
        await interaction.followup.send("You cannot timeout yourself!", ephemeral=True)
        return
    if not (has_team_permissions(interaction.user) or has_council_permissions(interaction.user)):
        await interaction.followup.send("You don't have permission to use this command!", ephemeral=True)
        return
    duration_seconds = 0
    duration_text = ""
    try:
        if duration.endswith('s'):
            duration_seconds = int(duration[:-1])
            duration_text = f"{duration_seconds} second{'s' if duration_seconds != 1 else ''}"
        elif duration.endswith('m'):
            duration_seconds = int(duration[:-1]) * 60
            minutes = int(duration[:-1])
            duration_text = f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif duration.endswith('h'):
            duration_seconds = int(duration[:-1]) * 3600
            hours = int(duration[:-1])
            duration_text = f"{hours} hour{'s' if hours != 1 else ''}"
        elif duration.endswith('d'):
            duration_seconds = int(duration[:-1]) * 86400
            days = int(duration[:-1])
            duration_text = f"{days} day{'s' if days != 1 else ''}"
        elif duration.endswith('w'):
            duration_seconds = int(duration[:-1]) * 604800
            weeks = int(duration[:-1])
            duration_text = f"{weeks} week{'s' if weeks != 1 else ''}"
        else:
            await interaction.followup.send("Invalid duration format! Use s for seconds, m for minutes, h for hours, d for days, or w for weeks.", ephemeral=True)
            return
        if duration_seconds < 1 or duration_seconds > 2419200:
            await interaction.followup.send("Duration must be between 1 second and 28 days!", ephemeral=True)
            return
        timeout_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration_seconds)
        await user.timeout(timeout_until, reason=f"Timed out by {interaction.user.name}: {reason}")
        embed = discord.Embed(
            title="⏰ User Timed Out",
            color=0xffff00,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Timed Out By", value=interaction.user.mention, inline=True)
        embed.add_field(name="Duration", value=duration_text, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Until", value=f"<t:{int(timeout_until.timestamp())}:R>", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.followup.send(embed=embed)
        try:
            dm_embed = discord.Embed(
                title="⏰ You have been timed out",
                description=f"You have been **timed out** in **{interaction.guild.name}**",
                color=0xffff00,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Server", value=interaction.guild.name, inline=True)
            dm_embed.add_field(name="Duration", value=duration_text, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Timed Out By", value=f"{interaction.user.name} ({interaction.user.id})", inline=True)
            dm_embed.add_field(name="Until", value=f"<t:{int(timeout_until.timestamp())}:F>", inline=True)
            dm_embed.add_field(name="Time Remaining", value=f"<t:{int(timeout_until.timestamp())}:R>", inline=True)
            dm_embed.set_footer(text="You will be able to send messages again when the timeout expires")
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            pass
        except Exception:
            pass
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to timeout this user!", ephemeral=True)
    except ValueError:
        await interaction.followup.send("Invalid duration format! Please use a valid number followed by s, m, h, d, or w.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An error occurred while timing out the user: {str(e)}", ephemeral=True)

@bot.tree.command(name="untimeout", description="Remove timeout from a user")
@is_council()
async def untimeout(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    """
    Remove timeout from a user.
    Only council members can use this command.
    """
    await interaction.response.defer()
    
    if user.top_role >= interaction.user.top_role:
        await interaction.followup.send("You cannot untimeout someone with a higher or equal role!", ephemeral=True)
        return
    
    if not user.timed_out:
        await interaction.followup.send("This user is not timed out!", ephemeral=True)
        return
    
    try:
        await user.timeout(None, reason=f"Timeout removed by {interaction.user.name}: {reason}")
        
        embed = discord.Embed(
            title="✅ Timeout Removed",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Removed By", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title="✅ Your timeout has been removed",
                description=f"Your timeout in **{interaction.guild.name}** has been **removed**",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Server", value=interaction.guild.name, inline=True)
            dm_embed.add_field(name="Removed By", value=f"{interaction.user.name} ({interaction.user.id})", inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Date", value=f"<t:{int(datetime.datetime.now().timestamp())}:F>", inline=True)
            dm_embed.set_footer(text="You can now send messages again in the server")
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            print(f"Could not send DM to {user.name} - DMs are closed")
        except Exception as e:
            print(f"Error sending DM to {user.name}: {e}")
            
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to remove timeout from this user!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An error occurred while removing the timeout: {str(e)}", ephemeral=True)

@bot.tree.command(name="add_report", description="Add reports to a user's count (Council only)")
@app_commands.describe(
    user="The user to add reports to",
    amount="Number of reports to add"
)
async def add_report(interaction: discord.Interaction, user: discord.Member, amount: int):
    if not has_council_permissions(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return

    if amount < 1:
        await interaction.response.send_message("Please enter a number greater than 0!", ephemeral=True)
        return

    report_counts = load_report_counts()
    user_id = str(user.id)
    
    if user_id not in report_counts['user_report_counts']:
        report_counts['user_report_counts'][user_id] = 0
    
    report_counts['user_report_counts'][user_id] += amount
    save_report_counts(report_counts)
    
    embed = discord.Embed(
        title="✅ Reports Added",
        color=0x00ff00,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Reports Added", value=str(amount), inline=True)
    embed.add_field(name="New Report Count", value=str(report_counts['user_report_counts'][user_id]), inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title="📝 Reports Added",
            description=f"{amount} report(s) have been added to your count by {interaction.user.mention}",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        dm_embed.add_field(name="Reports Added", value=str(amount), inline=True)
        dm_embed.add_field(name="Your Total Reports", value=str(report_counts['user_report_counts'][user_id]), inline=True)
        await user.send(embed=dm_embed)
    except:
        pass

@bot.tree.command(name="remove_report", description="Remove reports from a user's count (Council only)")
@app_commands.describe(
    user="The user to remove reports from",
    amount="Number of reports to remove"
)
async def remove_report(interaction: discord.Interaction, user: discord.Member, amount: int):
    if not has_council_permissions(interaction.user):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return

    if amount < 1:
        await interaction.response.send_message("Please enter a number greater than 0!", ephemeral=True)
        return

    report_counts = load_report_counts()
    user_id = str(user.id)
    
    if user_id not in report_counts['user_report_counts'] or report_counts['user_report_counts'][user_id] <= 0:
        await interaction.response.send_message("This user has no reports to remove!", ephemeral=True)
        return
    
    amount = min(amount, report_counts['user_report_counts'][user_id])
    report_counts['user_report_counts'][user_id] -= amount
    save_report_counts(report_counts)
    
    embed = discord.Embed(
        title="✅ Reports Removed",
        color=0x00ff00,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Reports Removed", value=str(amount), inline=True)
    embed.add_field(name="New Report Count", value=str(report_counts['user_report_counts'][user_id]), inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title="📝 Reports Removed",
            description=f"{amount} report(s) have been removed from your count by {interaction.user.mention}",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        dm_embed.add_field(name="Reports Removed", value=str(amount), inline=True)
        dm_embed.add_field(name="Your Total Reports", value=str(report_counts['user_report_counts'][user_id]), inline=True)
        await user.send(embed=dm_embed)
    except:
        pass

@bot.tree.command(name="ticket_leaderboard", description="View the ticket closing leaderboard")
async def ticket_leaderboard(interaction: discord.Interaction):
    ticket_counts = load_ticket_counts()
    
    if not ticket_counts['user_ticket_counts']:
        await interaction.response.send_message("No ticket data available yet!", ephemeral=True)
        return
    
    sorted_users = sorted(ticket_counts['user_ticket_counts'].items(), 
                         key=lambda x: x[1], reverse=True)[:20]
    
    embed = discord.Embed(
        title="🏆 Ticket Closing Leaderboard",
        description="Top 20 ticket closers",
        color=0x5865F2,
        timestamp=datetime.datetime.now()
    )
    
    for i, (user_id, count) in enumerate(sorted_users, 1):
        user = bot.get_user(int(user_id))
        name = user.display_name if user else "Unknown User"
        avatar = user.display_avatar.url if user else "https://cdn.discordapp.com/embed/avatars/0.png"
        
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"#{i}"
        
        embed.add_field(
            name=f"{medal} {name}",
            value=f"**{count}** tickets closed",
            inline=False
        )
    
    embed.set_footer(text="Updated every 30 minutes")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="report_leaderboard", description="View the report submission leaderboard")
async def report_leaderboard(interaction: discord.Interaction):
    report_counts = load_report_counts()
    
    if not report_counts['user_report_counts']:
        await interaction.response.send_message("No report data available yet!", ephemeral=True)
        return
    
    sorted_users = sorted(report_counts['user_report_counts'].items(), 
                         key=lambda x: x[1], reverse=True)[:20]
    
    embed = discord.Embed(
        title="📊 Report Submission Leaderboard",
        description="Top 20 report submitters",
        color=0xff0000,
        timestamp=datetime.datetime.now()
    )
    
    for i, (user_id, count) in enumerate(sorted_users, 1):
        user = bot.get_user(int(user_id))
        name = user.display_name if user else "Unknown User"
        avatar = user.display_avatar.url if user else "https://cdn.discordapp.com/embed/avatars/0.png"
        
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"#{i}"
        
        embed.add_field(
            name=f"{medal} {name}",
            value=f"**{count}** reports submitted",
            inline=False
        )
    
    embed.set_footer(text="Updated every 30 minutes")
    await interaction.response.send_message(embed=embed)

@tasks.loop(minutes=30)
async def update_leaderboards():
    try:
        ticket_counts = load_ticket_counts()
        report_counts = load_report_counts()
        
        bot.ticket_leaderboard_data = ticket_counts['user_ticket_counts']
        bot.report_leaderboard_data = report_counts['user_report_counts']
        
        print("Leaderboards updated")
    except Exception as e:
        print(f"Error updating leaderboards: {e}")

@bot.tree.command(name="promo_demo", description="Analyze staff performance for promotion/demotion suggestions")
@is_council()
async def promo_demo(interaction: discord.Interaction):
    await interaction.response.defer()
    
    ticket_counts = load_ticket_counts()
    report_counts = load_report_counts()
    
    staff_role_ids = [TRIAL_ROLE_ID, HELPER_ROLE_ID, MOD_ROLE_ID, TICKET_ADMIN_ROLE_ID]
    
    guild = interaction.guild
    staff_members = []
    
    for role_id in staff_role_ids:
        role = guild.get_role(role_id)
        if role:
            staff_members.extend(role.members)
    
    staff_members = list(set(staff_members))
    
    demotion_candidates = []
    promotion_candidates = []
    
    for member in staff_members:
        user_id = str(member.id)
        tickets_closed = ticket_counts['user_ticket_counts'].get(user_id, 0)
        reports_submitted = report_counts['user_report_counts'].get(user_id, 0)
        
        member_roles = [role.id for role in member.roles]
        
        if TRIAL_ROLE_ID in member_roles:
            if tickets_closed < 5:
                demotion_candidates.append({
                    'member': member,
                    'role': 'Trial',
                    'tickets': tickets_closed,
                    'reports': reports_submitted,
                    'reason': 'Low ticket activity'
                })
            elif tickets_closed >= 15:
                promotion_candidates.append({
                    'member': member,
                    'role': 'Trial',
                    'tickets': tickets_closed,
                    'reports': reports_submitted,
                    'reason': 'High ticket activity'
                })
        
        elif HELPER_ROLE_ID in member_roles:
            if tickets_closed < 10:
                demotion_candidates.append({
                    'member': member,
                    'role': 'Helper',
                    'tickets': tickets_closed,
                    'reports': reports_submitted,
                    'reason': 'Low ticket activity'
                })
            elif tickets_closed >= 25:
                promotion_candidates.append({
                    'member': member,
                    'role': 'Helper',
                    'tickets': tickets_closed,
                    'reports': reports_submitted,
                    'reason': 'High ticket activity'
                })
        
        elif MOD_ROLE_ID in member_roles:
            if tickets_closed < 15:
                demotion_candidates.append({
                    'member': member,
                    'role': 'Mod',
                    'tickets': tickets_closed,
                    'reports': reports_submitted,
                    'reason': 'Low ticket activity'
                })
            elif tickets_closed >= 40:
                promotion_candidates.append({
                    'member': member,
                    'role': 'Mod',
                    'tickets': tickets_closed,
                    'reports': reports_submitted,
                    'reason': 'High ticket activity'
                })
    
    embed = discord.Embed(
        title="📊 Staff Performance Analysis",
        color=0x5865F2,
        timestamp=datetime.datetime.now()
    )
    
    if demotion_candidates:
        demotion_text = ""
        for candidate in demotion_candidates[:10]:
            demotion_text += f"• **{candidate['member'].name}** ({candidate['role']}) - {candidate['tickets']} tickets, {candidate['reports']} reports - {candidate['reason']}\n"
        embed.add_field(name="🔻 Demotion Candidates", value=demotion_text, inline=False)
    else:
        embed.add_field(name="🔻 Demotion Candidates", value="No demotion candidates found", inline=False)
    
    if promotion_candidates:
        promotion_text = ""
        for candidate in promotion_candidates[:10]:
            promotion_text += f"• **{candidate['member'].name}** ({candidate['role']}) - {candidate['tickets']} tickets, {candidate['reports']} reports - {candidate['reason']}\n"
        embed.add_field(name="🔺 Promotion Candidates", value=promotion_text, inline=False)
    else:
        embed.add_field(name="🔺 Promotion Candidates", value="No promotion candidates found", inline=False)
    
    embed.set_footer(text="Based on ticket and report activity")
    
    await interaction.followup.send(embed=embed)

def load_afk_data():
    try:
        with open(AFK_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {'afk_users': {}}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        default_data = {'afk_users': {}}
        try:
            with open(AFK_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2)
        except Exception as e:
            print(f"Error creating AFK data file: {e}")
        return default_data

def save_afk_data(data):
    try:
        with open(AFK_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving AFK data: {e}")

@bot.tree.command(name="afk", description="Set yourself as AFK")
@app_commands.describe(
    reason="Reason for being AFK",
    duration="Duration (e.g., 1h, 30m, 1d)"
)
async def afk(interaction: discord.Interaction, reason: str, duration: str):
    if not any(role.id == COMMUNITY_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("You need the Community role to use this command!", ephemeral=True)
        return

    try:
        duration_seconds = 0
        if duration.endswith('h'):
            duration_seconds = int(duration[:-1]) * 3600
        elif duration.endswith('m'):
            duration_seconds = int(duration[:-1]) * 60
        elif duration.endswith('d'):
            duration_seconds = int(duration[:-1]) * 86400
        else:
            await interaction.response.send_message("Invalid duration format! Use h for hours, m for minutes, or d for days.", ephemeral=True)
            return

        if duration_seconds <= 0:
            await interaction.response.send_message("Duration must be greater than 0!", ephemeral=True)
            return

        original_nickname = interaction.user.display_name
        new_nickname = f"{interaction.user.name}[AFK]"
        
        try:
            await interaction.user.edit(nick=new_nickname)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to change your nickname!", ephemeral=True)
            return
        except Exception as e:
            print(f"Error changing nickname: {e}")
            await interaction.response.send_message("Failed to change nickname. Please try again.", ephemeral=True)
            return

        try:
            afk_data = load_afk_data()
            afk_data['afk_users'][str(interaction.user.id)] = {
                'original_nickname': original_nickname,
                'reason': reason,
                'end_time': (datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)).isoformat()
            }
            save_afk_data(afk_data)
        except Exception as e:
            print(f"Error saving AFK data: {e}")
            try:
                await interaction.user.edit(nick=original_nickname)
            except:
                pass
            await interaction.response.send_message("Failed to save AFK data. Please try again.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⏸️ AFK Status Set",
            color=0xffff00,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.add_field(name="Until", value=f"<t:{int((datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)).timestamp())}:R>", inline=True)

        await interaction.response.send_message(embed=embed)

    except ValueError:
        await interaction.response.send_message("Invalid duration format! Please use a valid number followed by h, m, or d.", ephemeral=True)
    except Exception as e:
        print(f"AFK command error: {e}")
        await interaction.response.send_message("An unexpected error occurred. Please try again.", ephemeral=True)

class StaffReportModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Anonymous Staff Report")
        
        self.staff_username = discord.ui.TextInput(
            label="Staff Member Username",
            placeholder="Enter the staff member's username...",
            required=True,
            max_length=32
        )
        
        self.reason = discord.ui.TextInput(
            label="Reason for Report",
            placeholder="Explain why you're reporting this staff member...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.staff_username)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        staff_username = self.staff_username.value
        reason = self.reason.value
        
        staff_member = None
        for member in interaction.guild.members:
            if member.name.lower() == staff_username.lower() or member.display_name.lower() == staff_username.lower():
                staff_roles = [TRIAL_ROLE_ID, HELPER_ROLE_ID, MOD_ROLE_ID, TICKET_ADMIN_ROLE_ID]
                if any(role.id in staff_roles for role in member.roles):
                    staff_member = member
                    break
        
        if not staff_member:
            await interaction.response.send_message("Staff member not found or they are not a staff member!", ephemeral=True)
            return
        
        if staff_member == interaction.user:
            await interaction.response.send_message("You cannot report yourself!", ephemeral=True)
            return
        
        reports_channel = interaction.guild.get_channel(STAFF_REPORTS_CHANNEL_ID)
        if not reports_channel:
            await interaction.response.send_message("Reports channel not found!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🚨 Anonymous Staff Report",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Staff Member", value=staff_member.mention, inline=True)
        embed.add_field(name="Staff Role", value=staff_member.top_role.name, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Reported By", value="Anonymous", inline=True)
        embed.set_footer(text="Anonymous Report")
        
        await reports_channel.send(embed=embed)
        await interaction.response.send_message("Your anonymous report has been submitted successfully.", ephemeral=True)

@bot.tree.command(name="rep", description="Submit an anonymous report about a staff member")
async def report_staff(interaction: discord.Interaction):
    if not any(role.id == COMMUNITY_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("You need the Community role to use this command!", ephemeral=True)
        return
    
    await interaction.response.send_modal(StaffReportModal())

@bot.tree.command(name="mute", description="Mute a user")
@app_commands.describe(
    user="The user to mute",
    duration="Duration (e.g., 1h, 30m, 1d)",
    reason="Reason for the mute"
)
async def mute(interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
    if not (has_team_permissions(interaction.user) or has_council_permissions(interaction.user)):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return

    if user.top_role >= interaction.user.top_role:
        await interaction.response.send_message("You cannot mute someone with a higher or equal role!", ephemeral=True)
        return

    if user == interaction.user:
        await interaction.response.send_message("You cannot mute yourself!", ephemeral=True)
        return

    try:
        duration_seconds = 0
        if duration.endswith('s'):
            duration_seconds = int(duration[:-1])
        elif duration.endswith('m'):
            duration_seconds = int(duration[:-1]) * 60
        elif duration.endswith('h'):
            duration_seconds = int(duration[:-1]) * 3600
        elif duration.endswith('d'):
            duration_seconds = int(duration[:-1]) * 86400
        else:
            await interaction.response.send_message("Invalid duration format! Use s, m, h, or d.", ephemeral=True)
            return

        if duration_seconds < 1 or duration_seconds > 2419200:
            await interaction.response.send_message("Duration must be between 1 second and 28 days!", ephemeral=True)
            return

        timeout_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration_seconds)
        await user.timeout(timeout_until, reason=f"Muted by {interaction.user.name}: {reason}")

        embed = discord.Embed(
            title="🔇 User Muted",
            color=0xff8800,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Muted By", value=interaction.user.mention, inline=True)
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Until", value=f"<t:{int(timeout_until.timestamp())}:R>", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

        try:
            dm_embed = discord.Embed(
                title="🔇 You have been muted",
                description=f"You have been **muted** in **{interaction.guild.name}**",
                color=0xff8800,
                timestamp=datetime.datetime.now()
            )
            dm_embed.add_field(name="Server", value=interaction.guild.name, inline=True)
            dm_embed.add_field(name="Duration", value=duration, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Muted By", value=f"{interaction.user.name} ({interaction.user.id})", inline=True)
            dm_embed.add_field(name="Until", value=f"<t:{int(timeout_until.timestamp())}:F>", inline=True)
            dm_embed.set_footer(text="You will be able to send messages again when the mute expires")
            await user.send(embed=dm_embed)
        except:
            pass

    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to mute this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while muting the user: {str(e)}", ephemeral=True)

@tasks.loop(minutes=1)
async def check_afk_status():
    try:
        afk_data = load_afk_data()
        current_time = datetime.datetime.now()
        
        for user_id, data in list(afk_data['afk_users'].items()):
            try:
                end_time = datetime.datetime.fromisoformat(data['end_time'])
                if current_time >= end_time:
                    guild = bot.guilds[0] if bot.guilds else None
                    if guild:
                        user = guild.get_member(int(user_id))
                        if user:
                            try:
                                await user.edit(nick=data['original_nickname'])
                                del afk_data['afk_users'][user_id]
                                save_afk_data(afk_data)
                                
                                embed = discord.Embed(
                                    title="✅ AFK Status Removed",
                                    description=f"{user.mention} is no longer AFK",
                                    color=0x00ff00,
                                    timestamp=datetime.datetime.now()
                                )
                                await guild.system_channel.send(embed=embed) if guild.system_channel else None
                            except:
                                pass
            except Exception as e:
                print(f"Error processing AFK for user {user_id}: {e}")
                continue
    except Exception as e:
        print(f"Error in check_afk_status task: {e}")

LEVEL_DATA_FILE = 'level_data.json'
LEVEL_ANNOUNCE_CHANNEL_ID = 1390755666657808455
LEVEL_ROLE_5 = 1390755746303578355
LEVEL_ROLE_10 = 1390756100382527488
LEVEL_ROLE_15 = 1390757114653315153
LEVEL_ROLE_20 = 1390757197872500892
LEVEL_ROLE_25 = 1390759194512195755
ECHO_ROLE_ID = 1390759311613100173
LEVEL_ROLE_30 = 1390759311613100173
LEVEL_ROLE_35 = 1390759468089999420
LEVEL_ROLE_40 = 1390759758436499516
LEVEL_ROLE_45 = 1390759828296569023
LEVEL_ROLE_50 = 1390760197034610759

import threading

def load_level_data():
    try:
        with open(LEVEL_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        default_data = {}
        try:
            with open(LEVEL_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2)
        except Exception as e:
            print(f"Error creating level data file: {e}")
        return default_data

def save_level_data(data):
    try:
        with open(LEVEL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving level data: {e}")

async def give_level_role(member, level):
    role_map = {
        5: LEVEL_ROLE_5,
        10: LEVEL_ROLE_10,
        15: LEVEL_ROLE_15,
        20: LEVEL_ROLE_20,
        25: LEVEL_ROLE_25,
        30: LEVEL_ROLE_30,
        35: LEVEL_ROLE_35,
        40: LEVEL_ROLE_40,
        45: LEVEL_ROLE_45,
        50: LEVEL_ROLE_50
    }
    if level in role_map:
        role = member.guild.get_role(role_map[level])
        if role and role not in member.roles:
            await member.add_roles(role)
    if level == 50:
        echo_role = member.guild.get_role(ECHO_ROLE_ID)
        if echo_role and echo_role not in member.roles:
            await member.add_roles(echo_role)
            async def remove_echo_role_later():
                await asyncio.sleep(2592000)
                if echo_role in member.roles:
                    await member.remove_roles(echo_role)
            asyncio.create_task(remove_echo_role_later())

async def announce_level_up(member, level):
    channel = member.guild.get_channel(LEVEL_ANNOUNCE_CHANNEL_ID)
    if channel:
        await channel.send(f"{member.mention} reached level {level}!")

def get_xp_needed(level):
    if level < 10:
        return 200 + (level - 1) * 50
    elif level < 20:
        return 1000 + (level - 10) * 250
    elif level < 30:
        return 3500 + (level - 20) * 1000
    elif level < 40:
        return 13500 + (level - 30) * 2500
    elif level < 50:
        return 38500 + (level - 40) * 5000
    else:
        return 88500

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    afk_data = load_afk_data()
    excluded_channels = [
        DISCUSSION_CHANNEL_ID,
        CHAT_CHANNEL_ID,
        APPLICATIONS_CHANNEL_ID,
        LOA_CHANNEL_ID,
        STAFF_MOVEMENT_CHANNEL_ID,
        LIVE_ANNOUNCEMENT_CHANNEL_ID,
        EVIDENCE_CHANNEL_ID,
    ]
    if str(message.author.id) in afk_data['afk_users'] and message.channel.id not in excluded_channels:
        try:
            data = afk_data['afk_users'][str(message.author.id)]
            await message.author.edit(nick=data['original_nickname'])
            del afk_data['afk_users'][str(message.author.id)]
            save_afk_data(afk_data)
            embed = discord.Embed(
                title="✅ Welcome Back!",
                description=f"{message.author.mention} is no longer AFK",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            await message.channel.send(embed=embed)
        except:
            pass
    for mention in message.mentions:
        user_id = str(mention.id)
        if user_id in afk_data['afk_users']:
            data = afk_data['afk_users'][user_id]
            end_time = datetime.datetime.fromisoformat(data['end_time'])
            time_remaining = end_time - datetime.datetime.now()
            if time_remaining.total_seconds() > 0:
                embed = discord.Embed(
                    title="⏸️ User is AFK",
                    description=f"{mention.mention} is currently AFK",
                    color=0xffff00,
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="Reason", value=data['reason'], inline=True)
                embed.add_field(name="Time Remaining", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
                embed.set_thumbnail(url=mention.display_avatar.url)
                await message.channel.send(embed=embed, delete_after=10)
    level_data = load_level_data()
    user_id = str(message.author.id)
    if user_id not in level_data:
        level_data[user_id] = {"xp": 0, "level": 1, "echo_time": None}
    level = level_data[user_id]["level"]
    xp = level_data[user_id]["xp"]
    if level < 10:
        gain = 10
    elif level < 20:
        gain = 5
    elif level < 30:
        gain = 2
    elif level < 40:
        gain = 1
    elif level < 50:
        gain = 1
    else:
        gain = 0
    if level < 50:
        level_data[user_id]["xp"] += gain
        xp_needed = get_xp_needed(level)
        while level_data[user_id]["xp"] >= xp_needed and level < 50:
            level_data[user_id]["xp"] -= xp_needed
            level += 1
            level_data[user_id]["level"] = level
            asyncio.create_task(give_level_role(message.author, level))
            asyncio.create_task(announce_level_up(message.author, level))
            xp_needed = get_xp_needed(level)
            if level == 50:
                level_data[user_id]["echo_time"] = (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
    save_level_data(level_data)
    await bot.process_commands(message)

@tasks.loop(minutes=10)
async def check_echo_roles():
    await bot.wait_until_ready()
    level_data = load_level_data()
    for user_id, data in list(level_data.items()):
        if data.get("level") == 50 and data.get("echo_time"):
            try:
                end_time = datetime.datetime.fromisoformat(data["echo_time"])
                if datetime.datetime.now() >= end_time:
                    for guild in bot.guilds:
                        member = guild.get_member(int(user_id))
                        if member:
                            echo_role = guild.get_role(ECHO_ROLE_ID)
                            if echo_role and echo_role in member.roles:
                                await member.remove_roles(echo_role)
                    data["echo_time"] = None
            except:
                pass
    save_level_data(level_data)

@bot.tree.command(name="whois", description="Get information about a user")
@app_commands.describe(user="The user to get information about")
async def whois(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    
    level_data = load_level_data()
    user_id = str(user.id)
    user_level_data = level_data.get(user_id, {"level": 1, "xp": 0})
    
    embed = discord.Embed(
        title=f"User Information",
        color=user.color if user.color != discord.Color.default() else 0x5865F2,
        timestamp=datetime.datetime.now()
    )
    
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Name", value=user.name, inline=True)
    embed.add_field(name="Display Name", value=user.display_name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Account Created", value=f"<t:{int(user.created_at.timestamp())}:F>", inline=True)
    embed.add_field(name="Joined Server", value=f"<t:{int(user.joined_at.timestamp())}:F>", inline=True)
    embed.add_field(name="Level", value=f"{user_level_data['level']}", inline=True)
    
    roles = [role for role in user.roles if role.name != "@everyone"]
    if roles:
        roles_text = ""
        for role in roles:
            roles_text += f"<@&{role.id}> "
        roles_text = roles_text.strip()
        if len(roles_text) > 1024:
            roles_text = roles_text[:1021] + "..."
    else:
        roles_text = "No roles"
    
    embed.add_field(name="Roles", value=roles_text, inline=False)
    
    if user.activity:
        activity_type = str(user.activity.type).split('.')[-1].title()
        embed.add_field(name="Activity", value=f"{activity_type}: {user.activity.name}", inline=True)
    
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)  