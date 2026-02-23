# Secure API Platform using Kong on Kubernetes

------------------------------------------------------------------------

## Overview

This project implements a secure internal API platform running on
Kubernetes using Kong Gateway with Envoy as an edge/proxy layer.

It demonstrates:

-   JWT-based authentication
-   IP-based rate limiting
-   IP whitelisting
-   Authentication bypass for selected endpoints
-   Custom Lua logic

------------------------------------------------------------------------

## Architecture

Client → Envoy → Kong Gateway → User Microservice (FastAPI + SQLite)

------------------------------------------------------------------------

## Components

-   **Envoy**: Edge proxy for connection management and basic traffic
    controls
-   **Kong Gateway**: API Gateway
-   **User Microservice**: /login, /verify, /users, /health endpoints
-   **SQLite**: Local database
-   **Helm**: Deploy microservice and Kong declaratively

------------------------------------------------------------------------

## Repo Structure

    ├── ai-usage.md
    ├── helm
    │   ├── envoy-chart
    │   │   ├── Chart.yaml
    │   │   ├── templates
    │   │   │   ├── configmap.yaml
    │   │   │   ├── deployment.yaml
    │   │   │   └── service.yaml
    │   │   └── values.yaml
    │   ├── kong
    │   │   ├── header_check.lua
    │   │   ├── kong.yaml
    │   │   ├── plugins
    │   │   │   └── custom
    │   │   │       ├── handler.lua
    │   │   │       └── schema.lua
    │   │   └── values.yaml
    │   ├── old_version_kong
    │   │   ├── kong.yaml
    │   │   ├── plugins
    │   │   │   └── custom
    │   │   │       ├── handler.lua
    │   │   │       └── schema.lua
    │   │   └── values.yaml
    │   └── user-service
    │       ├── Chart.yaml
    │       ├── templates
    │       │   ├── deployment.yaml
    │       │   ├── _helpers.tpl
    │       │   └── service.yaml
    │       └── values.yaml
    ├── k8s
    │   ├── deployment.yaml
    │   ├── envoy
    │   │   ├── deploy.yaml
    │   │   └── envoy.yaml
    │   └── mod
    │       ├── modsecurity-config.yaml
    │       ├── waf-deployment.yaml
    │       └── waf-service.yaml
    ├── kong
    │   ├── kong.yaml
    │   └── plugins
    │       └── custom.lua
    ├── microservice
    │   ├── app
    │   │   ├── auth.py
    │   │   ├── db.py
    │   │   ├── main.py
    │   │   └── requirements.txt
    │   ├── backup
    │   │   ├── app
    │   │   │   ├── auth.py
    │   │   │   ├── db.py
    │   │   │   ├── main.py
    │   │   │   └── requirements.txt
    │   │   └── Dockerfile
    │   └── Dockerfile
    ├── README.md
    └── terraform
        └── main.tf

------------------------------------------------------------------------

## What is Envoy?

Envoy is an open-source, high-performance edge and service proxy
designed for cloud-native applications. It sits between clients and
services to manage, observe, and secure traffic.

### Key Features

-   Traffic management: Load balancing, retries, rate limiting, circuit
    breaking
-   Security: TLS termination, connection limits, IP-based controls
-   Observability: Metrics, logging, distributed tracing
-   Cloud-native: Works well with Kubernetes and integrates with API
    gateways like Kong

Envoy acts as the edge proxy, handling connection-level traffic control
and rate limits before requests reach Kong.

------------------------------------------------------------------------

## What is Kong?

Kong is an open-source API Gateway that secures, manages, and routes API
traffic.

It provides:

-   JWT authentication
-   Rate limiting
-   IP whitelisting
-   Custom plugins for logging or request manipulation

In this project, Kong sits behind Envoy to protect and manage access to
the microservice APIs.

------------------------------------------------------------------------

## User Microservice

Tech Stack: FastAPI, SQLite database inside the container.

In this Microservice, we have deployed the total 4 APIs:

-   /health
-   /verify
-   /login
-   /users

/login is protected and it is required the user and password to get
authenticated.

/users also comes under protection and it requires the Token to complete
the validation and get the values from user-service.

------------------------------------------------------------------------

## Kong Plugin Information

### Rate-Limiting Plugin

This Kong plugin enforces IP-based rate limiting, allowing a maximum of
10 requests per minute per client IP.

``` yaml
- name: rate-limiting
  config:
    minute: 10
    policy: local
    limit_by: ip
```
	
- minute: 10 – Limits each client to 10 requests per minute.
- policy: local – Counts requests on this Kong node only (use cluster for distributed counting).
- limit_by: ip – Rate limiting is applied individually per client IP.

### Kong IP Restriction

This Kong plugin allows only requests from specified IP ranges (CIDR). All other client IPs are blocked, enforcing IP-based access control.

``` yaml
- name: ip-restriction
  config:
    allow:
      - 192.168.49.0/24
      - 10.244.0.67/24
```

- allow : Only requests from these CIDR ranges are permitted.
- Requests from any other IPs are blocked at the gateway level.
- Ensures IP whitelisting for secure access to your APIs.

------------------------------------------------------------------------

## Envoy Connection Limit

This Envoy configuration restricts the number of concurrent client connections to 50. It protects the system from connection exhaustion and basic DDoS attacks.


``` yaml
max_connections: 50
```

- Limits the maximum number of simultaneous active connections to 50.
- Helps prevent connection flooding and reduces the risk of DDoS attacks at the edge layer.


------------------------------------------------------------------------

## Project Deployment Commands

### Login to Github and Clone the Repo.

### Install the Kubernetes Cluster/Minikube Cluster / Install the EKS Cluster on the AWS

  Minikube Steps Ref : https://minikube.sigs.k8s.io/docs/start/

- Check if all master nodes and Worker nodes are healthy.

- We have implemented this project deployment using Helm (Preferred).


### Build Microservice Docker Image

``` bash
docker build -t user-service:latest .
```

### Install User Service

``` bash
helm install user-service .
```

### Deploy Kong

``` bash
helm upgrade kong kong/kong -f values.yaml --set jwtSecret=admin123
```

### Deploy Envoy

``` bash
helm upgrade --install envoy ./envoy-chart   --namespace default   --set service.nodePort=31001   --set replicaCount=1
```

------------------------------------------------------------------------

## Test Commands

``` bash
curl -i http://192.168.58.2:32101/health
curl -i http://192.168.58.2:32101/verify
```

``` bash
curl -s -X POST http://192.168.58.2:32101/login   -H "Content-Type: application/json"   -d '{"username":"admin","password":"admin123"}'
```

``` bash
curl -i http://192.168.58.2:32504/users   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3MTg0ODY2Nn0.WEdqM3mGMmj_E5yfvFiWiKRQT8TfcVZSMxdADHyxMZ0"
```

------------------------------------------------------------------------

## Rate Limiting Test

``` bash
ab -n 20 -c 1 http://192.168.58.2:32101/health
```

## Concurrent Connection Test

``` bash
ab -n 150 -c 50 http://192.168.58.2:31001/health
```
