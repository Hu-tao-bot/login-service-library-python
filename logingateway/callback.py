import warnings

from typing import Callable, Dict


class Callback:
    DECORECTOR: Dict[str, Callable] = {}

    def ready(self, cb: Callable = None):
        def _callback(func: Callable):
            self.DECORECTOR["ready"] = func
            return func

        if cb:
            self.DECORECTOR["ready"] = cb
            return

        return _callback

    def player(self, cb: Callable = None):
        def _callback(func: Callable):
            self.DECORECTOR["player_register"] = func
            return func

        if cb:
            self.DECORECTOR["player_register"] = cb
            return

        return _callback

    def player_update(self, cb: Callable = None):
        def _callback(func: Callable):
            self.DECORECTOR["player_update"] = func
            return func

        if cb:
            self.DECORECTOR["player_update"] = cb
            return

        return _callback

    def error(self, cb: Callable = None):
        warnings.warn(
            "This function has been depercated. You can remove this function")
        return None

    def disconnect(self, cb: Callable = None):
        def _callback(func: Callable):
            self.DECORECTOR["disconnect"] = func
            return func

        if cb:
            self.DECORECTOR["disconnect"] = cb
            return

        return _callback
