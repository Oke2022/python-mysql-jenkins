pipeline {
    agent any

    environment {
        SCANNER_HOME = tool 'Sonar-scanner'
        SONARQUBE_ENV = 'MySonarQube'
        SONAR_TOKEN = credentials('jenkins-token')
        SONAR_URL = 'http://3.236.223.97:9000'
        ARTIFACT_NAME = 'python-script-bundle.zip'
        S3_BUCKET = 'syslogs-bkt'
        AWS_ACCESS_KEY_ID = credentials('aws-access-key')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
        SSH_CREDENTIALS = credentials('jenkins-access-keypair')
    }

    stages {
        stage ('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                python3 --version
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install psutil mysql-connector-python unittest-xml-reporting
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                . venv/bin/activate
                mkdir -p target/surefire-reports
                python test_system_stats.py
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
                withCredentials([sshUserPrivateKey(credentialsId: 'jenkins-access-keypair', keyFileVariable: 'SSH_KEY')]) {
                    sh '''
                    . venv/bin/activate
                    ssh -o StrictHostKeyChecking=no -i $SSH_KEY ec2-user@172.31.23.4 "cd python-mysql-jenkins/ansibleScripts && ansible-playbook -i host.ini deploy.yml"
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
        success {
            emailext (
                subject: "✅ SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>BUILD SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'</p>
                <p>Check console output at: <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                to: 'okejoshua391@gmail.com',
                mimeType: 'text/html'
            )
        }
        failure {
            emailext (
                subject: "❌ FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>BUILD FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'</p>
                <p>Check console output at: <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                to: 'okejoshua391@gmail.com',
                mimeType: 'text/html'
            )
        }
    }
}
