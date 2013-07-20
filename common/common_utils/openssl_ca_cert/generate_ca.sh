#!/bin/sh

#selfpath=$(cd "$(dirname "$0")"; pwd)


mkdir -p ./demoCA/private
mkdir -p ./demoCA/newcerts
touch ./demoCA/index.txt
echo 00 > ./demoCA/serial

#CA中心生成私钥
echo "generate ca key..."
if
openssl genrsa -out CA.key 2048
then
	echo "generate ca key ok."
else
	echo "generate ca key failed!"
	exit 1;
fi

#CA中心生成公钥，暂定36500天
echo "generate ca crt..."
SUBJECT_CA='/C=cn/ST=FuJian/L=Xiamen/O=Behill/OU=Python/CN=CA中心名称如ca.req.com/emailAddress=280632307@qq.com'
if
openssl req -new -x509 -days 36500 -subj $SUBJECT_CA  -key CA.key -out CA.crt
then
	echo "generate ca crt ok."
else
	echo "generate ca crt failed!"
	exit 1;
fi

#服务器生成私钥
echo "generate server key..."
if
openssl genrsa -out server.key 2048
then
	echo "generate server key ok."
else
	echo "generate server key failed!"
	exit 1;
fi

#服务器生成证书请求文件
SUBJECT_SER='/C=cn/ST=FuJian/L=Xiamen/O=Behill/OU=Python/CN=服务器名称如www.jg.com/emailAddress=280632307@qq.com'
echo "generate server csr..."
if
openssl req -new -subj $SUBJECT_SER -key server.key -out server.csr
then
	echo "generate server csr ok."
else
	echo "generate server csr failed!"
	exit 1;
fi


#CA中心根据服务器的证书请求文件server.csr生成对应的证书server.crt
echo "generate server cert..."
if
openssl ca -in server.csr -out server.crt -cert CA.crt -keyfile CA.key <<!
y
y
!
then
	echo "generate server cert ok."
else
	echo "generate server cert failed!"
	exit 1;
fi

rm -rf ./demoCA
rm ./server.csr


#openssl pkcs12 -passout pass:520behill -export -inkey server.key -in server.crt -out server.p12

exit 0;