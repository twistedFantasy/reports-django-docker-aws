ARG IMAGE
FROM $IMAGE
LABEL maintainer="Denis Sventitsky <denis.sventitsky@gmail.com> / Twisted Fantasy <twisteeed.fantasy@gmail.com>"

ARG APP_PATH

ENV PYTHONUNBUFFERED 1

RUN mkdir -p $APP_PATH
WORKDIR $APP_PATH

RUN pip install pipenv==2018.11.26

COPY srt/Pipfile srt/Pipfile.lock ./
RUN pipenv install --system --deploy
COPY srt/ .

CMD python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000
