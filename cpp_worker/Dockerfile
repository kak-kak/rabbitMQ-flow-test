FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y cmake libboost-all-dev libssl-dev librabbitmq-dev build-essential git libjsoncpp-dev iputils-ping

RUN ln -s /usr/include/jsoncpp/json/ /usr/include/json

RUN git clone https://github.com/alanxz/SimpleAmqpClient.git /SimpleAmqpClient && \
    cd /SimpleAmqpClient && \
    cmake . && \
    make && \
    make install
RUN ln -s /SimpleAmqpClient/build/libSimpleAmqpClient.so.7 /usr/lib/libSimpleAmqpClient.so.7


COPY CMakeLists.txt /usr/src/CMakeLists.txt
COPY main.cpp /usr/src/main.cpp

WORKDIR /usr/src
RUN mkdir build 

WORKDIR /usr/src/build
RUN cmake .. && make

RUN ldconfig


ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH


CMD ["sh", "-c", "sleep 5 && ping -c 10 rabbitmq && /usr/src/build/cpp_worker"]
# CMD [ "bash" ]