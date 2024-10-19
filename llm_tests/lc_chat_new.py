from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnableMap, RunnablePassthrough
import os
import json

os.environ["OPENAI_API_KEY"] = ""

def docs2str(docs, title="Document"):
    """Useful utility for making chunks into context string. Optional, but useful"""
    out_str = ""
    for doc in docs:
        doc_name = getattr(doc, 'metadata', {}).get('Title', title)
        if doc_name: out_str += f"[Quote from {doc_name}] "
        out_str += getattr(doc, 'page_content', str(doc)) + "\n"
    return out_str

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

def parse_output(output):
    # Split the string into two parts: the key and the list of bullets
    key, bullets_string = output.split(":", 1)  # Split only at the first ':'
    
    # Strip whitespace from the key
    key = key.strip("[]").strip()
    
    # Split the bullets by commas and strip whitespace around them
    bullets = [bullet.strip("[]").strip() for bullet in bullets_string.split(",")]
    
    return key, bullets

def main():
    model = ChatOpenAI(model="gpt-4o-mini")
    with open('topics.json', 'r') as json_file:
        template_dict = json.load(json_file)

    flattened = flatten_dict(template_dict)

    #memory = ConversationBufferMemory()

    question_prompt = ChatPromptTemplate.from_template(
        "System"
        "You are a nurse. Ask a question to answer one or more of the keys with null values in this information\n{input}\n"
        "Ask the question conversationally. Limit to only ONE question! Make sure the conversation flows naturally.\n"
    )

    read_answer = ChatPromptTemplate.from_template(
        "System"
        "Chatbot question: {initial_output}"
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
        | RunnableLambda(lambda x: input(x) if x else x)
        | process_clarification
        | model
        | output_parser
    )

    while any(value == "None" for value in flattened.values()):
        json_str = json.dumps(flattened, indent=2)
        question_output = question_chain.invoke(json_str)
        
        print(question_output)
        user_input = input("Enter response: ")
        
        answer_output = answer_chain.invoke({"user_input": user_input, "question": question_output})
        
        key, bullets = parse_output(answer_output)
        if key in flattened:
            print(f"DEBUG: Updating {key}: {bullets}")
            flattened[key] = bullets
        
        clarification = check_clar.invoke(answer_output)
        while clarification.strip() != "NO_CLARIFICATION_NEEDED":
            print(clarification)
            user_input = input("Enter response: ")
            clarification = clarification_chain.invoke({"clarification": clarification, "user_input": user_input, "question": question_output})

if __name__ == "__main__":
    main()