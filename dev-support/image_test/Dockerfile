FROM centos:centos7.3

RUN mkdir /etc/yum.repos.d/bak;
    mv /etc/yum.repos.d/CentOS* /etc/yum.repos.d/bak;
    curl http://mirrors.aliyun.com/repo/Centos-7.repo > /etc/yum.repos.d/aliyun.repo;
    curl http://mirrors.163.com/.help/CentOS7-Base-163.repo > /etc/yum.repos.d/163.repo;
ADD mongodb.repo /etc/yum.repos.d/

RUN yum clean all;
    yum install initscripts -y;
    yum install epel-release -y;
    yum install python-pip -y;
    yum install mongodb-org-shell -y;
    pip install mongoengine;
    yum groupinstall "Development Tools" -y;
    yum install tmux -y;
    yum install vim -y;
