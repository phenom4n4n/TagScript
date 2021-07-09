"""
MIT License

Copyright (c) 2020-2021 phenom4n4n

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Optional, Any, Dict
import time

from discord.ext.commands import CooldownMapping

from .helpers import helper_split
from ..interface import Block
from ..interpreter import Context
from ..exceptions import CooldownExceeded

__all__ = ("CooldownBlock",)


class CooldownBlock(Block):
    """
    cooldown desc

    **Usage:** ``{cooldown(<rate>,<per>):<key>|[message]}``

    **Payload:** key, message

    **Parameter:** rate, per

    **Examples:** ::

        {cooldown(1,10):{author(id)}}
    """

    __COOLDOWNS: Dict[Any, CooldownMapping] = {}

    def will_accept(self, ctx: Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return dec == "cooldown"

    @classmethod
    def create_cooldown(cls, key: Any, rate: int, per: int) -> CooldownMapping:
        cooldown = CooldownMapping.from_cooldown(rate, per, lambda x: x)
        cls.__COOLDOWNS[key] = cooldown
        return cooldown

    def process(self, ctx: Context) -> Optional[str]:
        verb = ctx.verb
        if not (verb.parameter and verb.payload):
            return
        try:
            rate, per = verb.parameter.split(",", 1)
            per = int(per)
            rate = float(rate)
        except ValueError:
            return

        if split := helper_split(verb.payload, False, maxsplit=1):
            key, message = split
        else:
            key = verb.payload
            message = None

        cooldown_key = ctx.response.extra_kwargs.get("cooldown_key")
        if cooldown_key is None:
            cooldown_key = ctx.original_message
        try:
            cooldown = self.__COOLDOWNS[cooldown_key]
            base = cooldown._cooldown
            if (rate, per) != (base.rate, base.per):
                cooldown = self.create_cooldown(cooldown_key, rate, per)
        except KeyError:
            cooldown = self.create_cooldown(cooldown_key, rate, per)

        current = time.time()
        bucket = cooldown.get_bucket(key, current)
        retry_after = bucket.update_rate_limit(current)
        if retry_after:
            retry_after = round(retry_after, 2)
            message = message or f"The bucket for {key} has reached its cooldown. Retry in {retry_after} seconds."
            message = message.replace("{key}", str(key)).replace("{retry_after}", str(retry_after))
            raise CooldownExceeded(message, bucket, key, retry_after)
        return ""
