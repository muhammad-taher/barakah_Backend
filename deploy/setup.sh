#!/bin/bash
set -e

echo "Starting deployment setup for Barakah Backend..."

# 1. Update and install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx python3-dev build-essential libpq-dev

# 2. Setup virtual environment and install packages
cd /root/barakah/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 3. Setup systemd service
sudo cp /root/barakah/deploy/barakah.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start barakah
sudo systemctl enable barakah

# 4. Setup Nginx
sudo cp /root/barakah/deploy/barakah.nginx /etc/nginx/sites-available/barakah
sudo ln -sf /etc/nginx/sites-available/barakah /etc/nginx/sites-enabled/
# Remove default nginx config if it exists
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx

echo "================================================================"
echo "Deployment setup complete!"
echo "Your backend should now be running."
echo "Please make sure to set up your .env file in /root/barakah/backend"
echo "You can view logs with: sudo journalctl -u barakah"
echo "================================================================"
