from collections import namedtuple

from django.core.cache.backends.locmem import LocMemCache
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.timezone import now


FakeContent = namedtuple('FakeContent', ['content', 'time'])


@deconstructible
class LocMemStorage(Storage):

    def __init__(self):
        params = {
            'timeout': 24 * 60 * 60,
            'max_entries': 300,
        }
        self.cache = LocMemCache(name='test_storage', params=params)

    def _open(self, name, mode='rb'):
        if 'w' in mode:
            raise Exception('Oh Geez...')
        return ContentFile(self.cache.get(name).content)

    def _save(self, name, content):
        # Make sure that the cache stores the file as bytes, like it would be
        # on disk.
        content = content.read()
        try:
            content = content.encode()
        except AttributeError:
            pass
        self.cache.add(name, FakeContent(content, now()))
        return name

    # These methods are part of the public API, with default implementations.

    def path(self, name):
        """
        Return a local filesystem path where the file can be retrieved using
        Python's built-in open() function. Storage systems that can't be
        accessed using open() should *not* implement this method.
        """
        raise NotImplementedError("This backend doesn't support absolute paths.")

    # The following methods form the public API for storage systems, but with
    # no default implementations. Subclasses must implement *all* of these.

    def delete(self, name):
        """
        Delete the specified file from the storage system.
        """
        self.cache.delete(name)

    def exists(self, name):
        """
        Return True if a file referenced by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        return name in self.cache

    def listdir(self, path):
        """
        List the contents of the specified path. Return a 2-tuple of lists:
        the first item being directories, the second item being files.
        """
        raise NotImplementedError('subclasses of Storage must provide a listdir() method')

    def size(self, name):
        """
        Return the total size, in bytes, of the file specified by name.
        """
        return len(self.cache.get(name).content)

    def url(self, name):
        """
        Return an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        return name

    def get_accessed_time(self, name):
        """
        Return the last accessed time (as a datetime) of the file specified by
        name. The datetime will be timezone-aware if USE_TZ=True.
        """
        return self.cache.get(name).time

    def get_created_time(self, name):
        """
        Return the creation time (as a datetime) of the file specified by name.
        The datetime will be timezone-aware if USE_TZ=True.
        """
        return self.cache.get(name).time

    def get_modified_time(self, name):
        """
        Return the last modified time (as a datetime) of the file specified by
        name. The datetime will be timezone-aware if USE_TZ=True.
        """
        return self.cache.get(name).time
