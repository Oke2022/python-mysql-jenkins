pipeline {
    agent {
        label 'python-agent'
    }

    environment {
        SCANNER_HOME = tool 'Sonar-scanner'
        SONARQUBE_ENV = 'MySonarQube'
        SONAR_TOKEN = credentials('jenkins-token')
        SONAR_URL = 'http://3.235.222.19:9000'
        ARTIFACT_NAME = 'python-script-bundle.zip'
        S3_BUCKET = 'syslogs-bkt'
    }

    stages {
        stage ('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                # Check if Python is installed
                python3 --version
                
                # Install system dependencies if needed
                sudo apt-get update -y || true
                sudo apt-get install -y python3-pip python3-psutil || true
                
                # Install Python dependencies directly
                pip3 install psutil mysql-connector-python unittest-xml-reporting
                
                # Install Ansible for deployment
                pip3 install ansible
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                # Create directory for test reports
                mkdir -p target/surefire-reports
                
                # Run the tests
                python3 test_system_stats.py
                '''
            }
        }
        
        stage('Test Report') {
            steps {
                junit 'target/surefire-reports/*.xml'
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh """
                    ${SCANNER_HOME}/bin/sonar-scanner \\
                    -Dsonar.projectKey=python-mysql-jenkins \\
                    -Dsonar.sources=. \\
                    -Dsonar.host.url=${SONAR_URL}
                    """
                }
            }
        }

        stage('Deploy Python Script using Ansible') {
            steps {
                withCredentials([file(credentialsId: 'ssh-private-key', variable: 'SSH_KEY')]) {
                    sh '''
                    # Copy the SSH key to a location Ansible can use
                    mkdir -p ~/.ssh
                    cp $SSH_KEY ~/.ssh/id_rsa
                    chmod 600 ~/.ssh/id_rsa
                    
                    # Run the Ansible playbook
                    ansible-playbook -i ansibleScripts/host.ini ansibleScripts/deploy.yml
                    
                    # Clean up
                    rm -f ~/.ssh/id_rsa
                    '''
                }
            }
        }

        stage('Zip Script and Config') {
            steps {
                sh '''
                zip -r ${ARTIFACT_NAME} system_stats.py test_system_stats.py target/surefire-reports/ ansibleScripts/
                '''
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
            cleanWs()
        }
    }
}