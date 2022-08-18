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
    
    def will_accept(self, ctx: Context) -> bool:
        return super().will_accept(ctx) and ctx.verb.parameter in ["message", "embed"]
    
    def process(self, ctx: Context) -> Optional[str]:
        to_send = ctx.response.actions.get("send", [{"message": "", "embed": None}])
        
        param = ctx.verb.parameter
        payload = ctx.verb.payload
        
        thing_to_send = param or "message"
        
        
        for ind, send_dict in enumerate(to_send.copy()):
            
            object_to_send = send_dict[ind][thing_to_send]
            
            try:
                object_to_send = EmbedBlock().text_to_embed(payload)
                
            except Exception:
                pass
            
            if object_to_send is None:
                to_send[ind][thing_to_send] = payload
                
            elif isinstance(object_to_send, Embed):
                to_send.append({"message": "", "embed": object_to_send})
                
            elif object_to_send == "":
                to_send[ind][thing_to_send] = payload
                
            elif object_to_send == payload:
                pass
            
            elif len(object_to_send) >= 4096:
                org_msg = object_to_send[:4093] + "..."
                new_msg = object_to_send[4093:] + "\n\n" + payload
            
                to_send[ind][thing_to_send] = org_msg
                to_send.append({"message": new_msg, "embed": None})
            
            else:
                to_send[ind][thing_to_send] = object_to_send + "\n\n" + payload
                
        ctx.response.actions.update({"send": to_send})
        return ""