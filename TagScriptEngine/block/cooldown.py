import time
from typing import Any, Dict, Optional

from discord.ext.commands import CooldownMapping

from ..exceptions import CooldownExceeded
from ..interface import verb_required_block
from ..interpreter import Context
from .helpers import helper_split

__all__ = ("CooldownBlock",)


class CooldownBlock(verb_required_block(True, payload=True, parameter=True)):
    """
    The cooldown block implements cooldowns when running a tag.
    The parameter requires 2 values to be passed: ``rate`` and ``per`` integers.
    The ``rate`` is the number of times the tag can be used every ``per`` seconds.

    The payload requires a ``key`` value, which is the key used to store the cooldown.
    A key should be any string that is unique. If a channel's ID is passed as a key, the
    the tag's cooldown will be enforced on that channel. Running the tag in a separate channel
    would have a different cooldown with the same ``rate`` and ``per`` values.

    The payload also has an optional ``message`` value, which is the message to be sent when the
    cooldown is exceeded. If no message is passed, the default message will be sent instead.
    The cooldown message supports 2 blocks: ``key`` and ``retry_after``.

    **Usage:** ``{cooldown(<rate>|<per>):<key>|[message]}``

    **Payload:** key, message

    **Parameter:** rate, per

    **Examples:** ::

        {cooldown(1|10):{author(id)}}
        # the tag author used the tag more than once in 10 seconds
        # The bucket for 741074175875088424 has reached its cooldown. Retry in 3.25 seconds."

        {cooldown(3|3):{channel(id)}|Slow down! This tag can only be used 3 times per 3 seconds per channel. Try again in **{retry_after}** seconds."}
        # the tag was used more than 3 times in 3 seconds in a channel
        # Slow down! This tag can only be used 3 times per 3 seconds per channel. Try again in **0.74** seconds.
    """

    ACCEPTED_NAMES = ("cooldown",)
    __COOLDOWNS: Dict[Any, CooldownMapping] = {}

    @classmethod
    def create_cooldown(cls, key: Any, rate: int, per: int) -> CooldownMapping:
        cooldown = CooldownMapping.from_cooldown(rate, per, lambda x: x)
        cls.__COOLDOWNS[key] = cooldown
        return cooldown

    def process(self, ctx: Context) -> Optional[str]:
        verb = ctx.verb
        try:
            rate, per = helper_split(verb.parameter, maxsplit=1)
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
            if message:
                message = message.replace("{key}", str(key)).replace(
                    "{retry_after}", str(retry_after)
                )
            else:
                message = f"The bucket for {key} has reached its cooldown. Retry in {retry_after} seconds."
            raise CooldownExceeded(message, bucket, key, retry_after)
        return ""
