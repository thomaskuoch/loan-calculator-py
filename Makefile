build:
	docker build -t loan-calculator .

start:
	docker run -d --restart=always -p 8601:8601 --name loan-calculator loan-calculator

stop:
	docker rm -f loan-calculator