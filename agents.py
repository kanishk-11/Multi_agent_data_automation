from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
 
class AgentFactory:
    @staticmethod
    def create_user_proxy(termination_message, termination_notice):
        return UserProxyAgent(
            name="User_Proxy",
            is_termination_msg=termination_message,
            human_input_mode="NEVER",
            system_message="A human admin.\n" + termination_notice,
            code_execution_config=False,
        )
 
    @staticmethod
    def create_coder(system_message,termination_message, llm_config, termination_notice, ):
        system_message = system_message + termination_notice
        
        return AssistantAgent(
            name="Python_Programmer",
            is_termination_msg=termination_message,
            system_message=system_message,
            llm_config=llm_config,
        )
    
    @staticmethod
    def create_executor(work_dir):
        local_executor = LocalCommandLineCodeExecutor(
            timeout=10,
            work_dir=work_dir,
        )
        
        return UserProxyAgent(
            name="Code_Executor",
            system_message="Executor. Execute the code written by the engineer and report the result.",
            human_input_mode="NEVER",
            code_execution_config={
                "last_n_messages": 3,
                "executor": local_executor,
            },
        )