import unittest

import TagScriptEngine as tse
import discord

class Sendtest(unittest.TestCase):
    def setUp(self):
        self.blocks = [
            tse.SendBlock(),
            tse.EmbedBlock(),
        ]
        self.engine = tse.Interpreter(self.blocks)

    def tearDown(self):
        self.blocks = None
        self.engine = None
        
    def test_send(self):
        resp = self.engine.process(
            """
            {embed(title):Hello} {embed(description):World}
            {send(message):abcd}
            {embed({"title": "test", "description":"Test", "author": {"name": "test", "url": "test"}})}
            {send(embed):{__emb}}"""
        )
        print(resp)
        self.assertEqual(resp.actions, {"send": [{"message": "abcd", "embed": discord.Embed(title="Hello", description="World")}, {"message": "", "embed": discord.Embed(title="test", description="Test").set_author(name="test", url="test")}]})
        
if __name__ == "__main__":
    x = Sendtest()
    x.setUp()
    x.test_send()
    x.tearDown()