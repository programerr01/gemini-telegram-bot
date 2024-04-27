FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt

# Install Python dependencies using pip
RUN pip install -r requirements.txt

# Copy your application code
COPY . .


# Set the command to run your application (modify as needed)
CMD [ "python", "main.py" ]
