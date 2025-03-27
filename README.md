# Auto-Provisioning Jenkins Agents and System Stats Logging with MySQL

## Overview
This project automates the deployment of Jenkins agents, MySQL, and a Python script that logs system stats to a MySQL database. The setup uses Jenkins, Ansible, and AWS EC2 instances to ensure smooth operations and automation.

## Project Components
- **Jenkins Master (Ubuntu)**: Manages CI/CD pipeline and provisions agents dynamically.
- **Jenkins Agents (Amazon Linux EC2s)**: Spawned dynamically for executing jobs.
- **MySQL Database (Ubuntu EC2)**: Stores system stats logged by a Python script.
- **Application EC2 Instances (Ubuntu or CentOS)**: Run the Python script to collect system metrics.
- **Ansible**: Automates software installation and script deployment.

## Step 1: Set Up Jenkins Master (Ubuntu)
### 1.1 Install Jenkins
Run the following commands on your Jenkins Master EC2 instance (Ubuntu):
```bash
sudo apt update && sudo apt install -y openjdk-11-jdk
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list
sudo apt update
sudo apt install -y jenkins
```
Start and enable Jenkins:
```bash
sudo systemctl start jenkins
sudo systemctl enable jenkins
```
Retrieve the initial admin password:
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```
Access Jenkins at `http://your-server-ip:8080` and complete the setup.

## Step 2: Configure Jenkins for Dynamic Agents
### 2.1 Install Required Plugins
- **Amazon EC2 Plugin** (for auto-scaling agents)
- **Ansible Plugin**
- **Pipeline Plugin**

### 2.2 Set Up EC2 Dynamic Agents
1. Navigate to **Manage Jenkins → Configure Clouds → Add a new cloud → Amazon EC2**
2. Add your AWS credentials
3. Configure an **Amazon Linux AMI** as the Jenkins Agent
4. Set up an **EC2 Key Pair** for SSH access
5. Specify the **label** (e.g., `ec2-agent`)

## Step 3: Set Up MySQL Server
### 3.1 Install MySQL on Ubuntu EC2
```bash
sudo apt update
sudo apt install -y mysql-server
```
Secure MySQL installation:
```bash
sudo mysql_secure_installation
```
### 3.2 Create Database and Table
```sql
CREATE DATABASE system_stats;
USE system_stats;

CREATE TABLE stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_usage FLOAT,
    memory_usage FLOAT
);

CREATE USER 'monitor'@'%' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON system_stats.* TO 'monitor'@'%';
FLUSH PRIVILEGES;
```
### 3.3 Enable Remote Access
Edit `/etc/mysql/mysql.conf.d/mysqld.cnf` and set:
```ini
bind-address = 0.0.0.0
```
Restart MySQL:
```bash
sudo systemctl restart mysql
```

## Step 4: Prepare the Python Script
The script collects CPU and memory usage and logs them into MySQL.
### 4.1 Install Dependencies
```bash
pip install pymysql psutil
```
### 4.2 Python Script (`system_stats.py`)
```python
import pymysql
import psutil
from datetime import datetime

conn = pymysql.connect(host='your-mysql-server-ip', user='monitor', password='password123', database='system_stats')
cursor = conn.cursor()

cpu_usage = psutil.cpu_percent(interval=1)
memory_usage = psutil.virtual_memory().percent

query = "INSERT INTO stats (cpu_usage, memory_usage) VALUES (%s, %s)"
cursor.execute(query, (cpu_usage, memory_usage))
conn.commit()

cursor.close()
conn.close()
```
### 4.3 Test Script
```bash
python3 system_stats.py
```

## Step 5: Deploy with Ansible
### 5.1 Ansible Inventory (`inventory.ini`)
```ini
[app_servers]
app1 ansible_host=your-app-ec2-ip ansible_user=ec2-user ansible_ssh_private_key_file=~/.ssh/your-key.pem
```
### 5.2 Install Python (`roles/python/tasks/main.yml`)
```yaml
- name: Install Python
  yum:
    name: python3
    state: present
```
### 5.3 Deploy Python Script (`roles/deploy_script/tasks/main.yml`)
```yaml
- name: Copy system_stats.py
  copy:
    src: system_stats.py
    dest: /home/ec2-user/system_stats.py
    mode: '0755'
```
### 5.4 Set Up Cron Job (`roles/schedule_cron/tasks/main.yml`)
```yaml
- name: Schedule the script via cron
  cron:
    name: "Run system stats logger"
    job: "/usr/bin/python3 /home/ec2-user/system_stats.py"
    minute: "*/5"
```
### 5.5 Playbook (`deploy.yml`)
```yaml
- hosts: app_servers
  become: true
  roles:
    - python
    - deploy_script
    - schedule_cron
```
### 5.6 Run the Playbook
```bash
ansible-playbook -i inventory.ini deploy.yml
```

## Step 6: Configure Jenkins Job for Deployment
Create a new **Pipeline Job** in Jenkins and use the following pipeline:
```groovy
pipeline {
    agent { label 'ec2-agent' }
    
    stages {
        stage('Checkout') {
            steps {
                git 'your-repo-url'
            }
        }
        
        stage('Deploy with Ansible') {
            steps {
                sh 'ansible-playbook -i inventory.ini deploy.yml'
            }
        }
    }
}
```
Trigger the job to deploy and schedule the Python script.

## Expected Outcome
✅ Jenkins dynamically provisions agents  
✅ Python script logs system stats into MySQL every 5 minutes  
✅ Deployment fully automated via Ansible  

## Conclusion
This setup ensures efficient system monitoring and automated deployment using Jenkins, Ansible, and MySQL. You can expand it further by adding alerting mechanisms or dashboards for monitoring system performance.
