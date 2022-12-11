import asyncio

from logingateway.api import HuTaoLoginRESTAPI

# Init REST API
rest_client = HuTaoLoginRESTAPI(
    client_id="abc-123-abc-123456",
    client_secret="abcdefghijk1234567890"
)

async def reload_cookies(id:str):
    #get token from history and reload cookies will only work for mail type setup
    history  = await rest_client.get_history_user(id,login_type='mail')
    if history.data is not []: #check if history is not empty if it is empty it will return empty list
        token = history.data[0].token #get recent token from history
    else:
        return None 
    new_cookie =await rest_client.reload_new_cookie(id,token)
    return new_cookie


asyncio.run(reload_cookies("123456789012345678"))