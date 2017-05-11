
# 绅士图三贱客爬虫
====================

## iOS App Name：

* **ACT Art**

    [AppStore Link](https://itunes.apple.com/cn/app/?mt=8)

* **Artibee**

    [AppStore Link](https://itunes.apple.com/cn/app/artibee-二次元动漫美女壁纸杂志/id1190202850?mt=8)

* **Beauty**

    [AppStore Link](https://itunes.apple.com/cn/app/the-beauty-美伦壁纸写真杂志/id1190341460?mt=8)


## usage:
```
usage: script.py [-h] [-f FLAG] token

positional arguments:
  token                 token for scrapy, eg: 9132210801044103780693

optional arguments:
  -h, --help            show this help message and exit
  -f FLAG, --flag FLAG  1 or 0,only download H imgs,Deafult false

```

### Example:
```
python Artibee.py 9132210801044105040315
python Beauty.py 9132210801044103780693 -f 1
```

### Forked from 

[nomemo/ACGArtImageBatchDone](https://github.com/nomemo/ACGArtImageBatchDone)