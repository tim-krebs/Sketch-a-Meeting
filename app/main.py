import os
from random import choices
from urllib import response
import openai
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import replicate


def get_env_variables():
    load_dotenv(Path("C:/Users/timkrebs/OneDrive/Developer/06_Python/Hackathon22-SAM/.env"))
    api_key = os.getenv("REPLICATE_API_TOKEN")

    return api_key

def get_response(api_key, v_prompt):

    # Call the openai API 
    openai.api_key = api_key

    response = openai.Completion.create(
    model="text-davinci-002",
    prompt=v_prompt,
    temperature=0.7,
    max_tokens=64,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
    )

    return response


def replicate_text_image(apiKey,strPrompt):
    replicate.Client(api_token=apiKey)
    model = replicate.models.get("kvfrans/clipdraw")

    i = 0
    for image in model.predict(prompt=strPrompt,num_paths=256, num_iterations=500):
        print("Iteration: " + str(i)+", "+image)
        i+=1

def main():

    # Extract the api from env var
    api_key = get_env_variables()

    strPrompt = "horse with astronaut"
    replicate_text_image(api_key, strPrompt)
    

    # Extract the choices from the repsonse
        #v_prompt = "Summarize this for a second-grade student:\n\nJupiter is the fifth planet from the Sun and the largest in the Solar System. It is a gas giant with a mass one-thousandth that of the Sun, but two-and-a-half times that of all the other planets in the Solar System combined. Jupiter is one of the brightest objects visible to the naked eye in the night sky, and has been known to ancient civilizations since before recorded history. It is named after the Roman god Jupiter.[19] When viewed from Earth, Jupiter can be bright enough for its reflected light to cast visible shadows,[20] and is on average the third-brightest natural object in the night sky after the Moon and Venus."
    
    # feed api with the vars
        #response = get_response(api_key, v_prompt)
        #choice1 = response.get("choices")
        #print(choice1[0]["text"])




if __name__ == '__main__':
    # Execute main file
    main()
    