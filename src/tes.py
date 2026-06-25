from pypresence import Presence
import time

RPC = Presence("1519532503055208458")
RPC.connect()

result = RPC.update(
    details="TubeTunes Test",
    state="Debug Mode",
    large_image="tubetunes",
    large_text="TubeTunes"
)

print("result =", result)

input("enter...")