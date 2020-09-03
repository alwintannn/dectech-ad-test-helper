# Dockerfile to create a Docker image for the Ad Test helper Streamlit app

# Creates a layer from the Docker image that already set up opencv on Python 3.6
FROM yoanlin/opencv-python3:latest
# Copy all the files from the folders the Dockerfile is in to the container app folder
COPY . /app
# Set working directory to app
WORKDIR /app
# Install the modules specified in the requirements.txt
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
# The port on which a container listens for connections
EXPOSE 8501
# The command that run the app
CMD streamlit run app.py