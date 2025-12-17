/**
 * Jenkins Pipeline for Project Nexus E-Commerce Backend
 * 
 * This pipeline provides comprehensive CI/CD with:
 * - Multi-stage build process
 * - Parallel testing
 * - Security scanning
 * - Docker image building
 * - Deployment to multiple environments
 */

pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.11'
        DOCKER_REGISTRY = credentials('docker-registry')
        DOCKER_IMAGE = 'project-nexus'
        RENDER_API_KEY = credentials('render-api-key')
        SLACK_WEBHOOK = credentials('slack-webhook')
    }
    
    options {
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        ansiColor('xterm')
        disableConcurrentBuilds()
    }
    
    triggers {
        pollSCM('H/5 * * * *')
        githubPush()
    }
    
    stages {
        // =====================================================================
        // PREPARATION
        // =====================================================================
        stage('🔧 Preparation') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
                
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    env.GIT_BRANCH_NAME = sh(
                        script: 'git rev-parse --abbrev-ref HEAD',
                        returnStdout: true
                    ).trim()
                }
                
                echo "Branch: ${env.GIT_BRANCH_NAME}"
                echo "Commit: ${env.GIT_COMMIT_SHORT}"
            }
        }
        
        // =====================================================================
        // ENVIRONMENT SETUP
        // =====================================================================
        stage('🐍 Setup Python Environment') {
            steps {
                echo '📦 Setting up Python environment...'
                
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r project-nexus/requirements.txt
                    pip install pytest pytest-django pytest-cov flake8 bandit safety black isort
                '''
            }
        }
        
        // =====================================================================
        // CODE QUALITY
        // =====================================================================
        stage('🔍 Code Quality') {
            parallel {
                stage('Lint - Flake8') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            flake8 project-nexus/ --count --select=E9,F63,F7,F82 --show-source --statistics || true
                            flake8 project-nexus/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                        '''
                    }
                }
                
                stage('Format Check - Black') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            black --check --diff project-nexus/ || true
                        '''
                    }
                }
                
                stage('Import Sort - isort') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            isort --check-only --diff project-nexus/ || true
                        '''
                    }
                }
            }
        }
        
        // =====================================================================
        // SECURITY SCANNING
        // =====================================================================
        stage('🛡️ Security Scanning') {
            parallel {
                stage('Bandit SAST') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            bandit -r project-nexus/ -f json -o bandit-report.json -ll -ii || true
                        '''
                    }
                }
                
                stage('Dependency Check') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            safety check -r project-nexus/requirements.txt --full-report || true
                        '''
                    }
                }
            }
            
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.json', allowEmptyArchive: true
                }
            }
        }
        
        // =====================================================================
        // TESTING
        // =====================================================================
        stage('🧪 Run Tests') {
            environment {
                DATABASE_URL = 'sqlite:///test_db.sqlite3'
                SECRET_KEY = 'test-secret-key-for-jenkins'
                DEBUG = 'True'
                REDIS_URL = 'redis://localhost:6379'
            }
            
            steps {
                echo '🧪 Running tests...'
                
                sh '''
                    . venv/bin/activate
                    cd project-nexus
                    python manage.py migrate --noinput
                    python -m pytest --cov=. --cov-report=xml --cov-report=html -v --junitxml=test-results.xml
                '''
            }
            
            post {
                always {
                    junit 'project-nexus/test-results.xml'
                    publishHTML target: [
                        reportName: 'Coverage Report',
                        reportDir: 'project-nexus/htmlcov',
                        reportFiles: 'index.html',
                        keepAll: true,
                        alwaysLinkToLastBuild: true
                    ]
                }
            }
        }
        
        // =====================================================================
        // BUILD DOCKER IMAGE
        // =====================================================================
        stage('🐳 Build Docker Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            
            steps {
                echo '🐳 Building Docker image...'
                
                dir('project-nexus') {
                    script {
                        def imageTag = "${DOCKER_IMAGE}:${env.GIT_COMMIT_SHORT}"
                        def latestTag = "${DOCKER_IMAGE}:latest"
                        
                        docker.build(imageTag)
                        docker.build(latestTag)
                        
                        env.DOCKER_IMAGE_TAG = imageTag
                    }
                }
            }
        }
        
        // =====================================================================
        // PUSH TO REGISTRY
        // =====================================================================
        stage('📤 Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            
            steps {
                echo '📤 Pushing to Docker registry...'
                
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-registry') {
                        def image = docker.image(env.DOCKER_IMAGE_TAG)
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }
        
        // =====================================================================
        // DEPLOY TO STAGING
        // =====================================================================
        stage('🚀 Deploy to Staging') {
            when {
                branch 'develop'
            }
            
            steps {
                echo '🚀 Deploying to staging environment...'
                
                input message: 'Deploy to Staging?', ok: 'Deploy'
                
                withCredentials([string(credentialsId: 'render-staging-service-id', variable: 'SERVICE_ID')]) {
                    sh '''
                        curl -X POST \
                            "https://api.render.com/v1/services/${SERVICE_ID}/deploys" \
                            -H "Authorization: Bearer ${RENDER_API_KEY}" \
                            -H "Content-Type: application/json"
                    '''
                }
            }
            
            post {
                success {
                    slackSend(
                        channel: '#deployments',
                        color: 'good',
                        message: "✅ Staging deployment successful!\nBranch: ${env.GIT_BRANCH_NAME}\nCommit: ${env.GIT_COMMIT_SHORT}"
                    )
                }
                failure {
                    slackSend(
                        channel: '#deployments',
                        color: 'danger',
                        message: "❌ Staging deployment failed!\nBranch: ${env.GIT_BRANCH_NAME}\nCommit: ${env.GIT_COMMIT_SHORT}"
                    )
                }
            }
        }
        
        // =====================================================================
        // DEPLOY TO PRODUCTION
        // =====================================================================
        stage('🚀 Deploy to Production') {
            when {
                branch 'main'
            }
            
            steps {
                echo '🚀 Deploying to production environment...'
                
                input message: 'Deploy to Production?', ok: 'Deploy to Production'
                
                withCredentials([string(credentialsId: 'render-production-service-id', variable: 'SERVICE_ID')]) {
                    sh '''
                        curl -X POST \
                            "https://api.render.com/v1/services/${SERVICE_ID}/deploys" \
                            -H "Authorization: Bearer ${RENDER_API_KEY}" \
                            -H "Content-Type: application/json"
                    '''
                }
            }
            
            post {
                success {
                    slackSend(
                        channel: '#deployments',
                        color: 'good',
                        message: "🎉 Production deployment successful!\nCommit: ${env.GIT_COMMIT_SHORT}\nBuild: ${env.BUILD_NUMBER}"
                    )
                }
                failure {
                    slackSend(
                        channel: '#deployments',
                        color: 'danger',
                        message: "🚨 Production deployment failed!\nCommit: ${env.GIT_COMMIT_SHORT}\nBuild: ${env.BUILD_NUMBER}"
                    )
                }
            }
        }
        
        // =====================================================================
        // HEALTH CHECK
        // =====================================================================
        stage('✅ Health Check') {
            when {
                branch 'main'
            }
            
            steps {
                echo '✅ Running health check...'
                
                sleep time: 60, unit: 'SECONDS'
                
                sh '''
                    response=$(curl -s -o /dev/null -w "%{http_code}" https://api.projectnexus.com/health/)
                    if [ "$response" != "200" ]; then
                        echo "Health check failed with status code: $response"
                        exit 1
                    fi
                    echo "Health check passed!"
                '''
            }
        }
    }
    
    // =========================================================================
    // POST-BUILD ACTIONS
    // =========================================================================
    post {
        always {
            echo '🧹 Cleaning up...'
            cleanWs()
        }
        
        success {
            echo '✅ Pipeline completed successfully!'
        }
        
        failure {
            echo '❌ Pipeline failed!'
            slackSend(
                channel: '#alerts',
                color: 'danger',
                message: "❌ Build failed!\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nBranch: ${env.GIT_BRANCH_NAME}"
            )
        }
        
        unstable {
            echo '⚠️ Pipeline is unstable'
        }
    }
}
