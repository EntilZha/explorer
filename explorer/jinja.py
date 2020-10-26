from typing import Optional, Dict
from starlette.templating import Jinja2Templates


class ConfigurableJinja2Templates(Jinja2Templates):
    def __init__(self, directory: str, jinja_globals: Optional[Dict] = None):
        super().__init__(directory)
        self.jinja_globals = jinja_globals
        if jinja_globals is not None:
            for k, v in jinja_globals.items():
                self.env.globals[k] = v
