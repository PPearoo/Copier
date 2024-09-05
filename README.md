# CopyCategory
A bot that lets you copy categories, just like how you can copy channels in Discord.

I might add other things to copy as well (roles, channel overwrites, etc.) but for now it's just categories.

## Usage
1. Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications).
2. Invite the bot to your server. It needs the `bot` scope and either `Manage Channels` or `Administrator` permissions. `Manage Channels` will not allow the bot to see channels it doesn't have access to, so `Administrator` is recommended.
3. Reset and copy the bot's token.
4. Clone the repository.
5. Replace `<token-here>` with the bot's token in the `.env` file.
6. Install prerequisites with `pip install -r requirements.txt`.
7. Run the bot with `python3 bot.py`.

The code is under The Unlicense license, feel free to do anything you want with it.

### Prefix: 'copy ' or mention!
- `copy category [roles] [new_name]` Clones the current category and all its channels.
    
    `roles` - Optional. A list of roles to give access to the new category. Seperate them with spaces.
    
    `new_name` - Optional. The name of the new category.
    
    -# Note: The category will be private if you specify any roles, but visually, the switch for 'private category' will be off. This is a discord limitation, but the category will still be private.`

- `copy delete` Deletes the category that the command is used in, and all its channels.

- `copy nuke` Deletes the current channel and clones it.