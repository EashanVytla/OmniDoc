from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnableMap, RunnablePassthrough
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
import socket
from openai import OpenAI
from omnidoc_app.models import Session

load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')

model = ChatOpenAI(model="gpt-4o-mini")
client = OpenAI()

with open('omnidoc_app/topics.json', 'r') as json_file:
    template_dict = json.load(json_file)

def flatten_dict(nested_dict):
    items = {}

    def flatten(d):
        for key, value in d.items():
            if isinstance(value, dict):
                flatten(value)
            else:
                items[key] = "None"

    flatten(nested_dict)
    return items

flattened = flatten_dict(template_dict)

#memory = ConversationBufferMemory()

question_prompt = ChatPromptTemplate.from_template(
    "System"
    "You are an AI assistant with the purpose of screening someone who has scheduled an appointment with a doctor."
    "This person isn't aware that they are talking to a chatbot, so don't give them information on what you are thinking internally."
    "Your task is to ask this patient general screening questions, to get information regarding the patient's symptoms, demographics, and more."
    "Essentially, you are an AI nurse."
    "Given the following schema, your task is to fill out every value for every key in this schema, by asking ONE relevant question per key."
    "If a key already has a value that is NOT None associated with it, then do not ask a question about that key."
    "Repeat this until all keys have values associated with them that are not None."
    "This is the list of keys\n{input}\n"
    "Make this screening as a very natural conversation, with fluid transitions between each question you ask.\n"
    "This is what has been said so far in the current conversation: {context}"
    "DO NOT SAY 'Chatbot question' or question."
    "No need to be expicit or too verbose about restating my previous answer. Have a bit of a follow up response, but quickly move into the next quesiton."
)

read_answer = ChatPromptTemplate.from_template(
    "System"
    #"Chatbot question: {initial_output}"
    "Read the users response: {answer}"
    "List of Keys: {keys}"
    "Give me the key from the list of keys that fits this response most and important points from the response in a list of bullet points"
    "You don't need to write complete sentences for the bullet points"
    "FOLLOW THIS FORMAT FOR THE OUTPUT! THIS IS IMPORTANT!: [Key]: [bullet 1], [bullet 2]..."
)

clarification_prompt = ChatPromptTemplate.from_template(
    "System: You are an AI assistant helping a nurse gather patient information. "
    "Based on the patient's response: '{user_input}' "
    "and the current question: {question}, "
    "determine if you need any clarification or additional information. "
    "If you do, ask a single, specific follow-up question. "
    "If you don't need any clarification, respond with 'NO_CLARIFICATION_NEEDED'. "
    "Your question should be direct and easy for the patient to understand. "
    "Remember, you're gathering information for a medical professional, so focus on relevant medical details."
)

check_clar_prompt = ChatPromptTemplate.from_template(
    "System: You are an AI assistant helping a nurse gather patient information. "
    "Based on the updated data, in the format of [Key]: [bullet 1], [bullet 2]...:'{answer_output}' "
    "determine if you need any clarification or additional information about the key. "
    "If you do, ask a single, specific follow-up question. "
    "If you don't need any clarification, respond with 'NO_CLARIFICATION_NEEDED'. "
    "Your question should be direct and easy for the patient to understand. "
    "Remember, you're gathering information for a medical professional, so focus on relevant medical details about the key."
)


process_clarification = ChatPromptTemplate.from_template(
    "System: Given the patient's clarification: '{clarification_response}' "
    "and the previous context: {previous_context}, "
    "summarize the new information and update the relevant fields. "
    "If you need further clarification, ask another question. "
    "If all necessary information has been gathered, respond with 'INFORMATION_COMPLETE'. "
    "Format your response as: [Key]: [Updated information]"
)

output_parser = StrOutputParser()

question_chain = (RunnablePassthrough()
                | question_prompt
                | model
                | output_parser
                )

answer_chain = (RunnableMap({
                    "keys": lambda _: list(flattened.keys()),
                    "answer": lambda x: x['user_input'],
                    "initial_output": lambda x: x['question']
                })
                | read_answer
                | model
                | output_parser
                )

check_clar = (
    check_clar_prompt
    | model
    | output_parser
)

clarification_chain = (
    clarification_prompt
    | model
    | output_parser
    | RunnableLambda(lambda x: x if x != "NO_CLARIFICATION_NEEDED" else "")
)

process_clarification_chain = (
    process_clarification
    | model
    | output_parser
)

question = ""
chat_history = ""

def receive_data(user_input):
    global chat_history
    global question
    global flattened
    json_str = json.dumps(flattened, indent=2)

    print(json_str)

    chat_history += "Chatbot Question: " + question + "\n"

    str = ""
    
    if question != "":
        answer_output = answer_chain.invoke({"user_input": user_input, "question": question})

        chat_history += "User Answer: " + answer_output + "\n"
    
        key, bullets = parse_output(answer_output)
        if key in flattened:
            print(f"DEBUG: Updated {key}: {bullets}")
            str = f"Updating {key}: {bullets}"
            flattened[key] = bullets
    
        clarification = check_clar.invoke(answer_output)

        #if clarification.strip() == "NO_CLARIFICATION_NEEDED":
        if True:
            print("NO CLARIFICATION")
            question = question_chain.invoke({"input": json_str, "context": chat_history})
        else:
            print("CLARIFICATION")
            question = clarification_chain.invoke({"clarification": clarification, "user_input": user_input, "question": question})
    else:
        str = "Asked first question..."
        question = question_chain.invoke({"input": json_str, "context": chat_history})

    if any(value == "None" for value in flattened.values()):
    # if False:
        state = 0
    else:
        state = 1
        question = "You have completed the screening. Thank you for your time!"

    print(state)

    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=question
        )

    response.stream_to_file("speech.mp3")

    return {
        "status": "success",
        "question": str,
        "state": state,
        "first_name": flattened["first_name"],
        "last_name": flattened["last_name"],
        "json": json_str
    }

def docs2str(docs, title="Document"):
    """Useful utility for making chunks into context string. Optional, but useful"""
    out_str = ""
    for doc in docs:
        doc_name = getattr(doc, 'metadata', {}).get('Title', title)
        if doc_name: out_str += f"[Quote from {doc_name}] "
        out_str += getattr(doc, 'page_content', str(doc)) + "\n"
    return out_str

def parse_output(output):
    # Split the string into two parts: the key and the list of bullets
    key, bullets_string = output.split(":", 1)  # Split only at the first ':'
    
    # Strip whitespace from the key
    key = key.strip("[]").strip()
    
    # Split the bullets by commas and strip whitespace around them
    bullets = [bullet.strip("[]").strip() for bullet in bullets_string.split(",")]
    
    return key, bullets

# def main():
    

#     while any(value == "None" for value in flattened.values()):
        
#         while clarification.strip() != "NO_CLARIFICATION_NEEDED":
#             print(clarification)
#             user_input = input("Enter response: ")
#             clarification = clarification_chain.invoke({"clarification": clarification, "user_input": user_input, "question": question_output})

# if __name__ == "__main__":
#     main()