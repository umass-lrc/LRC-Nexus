# If you want to run project locally
run_local_docker:
	docker-compose -f docker-compose.yml up -d

run_local_docker_with_logs:
	docker-compose -f docker-compose.yml up

run_local_docker_from_scratch:
	docker-compose -f docker-compose.yml up --build

load_data_docker:
	@echo "Loading data into local Docker container"
	@docker exec -it django-nexus bash -c "cd /usr/src/app/datadump && python load_data.py"

stop_local_docker:
	docker-compose -f docker-compose.yml down

# Check if you have the required tools installed
check_version:
	@echo "Checking version, each of this command should return some version"
	docker version
	docker-compose version
	minikube version
	kubectl version

# Start local Kubernetes cluster
start_local_cluster:
	@echo "Starting local Kubernetes cluster"
	@minikube start
	@minikube dashboard

# Apply new deployment
apply_local_deployment:
	@echo "Applying new deployment"
	@kubectl apply -k deploy/

# Get current Deployment status & Pods status & Service status
get_local_status:
	@echo "Getting current Deployment status"
	@kubectl get deployment
	@echo "\nGetting current Pods status"
	@kubectl get pods
	@echo "\nGetting current Service status"
	@kubectl get service

# Build Local Docker image and push to local registry
build_local_image:
	@echo "Building local Docker image"
	@docker build -t nexus:latest nexus/ --no-cache
	@docker build -t nginx:latest nginx/ --no-cache
	@echo "\nPushing local Docker image to local registry..."
	@minikube image load nexus:latest
	@echo "- Done pushing nexus:latest"
	@minikube image load nginx:latest
	@echo "- Done pushing nginx:latest"
	@echo "Pushing local Docker image to local registry... Done"
