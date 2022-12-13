__all__ = ('Unauthorized','RetryTimeout',)

class Unauthorized(Exception):
    """ If authenticate failed """

class RetryTimeout(Exception):
    """ If retry connection has timeout """


class LoginFailed(Exception):
    """ If Login username and password goes wrong """

class LoginRequired(Exception):
    """ If user has not logged """

class UserCookieInvalid(Exception):
    """ If user has use old account. You must remove account and login again. """

class CookieTokenAlreadyLoaded(Exception):
    """ If bot provider has been already reloaded. """
    
class UserTokenExpired(Exception):
    """ If user has changed password or something in account """

class UserTokenNotFound(Exception):
    """ If token user has not found in database """

class UserTokenNotSupport(Exception):
    """ If User has login another method (Ex. UID or token) """

class TokenInvaild(Exception):
    """ If user has send token. And validate failed """

class TokenExpired(Exception):
    """ If token has expired """

class TokenSyntaxError(Exception):
    """ Token has validate JSON failed """

class MaximumRetryLogin(Exception):
    """ Loop if max login retry """
    
ERRORS = {
    1002: TokenSyntaxError,
    1020: TokenExpired,
    1021: TokenInvaild,
    2000: LoginFailed,
    4000: UserTokenNotFound,
    4002: CookieTokenAlreadyLoaded,
    4010: UserTokenNotSupport,
    4011: UserCookieInvalid,
    4012: UserTokenExpired
}