
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'bharaniagithe/student-internship-tracker'
        K8S_NAMESPACE = 'default'
        PYTHON = 'C:\\Users\\Gift a Smile\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test Flask application') {
            steps {
                bat '"%PYTHON%" -m pip install --upgrade pip'
                bat '"%PYTHON%" -m pip install -r requirements.txt'
                bat '"%PYTHON%" -m pytest -q'
            }
        }

        stage('Build Docker image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest .'
            }
        }

        stage('Login and push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    bat 'echo %DOCKERHUB_TOKEN%| docker login -u %DOCKERHUB_USERNAME% --password-stdin'
                    bat 'docker push %IMAGE_NAME%:%BUILD_NUMBER%'
                    bat 'docker push %IMAGE_NAME%:latest'
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat 'kubectl config current-context'
                bat 'kubectl apply -f k8s\\deployment.yaml'
                bat 'kubectl apply -f k8s\\service.yaml'

                bat 'kubectl set image deployment/student-internship-tracker student-internship-tracker=%IMAGE_NAME%:%BUILD_NUMBER% -n %K8S_NAMESPACE%'

                bat 'kubectl rollout status deployment/student-internship-tracker --timeout=180s -n %K8S_NAMESPACE%'

                bat 'kubectl get pods -l app=student-internship-tracker -n %K8S_NAMESPACE%'
            }
        }
    }

    post {
        always {
            bat 'docker logout'
        }
        success {
            echo 'CI/CD completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Review the stage logs above.'
        }
    }
}
