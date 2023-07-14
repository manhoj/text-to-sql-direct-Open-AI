import openai

# Set up your OpenAI API credentials
openai.api_key = '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'

# Define your chat conversation
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    {"role": "user", "content": "Where was it played?"}
]

# Send the API request
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k-0613",
    messages=conversation
)

# Retrieve the assistant's reply
reply = response['choices'][0]['message']['content']
print("Assistant: " + reply)
