FROM python:3.8
WORKDIR /NSFWBot/
COPY . ./
RUN python3 -m pip install -vvv --no-cache-dir -r /NSFWBot/requirements.txt
EXPOSE 8084
CMD ["python3", "main.py"]
