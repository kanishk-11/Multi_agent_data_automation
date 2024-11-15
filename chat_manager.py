import chainlit as cl
from autogen import ConversableAgent, GroupChat, GroupChatManager
from prompts import Prompts
from agents import AgentFactory
 
class ChatManager:
    print_output = False
    def __init__(self):
        self.file_names = []
 
    @staticmethod
    def chat_new_message(self, message, sender):
        if sender.name == "Code_Executor" and self.print_output:
            content = message.split("\n") 
            new_message = []
            for i in content:
                if "exitcode" in i:
                    continue
                new_message.append(i)
            cl.run_sync(
                cl.Message(
                    content="\n".join(new_message),
                    author=sender.name,
                ).send()
            )
 
    async def start_chat(self, message, llm_config, system_message, termination_message, termination_notice, print_output = False):
        ConversableAgent.print_output = print_output
        ConversableAgent._print_received_message = self.chat_new_message
 
        agent_factory = AgentFactory()
        user_proxy = agent_factory.create_user_proxy(termination_message, termination_notice)
        coder = agent_factory.create_coder(system_message,termination_message, llm_config, termination_notice)
        executor = agent_factory.create_executor(Prompts.CLEANED_DATA_STORAGE_DIRECTORY)
 
        groupchat = GroupChat(
            agents=[coder, executor],
            messages=[],
            max_round=50,
            speaker_selection_method="round_robin",
            allow_repeat_speaker=False,
        )
        
        manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        user_proxy.initiate_chat(manager, message=message)
 
        return user_proxy, manager