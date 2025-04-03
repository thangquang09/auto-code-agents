import streamlit as st 
from workflow import *

@st.cache_resource
def app():
    return get_app()

st.set_page_config(page_title="Code Generation Workflow", page_icon=":guardsman:", layout="wide")

def main():
    app_instance = app()
    st.title("Code Generation Workflow")
    st.write("This application generates code based on requirements and tests it.")
    st.write("### Input Requirements")
    requirement = st.text_area("Enter your requirements here:", height=200)
    st.write("### Execution Results")
    
    if requirement:
        initial_state: State = {
                "requirement": requirement,
                "test_cases": [],
                "execution_results": [],
                "errors": [],
                "iteration": 0
            } 
        if st.button("Run Workflow"):
            
            with st.spinner("Running the workflow..."):
                result = app_instance.invoke(initial_state)
            
            st.write("Final Code:")
            st.code(result["code"], language="python")
            # st.write("Execution Results:", result["execution_results"])
            # st.write("Errors:", result["errors"])
    else:
        st.warning("Please enter the requirements before running the workflow.")
            
if __name__ == "__main__":
    main()