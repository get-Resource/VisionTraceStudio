FROM postgres:16
RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list.d/debian.sources
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install postgresql-16-pgvector -y