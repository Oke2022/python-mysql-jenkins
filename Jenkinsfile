pipeline {
    agent any

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
        
        stage('Setup Python') {
            steps {
                sh '''
                # Check if Python is installed
                which python3 || sudo apt-get update && sudo apt-get install -y python3
                
                # Check if pip is installed
                which pip3 || sudo apt-get install -y python3-pip
                
                # Verify installations
                python3 --version
                pip3 --version
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                // Install dependencies directly without virtual environment
                sh '''
                # Install required packages if not available
                pip3 install --user psutil mysql-connector-python unittest-xml-reporting
                
                # Create directory for test reports
                mkdir -p target/surefire-reports
                
                # Run the tests
                python3 test_system_stats.py
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
                sh 'ansible-playbook -i ansibleScripts/host.ini ansibleScripts/deploy.yml'
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