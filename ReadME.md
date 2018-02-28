#### 2018-02-27

selenium + chromedriver 模拟浏览器登录微博

#### 2018-02-28
更新自动发动态。
唯一要注意的一点是设置好延时 , 给 browser 获取 cookie 的时间。在点击登录按钮后 , 立刻再请求主页面则是不带 cookie 的browser 发起请求。相当于没有进行登录