# PySpider-World
PySpider爬虫框架使用

# 环境

- python3.6
- miniconda
- mongodb
- redis
- PhantomJS

# 安装

1. PhantomJS

下载链接：
http://phantomjs.org/download.html

2. 使用conda命令创建运行环境，将自动创建一个名为python36的环境

```
conda env create -f conda-env.yml
```

# 配置
无

# 运行

使用conda命令切换运行环境

```
activate python36
```

运行PySpider

```
pyspider all
```

# pyspider目录

用户爬虫代码保存在sqlite中
目录为：用户目录下的data目录
  project.db 保存了爬虫代码
  task.db 保存了爬虫任务执行记录
  result.db 保存了默认的返回结果