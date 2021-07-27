sudo apt -y install prometheus

sudo mv /etc/prometheus/prometheus.yml /etc/prometheus/prometheus.yml.org
sudo mv /home/pi/rpid/setup/prometheus.yml /etc/prometheus/prometheus.yml

sudo nohup /usr/bin/prometheus --config.file=/etc/prometheus/prometheus.yml &
