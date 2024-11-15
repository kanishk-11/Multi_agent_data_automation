import chainlit as cl
import pandas as pd
from decouple import config
from prompts import Prompts
from chat_manager import ChatManager

chat_manager = ChatManager()

CONFIG_LIST = [
    {
        "model": "gpt-4o-mini",
        "api_key": config('OPENAI_API_KEY'),
    }
]

def is_termination_message(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

@cl.on_chat_start
async def on_chat_start():
    files = None
    while files == None:
        files = await cl.AskFileMessage(
            content="Welcome to your Flight Data Assistant! Let's begin with uploading the CSV files that need to be ingested.",
            accept={"text/plain": [".csv"]},
            max_size_mb=3,
            max_files=2,
        ).send()

    if len(files) < 2:
        await cl.Message(content="Please upload 2 files").send()
        return

    for file in files:
        chat_manager.file_names.append(file)

    actions_start_standardization = [
        cl.Action(
            name="Start Ingestion",
            value="Standardizing Data",
            description="Click to Start Ingestion"
        )
    ]

    await cl.Message(
        content="Start automatic data standardization by clicking on this button:",
        actions=actions_start_standardization,
    ).send()

@cl.action_callback("Start Ingestion")
async def on_action(action: cl.Action):
    # Create a loading message
    loading_msg = cl.Message(content="⌛ Ingesting and standardizing data, please wait...")
    await loading_msg.send()

    try:
        message = Prompts.get_problem_prompt(
            chat_manager.file_names,
            Prompts.FLIGHT_COLUMN_TYPES,
            Prompts.ORIGINAL_COLUMNS,
        )
        
        await chat_manager.start_chat(
            message=message,
            llm_config = {
                "timeout": 60,
                "cache_seed": 42,
                "config_list": CONFIG_LIST,
                "temperature": 0,
            },
            system_message=Prompts.ClEANR_SYSTEM_MESSAGE,
            termination_message=is_termination_message,
            termination_notice=Prompts.TERMINATION_NOTICE
        )

        # Remove the loading message
        await loading_msg.remove()

        actions_show_cleaned_table = [
            cl.Action(
                name="Get Ingested Data",
                value="Ingesting Data",
                description="Download Ingested Data"
            )
        ]

        await cl.Message(
            content="Download the ingested table:",
            actions=actions_show_cleaned_table,
        ).send()
        
        await cl.Message(content="Data Standardization Completed ✅ You Can Now Query Your Data!").send()

    except Exception as e:
        # Remove the loading message and show error
        await loading_msg.remove()
        await cl.Message(content=f"❌ An error occurred during data processing: {str(e)}").send()

@cl.action_callback("Get Ingested Data")
async def on_action(action: cl.Action):
    # Add loading state for data retrieval
    loading_msg = cl.Message(content="⌛ Preparing your cleaned data...")
    await loading_msg.send()

    try:
        elements = [
            cl.File(
                name="cleaned_data.csv",
                path=f"{Prompts.CLEANED_DATA_STORAGE_DIRECTORY}/cleaned_data.csv",
                display="inline",
            ),
        ]
        await loading_msg.remove()
        await cl.Message(
            content="Here's your cleaned data:",
            elements=elements
        ).send()
    except Exception as e:
        await loading_msg.remove()
        await cl.Message(content=f"❌ Error retrieving cleaned data: {str(e)}").send()

@cl.on_message
async def receive_user_requirement(message: cl.Message):
    # Add loading state for query processing
    loading_msg = cl.Message(content="⌛ Processing your query...")
    await loading_msg.send()

    try:
        data = pd.read_csv(f"{Prompts.CLEANED_DATA_STORAGE_DIRECTORY}/cleaned_data.csv")
        message_in = Prompts.get_query_prompt(
            dataframe=data.head(),
            path="cleaned_data.csv",
            question=message.content,
        )
        await chat_manager.start_chat(
            message=message_in,
            llm_config = {
                "timeout": 60,
                "cache_seed": 42,
                "config_list": CONFIG_LIST,
                "temperature": 0,
            },
            system_message=Prompts.QUERY_SYSTEM_MESSAGE,
            termination_message=is_termination_message,
            termination_notice=Prompts.TERMINATION_NOTICE,
            print_output=True
        )
        await loading_msg.remove()
    except Exception as e:
        await loading_msg.remove()
        await cl.Message(content=f"❌ Error processing query: {str(e)}").send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)