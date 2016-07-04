{{ project_name }}
=========================

Quickstart
=========================
```bash
cd ~/workspace
django-admin.py startproject --template=django_layout {{ project_name }}
cd ~/workspace/{{ project_name }}
fab local_install
fab local_makemessages
```
```bash
cd ~/workspace/{{ project_name }}
fab local_runserver
```
```bash
cd ~/workspace/{{ project_name }}
chmod 700 go/signature_ubuntu
chmod 700 go/signature_mac
```

```sql
CREATE SCHEMA `{{ project_name }}_default` DEFAULT CHARACTER SET utf8mb4 ;
CREATE SCHEMA `{{ project_name }}_0` DEFAULT CHARACTER SET utf8mb4 ;
CREATE SCHEMA `{{ project_name }}_1` DEFAULT CHARACTER SET utf8mb4 ;
```
```sql
INSERT INTO `cmcaifu_default`.`accounts_user` (`id`, `username`, `nickname`, `email`, `gender`, `is_staff`, `is_active`, `date_joined`) VALUES ('110', 'ny@fhic.com', 'NY', 'ny@fhic.com', 'm', '1', '1', '2016-01-20 00:00:00.000000');
```
如果出现未知500错误
检查cache服务器是否设置

Introduction
=========================
Tips
----
`# nopep8` 对PyDev似乎无效
worker 数建议 1 + 2 * cpu核心数

Django
------
的用户名大小写敏感, 但MySQL自动大小写不敏感, 所以无需特别处理
要处理参见下面, 修改UserManager的get_by_natural_key即可无需写后端
https://code.djangoproject.com/ticket/2273

永远不要设置任何(包括字符串)类型为`null=True`，只使用`blank=True`
顺序 max_length, choices, default, blank=True
!!! 手动建立migrations模块, 否则不会自动建库

Python
------
代码使用单引号`''`，只在注释的时候和被单引号包围的时候使用双引号`""`
定期清理print()

JavaScript
----------
代码使用单引号`''`

Design
-------------------------

Documentation & Example Code
----------------------------

Installation
=========================

Community Resources
-------------------------

Contributing
-------------------------

Forks, patches and other feedback are always welcome.

Credits
-------------------------

[Design Document]: https://github.com/nypisces/{{ project_name }}/blob/master/Docs/test.md
* [Eclipse](http://www.eclipse.org/)
* [Django](http://www.djangoproject.com/)
* [Django REST framework](http://www.django-rest-framework.org/)
