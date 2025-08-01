import asyncio
from DeeperSeek import DeepSeek

async def main():

    api = DeepSeek(
        token = "nEQA4oK5cAiQshlWr9woZDnJj5FDHNFh3VlF9M2gGA3IKdWGB3WmQ6b7YNsabFlp",
        headless = True,
    )

    await api.initialize()  # Necessary to initialize the class, must be called before using other methods

    response = await api.send_message(
    "Hey DeepSeek!",
    deepthink = False,  # Whether to use the DeepThink option or not
    search = False,  # Whether to use the Search option or not
    slow_mode = True,  # Whether to send the message in slow mode or not
    slow_mode_delay = 0.25,  # The delay between each character when sending the message in slow mode
    timeout = 60,  # The time to wait for the response before timing out
    )  # Returns a Response object
    print(response.text, response.deepthink_duration, response.deepthink_content)


print('starting')
asyncio.run(main())
print('done')