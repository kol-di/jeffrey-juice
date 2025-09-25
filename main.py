import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon import events, Button
from yaml import safe_load
from telethon.errors.rpcerrorlist import FilePart0MissingError

from src.novel_parser import NovelParser
from src.image_cache import ImageCache
from src.subscription_validator import SubscriptionValidator

load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

config_path = os.getenv('CONFIG_PATH') or './config.yaml'
with open(config_path) as f:
    config = safe_load(f)
novel_parser = NovelParser(
    config['config_path'], 
    config['images_path']
)


bot = TelegramClient('anon', API_ID, API_HASH)
bot.start(bot_token=BOT_TOKEN)

# Initialize subscription validator
subscription_validator = SubscriptionValidator(bot, config_path)

images = [fork['img'] for fork in novel_parser]
images.append('start.jpeg')
image_cache = ImageCache(bot, images, config['images_path'])


@bot.on(events.NewMessage(incoming=True, pattern=r'/start'))
async def my_event_handler(event):
    if not await subscription_validator.ensure_subscription(event):
        return
    
    sender = await event.get_sender()
    try:
        file = (await image_cache.get('start.jpeg'))
        await bot.send_message(
            sender,
            message="Сыграем?",
            buttons=[
                Button.inline('Конечно!', data='0')],
            file=file
        )
    except FilePart0MissingError:
        file = (await image_cache.refresh('start.jpeg'))
        await bot.send_message(
            sender,
            message="Сыграем?",
            buttons=[
                Button.inline('Конечно!', data='0')],
            file=file
        )

for fork in novel_parser:

    @bot.on(events.CallbackQuery(data=fork['cur']))
    async def handler(event, fork=fork):
        if not await subscription_validator.answer_callback_with_subscription_check(event):
            return

        # create buttons
        buttons = []
        options = fork.get('next') or []  # list of (text, data)
        options_sorted = sorted(options, key=lambda item: len(item[0]))
        # group: short (<28) in pairs, long (>=28) single
        i = 0
        while i < len(options_sorted):
            text, data = options_sorted[i]
            if i + 1 < len(options_sorted) and len(options_sorted[i + 1][0]) < 28:
                buttons.append([
                    Button.inline(text, data=data),
                    Button.inline(options_sorted[i + 1][0], data=options_sorted[i + 1][1])
                ])
                i += 2
            else:
                buttons.append([Button.inline(text, data=data)])
                i += 1
        if fork['prev'] is not None:
            buttons.append([Button.inline(
                'Назад', data=fork['prev']
            )])

        msg_to_edit = await event.get_message()

        try:
            file = (await image_cache.get(fork['img']))
            await bot.edit_message(
                entity=msg_to_edit,
                message=fork['text'],
                file=file, 
                buttons=buttons
            )
        except FilePart0MissingError:
            file = (await image_cache.refresh(fork['img']))
            await bot.edit_message(
                entity=msg_to_edit,
                message=fork['text'],
                file=file, 
                buttons=buttons
            )


bot.run_until_disconnected()
