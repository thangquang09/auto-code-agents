import ast

def extract_function_signature(code):
    """Extract the function signature from code to understand input/output types"""
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'solution':
                # Get function parameters
                params = []
                for arg in node.args.args:
                    # Get parameter name and annotation if exists
                    param_name = arg.arg
                    param_type = ""
                    if arg.annotation:
                        param_type = ast.unparse(arg.annotation)
                    params.append(f"{param_name}: {param_type}")
                
                # Get return type if exists
                returns = ""
                if node.returns:
                    returns = f" -> {ast.unparse(node.returns)}"
                
                # Construct signature
                return f"def solution({', '.join(params)}){returns}"
        return "Function signature not found"
    except:
        return "Could not parse code"
    
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
        