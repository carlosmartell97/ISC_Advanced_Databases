# not yet a working image...
FROM ubuntu:14.04
RUN echo "creating Twitter Analysis image..."
RUN mkdir Twitter_Analysis
RUN mkdir Twitter_Analysis/csv
RUN mkdir Twitter_Analysis/txt
RUN mkdir Twitter_Analysis/png
ADD main.py /Twitter_Analysis/main.py
ADD kivy_window.py /Twitter_Analysis/kivy_window.py
ADD Global.py /Twitter_Analysis/Global.py
ADD timeline.py /Twitter_Analysis/timeline.py
ADD neo4j-desktop-offline-1.0.22-x86_64.AppImage /Twitter_Analysis/neo4j-desktop-offline-1.0.22-x86_64.AppImage

RUN apt-get update
RUN apt-get -y install python-pip
RUN pip install --upgrade pip
RUN apt-get install -y python-kivy
RUN pip install --ignore-installed tweepy
RUN apt-get -y install python-dev
RUN apt-get -y install python-tk
RUN pip install matplotlib
RUN pip install unidecode
RUN pip install wordcloud
RUN pip install py2neo
RUN apt-get install fuse
RUN modprobe fuse
RUN groupadd fuse
RUN user="$(whoami)"
RUN usermod -a -G fuse $user
RUN apt-get -y install libgtk2.0
RUN apt-get -y install libnss3
RUN apt-get install libdbus-glib-1-2
