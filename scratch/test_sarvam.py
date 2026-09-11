import os
from sarvamai import SarvamAI

# Mock key to see if it imports and initializes
os.environ["SARVAM_API_KEY"] = "fake_key"

client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])
print("Client initialized:", client)
print("Methods on client.chat.completions:", dir(client.chat.completions))
