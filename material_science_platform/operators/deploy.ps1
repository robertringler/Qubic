param()
kubectl apply -f ..\\infra\\k8s\\namespace.yaml
kubectl apply -f ..\\infra\\k8s\\deployment.yaml
kubectl apply -f ..\\infra\\k8s\\service.yaml
kubectl apply -f ..\\infra\\k8s\\ingress.yaml
kubectl apply -f ..\\infra\\k8s\\hpa.yaml

