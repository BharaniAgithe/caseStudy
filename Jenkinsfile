pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        // Replace with your Docker Hub repository, e.g. mydockerid/student-internship-tracker
        IMAGE_NAME = 'YOUR_DOCKERHUB_USERNAME/student-internship-tracker'
        K8S_NAMESPACE = 'default'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test Flask application') {
            steps {
                bat 'py -m pip install --upgrade pip'
                bat 'py -m pip install -r requirements.txt'
                bat 'py -m pytest -q'
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
                // Jenkins agent must be able to run kubectl and access Docker Desktop's cluster.
                bat 'kubectl config current-context'
                bat 'kubectl apply -f k8s\\deployment.yaml'
                bat 'kubectl apply -f k8s\\service.yaml'
                bat 'kubectl set image deployment/student-internship-tracker app=%IMAGE_NAME%:%BUILD_NUMBER% -n %K8S_NAMESPACE%'
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
