
# Secure API Platform

## Architecture

Client → Kong (JWT + RateLimit + IP Restrict + Custom Lua) → User Service → SQLite

## Features

- Auto DB bootstrap
- Auto admin creation
- JWT authentication
- Public route bypass
- Rate limiting
- IP restriction
- Custom Lua header injection
- Helm ready
- Kubernetes ready
- Terraform ready

## Build Docker

eval $(minikube docker-env)
cd microservice
docker build -t user-service:latest .

## Deploy

helm install user-service ./helm/user-service
helm install kong ./helm/kong
