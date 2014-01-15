import sys


class GenericFileMailbox(object):
    _variant = None
    _path = None

    def __init__(self, path):
        super(GenericFileMailbox, self).__init__()
        self._path = path.encode(
            sys.getfilesystemencoding()
        )

    def get_instance(self):
        return self._variant(self._path)

    def get_message(self):
        repository = self.get_instance()
        repository.lock()
        for key, message in repository.items():
            repository.remove(key)
            yield message
        repository.unlock()
