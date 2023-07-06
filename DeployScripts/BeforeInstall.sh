#!/bin/bash
sudo rm -rf /home/ubuntu/foodhealers-backends/*
sudo rm -rf /home/ubuntu/foodhealers-backends/.git/
sudo rm -rf /home/ubuntu/foodhealers-backends/.gitignore
sudo rm -rf /home/ubuntu/foodhealers-backends/.gitlab-ci.yml
sudo systemctl restart codedeploy-agent.service
