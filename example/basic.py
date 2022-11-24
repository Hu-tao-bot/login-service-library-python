import asyncio

from logingateway import HuTaoLoginAPI
from logingateway.model import Ready, Player

# Init gateway
gateway = HuTaoLoginAPI(
    "abc-123-abc-123456",
    "abcdefghijk1234567890"
)

@gateway.ready()
async def on_ready(data: Ready):
    print(data)

@gateway.player()
async def on_player(data: Player):
    """
        When user has selected Genshin account and accepted
    """
    print(data)

@gateway.player_update()
async def player_update(data: Player):
    # Recieved player update data
    print(data.genshin)

# Generate URL
url, token = gateway.generate_login_url(
    user_id="123456789012345678",
    guild_id="123456789012345678",
    channel_id="123456789012345678",
    message_id="123456789012345678",
    language="th"
)
print(url)

asyncio.run(gateway._start())