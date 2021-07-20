# 更新go-cqhttp
rm -fr go-cqhttp
#git clone https://github.com/Mrs4s/go-cqhttp.git
cp Dockerfile config.yml go-cqhttp/
cd go-cqhttp/
docker build -t  go-cqhttp:latest
docker kill qq
docker rm qq
docker run --name qq -d -it -p 5700:5700  --restart always  go-cqhttp:latest
