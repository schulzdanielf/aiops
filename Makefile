
# Implantar aplicação no cluster
deploy:
	@kubectl apply -f k8s/
# Verificar status da aplicação
status:
	@kubectl get pods
	@kubectl get services
	@kubectl get pvc
	@kubectl get pv

