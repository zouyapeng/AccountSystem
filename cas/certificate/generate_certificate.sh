#!/bin/bash
cbs_key=private/cbs_ca_cert.key
cbs_crt=cbs_ca_cert.crt

Country=CN
State=Shanghai
Locality=Shanghai
Organization=Linux
Common=0.0.0.0
Passwd=123456
Email=xx@xxx.com
p12=0

while getopts n:c:s:l:o:m:p:e:w name
do

case ${name} in
    n)
        Name=$OPTARG
        ;;
    c)
        Country=$OPTARG
        ;;
    s)
        State=$OPTARG
        ;;
    l)
        Locality=$OPTARG
        ;;
    o)
        Organization=$OPTARG
        ;;
    m)
        Common=$OPTARG
        ;;
    p)
        Passwd=$OPTARG
        ;;
    e)
        Email=$OPTARG
        ;;
    w)
        p12=1
        ;;
esac

done

pkcs12(){
    expect -c "
    spawn openssl pkcs12 -export -inkey certs/${Name}.key -in certs/${Name}.crt -CAfile ${cbs_crt} -out certs/${Name}.p12
    expect {
                    \"Enter*Password:\" {send \"$Passwd\r\"; exp_continue}
                    \"Verifying*Password:\" {send \"$Passwd\r\"; exp_continue}
            }
    "
}


if [ ! ${Name} ];then
echo -1
exit 1
fi

if [ ${p12} = 1 ];then
pkcs12
echo certs/${Name}.p12
exit 0
fi




Common=$Name

openssl genrsa -out certs/${Name}.key 2048

expect -c "
spawn openssl req -config ssl.cnf -new -nodes -out certs/${Name}.csr -key certs/${Name}.key
expect {
\"Country Name*\" {send \"$Country\r\"; exp_continue}
\"*full name*\" {send \"$State\r\"; exp_continue}
\"*eg, city*\" {send \"$Locality\r\"; exp_continue}
\"eg, company*\" {send \"$Organization\r\"; exp_continue}
\"eg, section*\" {send \"$Organization\r\"; exp_continue}
\"*hostname*\" {send \"$Common\r\"; exp_continue}
\"Email*\" {send \"$Email\r\"; exp_continue}
\"A challenge password*\" {send \"\r\"; exp_continue}
\"An optional company *\" {send \"\r\"; exp_continue}
}
"

expect -c "
    spawn openssl ca -config ssl.cnf -keyfile ${cbs_key} -cert ${cbs_crt} -out certs/${Name}.crt -outdir certs -infiles certs/${Name}.csr
    expect {
    \"*certificate?*\" {send \"y\r\"; exp_continue}
    \"*commit?*\" {send \"y\r\"; exp_continue}
    }
    "
serial=`cat serial.old`

pkcs12

echo $serial
echo certs/${Name}.p12
exit 0