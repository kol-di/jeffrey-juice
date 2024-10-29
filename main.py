import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon import events, Button
from telethon.sessions import StringSession
from pathlib import Path
from yaml import safe_load

from src.novel_parser import NovelParser

load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

with open('./config.yaml') as f:
    config = safe_load(f)
novel_parser = NovelParser(
    config['config_path'], 
    config['images_path']
)


# bot = TelegramClient(StringSession(), API_ID, API_HASH)
bot = TelegramClient('anon', API_ID, API_HASH)
bot.start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(incoming=True, pattern=r'/start'))
async def my_event_handler(event):
    sender = await event.get_sender()
    await bot.send_message(
        sender,
        message="Сыграем?",
        buttons=[
            Button.inline('Конечно!', data='0')],
        file=Path(config['images_path']) / 'start.jpeg'
        )

for fork in novel_parser:

    @bot.on(events.CallbackQuery(data=fork['cur']))
    async def handler(event, fork=fork):

        # create buttons
        buttons = []
        if fork.get('next') is not None:
            buttons.extend([
                Button.inline(next_text, data=next_data)
                for next_text, next_data in fork['next']])
        buttons = [
            buttons[i*2:(i+1)*2] 
            for i in range(len(buttons) // 2 + 1)
        ]
        if fork['prev'] is not None:
            buttons.append([Button.inline(
                'Назад', data=fork['prev']
            )])

        if fork['img'] is not None:
            img_path = Path(config['images_path']) / fork['img']
        else:
            img_path = None

        msg_to_edit = await event.get_message()
        await bot.edit_message(
            entity=msg_to_edit,
            message=fork['text'],
            file=img_path, 
            buttons=buttons
        )

# bot.start(bot_token=BOT_TOKEN)
bot.run_until_disconnected()

