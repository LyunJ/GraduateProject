FROM python:3.7.7
WORKDIR /usr/src/app
COPY . .
RUN pip3 install -r requirements.txt

EXPOSE 8003
CMD python manage.py runserver 0.0.0.0:8003 && cd kafka && python save_image_to_local.py good_acc_label