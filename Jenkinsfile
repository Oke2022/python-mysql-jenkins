pipeline {
    agent any

    environment {
        SONARQUBE_ENV = 'MySonarQube'
        ARTIFACT_NAME = 'python-script-bundle.zip'
        S3_BUCKET = 'syslogs-bkt'
    }


    stages {
        stage ('Checkout') {
            steps {
                checkout scm
            }
        }
        
    
        stage('SonarQube Analysis') {
             environment {
                SONAR_TOKEN = credentials('jenkins-token')
                SONAR_URL = 'http://3.235.222.19:9000'
            }
            steps {
                withSonarQubeEnv('MySonarQube') {
                sh """
                    sonar-scanner \
                    -Dsonar.projectKey=python-mysql-jenkins \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=$SONAR_URL \
                    -Dsonar.login=$SONAR_TOKEN
                """
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
