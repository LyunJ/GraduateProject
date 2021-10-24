FROM python:3.7.7
WORKDIR /usr/src/app
COPY . .
RUN pip3 install -r requirements.txt

CMD python save_data_to_mongodb.py bad_acc_label