FROM python:3.13-alpine

# Set the working directory
WORKDIR /code

# Update the package repository and install LibreOffice and necessary dependencies
RUN apk add --no-cache libreoffice

# Copy the requirements file and install the Python dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application into the container
COPY ./app /code/app

# Command to run the application
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
