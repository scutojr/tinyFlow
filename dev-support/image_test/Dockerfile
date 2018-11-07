FROM centos:centos7.3

RUN mkdir /etc/yum.repos.d/bak
RUN mv /etc/yum.repos.d/CentOS* /etc/yum.repos.d/bak
RUN curl http://mirrors.aliyun.com/repo/Centos-7.repo > /etc/yum.repos.d/aliyun.repo
RUN curl http://mirrors.163.com/.help/CentOS7-Base-163.repo > /etc/yum.repos.d/163.repo
ADD mongodb.repo /etc/yum.repos.d/
RUN yum clean all

RUN yum install initscripts -y
RUN yum install epel-release -y
RUN yum install python-pip -y
RUN yum install mongodb-org-shell -y
RUN pip install mongoengine
RUN yum groupinstall "Development Tools" -y
RUN yum install tmux -y