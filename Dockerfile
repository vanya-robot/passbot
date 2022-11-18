FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1
WORKDIR /passbot_prod
COPY . /passbot_prod
RUN pip install --upgrade pip
RUN pip install -r requirements.txt