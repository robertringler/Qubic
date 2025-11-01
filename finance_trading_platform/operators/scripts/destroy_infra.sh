#!/usr/bin/env bash
set -e
kubectl delete -f ../infra/k8s --ignore-not-found
