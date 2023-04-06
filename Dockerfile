FROM python:3.10
WORKDIR /app/
ADD ./app /app/
ADD ./requirements /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r base.txt
CMD [ "python3", "__main__.py" ]