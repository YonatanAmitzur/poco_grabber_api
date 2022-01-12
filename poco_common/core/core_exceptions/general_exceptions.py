
class DbIntegrityException(Exception):

    def __init__(self, message, **kwargs):
        self.reason = "database_integrity_exception"
        self.extra = kwargs
        msg = f"Database integrity exception, message={message}"
        super(DbIntegrityException, self).__init__(msg)
