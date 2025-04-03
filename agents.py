from langgraph.graph import END, StateGraph
from typing import TypedDict, Dict, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from utils import extract_function_signature
from settings import MAX_ITERATIONS

import os
import ast
import logging
import re

logging.basicConfig(level=logging.INFO)
current_dir = os.path.dirname(os.path.abspath(__file__))
llm = None


def get_llm(force_new: bool = False):
    """Initialize the LLM model"""
    global llm
    
    if llm is None or force_new:
        
        load_dotenv()
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if GOOGLE_API_KEY is None:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables.")
        
        logging.info("Initializing LLM model...")
        llm = init_chat_model(
            model="gemini-2.0-flash", 
            model_provider="google_genai", 
            GOOGLE_API_KEY=GOOGLE_API_KEY
        )
    return llm


def load_prompt(prompt_path: str) -> dict:
    """Load a prompt from a file"""
    with open(prompt_path, 'r') as f:
        content = f.read()
        local_vars = {}
        exec(content, {}, local_vars)
        return {
                "system_message": local_vars["SYSTEM_MESSAGE"],
                "user_message": local_vars["USER_MESSAGE"]
            }

class State(TypedDict):
    requirement: str  # mô tả về bài toán cần giải
    code: str  # solution generate từ programmer
    test_cases: List[Dict]  # test cases được tạo ra từ tester
    execution_results: List[Dict]  # kết quả của từng test case
    errors: List[str]  # danh sách các lỗi
    iteration: int  # số lần lặp gỡ lỗi
    

def process_output(response: str) -> str:
    if not response:
        return None
    match = re.search(r'```python(.*?)```', response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def programmer(state: State) -> State:
    path_to_prompt = os.path.join(current_dir, "prompts", "prompt_programmer.py")
    messages = load_prompt(path_to_prompt)
    llm = get_llm()
    
    # Prompt
    system_message = messages["system_message"]
    user_message = messages["user_message"].format(requirement=state["requirement"])
    
    prompt = [
        SystemMessage(system_message), 
        HumanMessage(user_message)
    ]
    
    # gọi llm
    code = llm.invoke(prompt).content
    
    # Tách code
    code = process_output(code)
    if not code:
        raise ValueError("Generated code is empty.")
    
    state["code"] = code
    logging.info(f"Generated code: {code}")
    return state


def tester(state: State) -> State:
    path_to_prompt = os.path.join(current_dir, "prompts", "prompt_tester.py")
    messages = load_prompt(path_to_prompt)
    llm = get_llm()
    
    requirement = state["requirement"]
    code = state["code"]
    test_cases = []
    
    # Tách ra các tham số của hàm và kiểu trả về
    function_signature = extract_function_signature(code)
    if function_signature is None:
        function_signature = "def solution(*args) -> Any:"
    
    # Prompt
    system_message = messages["system_message"].format(
        max_test_cases=MAX_ITERATIONS,
        function_signature=function_signature
    )
    
    user_message = messages["user_message"].format(
        requirement=requirement,
        code=code
    )
    
    prompt = [
        SystemMessage(system_message), 
        HumanMessage(user_message)
    ]
    
    response = llm.invoke(prompt).content
    
    # Tách test cases
    try:
        logging.info(f"Raw test cases response: {response}")
        response = process_output(response)
        # Lấy từ text thành python object
        test_cases = ast.literal_eval(response.strip())
        
        logging.info(f"Generated test cases: {test_cases}")
        state["test_cases"] = test_cases
    except Exception as e:
        logging.error(f"Error generating test cases: {str(e)}")
        state["errors"].append(f"Error generating test cases: {str(e)}")
        state["test_cases"] = []
    
    return state
    
    
def executor(state: State) -> State:
    code = state["code"]
    test_cases = state.get("test_cases", [])
    execution_results = []
    
    if not test_cases:
        state["errors"].append("No test cases available.")
        state["execution_results"] = []
        return state
    
    # tạo namespace cho exec
    local_vars = {}
    
    # Chạy code với hàm exec
    try:
        exec(code, globals(), local_vars)
    except Exception as e:
        state["errors"].append(f"Execution error: {str(e)}")
        return state
    
    solution = local_vars.get("solution")
    if not solution:
        state["errors"].append("No solution function found in the code.")
        return state
    
    # Chạy test cases
    for test_case in test_cases:
        args = test_case["args"]
        expected_output = test_case["expected_output"]
        # Chạy hàm solution với args
        try:
            result = solution(*args)
            execution_results.append({
                "args": args,
                "expected_output": expected_output,
                "result": result,
                "pass": result == expected_output
            })
        except Exception as e:
            execution_results.append({
                "args": args,
                "expected_output": expected_output,
                "result": None,
                "pass": False,
                "error": str(e)
            })
            state["errors"].append(f"Execution error: {str(e)}")
    state["execution_results"] = execution_results
    
    # logging có bao nhiêu test case pass trên tổng số test case
    total_cases = len(execution_results)
    passed_cases = sum(1 for result in execution_results if result["pass"])
    logging.info(f"Execution results: {passed_cases}/{total_cases} test cases passed.")
    return state
    
    
def debugger(state: State) -> State:
    llm = get_llm()
    path_to_prompt = os.path.join(current_dir, "prompts", "prompt_debugger.py")
    messages = load_prompt(path_to_prompt)
    
    requirement = state["requirement"]
    code = state["code"]
    test_cases = state["test_cases"]
    execution_results = state["execution_results"]
    
    # lấy ra các test case thất bại
    failed_results = [result for result in execution_results if not result["pass"]]
    if not failed_results:
        # nếu không có test case nào bị fail thì không cần debug
        return state
    
    # Chuẩn bị thông tin cho llm
    failed_info = ""
    for i, result in enumerate(failed_results):
        failed_info += (
            f"Test case {i+1}:\n"
            f"Args: {result['args']}\n"
            f"Expected Output: {result['expected_output']}\n"
            f"Actual Result: {result['result']}\n"
            f"Error: {result.get('error', 'No error')}\n"
        )
    
    # Prompt
    system_message = messages["system_message"]
    user_message = messages["user_message"].format(
        requirement=requirement,
        code=code,
        failed_info=failed_info
    )
    prompt = [
        SystemMessage(system_message), 
        HumanMessage(user_message)
    ]
    
    # goi llm
    response = llm.invoke(prompt).content
    
    # Thực hiện tách code và test cases từ response
    logging.info(f"Raw debugger response: {response}")
    try:
        # Tìm phần code
        code_match = re.search(r'Code:\s*```python\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            new_code = code_match.group(1).strip()
            state["code"] = new_code
            logging.info(f"Debugger updated code: {new_code}")
            
        # Tìm phần test cases
        test_match = re.search(r'Test Cases:\s*```python\s*(.*?)\s*```', response, re.DOTALL)
        if test_match:
            test_str = test_match.group(1).strip()
            new_test_cases = ast.literal_eval(test_str)
            state["test_cases"] = new_test_cases
            logging.info(f"Debugger updated test cases: {new_test_cases}")
            
        state["iteration"] += 1
    except Exception as e:
        state["errors"].append(f"Debugger failed to process response: {str(e)}")
        
    return state
    

if __name__ == "__main__":
    
    with open("test.txt", 'r') as f:
        requirement = f.read()

    initial_state: State = {
        "requirement": requirement,
        "test_cases": [],
        "execution_results": [],
        "errors": [],
        "iteration": 0
    } 
    
    programmer_state = programmer(initial_state)
    tester_state = tester(programmer_state)
    executor_state = executor(tester_state)
    
    debugger_state = debugger(executor_state)
    
    print("Final Code:", debugger_state["code"])