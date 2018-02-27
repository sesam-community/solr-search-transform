FROM python:3-alpine
MAINTAINER Geir Ove Grønmo "geir.gronmo@sesam.io"
ADD ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./service /service
WORKDIR /service
EXPOSE 5000/tcp
ENTRYPOINT ["python"]
CMD ["service.py"]
