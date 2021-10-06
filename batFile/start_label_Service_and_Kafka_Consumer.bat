@REM conda activate graduate
START python C:\Users\tedle\work\project\graduate\labelService\manage.py runserver 8001
START python C:\Users\tedle\work\project\graduate\labelService\kafka\save_data_to_mongodb.py
SET /P P=Press any key continue:
exit