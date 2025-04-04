pipeline {
    agent any

    environment {
        SONARQUBE_ENV = 'MySonarQube'
        ARTIFACT_NAME = 'python-script-bundle.zip'
        S3_BUCKET = 'syslogs-bkt'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git(
                    branch: 'main', 
                    credentialsId: 'github-jenkins', 
                    url 'https://github.com/Oke2022/python-mysql-jenkins.git'
                   )
            }
        }

        stage('Install Python & Ansible') {
            steps {
                sh '''
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip ansible zip curl unzip
                pip3 install -r requirements.txt || true
                
                # Install AWS CLI manually
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                unzip awscliv2.zip
                sudo ./aws/install
                aws --version
                '''
            }
        }


        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    sh 'sonar-scanner'
                }
            }
        }

        stage('Test Report') {
            steps {
                junit '**/target/surefire-reports/*.xml'  // Publish JUnit test results
            }
        }

        stage('Deploy Python Script using Ansible') {
            steps {
                sh 'ansible-playbook -i ansibleScripts/host.ini ansibleScripts/deploy.yml'
            }
        }

        stage('Zip Script and Config') {
            steps {
                sh 'zip -r ${ARTIFACT_NAME} ansibleScripts/roles/deploy_script/files/ ansibleScripts/deploy.yml'
            }
        }

        stage('Upload ZIP to S3') {
            environment {
                AWS_ACCESS_KEY_ID = credentials('aws-access-key')
                AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
            }
            steps {
                sh '''
                aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
                aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
                aws s3 cp ${ARTIFACT_NAME} s3://$S3_BUCKET/${ARTIFACT_NAME}
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "${ARTIFACT_NAME}", fingerprint: true
        }
    }
}
