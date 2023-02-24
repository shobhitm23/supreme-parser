FROM python:3.9

# Create a new directory and set it as the working directory
RUN mkdir /app
WORKDIR /app

COPY /app .

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8279"]