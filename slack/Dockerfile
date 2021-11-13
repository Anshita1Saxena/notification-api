FROM python:3.6
LABEL maintainer="Anshita Saxena, anshita333saxena@gmail.com"
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install -r ./requirements.txt
EXPOSE 3000
CMD ["python", "slack_api.py"]
