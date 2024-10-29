from pathlib import Path


# class ImageCache:
#     def __init__(self, bot, images, images_dir, refresh_timer=12*60*60):
#         self.last_refresh = None
#         self.cache = None

#         self.bot = bot
#         self.images = images
#         self.images_dir = Path(images_dir)
#         self.refresh_timer = refresh_timer

#     async def refresh(self):
#         if (self.last_refresh is None) or ((datetime.now() - self.last_refresh).seconds > self.refresh_timer):
#             print('refreshing')
#             self.last_refresh = datetime.now()
#             new_cache = {}
#             for img in self.images:
#                 file = await self.bot.upload_file(self.images_dir / img)
#                 new_cache[img] = file
#             self.cache = new_cache
#         return self.cache


class ImageCache:
    def __init__(self, bot, images, images_dir):
        self.bot = bot
        self.images = images
        self.images_dir = Path(images_dir)

        self.cache = {img: None for img in self.images}

    async def get(self, img):
        if self.cache.get(img) is None:
            self.cache[img] = await self.refresh(img)
        return self.cache[img]

    async def refresh(self, img):
        file = await self.bot.upload_file(self.images_dir / img)
        self.cache[img] = file
        return file
