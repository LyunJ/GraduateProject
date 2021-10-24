FROM python:3.7.7
WORKDIR /usr/src/app
COPY . .
RUN pip3 install -r requirements.txt

EXPOSE 8001
CMD python manage.py runserver 0.0.0.0:8001 && cd kafka && python save_data_to_mongodb.py bad_acc_label