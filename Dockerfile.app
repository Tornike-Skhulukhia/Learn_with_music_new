# Pull base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# install requirements
COPY requirements.txt .

RUN pip install -r requirements.txt


# # TIMEZONE - SET TO TBILISI TIMEZONE
# ENV TZ='Asia/Tbilisi'
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
