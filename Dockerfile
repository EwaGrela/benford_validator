FROM python:3
WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000:5000
CMD [ "python", "-u", "./app.py"]