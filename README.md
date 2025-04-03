# Auto Code Agents

Auto Code Agents is a workflow-based application that generates code based on user requirements, tests it, and iteratively improves it through debugging. The application leverages LLMs (Large Language Models) to automate the process of programming, testing, and debugging.

## Features
- Generate code based on user requirements.
- Automatically create test cases for the generated code.
- Execute the code and validate it against the test cases.
- Debug and improve the code iteratively.

## Prerequisites
1. Python 3.12 installed on your system.
2. Docker installed if you prefer running the application in a container.
3. A `.env` file containing your `GOOGLE_API_KEY` for LLM integration.

### Example `.env` file:
```
GOOGLE_API_KEY=your_google_api_key_here
```

---

## Running the Application

### Option 1: Using Python Virtual Environment

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd auto-code-agents
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   streamlit run src/app.py
   ```

5. **Access the Application**:
   Open your browser and navigate to `http://localhost:8501`.

---

### Option 2: Using Docker

1. **Pull the Docker Image**:
   ```bash
   docker pull auto_code_agents:v1.0
   ```

2. **Run the Docker Container**:
   ```bash
   docker run --env-file .env -d --name auto_code_agents_container -p 9090:8501 auto_code_agents:v1.0
   ```

3. **Access the Application**:
   Open your browser and navigate to `http://localhost:9090`.

---

## Notes
- Ensure your `.env` file is correctly configured with a valid `GOOGLE_API_KEY`.
- If you encounter any issues, check the logs for debugging:
  - For Python: Logs will appear in the terminal.
  - For Docker: Use `docker logs auto_code_agents_container`.

Enjoy using Auto Code Agents!
