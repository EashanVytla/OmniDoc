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
import time

load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')

answer_model = ChatOpenAI(model="gpt-4o")
question_model = ChatOpenAI(model="gpt-4o")
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
    """
    You are an AI agent responsible for gathering missing information. Your goal is to ask relevant questions to fill in empty fields in the provided JSON state.

    ## Instructions:
    1. Look at the **state**, which is a JSON string containing all fields. Empty fields need to be filled.
    2. Use **actions** to ask clear and concise questions that help obtain missing information.
    3. Refer to the **current trajectory** to maintain context and avoid redundant questions.

    ---
    ### State (JSON):
    {state}

    ---
    ### Actions (Questions asked so far):
    {current_trajectory}

    ---
    ### Task:
    Generate the next best question that will fill in a field that is NONE while ensuring it is relevant and non-redundant.
    ONCE A FIELD NO LONGER NONE, then DO NOT ASK THAT QUESTION
    DO NOT ASK A QUESTION THAT IS IN THE SET OF ACTIONS TAKEN SO FAR!
    THE REWARDS OF YOUR TRAJECTORY IS SCORED ON HOW MANY FIELDS YOU ARE ABLE TO UPDATE WITH A QUESTION.
    """
)

read_answer = ChatPromptTemplate.from_template(
    """
    You are an AI system that analyzes user responses and categorizes them based on a provided list of keys. Your task is to:
    
    1. Read the user's response.
    2. Identify the most relevant key from the given list.
    3. Extract important points from the response as bullet points.
    
    ---
    **User Response:**  
    {answer}
    
    **List of Keys:**  
    {keys}
    
    ---
    **Output Format (Strictly Follow This):**  
    [Selected Key]: [Bullet Point 1], [Bullet Point 2], [Bullet Point 3]...

    **Reward: **
    You will be rewarded for giving short bullet points that are medically accurate and professional terminology
    Here are some EXAMPLES:
        Answer: "My first name is Eashan"
        Output: first_name: Eashan

        Answer: "My last name is Vytla"
        Output: last_name: Vytla

        Answer: "I have had this cough and sore throat for about two weeks"
        Output: primary_complaint: Cough, Sore Throat**

        Answer: "I had a blood clot in my lungs and I have high blood pressure."
        Output: past_conditions: Pulmonary Embolism, Hypertension
    
    ---
    **Now, provide the output following the exact format above.**
    """
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
                | question_model
                | output_parser
                )

answer_chain = (RunnableMap({
                    "keys": lambda _: list(flattened.keys()),
                    "answer": lambda x: x['user_input']
                })
                | read_answer
                | answer_model
                | output_parser
                )

check_clar = (
    check_clar_prompt
    | answer_model
    | output_parser
)

clarification_chain = (
    clarification_prompt
    | answer_model
    | output_parser
    | RunnableLambda(lambda x: x if x != "NO_CLARIFICATION_NEEDED" else "")
)

process_clarification_chain = (
    process_clarification
    | answer_model
    | output_parser
)

times = {"LLM-1": 0.0, "LLM-2": 0.0, "LLM-3": 0.0, "Whisper": 0.0}

def receive_data(user_input, json_state, traj):
    if not json_state:
        json_state = json.dumps(flattened)
        json_state_dict = flattened
    else:
        json_state_dict = json.loads(json_state)
    question = traj[-1] if len(traj) > 0 else ""

    str = ""
    json_str = ""
    
    if question != "":
        print(f"User input: {user_input}")
        times["LLM-1"] = time.time()
        answer_output = answer_chain.invoke({"user_input": user_input, "keys": json_state_dict})

        traj += "State transition: " + answer_output + "\n"

        times["LLM-1"] -= time.time()

        # chat_history += "User Answer: " + answer_output + "\n"

        key, bullets = parse_output(answer_output)
        if key in flattened:
            print(f"DEBUG: Updated {key}: {bullets}")
            str = f"Updating {key}: {bullets}"
            json_state_dict[key] = bullets
    

        json_str = json.dumps(json_state_dict, indent=2)

        times["LLM-2"] = time.time()
        
        clarification = check_clar.invoke(answer_output)

        times["LLM-2"] -= time.time()

        times["LLM-3"] = time.time()

        # if clarification.strip() == "NO_CLARIFICATION_NEEDED":
        if True:
            print("NO CLARIFICATION")
            question = question_chain.invoke({"state": json_str, "current_trajectory": traj})
        else:
            print("CLARIFICATION")
            question = clarification_chain.invoke({"clarification": clarification, "user_input": user_input, "question": question})

        times["LLM-3"] -= time.time()
    else:
        json_str = json.dumps(json_state_dict, indent=2)
        str = "Asked first question..."
        question = question_chain.invoke({"state": json_str, "current_trajectory": traj})
    
    if any(value == "None" for value in json_state_dict.values()):
    # if False:
        state = 0
    else:
        state = 1
        question = "You have completed the screening. Thank you for your time!"

    times["Whisper"] = time.time()
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=question
        )
    times["Whisper"] -= time.time()
    

    response.stream_to_file("speech.mp3")

    print(times)

    traj += "Chatbot Question: " + question + "\n"

    return {
        "status": "success",
        "question": str,
        "state": state,
        "json": json_str,
        "traj": traj
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
    print(output)
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