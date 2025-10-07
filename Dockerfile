FROM python:3.10

COPY requirements.txt ./ 

RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN apt-get update && apt-get install -y openjdk-17-jdk

COPY . ./

# run the project
CMD ["python3", "-m", "main"]

