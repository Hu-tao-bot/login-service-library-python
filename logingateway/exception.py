__all__ = ('Unauthorized','RetryTimeout',)

class Unauthorized(Exception):
    """ If authenticate failed """

class RetryTimeout(Exception):
    """ If retry connection has timeout """