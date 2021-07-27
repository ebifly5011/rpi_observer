sudo apt -y install wget git git-core
sudo apt -y install python3-dev python3-pip
sudo apt -y install libatlas-base-dev

echo "alias activate_rpid='source /home/pi/rpid/setup/_activate_rpid.sh'" >> .bashrc
echo "export PYTHONPATH='/home/pi/rpid:\$PYTHONPATH'" >> .bashrc

source /home/pi/rpid/setup/prometheus.sh
source /home/pi/rpid/setup/venv.sh
