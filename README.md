# Copier [**__`INVITE`__**](https://discord.com/oauth2/authorize?client_id=1281304101715710022)

A bot that lets you copy things, just like how you can copy channels in Discord.

### Prefix: 'copier ' or mention!
Use `copier help` to view every category & their commands.

## Self-host
1. Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications).
2. Invite the bot to your server. It needs the `bot` scope and either `Manage Channels` or `Administrator` permission. `Manage Channels` will not allow the bot to see channels it doesn't have access to, so `Administrator` is recommended.
3. Reset and copy the bot's token.
4. Clone the repository.
5. Replace `<token-here>` with the bot's token in the `.env` file.
6. If you want to, create a virtual environment with `pip install virtualenv && python -m venv env` and run the corresponding file for your OS.
   - On Windows: `env/Scripts/activate.bat` (Command line) or `env/Scripts/Activate.ps1` (PowerShell)
   - On Linux & Mac: `source env/bin/activate`
7. Install prerequisites with `pip install -r requirements.txt`.
8. Run the bot with `python3 bot.py`.

The code is under The Unlicense license, feel free to do anything you want with it.
