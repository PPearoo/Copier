import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import platform

load_dotenv()

bot = commands.Bot(command_prefix=commands.when_mentioned_or("copier "), intents=discord.Intents.all())

class Help(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(
            title="Help",
            url="https://github.com/rnxm/copier",
            description=f"Use `{ctx.clean_prefix} help [command]` for more information on a command.",
            color=discord.Color.blurple()
        )
        for cog, commands in mapping.items():
            for command in commands:
                if command.hidden:
                    continue
                embed.add_field(
                    name=ctx.clean_prefix + command.qualified_name,
                    value=command.short_doc,
                    inline=False
                )
        await ctx.send(embed=embed)
    
    async def send_group_help(self, group: commands.Group):
        ctx = self.context
        embed = discord.Embed(
            title=group.name.capitalize(),
            url="https://github.com/rnxm/copier",
            description=group.help,
            color=discord.Color.blurple()
        )
        for command in group.commands:
            if command.hidden:
                continue
            embed.add_field(
                name=ctx.clean_prefix + (command.usage or command.qualified_name),
                value=command.short_doc,
                inline=False
            )
        await ctx.send(embed=embed)
    
    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        embed = discord.Embed(
            title=command.usage or ctx.clean_prefix + command.qualified_name,
            url="https://github.com/rnxm/copier",
            description=command.help,
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)

async def update_status(bot: commands.Bot):
    print(f"Updating status to {len(bot.guilds)} servers")
    await bot.change_presence(activity=discord.CustomActivity(name=f"{len(bot.guilds)} servers"), status=discord.Status.online)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} with {len(bot.commands)} commands.")
    await update_status(bot)

@bot.event
async def on_guild_join(guild: discord.Guild):
    await update_status(bot)

@bot.event
async def on_guild_remove(guild: discord.Guild):
    await update_status(bot)

@bot.before_invoke
async def before_invoke(ctx: commands.Context):
    try:
        await ctx.message.add_reaction("<a:loading:1325859336857059379>")
    except discord.HTTPException:
        pass

@bot.after_invoke
async def after_invoke(ctx: commands.Context):
    try:
        await ctx.message.remove_reaction("<a:loading:1325859336857059379>", ctx.me)
        # we specify that we want to remove the reaction from the bot
    except discord.HTTPException:
        pass

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You need the following permission(s) to run this command: `{', '.join(error.missing_perms)}`")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"I need the following permission(s) to run this command: `{', '.join(error.missing_perms)}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send_help(ctx.command)
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send_help(ctx.command)
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("Man, come on. You can't use this command in DMs.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You don't have permission to run this command.")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("I don't have permission perform this action. Some of the command may have already run though.")
    else:
        await ctx.send(f"An error occurred. `{error}`\nYou can report this error by opening an issue [here](https://github.com/rnxm/Copier/issues)")
        raise error

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"An error occurred in the {event} event.\nargs: {args}\nkwargs: {kwargs}\n")
    raise

@bot.group(name="category", invoke_without_command=True)
async def category(ctx: commands.Context):
    """Utilities for categories. Because Discord is too lazy to add a clone feature."""
    if ctx.invoked_subcommand is None:
        await ctx.send_help("category")

@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
@category.command(name="clone", usage="category clone [roles] [new_name]", aliases=["copy"])
async def category_clone(ctx: commands.Context, roles: commands.Greedy[discord.Role] = None, *, new_name: str = None):
    """Clones the current category and all its channels.
    
    `roles` - Optional. A list of roles to give access to the new category. Seperate them with spaces.
    
    `new_name` - Optional. The name of the new category.
    
    **Aliases:** `copy`, `clone`
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

    category: discord.CategoryChannel = await parent.clone(
        name=name,
        reason=f"Copy {parent.name} - {ctx.author.id}"
    )
    await category.edit(overwrites=overwrites)
    
    await category.move(after=parent, sync_permissions=True)
    
    for channel in parent.channels:
        channel: discord.abc.GuildChannel
        
        emojis = {
            discord.TextChannel: "💬",
            discord.VoiceChannel: "🔊",
            discord.StageChannel: "🎙️",
            discord.ForumChannel: "📚"
        }
        
        cloned = await channel.clone(reason=f"Copy {parent.name} / {emojis[type(channel)]} {channel.name} | {ctx.author.id}")
        await msg.edit(content=f"Created channel {cloned.mention}...")
        await cloned.move(category=category, end=True, sync_permissions=True)
        await msg.edit(content=f"Moved channel {cloned.mention}...")

    await msg.edit(content=f"The new channels are available in `{category.name}`. You can delete them with the `copy delete` command.\n-# Only use the `copy delete` command in the channel that you want to delete the category of!!!", delete_after=30)
    await asyncio.sleep(30)
    await ctx.message.delete()

@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
@category.command(name="delete")
async def category_delete(ctx: commands.Context):
    """Deletes the category that the command is used in, and all its channels."""
    category: discord.CategoryChannel = ctx.channel.category
    if category is None:
        return await ctx.send("This channel is not in a category")
    
    for i in category.channels:
        await i.delete(reason=f"Delete {category.name} - {ctx.author.id}")
    await category.delete(reason=f"Delete {category.name} - {ctx.author.id}")

@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
@category.command(name="nuke")
async def category_nuke(ctx: commands.Context):
    """A shorthand for deleting and cloning a category."""
    await ctx.invoke(category_clone)
    await ctx.invoke(category_delete)

@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
@category.command(name="clear")
async def category_clear(ctx: commands.Context):
    """Deletes all channels in the category that the command is used in."""
    category: discord.CategoryChannel = ctx.channel.category
    if category is None:
        return await ctx.send("This channel is not in a category")
    
    for i in category.channels:
        await i.delete(reason=f"Delete {category.name} - {ctx.author.id}")
    await ctx.send(f"Channels in `{category.name}` deleted.")
    
@commands.guild_only()
@bot.group(name="channel", invoke_without_command=True)
async def channel(ctx: commands.Context):
    """Utilities for channels."""
    if ctx.invoked_subcommand is None:
        await ctx.send_help("channel")

@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
@channel.command(name="clone", usage="channel clone [roles] [new_name]", aliases=["copy"])
async def channel_clone(ctx: commands.Context, roles: commands.Greedy[discord.Role] = None, *, new_name: str = None):
    """Clones the current channel.
    
    `roles` - Optional. A list of roles to give access to the new channel. Seperate them with spaces.
    
    `new_name` - Optional. The name of the new channel.
    
    **Aliases:** `copy`, `clone`
    """
    channel: discord.abc.GuildChannel = ctx.channel
    overwrites = channel.overwrites
    if roles:
        overwrites = {
            role: discord.PermissionOverwrite(
                read_messages=True,
                connect=True
            )
            for role in roles
        }

    cloned = await channel.clone(
        name=new_name or channel.name,
        reason=f"Copy {channel.name} - {ctx.author.id}"
    )
    await cloned.edit(overwrites=overwrites)
    
    await ctx.send(f"Channel `{cloned.name}` created. {cloned.mention}")

@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
@channel.command(name="delete", usage="channel delete [channel]")
async def channel_delete(ctx: commands.Context, channel: discord.TextChannel = None):
    """Deletes the current channel or the specified channel.
    
    `channel` - Optional. The channel to delete. Can be a channel ID.
    """
    channel = channel or ctx.channel
    try:
        channel = await commands.TextChannelConverter().convert(ctx, str(channel))
    except commands.BadArgument:
        return await ctx.send("Channel not found.")
    
    await channel.delete(reason=f"Delete channel - {ctx.author.id}")

@commands.has_permissions(manage_channels=True)
@commands.bot_has_permissions(manage_channels=True)
@channel.command(name="nuke")
async def channel_nuke(ctx: commands.Context):
    """A shorthand for cloning and deleting a channel."""
    await ctx.invoke(channel_clone)
    await ctx.invoke(channel_delete)

@commands.guild_only()
@bot.group(name="role", invoke_without_command=True)
async def role(ctx: commands.Context):
    """Utilities for roles. Because Discord is too lazy to add a clone feature to them."""
    if ctx.invoked_subcommand is None:
        await ctx.send_help("role")

@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
@role.command(name="clone", usage="role clone [role] [new_color] [new_name]", aliases=["copy"])
async def role_clone(ctx: commands.Context, role: discord.Role, new_color: str = None, *, new_name: str = None):
    """Clones a role.
    
    `role` - The role to clone.
    
    `new_color` - Optional. The color of the new role. Must be a hex code and must start with a `#`.
    
    `new_name` - Optional. The name of the new role.
    
    **Aliases:** `copy`, `clone`
    """
    if new_color and not new_color.startswith("#"):
        new_name = new_color + " " + new_name if new_name else new_color if new_color else None
        new_color = None
    elif not new_color:
        new_color = None
    elif new_color and new_color.startswith("#"):
        try:
            new_color = await commands.ColorConverter().convert(ctx, new_color)
        except commands.BadArgument:
            return await ctx.send("Invalid color. Must be a hex code and must start with a `#`.")
    new_role = await ctx.guild.create_role(
        name=new_name or role.name,
        color=new_color or role.color,
        permissions=role.permissions,
        hoist=role.hoist,
        mentionable=role.mentionable,
        reason=f"Copy {role.name} - {ctx.author.id}"
    )
    extras = ""
    if role.position < ctx.me.top_role.position:
        new_role = await new_role.edit(
            position=role.position - 1 if role.position > 1 else 1
        )
    else:
        extras = "I couldn't move it below the existing role, though, because it is above my top role. You can find it below my top role."
        new_role = await new_role.edit(
            position=ctx.me.top_role.position - 1 if ctx.me.top_role.position > 1 else 1
        )
    
    await ctx.send(f"Role `{new_role.name}` created. {extras}\n{new_role.mention}")

@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
@role.command(name="delete", usage="role delete [role]")
async def role_delete(ctx: commands.Context, role: discord.Role):
    """Deletes a role.
    
    `role` - The role to delete.
    """
    try:
        role = await commands.RoleConverter().convert(ctx, str(role))
    except commands.BadArgument:
        return await ctx.send("Role not found.")
    if role.is_default():
        return await ctx.send("You cannot delete the everyone role.")
    if role.is_premium_subscriber():
        return await ctx.send("You cannot delete the premium subscriber role.")
    if role.managed or role.is_bot_managed():
        return await ctx.send("You cannot delete an integration's role.")
    if role.position >= ctx.me.top_role.position:
        return await ctx.send("I cannot delete a role that is above my top role.")
    
    await role.delete(reason=f"Delete {role.name} - {ctx.author.id}")
    await ctx.send(f"Role `{role.name}` deleted.")

@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
@role.command(name="nuke", usage="role nuke [role]")
async def role_nuke(ctx: commands.Context, role: discord.Role):
    """Nukes a role by cloning it and deleting the original. This should be used if you want to remove a role from everyone.
    
    `role` - The role to nuke. Can be a role ID.
    """
    await ctx.invoke(role_clone, role)
    await ctx.invoke(role_delete, role)

bot.help_command = Help()
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

bot.run(os.getenv("TOKEN"))