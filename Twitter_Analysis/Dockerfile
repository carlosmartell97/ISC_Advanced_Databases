FROM sequenceiq/hadoop-docker
RUN echo "creating Twitter Analysis image..."
RUN mkdir Twitter_Analysis
RUN mkdir Twitter_Analysis/csv
RUN mkdir Twitter_Analysis/txt
RUN mkdir Twitter_Analysis/png
ADD tweet_dumper.py /Twitter_Analysis/tweet_dumper.py
ADD kivy_window.py /Twitter_Analysis/kivy_window.py
ADD Global.py /Twitter_Analysis/Global.py

# installing python 3.0
# RUN yum install zlib -y
# RUN yum groupinstall "Development tools" -y
RUN yum install wget -y
RUN wget https://www.python.org/ftp/python/3.0/Python-3.0.tgz
RUN tar -xzvf Python-3.0.tgz
RUN cd Python-3.0 && ./configure --prefix=/usr/local && make altinstall
# CMD alias python='python2.7'
RUN yum install epel-release -y
RUN yum install python-pip -y

# RUN sudo yum install python-setuptools -y
# RUN sudo easy_install pip

# pip install python-kivy
# RUN pip install kivy
# RUN pip install unidecode
# pip install tweepy
# pip install wordcloud

# pip install py2neo

# cat /etc/centos-release
# rpm --query centos-release
