import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

bot = commands.Bot(command_prefix=commands.when_mentioned_or("copy "), intents=discord.Intents.all())

class Help(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(
            title="Help",
            description="This bot is used to clone categories and their channels.",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="Commands",
            value="`copy category [roles] [new_name]` - Clones the current category and all its channels.\n\n`copy delete` - Deletes the current category and all its channels.\n\n`copy nuke` - Deletes the current channel and clones it."
        )
        await ctx.send(embed=embed)
    
    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        embed = discord.Embed(
            title=command.usage if command.usage else "copy " + command.name,
            description=command.help,
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)

bot.help_command = Help()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@commands.has_permissions(manage_channels=True)
@bot.command(usage="copy category [roles] [new_name]")
async def category(ctx: commands.Context, roles: commands.Greedy[discord.Role] = None, *, new_name: str = None):
    """Clones the current category and all its channels.
    
    `roles` - Optional. A list of roles to give access to the new category. Seperate them with spaces.
    
    `new_name` - Optional. The name of the new category.
    
    -# Note: The category will be private if you specify any roles, but visually, the switch for 'private category' will be off. This is a discord limitation, but the category will still be private.
    """
    parent: discord.CategoryChannel = ctx.channel.category
    if parent is None:
        return await ctx.send("This channel is not in a category")
    
    msg: discord.Message = await ctx.send("This process will create channels inside the current category, create a new category, and move the channels there. Don't be alarmed.")

    overwrites = parent.overwrites
    if roles:
        overwrites = {
            role: discord.PermissionOverwrite(
                read_messages=True,
                connect=True
            )
            for role in roles
        }
    name = new_name or parent.name

    category: discord.CategoryChannel = await ctx.channel.category.clone(
        name=name,
        reason=f"Copy {ctx.channel.category.name} - {ctx.author.id}"
    )
    await category.edit(overwrites=overwrites)
    
    for channel in parent.channels:
        channel: discord.abc.GuildChannel
        
        emojis = {
            discord.TextChannel: "💬",
            discord.VoiceChannel: "🔊",
            discord.StageChannel: "🎙️",
            discord.ForumChannel: "📚"
        }
        
        cloned = await channel.clone(reason=f"Copy {ctx.channel.category.name} / {emojis[type(channel)]} {channel.name} | {ctx.author.id}")
        await msg.edit(content=f"Created channel {cloned.mention}...")
        await cloned.move(category=category, end=True, sync_permissions=True)
        await msg.edit(content=f"Moved channel {cloned.mention}...")

    await msg.edit(content=f"The new channels are available in `{category.name}`. You can delete them with the `copy delete` command.\n-# Only use the `copy delete` command in the channel that you want to delete the category of!!!", delete_after=30)
    await asyncio.sleep(30)
    await ctx.message.delete()

@commands.has_permissions(manage_channels=True)
@bot.command()
async def delete(ctx: commands.Context):
    """Deletes the category that the command is used in, and all its channels."""
    category: discord.CategoryChannel = ctx.channel.category
    if category is None:
        return await ctx.send("This channel is not in a category")
    
    for i in category.channels:
        await i.delete(reason=f"Delete {category.name} - {ctx.author.id}")
    await category.delete(reason=f"Delete {category.name} - {ctx.author.id}")
    await ctx.author.send(f"Deleted category `{category.name}`.")

@commands.has_permissions(manage_channels=True)
@bot.command()
async def nuke(ctx: commands.Context):
    """Deletes the current channel and clones it."""
    
    cloned = await ctx.channel.clone(reason=f"Nuke channel - {ctx.author.id}")
    await cloned.move(category=ctx.channel.category, before=ctx.channel)
    await ctx.channel.delete(reason=f"Nuke channel - {ctx.author.id}")
    await cloned.send(f"Channel nuked by {ctx.author.mention}.", allowed_mentions=discord.AllowedMentions.none())

bot.run(os.getenv("TOKEN"))