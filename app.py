import json, random, os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

# Load facts & coins
with open("facts.json") as f:
    facts = json.load(f)

coins = {}
if os.path.exists("coins.json"):
    with open("coins.json") as f:
        coins = json.load(f)

def save_coins():
    with open("coins.json", "w") as f:
        json.dump(coins, f)

def get_coins(user):
    return coins.get(user, 0)

def add_coins(user, amount):
    coins[user] = get_coins(user) + amount
    save_coins()

# /fact command
@app.command("/fact")
def fact_cmd(ack, body, client):
    ack()
    user = body["user_id"]
    fact = random.choice(facts["fun"])
    add_coins(user, 1)

    client.chat_postMessage(
        channel=body["channel_id"],
        blocks=[
            {"type": "section", "text": {"type": "mrkdwn", "text": f"🧠 *Fact Goblin says:*\n> {fact}"}},
            {
                "type": "actions",
                "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "🔮 Deep Fact"}, "action_id": "deep_fact"},
                    {"type": "button", "text": {"type": "plain_text", "text": "💰 Coins"}, "action_id": "check_coins"}
                ]
            }
        ]
    )

# /coins command
@app.command("/coins")
def coins_cmd(ack, body, say):
    ack()
    user = body["user_id"]
    say(f"💰 You have {get_coins(user)} coins!")

# Deep fact button
@app.action("deep_fact")
def deep_fact_btn(ack, body, client):
    ack()
    user = body["user"]["id"]
    if get_coins(user) < 5:
        client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=user,
            text="❌ Need 5 coins to get a Deep Fact."
        )
        return
    add_coins(user, -5)
    deep_fact = random.choice(facts["deep"])
    client.chat_postMessage(
        channel=body["channel"]["id"],
        text=f"🔎 *Deep Fact*: {deep_fact}"
    )

# Coins button
@app.action("check_coins")
def check_coins_btn(ack, body, client):
    ack()
    user = body["user"]["id"]
    client.chat_postEphemeral(
        channel=body["channel"]["id"],
        user=user,
        text=f"💰 You have {get_coins(user)} coins."
    )

# Run bot
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


[
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "🧠 *Fact Goblin says:*\n> Octopuses have three hearts."
    }
  },
  {
    "type": "actions",
    "elements": [
      {
        "type": "button",
        "text": {
          "type": "plain_text",
          "text": "🔮 Deep Fact"
        },
        "action_id": "deep_fact"
      },
      {
        "type": "button",
        "text": {
          "type": "plain_text",
          "text": "💰 Coins"
        },
        "action_id": "check_coins"
      }
    ]
  }
]
[
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "🔎 *Deep Fact:*\nOxford University is older than the Aztec Empire."
    }
  }
]
[
  {
    "type": "section",
    "text": {
      "type": "plain_text",
      "text": "❌ You need 5 coins to get a Deep Fact."
    }
  }
]
