import os
import random
from pathlib import Path

import openai
import twitter
from profanity import profanity

ROOT = Path(__file__).resolve().parents[0]


def lambda_handler(event, context):
    print("Get credentials")
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN_KEY")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
    openai_token = os.getenv("OPENAI_TOKEN")

    print("Authenticate")
    api = twitter.Api(consumer_key,
                      consumer_secret,
                      access_token,
                      access_token_secret,
                      )
    openai.api_key = openai_token

    print("configure stuff")
    profanity.set_censor_characters("*")
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

    print("Get a random word")
    # nltk.data.path.append("/tmp")
    #
    # nltk.download('brown', download_dir = "/tmp")
    # nltk.download('webtext', download_dir = "/tmp")
    # word_list = list(set(brown.words()) | set(webtext.words()))
    with open("words.txt", "r", encoding='utf-8') as f:
        word_list = f.read().split(",")
    word = random.choice(word_list)
    print(word)
    print("get AI response")
    prompt = random.choice(prompts).replace("X", word.title())
    response = openai.Completion.create(
        engine=random.choice(list(engines.keys())),
        prompt=prompt,
        max_tokens=100,
        temperature=0.8,
        echo=True,
        stop=". "
    )['choices'][0]['text']

    # https://en.wikipedia.org/wiki/Scunthorpe_problem
    # Honestly I think its hilarious that it might
    # write a fact about 'Charles ****ens'
    response = profanity.censor(response)

    # Lol
    response = response.strip() \
        .strip('\n') \
        .replace("\n", " ") \
        .replace("\"", "") \
        .replace("  ", " ") \
        .replace("  ", " ") \
        .replace("  ", " ")

    print("Post to Twitter")
    tweet = response[:250]
    api.PostUpdate(tweet)

    return {"statusCode": 200, "tweet": tweet}
