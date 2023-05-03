import pandas as pd
import numpy as np
import openai

openai.api_key = "OpenAI_KEY_HERE"


"""
Returns a dataframe of "Name", "Sentiment", "Feedback", "Tokens"

names (list of str) 
texts (list of str)

"""

def make_sentiment_df(names, texts):
    sentiment_list = []
    for name, text in zip(names, texts):
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Rate the sentiment of the company \"{name}\" from -100 to 100 and give the reasons why on a new line for following text: {text}",
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.01,
        )
        print(response)
        sentiment = response.choices[0].text.strip().splitlines()
        if len(sentiment) == 1 and sentiment[0].lstrip("-").isdigit():
            sentiment.append("")

        while len(sentiment) > 2:
            sentiment.pop(1)
        print([sentiment[0].split(". ", 1)])
        if (len(sentiment) == 2):
            pass        
        else:
            sentiment = sentiment[0].split(". ", 1)
            print(sentiment)
            if ("positive" in sentiment[0]):
                print("THIS SHOULD WORK")
                sentiment[0] ='100'
            elif ("negative" in sentiment[0]):
                sentiment[0] ='-100'
            else:
                numList = []
                words = sentiment[0].split()
                for word in words:
                    if word.lstrip("-").isdigit():
                        numList.append(word)
                if (len(numList) == 1):
                    sentiment[0] = numList[0]
                else:
                    sentiment[0] = numList[2]
            try:
                sentiment[1] = response.choices[0].text.strip().splitlines()
            except:
                sentiment.append(response.choices[0].text.strip().splitlines())
        
        sentiment.insert(0, name.capitalize())            
        sentiment.append(response.usage['total_tokens'])
        if type(sentiment[2]) == list:
            sentiment[2] = ' '.join(sentiment[2])

        # Final check if sentiment is a value
        if not sentiment[1].lstrip("-").isdigit():
            if ("positive" in sentiment[2]):
                print("THIS SHOULD WORK")
                sentiment[1] ='100'
            elif ("negative" in sentiment[2]):
                sentiment[1] ='-100'
            else:
                numList = []
                words = sentiment[2].split()
                for word in words:
                    if word.lstrip("-").isdigit():
                        numList.append(word)
                if (len(numList) == 1):
                    sentiment[1] = numList[0]
                else:
                    sentiment[1] = numList[2]
        if not sentiment[1].lstrip("-").isdigit():
            sentiment[1] = 0
        sentiment_list.append(sentiment)
    return pd.DataFrame(sentiment_list, columns = ["Name", "Sentiment", "Feedback", "Tokens"])