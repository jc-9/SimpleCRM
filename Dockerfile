# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Create a dedicated directory for persistent data
RUN mkdir -p /app/data

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# ENV FLASK_DEBUG=1 # Uncomment for debugging, but remove for production

# Expose the port that the Flask app will run on (5001, as configured in app.py)
EXPOSE 5001

# Run the Flask application
# CMD ["flask", "run"] # You could use this if you were running with 'flask run'
CMD ["python", "app.py"]