# -*- coding: utf-8 -*-

import gzip
import json
import mimetypes
import os
import shutil
import sys

from pip._vendor.distlib.compat import raw_input
import requests

from fabric.colors import blue, cyan, green, magenta, red, yellow
from fabric.context_managers import cd, hide, prefix, quiet, settings, path
from fabric.contrib.files import exists
from fabric.decorators import task, roles, parallel
from fabric.operations import local, run, sudo, put, get
from fabric.state import env
from fabric.tasks import execute
from fabric.utils import _AttributeDict, puts

"""手动配置"""

env.organization = 'dfds'
env.host = 'cmcaifu.com'
env.email_host = 'cmcaifu.com'
env.git_host = 'git.cmcaifu.com'  # 'github.com'
env.lb_https = True  # 负载均衡是否配置了https
env.newrelic_key = '7cba721d377c66139fb07c29ecf1bae50e3dbf43'


# ===========
# = GLOBALS =
# ===========
env.project_name = os.path.basename(os.path.dirname(__file__))
env.project_path = '~/Git/{}'.format(env.project_name)
# 其他:
env.repositories = {
    'django': 'git@{0.git_host}:{0.organization}/{0.project_name}.git'.format(env),  # SSH部署必须用git不能用http
    'java': 'git@{0.git_host}:{0.organization}/{0.project_name}_java.git'.format(env)
}
cloud = _AttributeDict({
    'name': '',
    'domain': '',
    'region': '',
    'bucket_static': ''
})
cloud.name = 'aliyun'  # 可选: aws, aliyun
cloud.region = 'oss-cn-hangzhou'
if cloud.name == 'aws':
    env.user = 'ubuntu'
    cloud.domain = 'amazonaws.com'
elif cloud.name == 'aliyun':
    env.user = 'root'
    cloud.domain = 'aliyuncs.com'
else:
    puts('没有云')
# env.forward_agent = True  # GitHub的代理转发部署方式需要开启这项, GitLab不要开启, 有SSH Key的时候会无效
env.colorize_errors = True


@task
def prod(branch='master'):
    """【生产环境】"""
    # env.key_filename = '~/key/{.organization}-aws.pem'.format(env)
    env.password = 'Abcd1234'
    env.branch = branch
    env.test = False
    env.database_host = 'cmcaifudefault.mysql.rds.aliyuncs.com'
    env.roledefs = {  # 无论是否同一个role中, 只要有重复的ip默认不执行
        'django': ['10.253.40.104', '10.253.40.138'],
        'java': ['10.139.48.127']
    }
    env.roledefs['static'] = [env.roledefs['django'][0]]
    cloud.bucket_static = 'static-cmcaifu-com'
    env.STATIC_URL = '//{}.{}.{}/'.format(cloud.bucket_static, cloud.region, cloud.domain)


@task
def test(branch='develop'):
    """【测试环境】"""
    # env.key_filename = '~/key/{.organization}-aws-test.pem'.format(env)
    env.password = 'Abcd1234'
    env.branch = branch
    env.test = True
    env.database_host = 'rm-bp1qqohl75k582g47.mysql.rds.aliyuncs.com'
    env.roledefs = {
        'django': ['121.43.103.47'],
        'java': ['121.43.57.18']
    }
    env.roledefs['static'] = [env.roledefs['django'][0]]
    cloud.bucket_static = 'test-static-cmcaifu-com'
    env.STATIC_URL = '//{}.{}.{}/'.format(cloud.bucket_static, cloud.region, cloud.domain)


@task
@roles('java')
def deploy_java():
    download('http://test.static.cmcaifu.com/downloads/apache-maven-3.1.0-bin.tar.gz')
    download('http://test.static.cmcaifu.com/downloads/apache-tomcat-7.0.67.zip')
    download('http://test.static.cmcaifu.com/downloads/jdk-7u79-linux-x64.rpm')
    run('rm -rf /opt/maven')
    run('mkdir /opt/maven')
    run('tar -xf apache-maven-3.1.0-bin.tar.gz -C /opt/maven')
    run('unzip -od /opt apache-tomcat-7.0.67.zip')
#     run('rpm --prefix=/opt/java/ -ivh jdk-7u79-linux-x64.rpm')
    run('mkdir /var/log/fhic/business-server -p')
    put('~/fhic/java.sh', '/etc/profile.d/java.sh')
    run('source /etc/profile.d/java.sh')
    put('~/fhic/maven.sh', '/etc/profile.d/maven.sh')
    run('source /etc/profile.d/maven.sh')
    maven_dir = '~/.m2/repository/com'
    run('rm -rf {}'.format(maven_dir))
    run('mkdir -p {}'.format(maven_dir))
    put('~/fhic/fhic.zip', '{}/fhic.zip'.format(maven_dir))
    run('unzip -d {0} {0}/fhic.zip'.format(maven_dir))
    run('rm {}/fhic.zip'.format(maven_dir))
    run('mkdir -p /opt/conf/business-server')
    put('~/fhic/config.properties', '/opt/conf/business-server/config.properties')


def download(path):
    if not exists(os.path.basename(path)):
        run('wget {}'.format(path))
    else:
        print('hahaah')


# ============
# =  Hello   =
# ============
@task(default=True, alias='别名测试')
def hello():
    puts('*' * 50)
    puts(cyan('  Fabric 使用指南\n'))
    puts(green('  查看所有命令: fab -l'))
    puts(green('  查看命令: fab -d 命令'))
    puts(yellow('  带参数命令请输入: fab 命令:参数'))
    puts(magenta('  手动配置env.(organization, .host, .email_host, .git_host, lb_https, newrelic_key, roledefs)'))
    puts(blue('  部署正式环境: fab prod deplay'))
    puts('  Project Name: {.project_name}'.format(env))  # 这种写法直观.
    puts('  Repositoreis: {}'.format(env.repositories))  # 这种写法可以方便链接查看.
    puts('*' * 50)


@task
def update_project():
    local('curl -fsSL https://raw.githubusercontent.com/nypisces/Free/master/gitignore/python.gitignore > .gitignore')


@task
@roles('static')
def get_file(path='~/.bashrc'):
    if exists(path):
        get(path, 'downloads/{}'.format(os.path.basename(path)))
    else:
        puts('文件 ' + yellow(path) + ' 不存在')


# ============
# =  初始化   =
# ============
@task
@roles('django')
def init_django():
    apt_upgrade()
    sudo('apt-get install -y libmysqlclient-dev libmemcached-dev libz-dev libjpeg-dev libfreetype6-dev python-dev python3-pip git gettext tree')  # tree只是为了登陆服务器时查看方便 libjpeg8-dev libpng-dev libgif-dev
    sudo('pip3 install -U virtualenvwrapper')
    # sudo('pip3 install git+https://github.com/Supervisor/supervisor.git')
    sudo('pip3 install https://github.com/Supervisor/supervisor/archive/master.zip')
    put('configs/{}.bashrc'.format(cloud.name), '~/.bashrc')
    init_code()
    run('mkvirtualenv {}'.format(env.project_name))  # 永远不要在virtualenv上用sudo
    with cd(env.project_path), prefix('workon {}'.format(env.project_name)):
        run('pip install -U -r requirements.txt')
    if env.lb_https:
        run('apt-get install －y nginx')
        put('configs/nginx.conf ', '/etc/nginx/sites-enabled/{}.conf'.format(env.host))
        run('service nginx start')


@task
@roles('django')
def init_code():
    """初始化代码库"""
    safe_mkmir('~/.ssh')
    put('configs/id_rsa', '~/.ssh/id_rsa')
    put('configs/id_rsa.pub', '~/.ssh/id_rsa.pub')
    run('chmod 400 ~/.ssh/id_rsa')
    run('chmod 400 ~/.ssh/id_rsa.pub')
    if exists(env.project_path):
        smartputs('● ├── 删除已存在代码库')
        run('rm -rf {}'.format(env.project_path))
    smartputs('● ├── 创建代码库')
    print('git clone {0.repositories[django]} {0.project_path}'.format(env))
    run('git clone {0.repositories[django]} {0.project_path}'.format(env))
    smartputs('● ├── 切换到 {} 分支'.format(env.branch))
    smartrun('git checkout {}'.format(env.branch))


@task
@roles('django')
def init_newrelic():
    sudo('echo deb http://apt.newrelic.com/debian/ newrelic non-free >> /etc/apt/sources.list.d/newrelic.list')
    sudo('wget -O- https://download.newrelic.com/548C16BF.gpg | apt-key add -')
    sudo('apt-get update')
    sudo('apt-get install -y newrelic-sysmond')
    sudo('nrsysmond-config --set license_key={}'.format(env.newrelic_key))
    sudo('/etc/init.d/newrelic-sysmond start')


@task
def init_user_table():
    sql = 'mysql -udjango -p888888 -h{} -e "alter table cmcaifu_default.accounts_user auto_increment=10000;"'.format(env.database_host)
    run(sql)


# ============
# =  Deploy  =
# ============
def apt_upgrade():
    smartputs('● ├── apt-get升级/安装')
    sudo('apt-get update')
    sudo('apt-get upgrade -y')  # 为了稳定, 不要用dist-upgrade
    sudo('apt-get clean')  # 为了稳定, 只用clean, 不要再加autoremove


@task
def deploy(mode=1):
    """部署, 可选参数0(开启DEBUG), 1(默认), 2(同时升级pip), 3(同时部署静态文件), 4(同时升级服务器)"""
    with settings(
        # hide('stdout'),
        warn_only=False
    ):
        if int(mode) > 2:
            local_deploy_static('img', 'libs', 'cloudfile', 'images')
        execute(deploy_django, mode)  # 就算只有一个地址, 只要是roles('django')这样使用, 就要放在execute内执行, 且不能加(), 否则取不到role


@roles('django')
# @parallel(pool_size=5)  # Windows下有问题
def deploy_django(mode=1):
    smartputs('🍺  开始部署')
    if int(mode) > 3:
        apt_upgrade()
        sudo('pip3 install -U pip virtualenvwrapper')
        sudo('pip3 install git+https://github.com/Supervisor/supervisor.git')
    settings = '{0.project_path}/{0.project_name}/settings.py'.format(env)
    run('sed -i "s/TEST_ENV = True/TEST_ENV = False/g" {}'.format(settings))  # 无论什么环境先还原.
    run('sed -i "s/DEBUG = True/DEBUG = False/g" {}'.format(settings))
    smartputs('● ├── 切换到 {} 分支'.format(env.branch))
    smartrun('git checkout {}'.format(env.branch))
    smartrun('git pull')
    if env.test:
        run('sed -i "s/TEST_ENV = False/TEST_ENV = True/g" {}'.format(settings))
    if int(mode) < 1:
        run('sed -i "s/DEBUG = False/DEBUG = True/g" {}'.format(settings))
    with cd(env.project_path), prefix('workon {}'.format(env.project_name)):
        if int(mode) > 1:
            run('pip install -U -r requirements.txt')
            run('pip install -U Pillow --no-cache-dir')  # 保证Pillow重新安装
        if env.test:
            run('pip install -U django-cors-headers')
        run('python manage.py compilemessages')
        if env.test:
            run('python manage.py makemigrations')
            run('python manage.py migrate')
            smartputs('● ├── 备份migrations')
            with quiet():
                run('find . -name  migrations |xargs tar -cvf migrations.tgz')
            run('mv migrations.tgz ~/')
        else:
            puts(yellow('正式环境不开启migrations, 请手动进行'))
    if exists('/tmp/supervisor.sock'):
        supervisor_update()
        supervisor_restart('gunicorn')
    else:
        supervisor_conf()
    smartputs('🍻  完成部署')


@task
@roles('django')
def restart_gunicorn():
    smartputs('🍺  开始重启')
    if exists('/tmp/supervisor.sock'):
        supervisor_update()
        supervisor_restart('gunicorn')
    else:
        supervisor_conf()
    smartputs('🍻  完成重启')


@task
@roles('static')
def restart_send_sms(mode=1):
    smartputs('🍺  先关闭掉进程')
    smartrun("ps -ef | grep 'send_sms_redis.py' |grep -v grep | awk '{print $2}' |xargs kill -9")
    puts('● ├── 重新启动脚本')
    with settings(warn_only=True), cd(env.project_path), prefix('workon {}'.format(env.project_name)):
        run('nohup python sbin/send_sms_redis.py 0 >/dev/null 2>&1 &'.format(mode))


# ============
# =  Local   =
# ============
@task
def local_init_mysql():
    auth = '-uroot'
    local('mysqldump {} {}_default -d > default.sql'.format(auth, env.project_name))
    for i in range(4):
        local('mysql {} -e "CREATE SCHEMA IF NOT EXISTS {}_{} DEFAULT CHARACTER SET utf8mb4 ;"'.format(auth, env.project_name, i))
        local('mysql {} {}_{} < migrate/shard.sql'.format(auth, env.project_name, i))


@task
def local_cleanmigrations():
    local('for dir in `find . -type d -name migrations`;do find $dir -type f |grep -v "__init__.py" ;done |xargs rm -f')


@task
def local_collectstatic(*args):
    """收集静态文件"""
    exclude = ('img', 'libs', 'cloudfile', 'images',
               'admin', 'django-redactor', 'rest_framework', 'rest_framework_swagger', 's3direct',
               'suit', 'cms', 'ckeditor')
    ignores = ['debug_toolbar'] + ([] if args == ('all',) else [x for x in exclude if x not in args])  # 不需要上传debug_toolbar
    local_workon('python manage.py collectstatic --no-input -i {} --settings={}.local_settings'.format(' -i '.join(ignores), env.project_name))


@task
def local_createsuperuser(username='admin'):
    local_workon('python manage.py createsuperuser --username {0} --email {0}@{1} --settings={2}.local_settings'.format(username, env.email_host, env.project_name))


@task
def local_deploy_static(*args):
    """可选参数all(上传所有) :img,libs(多上传img, libs), 注意子路径含img也会过滤"""
    local_collectstatic(*args)
    top = 'static/'
    tmp = 'tmp/static/'
    for dirpath, dirnames, filenames in os.walk(top):
        for filename in filenames:
            if filename.startswith('.'):  # 过滤隐藏文件.
                continue
            path = os.path.join(dirpath, filename)
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            if not path.startswith('libs/') and content_type in ['text/css', 'application/javascript']:  # 处理自己的css和js.
                css_in = open(path, 'r')
                try:
                    old = css_in.read()
                    # new = old.replace('url(/static/', 'url({}'.format(env.STATIC_URL))
                    new = old.replace('/static/', '{}'.format(env.STATIC_URL))
                    if old != new:
                        css_out = open(path, 'w')
                        css_out.write(new)
                        css_out.close()
                finally:
                    css_in.close()
            out_path = path
            is_gzip = content_type.startswith('text/') or content_type in ['application/javascript', 'application/json']
            dest_name = path[len(top):]  # 含路径.
            if is_gzip:
                out_path = os.path.join(tmp, dest_name)
                dir = os.path.dirname(out_path)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                f_in = open(path, 'rb')
                f_out = open(out_path, 'wb')
                try:
                    f_out = gzip.GzipFile(fileobj=f_out)
                    f_out.write(f_in.read())
                finally:
                    f_out.close()
                    f_in.close()
            params_url = 'http://test.cmcaifu.com/upload_params/{}/?filename={}&bucket={}'.format(cloud.name, dest_name, cloud.bucket_static)
            if is_gzip:
                params_url = '{}&content_encoding=gzip'.format(params_url)
            if path.startswith('static/libs'):
                params_url = '{}&cache_control=public,max-age=864000'.format(params_url)
            data = requests.get(params_url).text
            url = 'http://{}'.format(cloud.bucket_static.replace('-', '.'))  # 阿里云bucket名中不能出现.号
            response = requests.post(url, files={'file': open(out_path, 'rb')}, data=json.loads(data))
            if 200 < response.status_code < 300:
                puts(green(dest_name))
            else:
                puts(red(response.status_code))
    safe_delete(top)
    safe_delete(tmp)


@task
def local_diffsettings():
    local_workon('python manage.py diffsettings')


@task
def local_makemessages():
    """第一次自己在locale下手动建立需要翻译的目录"""
    with path('/usr/local/opt/gettext/bin'):  # OS X下brew install gettext 需手动path
        local_workon('python manage.py makemessages -l en --ignore={}/templates/registration/* --no-wrap'.format(env.project_name))
#         local_workon('python manage.py makemessages -d djangojs --no-wrap')
    puts(green('完成, 请用rosetta翻译英文然后执行tx_sync'))


@task
def local_compilemessages():
    """编译语言文件"""
    with path('/usr/local/opt/gettext/bin'):
        local_workon('python manage.py compilemessages')


@task
def local_makemigrations(app=''):
    local_workon('python manage.py makemigrations --settings={}.local_settings {}'.format(env.project_name, app))


@task
def local_migrate():
    local_workon('python manage.py migrate --settings={}.local_settings'.format(env.project_name))


@task
def local_runtest(testInfo=None):
    if testInfo:
        local_workon('python manage.py test {0}.apps.{1} --settings={0}.local_settings'.format(env.project_name, testInfo, env.project_name))
    else:
        dirlist = ['api']
        for dirname in dirlist:
            local_workon('python manage.py test {0}.apps.{1}.tests --settings={0}.local_settings'.format(env.project_name, dirname))


@task
def local_runserver(port='8000', migrate='yes', ssl=''):
    """可选参数<端口号><是否migrate> 例: local_runserver:8001,''"""
#     branch = local('git status', True).split('\n')[0].replace('On branch ', '')
#     if branch in ['develop', 'master']:
#         puts('不要在 {} 分支修改代码'.format(yellow(branch)))
#         return
#     if not os.path.exists('/tmp/mysql.sock'):
#         local('mysql.server start')
#         local('memcached -m 32 -l 127.0.0.1 -d')
    if migrate:
        local_makemigrations()
        local_migrate()
    local_workon('python manage.py run{}server 0.0.0.0:{} --settings={}.local_settings'.format(ssl, port, env.project_name))


@task
def local_install(source=' -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com'):
    local('sudo pip install -U Fabric requests{}'.format(source))
    local('sudo pip3 install -U virtualenvwrapper transifex-client'.format(source))
    local('sudo pip3 install -U -r requirements/code.txt{}'.format(source))
    if not os.path.exists(os.path.expanduser('~/Envs/{}'.format(env.project_name))):
        with settings(warn_only=True):  # 加了--system-site-packages执行会报错, 待查Fabric的问题
            local('/bin/bash -lc "mkvirtualenv {} --system-site-packages"'.format(env.project_name))
    local_workon('sudo pip install -U -r requirements/dev.txt{}'.format(source))  # 理论上不要sudo, DRF有时候需要
    puts(green('更新依赖完毕, 使用空参数 local_install: 可不走阿里云的源获取最新的包'))


@task
def local_reinstall(source=' -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com'):
    local('/bin/bash -lc "rmvirtualenv {}"'.format(env.project_name))
    local('sudo rm -rf ~/Envs/{}/'.format(env.project_name))  # python的shutil.rmtree和os.chmod无法解决权限问题
    local_install(source)


@task
def local_sendtestemail(email):
    local_workon('python manage.py sendtestemail {} '.format(email))  # TODO: 传入多个邮件地址.


def local_proxy(command, proxy=''):
    if command.startswith('git') and env.git_host == 'github.com':
        local('proxychains4 {}'.format(command))
    else:
        local(command)


def local_workon(command):
    local('/bin/bash -lc "workon {} && {}"'.format(env.project_name, command))


# =========
# =  git  =
# =========
@task
def commit_and_sync(comment=None):
    """git commit and sync"""
    output_list = local('git status', True).split('\n')
    branch = output_list[0].replace('On branch ', '')
    if branch in ['develop', 'master']:
        puts('不允许在 {} 分支 用 {} 命令直接操作'.format(yellow(branch), get_function_name()))
    elif 'nothing to commit' in output_list[-1]:
        puts('{} 分支没有变动, 不需要提交'.format(yellow(branch)))
        if 'is ahead of' in output_list[1]:
            puts('同步 {} 分支'.format(yellow(branch)))
            local_proxy('git push')
    else:
        local('git reset')
        delete_files = [x.strip() for x in output_list if x.find('deleted:') != -1]
        for file in delete_files:
            filename = file.split(':')[1].strip()
            local('git rm {}'.format(filename))
        local('git add .')
        if not comment:
            comment = raw_input('请输入提交的注解: ')
        local('git status')
        local('git commit -m "{}"'.format(comment))
        local_proxy('git push')


@task
def update_from_develop():
    """从 develop 更新到当前分支"""
    output_list = local('git status', True).split('\n')
    branch = output_list[0].replace('On branch ', '')
    if branch in ['develop', 'master']:
        puts('不允许在 {} 分支 用 {} 命令直接操作'.format(yellow(branch), get_function_name()))
    elif 'nothing to commit' in output_list[-1]:
        local_proxy('git pull origin develop')
        local_compilemessages()
    else:
        local('git status')
        puts('当前 {} 分支有更新未提交, 请先执行 fab git_commit 命令提交'.format(yellow(branch)))


@task
def update_to_develop():
    """从当前分支更新到 develop """
    output_list = local('git status', True).split('\n')
    branch = output_list[0].replace('On branch ', '')
    if branch in ['develop', 'master']:
        puts('不允许在 {} 分支 用 {} 命令直接操作'.format(yellow(branch), get_function_name()))
    elif 'nothing to commit' in output_list[-1]:
        confirm = raw_input('是否已经update_from_develop? [y/N]: '.format(yellow(branch)))
        if confirm.lower() in ['ok', 'y', 'yes']:
            puts('从 {} 合并到 develop'.format(yellow(branch)))
            local('git checkout develop')
            local_proxy('git pull')
            local('git merge {}'.format(branch))
            local_proxy('git push')
            local('git checkout {}'.format(branch))
    else:
        local('git status')
        puts('当前 {} 分支有更新未提交, 请先执行 fab git_commit 命令提交'.format(yellow(branch)))


# =============
# = Transifex =
# =============
@task
def tx_sync():
    local_proxy('tx push -s')
    local_proxy('tx pull -a')
    local_compilemessages()


# ==================
# = Configurations =
# ==================
# Supervisor
# --------------------------------------------------------------------------------
def supervisor_conf():
    run('supervisord -c {}/etc/supervisord.conf'.format(env.project_path))  # 配置好gunicorn的directory之后任意目录运行都行


def supervisor_unlink():  # 停止supervisord
    run('unlink /tmp/supervisor.sock')


def supervisor_start(process='all'):  # 因为上面是进入目录执行的, 所以重启之类的也要进入目录执行.
    smartrun('supervisorctl start {}'.format(process))


def supervisor_restart(process='all'):
    smartrun('supervisorctl restart {}'.format(process))


def supervisor_stop(process='all'):
    smartrun('supervisorctl stop {}'.format(process))


def supervisor_update():  # 更新配置文件.
    smartrun('supervisorctl update')


# ============
# = 工具方法  =
# ============
def safe_mkmir(dir):
    if not exists(dir):
        run('mkdir {}'.format(dir))


def safe_delete(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)


def smartrun(command):
    with cd(env.project_path):
        run(command)


def smartputs(prefix):
    if env.host_string in env.roledefs['django']:
        sputs(prefix, green('【Django 应用服务器】[{}]'.format(env.host_string)))
    elif env.host_string in env.roledefs['java']:
        sputs(prefix, red('【Java 应用服务器】[{}]'.format(env.host_string)))
    else:
        sputs(prefix, magenta('🌵 【未知类型服务器】[{}]'.format(env.host_string)))


def sputs(prefix, text):
    puts(cyan(prefix) + ('【测试】' if env.test else '') + cyan('环境') + text + cyan(' --'), show_prefix=False)


def get_function_name():
    return sys._getframe(1).f_code.co_name  # _getframe()则是自己的名字
