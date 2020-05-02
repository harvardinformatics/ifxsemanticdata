FROM python:3.6

EXPOSE 80
RUN apt-get update -y

ENV DJANGO_SETTINGS_MODULE=ifxsemanticdata.settings
RUN pip install --upgrade pip && \
    pip install git+https://github.com/harvardinformatics/ifxurls.git && \
    pip install Django==2.1.7 && \
    pip install djangorestframework==3.8.1 && \
    pip install requests && \
    pip install nose && \
    pip install Sphinx>2 && \
    pip install sphinx-py3doc-enhanced-theme>=2.4.0 && \
    pip install recommonmark==0.5.0

WORKDIR /app

CMD ./manage.py makemigrations && \
    ./manage.py migrate && \
    ./manage.py runserver 0.0.0.0:80 --insecure

