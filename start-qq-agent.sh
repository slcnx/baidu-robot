docker build -t  qq-agent ./ -f agent-Dockerfile
docker kill qq-agent
docker rm qq-agent
touch "G:/dockerfile/go-cqhttp/send.log"
docker run --restart always -d -p 9000:9000 -v "G:/dockerfile/go-cqhttp/send.log":/send.log --name qq-agent -it qq-agent
