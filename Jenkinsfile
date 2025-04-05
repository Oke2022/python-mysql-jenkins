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
                # Method 1: Try to use python3 -m pip instead of pip3 directly
                python3 -m pip --version || echo "Python3 pip module not found"
                
                # Method 2: Try to find pip3 in common locations
                /usr/bin/pip3 --version || echo "pip3 not found in /usr/bin"
                /usr/local/bin/pip3 --version || echo "pip3 not found in /usr/local/bin"
                
                # Method 3: If all else fails, install pip for the current user
                if ! command -v pip3 &> /dev/null && command -v python3 &> /dev/null; then
                    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                    python3 get-pip.py --user
                    export PATH=$HOME/.local/bin:$PATH
                    echo "PATH now includes: $PATH"
                fi
                
                # Check if installation was successful
                python3 --version
                python3 -m pip --version || echo "Still can't find pip module"
                
                # Show where pip might be installed
                find $HOME/.local -name pip3 2>/dev/null || echo "No pip3 in ~/.local"
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                # Try multiple ways to install packages
                # Method 1: Using python3 -m pip
                python3 -m pip install --user psutil mysql-connector-python unittest-xml-reporting || echo "Failed python3 -m pip install"
                
                # Method 2: Try to use pip directly with the full path (if found)
                if [ -f "$HOME/.local/bin/pip3" ]; then
                    $HOME/.local/bin/pip3 install --user psutil mysql-connector-python unittest-xml-reporting
                fi
                
                # Create directory for test reports
                mkdir -p target/surefire-reports
                
                # Make sure Python can find the user-installed packages
                export PYTHONPATH=$HOME/.local/lib/python3*/site-packages:$PYTHONPATH
                
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