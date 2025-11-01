#!/usr/bin/env bash
set -e
docker build -t quasim/backend:dev ../services/backend
docker build -t quasim/frontend:dev ../services/frontend
