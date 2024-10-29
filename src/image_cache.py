from pathlib import Path
from datetime import datetime


class ImageCache:
    def __init__(self, bot, images, images_dir, refresh_timer=12*60*60):
        self.last_refresh = None
        self.cache = None

        self.bot = bot
        self.images = images
        self.images_dir = Path(images_dir)
        self.refresh_timer = refresh_timer

    async def refresh(self):
        if (self.last_refresh is None) or ((datetime.now() - self.last_refresh).seconds > self.refresh_timer):
            print('refreshing')
            self.last_refresh = datetime.now()
            new_cache = {}
            for img in self.images:
                file = await self.bot.upload_file(self.images_dir / img)
                new_cache[img] = file
            self.cache = new_cache
        return self.cache
