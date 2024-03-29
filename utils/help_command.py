from typing import List, Mapping, NamedTuple, Optional

import discord
from discord.ext import commands, menus
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import Command, Group

__all__ = ("CustomHelp",)

BotHelp = NamedTuple("BotHelp", [("cog", Cog), ("commands", List[Command])]) # Use a NamedTuple for easier to read typehinting

class HelpPaginator(menus.MenuPages):
    def __init__(self, source, **kwargs):
        super().__init__(source, **kwargs)

class BotHelpSource(menus.ListPageSource):
    def __init__(self, entries, *, per_page=5):
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, entries: List[BotHelp]):

        embed = discord.Embed(
                color=menu.ctx.bot.color,
                title="Help"
            )
        
        if self.get_max_pages() > 0:

            embed.set_footer(
                text=f"Page {menu.current_page+1} / {self.get_max_pages()}"
            )
        
        for cog, commands in entries:

            embed.add_field(
                name=cog.qualified_name, value = "".join(f" `{cmd.name}`" for cmd in commands)
            )

        return embed

class GroupHelpSource(menus.ListPageSource):
    def __init__(self, entries, *, per_page=5, group: Group):
        super().__init__(entries, per_page=per_page)
        self.group = group
    
    async def format_page(self, menu: menus.Menu, page: List[Command]):
        
        embed = discord.Embed(
                color=menu.ctx.bot.color,
                title=f"Help for `{self.group.name}`"
            )
        
        if self.get_max_pages() > 0:

            embed.set_footer(
                text=f"Page {menu.current_page+1} / {self.get_max_pages()}"
            )
        
        for command in page:

            value = (
                f"{' '.join(f'`{alias}`' for alias in command.aliases)} \n"
                f"{command.help or 'No Help'}"
            )

            embed.add_field(
                name=command.name, value=value
            )

        return embed

class CogHelpSource(menus.ListPageSource):
    def __init__(self, entries, *, per_page=5, cog: Cog):
        super().__init__(entries, per_page=per_page)
        self.cog = cog
    
    async def format_page(self, menu: menus.Menu, page: List[Command]):
        
        embed = discord.Embed(
                color=menu.ctx.bot.color,
                title=f"Help for `{self.cog.qualified_name}`"
            )
        
        if self.get_max_pages() > 0:

            embed.set_footer(
                text=f"Page {menu.current_page+1} / {self.get_max_pages()}"
            )
        
        for command in page:

            value = (
                f"{' '.join(f'`{alias}`' for alias in command.aliases)} \n"
                f"{command.help or 'No Help'}"
            )

            embed.add_field(
                name=command.name, value=value
            )

        return embed
class CustomHelp(commands.HelpCommand):
    def __init__(self, **options):

        attrs = {
            "hidden": True
        }

        super().__init__(command_attrs=attrs, **options)
    
    async def send_bot_help(self, mapping: Mapping[Optional[Cog], List[Command]]):

        filtered_commands: List[BotHelp] = []

        for cog, commands in mapping.items():

            filtered = await self.filter_commands(commands)

            if filtered:
                filtered_commands.append(BotHelp(cog, commands))

        menu = HelpPaginator(BotHelpSource(filtered_commands, per_page=4))
        await menu.start(self.context)
    
    async def send_group_help(self, group: Group):
        
        filtered = await self.filter_commands(group.commands)

        if not filtered: # no unfiltered commands, so don't start the menu
            return await self.get_destination().send("Command not found. You may not have the proper permissions to see the command.") 

        menu = HelpPaginator(GroupHelpSource(filtered, group=group))
        await menu.start(self.context)
    
    async def send_cog_help(self, cog: Cog):
        filtered = await self.filter_commands(cog.get_commands())

        if not filtered: # no unfiltered commands, so don't start the menu
            return await self.get_destination().send("Command not found. You may not have the proper permissions to see the command.") 

        menu = HelpPaginator(CogHelpSource(filtered, cog=cog))
        await menu.start(self.context)
    
    async def send_command_help(self, command: commands.Command):

        if not await self.filter_commands([command]):
            return
        
        embed = discord.Embed(
            title=f"Help for {command.name}", color=self.context.bot.color
            )

        embed.add_field(
            name="Help", value=command.help or "No Help", inline=False
        ).add_field(
            name="Aliases", value=" ".join(f"`{alias}`" for alias in command.aliases) or "None", inline=False
        ).add_field(
            name="Arguments", value=command.signature or "None"
        )

        await self.get_destination().send(embed=embed)
        

