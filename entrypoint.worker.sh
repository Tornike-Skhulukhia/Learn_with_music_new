#! /bin/bash

wait-for-it -t 30 -s rabbitmq:5672

python -m rabbitmq_workers.consumer