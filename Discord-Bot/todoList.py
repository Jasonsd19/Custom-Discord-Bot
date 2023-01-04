from discord.ext import tasks, commands
import redis
import json


class todoList(commands.Cog):
    # Handles various todo lists
    def __init__(self, bot, db) -> None:
        self.bot = bot
        self.db = db
