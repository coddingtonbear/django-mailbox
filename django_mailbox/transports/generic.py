

from .base import EmailTransport


class GenericFileMailbox(EmailTransport):
    _variant = None
    _path = None

    def __init__(self, path):
        super().__init__()
        self._path = path

    def get_instance(self):
        return self._variant(self._path)

    def get_message(self, condition=None):
        repository = self.get_instance()
        repository.lock()
        for key, message in repository.items():
            if condition and not condition(message):
                continue
            repository.remove(key)
            yield message
        repository.flush()
        repository.unlock()
