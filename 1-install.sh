#!/bin/bash
git clone https://github.com/vitalfadeev/DataListener.git

cd DataListener
python3 -m venv venv
source venv/bin/activate
pip install pip --upgrade
pip install -r requirements.txt

./run.sh


