FROM python:3.10-buster

# Install Ansible and sshpass
RUN python3 -m pip install ansible && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl sshpass

# Set environment variables
ENV RADKIT_ANSIBLE_CLIENT_CA_PATH="/ansible/.radkit/identities/chain.pem"
ENV RADKIT_ANSIBLE_CLIENT_CERT_PATH="/ansible/.radkit/identities/certificate.pem"
ENV RADKIT_ANSIBLE_CLIENT_KEY_PATH="/ansible/.radkit/identities/private_key_encrypted.pem"


# Set working directory
WORKDIR /ansible

# Copy the Cisco RADkit collection file into the container
COPY ansible-cisco-radkit-0.6.1.tar.gz /ansible

RUN mkdir /ansible/.radkit
RUN mkdir /ansible/.radkit/identities
COPY .radkit/identities/*.pem /ansible/.radkit/identities/.

# Install the Cisco RADkit collection
RUN ansible-galaxy collection install /ansible/ansible-cisco-radkit-0.6.1.tar.gz --force

# Create a directory to store the extracted files
RUN mkdir /wheels_dir

# Copy the archive into the container
COPY cisco_radkit_1.6.4_pip_linux_x86.tgz /wheels_dir/

# Extract the contents of the archive
RUN tar zxvf /wheels_dir/cisco_radkit_1.6.4_pip_linux_x86.tgz -C /wheels_dir/

# Install the Python package from the extracted files
RUN python3 -m pip install -f /wheels_dir/ cisco_radkit_client


