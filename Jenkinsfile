pipeline {
    agent any
    options { timestamps(); disableConcurrentBuilds() }
    environment { DOCKERHUB_NAMESPACE = 'mezhnun' }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Build') {
            parallel {
                stage('Frontend') { steps { sh 'docker build -t taski-frontend frontend' } }
                stage('Backend') { steps { sh 'docker build -t taski-backend backend' } }
            }
        }
        stage('Run and verify') {
            steps {
                sh 'make run'
                sh 'python3 scripts/check_taski.py'
            }
        }
        stage('Publish') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
                    sh '''set +x
                    export DOCKER_CONFIG=$(mktemp -d)
                    trap 'rm -rf "$DOCKER_CONFIG"' EXIT
                    printf '%s' "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin
                    for service in frontend backend; do
                        image="$DOCKERHUB_NAMESPACE/taski-$service:$GIT_COMMIT"
                        docker tag "taski-$service" "$image"
                        docker push "$image"
                    done
                    '''
                }
            }
        }
    }
    post { always { sh 'make clear' } }
}
