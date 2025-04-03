FROM python:3.12

# Set the working directory
WORKDIR /app
# Copy the requirements file into the container
COPY requirements.txt .
# Install the dependencies
RUN apt-get update -y
RUN pip install --no-cache-dir -r requirements.txt
# copy src folder to the container
COPY src/ ./src/
# Expose the port the app runs on
EXPOSE 8501

CMD [ "streamlit", "run", "src/app.py" ]