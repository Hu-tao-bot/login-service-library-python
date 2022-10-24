# Hu Tao login gateway
Hu tao login gateway library for login Genshin easier

## Install
### Method 1 (Recommend)
```
pip3 install git+https://github.com/Hu-tao-bot/login-service-library
```
### Method 2
```
git clone https://github.com/Hu-tao-bot/login-service-library
pip3 install setup.py
```

## Usage
### Simple
```py
# Init gateway
gateway = HuTaoLoginAPI(
    "abc-123-abc-123456",
    "abcdefghijk1234567890"
)

@tao.ready()
async def on_ready(data: Ready):
    print(data)

@tao.player()
async def on_player(data: Player):
    """
        When user has selected Genshin account and accepted
    """
    print(data)

# Generate URL
url = gateway.generate_login_url(
    user_id="123456789012345678",
    guild_id="123456789012345678",
    channel_id="123456789012345678",
    message_id="123456789012345678",
    language="th"
)
print(url)

asyncio.run(gateway.start())
```

### Discord example
```py
# Soon
```

## License 
MIT