pipeline {
    agent {
        docker {
            image 'python:3.12'
            args '-v /var/run/docker.sock:/var/run/docker.sock -v $HOME/.aws:/root/.aws'
        }
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
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                # Check Python version
                python --version
                
                # Create a virtual environment
                python -m venv venv
                
                # Activate the virtual environment and install dependencies
                . venv/bin/activate
                pip install --upgrade pip
                pip install psutil mysql-connector-python unittest-xml-reporting
                
                # Add AWS CLI and Ansible for later stages
                pip install awscli ansible
                
                # Verify installations
                pip list
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                # Activate the virtual environment
                . venv/bin/activate
                
                # Create directory for test reports
                mkdir -p target/surefire-reports
                
                # Run the tests
                python test_system_stats.py
                '''
            }
        }
        
        stage('Test Report') {
            steps {
                junit 'target/surefire-reports/*.xml'  // Publish JUnit test results
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh """
                    ${SCANNER_HOME}/bin/sonar-scanner \\
                    -Dsonar.projectKey=python-mysql-jenkins \\
                    -Dsonar.sources=. \\
                    -Dsonar.host.url=${SONAR_URL} \\
                    -Dsonar.python.coverage.reportPaths=target/surefire-reports/coverage.xml
                    """
                }
            }
        }

        stage('Deploy Python Script using Ansible') {
            steps {
                sh '''
                # Activate the virtual environment for Ansible
                . venv/bin/activate
                
                # Run Ansible playbook
                ansible-playbook -i ansibleScripts/host.ini ansibleScripts/deploy.yml
                '''
            }
        }

        stage('Zip Script and Config') {
            steps {
                sh 'zip -r ${ARTIFACT_NAME} ansibleScripts/roles/deploy_script/files/ ansibleScripts/deploy.yml system_stats.py test_system_stats.py target/surefire-reports/'
            }
        }

        stage('Upload ZIP to S3') {
            environment {
                AWS_ACCESS_KEY_ID = credentials('aws-access-key')
                AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
            }
            steps {
                sh '''
                # Activate the virtual environment where AWS CLI is installed
                . venv/bin/activate
                
                # Upload to S3
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