#!/bin/bash

# This script sets up environment variables for RADKIT and Meraki API key

export RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64=$(echo -n 'my-password' | base64)
export RADKIT_ANSIBLE_IDENTITY="my-username"
export RADKIT_ANSIBLE_SERVICE_SERIAL="my-service-id"

export MERAKI_API_KEY="my-meraki-apy-key"