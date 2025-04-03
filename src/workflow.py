from langgraph.graph import END, StateGraph
from typing import TypedDict, Dict, List
from agents import *
from settings import MAX_ITERATIONS


def get_app(MAX_ITERATIONS: int = MAX_ITERATIONS) -> StateGraph:
    # workflow
    workflow = StateGraph(State)

    # thêm node vào
    workflow.add_node("programmer", programmer)
    workflow.add_node("tester", tester)
    workflow.add_node("executor", executor)
    workflow.add_node("debugger", debugger)

    # định nghĩa các cạnh
    workflow.add_edge("programmer", "tester")
    workflow.add_edge("tester", "executor")

    def route_execution(state: State):   
        # Nếu vượt quá lố lần kiểm tra thì cứ trả về state hiện tại
        if state["iteration"] >= MAX_ITERATIONS or state["test_cases"] == []:
            return "end" 
        
        if state["execution_results"] and all(result["pass"] for result in state["execution_results"]):
            return "end"  # tất cả các test case đều pass
        else:
            return "debugger"  # nếu có lỗi, tiến hành debug
        
    workflow.add_conditional_edges("executor", route_execution, {"end": END, "debugger": "debugger"})
    workflow.add_edge("debugger", "executor") # đi từ debugger quay lại executor

    # khởi tạo state
    workflow.set_entry_point("programmer")

    app = workflow.compile()

    return app

with open("test.txt", 'r') as f:
        requirement = f.read()
    
initial_state: State = {
    "requirement": requirement,
    "test_cases": [],
    "execution_results": [],
    "errors": [],
    "iteration": 0
} 

app = get_app()

result = app.invoke(initial_state)
print("Final Code:", result["code"])
print("Execution Results:", result["execution_results"])
print("Errors:", result["errors"])