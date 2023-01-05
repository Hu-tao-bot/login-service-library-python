import discord
from redis import asyncio as aioredis
import json

from discord import WebhookMessage, app_commands
from discord.ext import commands
from discord.http import Route

from logingateway import HuTaoLoginAPI
from logingateway.api import HuTaoLoginRESTAPI
from logingateway.model import Player, Ready

class LoginGatewayCog(commands.Cog):
    CLIENT_ID = "abc1234"
    CLIENT_SECRET = "abc1234"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.prefix = "htlogin"
        self.redis = aioredis.from_url(
            url="redis://localhost:6379"
        )
        self.gateway = HuTaoLoginAPI(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET
        )
        self.rest = HuTaoLoginRESTAPI(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET
        )
        
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
        interaction = await self.redis.get(":".join([self.prefix,data.token]))
        if interaction is None:
            return

        # Recieved data
        print(data.genshin)

        # Send if success
        js = json.loads(interaction)
        routes = Route("PATCH", "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}".format(
            webhook_id=self.bot.application.id,
            webhook_token=js["webhook_token"],
            message_id=js["message_id"]
        ))
        await self.bot.http.request(routes, json={
            "content": "🎉 Success to login genshin",
            "components": []
        })

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

        expire = 60 * 60

        message: WebhookMessage = await interaction.followup.send(f"Please login genshin to verify login via button\n\nURL Expire in 1 Hour", view=view)
        await self.redis.set(":".join([self.prefix, token]), json.dumps({
            "webhook_token": interaction.token,
            "message_id": message.id,
        }), ex=expire)
    
    @app_commands.command(name="reload", description="Reload Redeem token")
    async def reload(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        new_cookie = await self.reload_cookies(str(interaction.user.id))
        if new_cookie is None:
            await interaction.edit_original_response(content="Failed to reload redeem token, login using mail type setup")
        else:
            await interaction.edit_original_response(content="Successfull to reload redeem token")

async def setup(client: commands.Bot):
    await client.add_cog(LoginGatewayCog(client))