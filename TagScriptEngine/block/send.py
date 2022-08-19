from ..adapter import StringAdapter
from ..interface import verb_required_block
from ..interpreter import Context
from .embedblock import EmbedBlock
from discord import Embed

from typing import Optional

class SendBlock(verb_required_block(explicit=True, parameter=True, payload=True)):
    """
    The send block sends the payload to the channel the tagscript was run in.
    
    A parameter can be specified to differ between sending an embed or a plain message.
    This block can be used multiple times It tries to append the payload to the existing message.
    or it will send a new message.
    """
    ACCEPTED_NAMES = ("send",)
    
    def will_accept(self, ctx: Context) -> bool:
        b = super().will_accept(ctx) and ctx.verb.parameter.lower() in ["message", "embed"]
        return b
    
    def process(self, ctx: Context) -> Optional[str]:
        to_send = ctx.response.actions.get("send", [{"content": "", "embed": None}])
        
        param = ctx.verb.parameter
        payload = ctx.verb.payload
        
        thing_to_send = param or "content"
        
        
        for ind, send_dict in enumerate(to_send.copy()):
            
            thing_to_send = "content" if thing_to_send == "message" else "embed"
            
            object_to_send = send_dict[thing_to_send]
            
            if thing_to_send == "embed":
                if payload == "{__emb}":
                    payload = ctx.response.variables.get("__emb", StringAdapter("")).string
                payload = EmbedBlock().text_to_embed(payload)
            
            if object_to_send is None:
                to_send[ind][thing_to_send] = payload
                
            elif isinstance(object_to_send, Embed):
                to_send.append({"content": "", "embed": payload})
                
            elif object_to_send == "":
                to_send[ind][thing_to_send] = payload
                
            elif object_to_send == payload:
                continue
            
            elif len(object_to_send) >= 4096:
                org_msg = object_to_send[:4093] + "..."
                new_msg = object_to_send[4093:] + "\n\n" + payload
            
                to_send[ind][thing_to_send] = org_msg
                to_send.append({"content": new_msg, "embed": None})
            
            else:
                to_send[ind][thing_to_send] = object_to_send + "\n\n" + payload
                
        ctx.response.actions.update({"send": to_send})
        return ""