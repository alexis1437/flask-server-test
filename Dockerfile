FROM python:3.6
WORKDIR /app
COPY app.py requirements.txt /app/
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 5200
CMD ["python3", "app.py"]
