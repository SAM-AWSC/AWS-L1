#!/bin/bash

# Install pyenv
curl https://pyenv.run | bash

# Update shell configuration for pyenv
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# Reload the shell to apply changes
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install Python 3.9.18 using pyenv
pyenv install 3.9.18

# Set Python 3.9.18 as global version
pyenv global 3.9.18

# Verify the Python version
python --version

# Install pip if it's not already installed
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py --user

# Install boto3 using pip
pip install --user boto3

# Verify boto3 installation
python -c "import boto3; print('boto3 version:', boto3.__version__)"

echo "Python 3.9.18 and boto3 have been successfully installed!"
