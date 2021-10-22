FROM python:3.7.7
WORKDIR /usr/src/app
COPY . .
RUN pip3 install -r requirements.txt 
WORKDIR ./labelService
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
EXPOSE 8001