DOCKER_PASS?=
DOCKER_USER?=
VERSION?=1.0
ORGANIZATION=unicef
IMAGE_NAME=rapidpro-webhooks
DOCKER_IMAGE_NAME?=${ORGANIZATION}/${IMAGE_NAME}
DOCKER_IMAGE?=${DOCKER_IMAGE_NAME}:${VERSION}


release:
	docker build -t ${DOCKER_IMAGE} .
	@echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
	docker tag ${DOCKER_IMAGE_NAME}:${VERSION} ${DOCKER_IMAGE_NAME}:latest
	docker push ${DOCKER_IMAGE_NAME}:${VERSION}
	docker push ${DOCKER_IMAGE_NAME}:latest
	docker images | grep ${DOCKER_IMAGE_NAME}


info:
	@echo 'docker images'
	@docker images | grep webhooks
	@echo '------------------'
	@echo 'docker containers'
	@docker ps -a | grep webhooks


ssh-backend:
	@docker exec -it rapidpro_webhooks /bin/sh
