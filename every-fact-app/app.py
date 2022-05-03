import os
import random
import string
from pathlib import Path

import openai
import twitter
from profanity import profanity

ROOT = Path(__file__).resolve().parents[0]


def lambda_handler(event, context):
    # Authenticate with OpenAI and Twitter
    consumer_key = os.getenv("TwitterConsumerKey")
    consumer_secret = os.getenv("TwitterConsumerSecret")
    access_token = os.getenv("TwitterAccessTokenKey")
    access_token_secret = os.getenv("TwitterAccessTokenSecret")
    openai_token = os.getenv("OpenAiToken")
    api = twitter.Api(consumer_key,
                      consumer_secret,
                      access_token,
                      access_token_secret,
                      )
    openai.api_key = openai_token

    # Configure some stuff
    # Ada usually just spews nonsense, and Da Vinci costs a lot.
    engines = {
        # "text-davinci-001": "Da Vinci",
        "text-curie-001": "Curie",
        "text-babbage-001": "Babbage",
        # "text-ada-001": "Ada"
    }
    prompts = [
        "Cool X Fact:",
        "X Fact:",
        "Funny X fact:",
        "Fun X Fact:",
        "Weird X Fact:",
        "Interesting X Fact:",
    ]

    # Get a random word from the wordlist
    # We could use the nltk package, but it's slower than this pre-randomized list that I exported
    with open("words.txt", "r", encoding='utf-8') as f:
        word_list = f.read().split(",")
    word = random.choice(word_list)

    # Build the prompt
    prompt = random.choice(prompts).replace("X", string.capwords(word))

    # Pick a random Temperature value
    # 0.1% chance to just go wild with maximum temperature
    if random.random() > 0.999:
        temperature = 2.0
        presence_penalty = 2.0
        frequency_penalty = 2.0
    else:
        temperature = random.normalvariate(0.7, 0.2)  # Get some value between 0.5ish and 1.5ish
        presence_penalty = random.normalvariate(0, 0.1)
        frequency_penalty = random.normalvariate(0, 0.1)

    # Get OpenAI's response
    # TODO - get more than 1 response and pick one that doesn't contain "There is no evidence" and "Weird X Fact: The Weird X..." because they show up way too often
    response = openai.Completion.create(
        engine=random.choice(list(engines.keys())),
        prompt=prompt,
        max_tokens=100,
        temperature=temperature,
        echo=True,
        presence_penalty=frequency_penalty,
        frequency_penalty=presence_penalty,
        # stop="."
    )['choices'][0]['text']

    # https://en.wikipedia.org/wiki/Scunthorpe_problem
    # Honestly I think its hilarious that it might
    # write a fact about 'Charles ****ens'
    profanity.set_censor_characters("*")
    response = profanity.censor(response)

    # Clean up newlines and double spaces. Cut the response to tweet length
    response = response.replace("\n", " ").replace("  ", " ").strip()
    response = response[:250]

    # if response doesnt end in a period, either cut off the sentence at the last period or add one.
    if not response.endswith("."):
        if response.find(".") != -1:
            response = response[:response.rfind(".")] + "."
        else:
            response += '.'
    print(f"Posting tweet: '{response}'")
    api.PostUpdate(response)

    return {"statusCode": 200, "tweet": response}
