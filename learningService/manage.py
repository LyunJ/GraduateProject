#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


# 우리가 해야 할것
# 1. classification 모델 학습(내껀 학습시키지 않음)
# 2. model save해서 넘겨주기

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learningService.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

# 내가 해야할것
# labeling 서비스에다가 모델 넣기
# predict 코드 짜기

# data가 image/label 형식으로 들어올텐데
# 이걸 학습시키는 코드를 작성하고, 학습이 완료되면 파라미터를 저장해서 압축해서 보내줘야함
# zipfile이라는 모듈이 존재한다고 하네요
# 파라미터 저장은 tensorflow.keras.models.save_model(경로) 넣으면 저장됨

if __name__ == '__main__':
    main()
