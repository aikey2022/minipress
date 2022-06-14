pipeline {
    agent any

    // 配置保留构建的历史版本数量
    options {
        buildDiscarder logRotator(
            // 比此早的发布包将被删除，但构建的日志、操作历史、报告等将被保留
            artifactDaysToKeepStr: '',
            // 最多此数目的构建将保留他们的发布包
            artifactNumToKeepStr: '7', 
            // 构建记录将保存的天数
            daysToKeepStr: '', 
            // 最多此数目的构建记录将被保存
            numToKeepStr: '7'
            )
      }
    // 配置默认工具
    // tools {
        // 全局配置里的maven和jdk配置的名称
        // maven   "maven"
        // jdk     "jdk8"
    //}
    // 配置环境变量
    environment {
       // gitlab url
       GITLAB_URL = "https://github.com/aikey2022/minipress.git"

       // test hosts
       test_hosts = """
       [
            'minipress_test':'10.0.0.101'
       ]
       """
       // prod hosts
       prod_hosts = """
       [
            'minipress_prod':'10.0.0.101'
       ]
       """  
       // ssh 或者scp 执行参数
       cmd_args = "-p 22 -o  StrictHostKeyChecking=no  -i /root/.ssh/id_rsa"
       scp_args = "-P 22 -o  StrictHostKeyChecking=no  -i /root/.ssh/id_rsa"

       // 远程目录
       // target_path = "/opt/flask/minipress"

    }
    // 配置参数
    parameters {
        // git分支选择
        gitParameter name: 'BRANCH_TAG',
            type: 'PT_BRANCH_TAG',
            branchFilter: 'origin/(.*)',
            // 设置默认分支
            defaultValue: 'main',
            selectedValue: 'DEFAULT',
            sortMode: 'DESCENDING_SMART',
            description: 'Select your branch or tag'

        // 环境选择
        choice(
            name: 'HOST_ENV', 
            choices: [
                // 测试环境
                'test',
                // 生产环境
                'prod'
            ],
            description: 'Select Deploy Environment'
        )

        // 执行的操作
        choice(
            name: 'ACTION_MODE', 
            choices: [
                // 更新
                'update',
                // 重启
                'restart',
                // 停止
                'stop'
            ],
            description: 'Select Deploy Environment'
        )

        // 选择更新的服务
        choice(
            name: 'PROJECT_NAME',
            choices: [
                'minipress'
                ],
            description: 'Select service name for update'
        )
    }

    stages {
        // 获取代码前清空workspace
        stage('CleanWorkspace') {
            steps {
                cleanWs()
            }
        }
           
        stage('get source code') {
            steps {
                // 拉取项目代码  默认目录env.WORKSPACE
                    checkout([
                        $class: 'GitSCM', 
                        branches: [[name: "${params.BRANCH_TAG}"]],
                        doGenerateSubmoduleConfigurations: false, 
                        extensions: [[
                            $class: 'CloneOption', 
                            depth: 1, 
                            noTags: false, 
                            reference: '', 
                            shallow: true
                        ]], 
                        gitTool: 'Default',
                        submoduleCfg: [], 
                        userRemoteConfigs: [[
                            url: "${env.GITLAB_URL}",
                            // credentialsId: 'ssh-for-gitlab'
                        ]]
                    ])
            }
        }

        stage('send files to remote path') {
            steps {
                script {
                    // 更新操作
                    if("${ACTION_MODE}" == "update"){
                        // 发送文件到远程主机
                        sh """
                            ls -lh .
                            ls -lh ${env.WORKSPACE}
                        """
                    }else{
                        echo "${ACTION_MODE} 操作 请稍等......"
                    }
                }
            }

        }


        // 2 构建镜像
        stage('build  image and deploy minipress') {
           steps {
                
                script {
                    // 远程主机
                    def re_test_hosts = evaluate(env.test_hosts)
                    def re_prod_hosts = evaluate(env.prod_hosts)


                    def remote_path = "/opt/python/flask"
 
                    def remote_hosts=[:]

                    // 根据环境名改变远程主机
                    if ("${HOST_ENV}" == "test"){
                        remote_hosts = re_test_hosts
                        echo "${PROJECT_NAME}  ${remote_hosts}"
                    }else if ("${HOST_ENV}" == "prod"){
                        remote_hosts = re_prod_hosts
                        echo "${PROJECT_NAME}  ${remote_hosts}"
                    }


                    // 根据 ACTION_MODE 执行操作
                    if("${ACTION_MODE}" == "update"){
                        remote_hosts.each {
                            re_hostname,re_host ->
                            echo "${re_hostname}  ${re_host}"
                            sh """
                                # 检查远程目录
                                ssh ${env.cmd_args} root@${re_host} 'if [ ! -d ${remote_path}/${PROJECT_NAME} ];then mkdir -p ${remote_path}/${PROJECT_NAME};fi'

                                # 停止服务
                                ssh  ${env.cmd_args}   root@${re_host} 'docker-compose -f ${remote_path}/${PROJECT_NAME}/${PROJECT_NAME}-compose.yaml down'

                                # 删除旧文件
                                ssh  ${env.cmd_args}   root@${re_host} 'rm -rf ${remote_path}/${PROJECT_NAME}/*'

                                # 拷贝新文件到远程主机
                                scp  ${env.scp_args}   -r  ${env.WORKSPACE}/*  ${re_host}:${remote_path}/${PROJECT_NAME}

                                # 构建镜像
                                # ssh  ${env.cmd_args}   root@${re_host} 'cd ${remote_path}/${PROJECT_NAME} && docker build -t minipress:latest .'

                                # 启动容器
                                ssh  ${env.cmd_args}   root@${re_host} 'cd ${remote_path}/${PROJECT_NAME} && docker-compose -f ${PROJECT_NAME}-compose.yaml build &&docker-compose -f ${PROJECT_NAME}-compose.yaml up -d'
                            """
                        }
                    }else if ("${ACTION_MODE}" == "restart"){
                        remote_hosts.each {
                            re_hostname,re_host ->
                            echo "${re_hostname}  ${re_host}"
                            sh """
                                # 生成 .env文件,docker-compose命令默认使用
                                # ssh ${env.cmd_args} root@${re_host} "echo ACTIVE=${ACTIVE}>${remote_path}/${PROJECT_NAME}/.env"

                                # 停止服务
                                ssh  ${env.cmd_args}   root@${re_host} 'docker-compose -f ${remote_path}/${PROJECT_NAME}/${PROJECT_NAME}-compose.yaml down'
                                
                                # 启动服务
                                ssh  ${env.cmd_args}   root@${re_host} 'cd ${remote_path}/${PROJECT_NAME} && docker-compose -f ${PROJECT_NAME}-compose.yaml up -d'
                            """
                        }
                    }else if ("${ACTION_MODE}" == "stop"){
                        remote_hosts.each {
                            re_hostname,re_host ->
                            echo "${re_hostname}  ${re_host}"
                            sh """
                                # 停止服务
                                ssh  ${env.cmd_args}   root@${re_host} 'docker-compose -f ${remote_path}/${PROJECT_NAME}/${PROJECT_NAME}-compose.yaml down'
                                
                            """
                        }
                    }

                    // 停留5秒
                    sleep 6
                }               
           }
        }
        // 检查服务状态
        stage('check  status') {
            steps {
                // 查看服务运行状态
                script {
                    // ybspaceMall 主机
                    def re_test_hosts = evaluate(env.test_hosts)
                    def re_prod_hosts = evaluate(env.prod_hosts)

                    def remote_hosts=[:]

                    // 根据环境名改变远程主机
                    if ("${HOST_ENV}" == "test"){
                        remote_hosts = re_test_hosts
                        echo "${PROJECT_NAME}  ${remote_hosts}"
                    }else if ("${HOST_ENV}" == "prod"){
                        remote_hosts = re_prod_hosts
                        echo "${PROJECT_NAME}  ${remote_hosts}"
                    }

                    // 遍历主机检查状态
                    remote_hosts.each {
                        re_hostname,re_host ->
                        echo "${re_hostname}  ${re_host}"                        
                        sh """
                           # 查看容器状态
                           ssh ${env.cmd_args} root@${re_host} 'docker ps -a'

                           # 打印空行
                           echo  ''

                           # 查看容器启动参数
                           ssh ${env.cmd_args} root@${re_host} 'docker ps -a --no-trunc'
                        """
                       
                    }
                }
            }
        }  
    }
}
