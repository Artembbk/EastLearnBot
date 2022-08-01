#!/bin/bash

zip project.zip index.py main.py README.md requirements.txt && aws --endpoint-url=https://storage.yandexcloud.net/ s3 cp project.zip s3://easy-learn-bucket/project.zip && yc serverless function version create \
                                                             --function-name=easy-bot-function \
                                                             --runtime python39 \
                                                             --entrypoint index.handler \
                                                             --memory 128m \
                                                             --execution-timeout 3s \
                                                             --package-object-name project.zip \
                                                             --package-bucket-name easy-learn-bucket \
                                                             --service-account-id=aje1etno446r490326e5 \
                                                             --environment=BOT_TOKEN=5405067658:AAGtH8v7gqbGAJ-9qOB3IelU0_66qfOk32c



