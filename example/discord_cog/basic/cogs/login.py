import discord

from typing import Dict

from discord import WebhookMessage, app_commands
from discord.ext import commands

from logingateway import HuTaoLoginAPI
from logingateway.api import HuTaoLoginRESTAPI
from logingateway.model import Player, Ready

class LoginGatewayCog(commands.Cog):
    CLIENT_ID = "abc1234"
    CLIENT_SECRET = "abc1234"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.gateway = HuTaoLoginAPI(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET
        )
        self.rest = HuTaoLoginRESTAPI(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET
        )

        self.tokenStore: Dict[str, WebhookMessage] = {}
        

        
        # Event
        self.gateway.ready(self.gateway_connect)
        self.gateway.player(self.gateway_player)
        self.gateway.player_update(self.gateway_player_update)
        
        # Start gateway
        print("Connecting to Hu Tao Gateway")
        self.gateway.start()

    async def cog_unload(self) -> None:
        self.gateway.close()

    async def gateway_connect(self, data: Ready):
        print("Connected to Hu Tao Gateway")

    async def gateway_player_update(self, data: Player):
        # Recieved data
        print(data.genshin)

    async def gateway_player(self, data: Player):
        if not data.token in self.tokenStore:
            return

        ctx = self.tokenStore[data.token]

        # Recieved data
        print(data.genshin)

        # Send if success
        await ctx.edit(content="🎉 Success to login genshin")
    
    async def reload_cookies(self, id:str):
        async with self.rest as rest:
            history  = await rest.get_history_user(id,login_type='mail')
            if history.data is not []:
                token = history.data[0].token
            else:
                return None
            new_cookie=await rest.reload_new_cookie(id,token)
            return new_cookie

    @app_commands.command(name="login", description="Login Genshin account")
    async def login(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        url, token = self.gateway.generate_login_url(
            user_id=str(interaction.user.id),
            guild_id=str(interaction.guild_id),
            channel_id=str(interaction.channel_id),
            language="en"
        )

        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            url=url,
            label="Login Genshin account"
        ))

        message = await interaction.followup.send(f"Please login genshin to verify login via button", view=view)
        self.tokenStore[token] = message
    
    @app_commands.command(name="reload", description="Reload redeem token")
    async def reload(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        new_cookie = await self.reload_cookies(str(interaction.user.id))
        if new_cookie is not None:
            await interaction.edit_original_response(content="Success to reload redeem token")
        else:
            await interaction.edit_original_response(content="Failed to reload redeem token , please login using mail type setup")

async def setup(client: commands.Bot):
    await client.add_cog(LoginGatewayCog(client))