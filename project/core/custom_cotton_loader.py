from django_cotton.cotton_loader import Loader as BaseLoader
from django.conf import settings

class Loader(BaseLoader):
    def get_dirs(self):
        """This works like the file loader with APP_DIRS = True."""
        return self.dirs