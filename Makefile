# If you want to run project locally
run_local:
	docker-compose -f docker-compose.yml up

run_local_from_scratch:
	docker-compose -f docker-compose.yml up --build

# Check if you have the required tools installed
check_version:
	@echo "Checking version, each of this command should return some version"
	docker version
	docker-compose version
	minikube version
	kubectl version

#minikube start
#minikube dashboard