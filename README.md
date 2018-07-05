# WZ_cn_mooc_dl-master
下载公开网课视频

<br>说明：此代码是基于原作者renever的cn_mooc_dl进行修改的，renever的代码由于从2015年就停止维护了，现在运行时会有问题。目前只修改了其中的study163_dl.py和utils.py，可以正常下载网易云课堂（`study.163.com`）上的免费视频了，后续还会继续修改更新，也欢迎广大感兴趣的Coder一起参与进来，继续 modify & refine & optimize 。

1. 中国大学 MOOC（`icourse163.org`）视频下载
2. 清华学堂在线（`xuetangx.com`）视频下载
3. 网易云课堂（`study.163.com`）视频下载
4. 网易云课堂计算机专业课程（`mooc.study.163.com`）视频下载

<br>###测试环境：   `PYTHON 2.7.15； WIN 7 64位`
<br>###依赖包： `requests(2.19.1)， beautifulsoup4(4.6.0)`

	pip install requests
	pip install beautifulsoup4


###中国大学 MOOC（`icourse163.org`）       +++待修改+++

    python icourse163_dl.py  -u <username@xxx.xxx> -p <password>  "url"

* 其中 url 是打开课程页面后，浏览器地址栏‘#’之前部分。以“国防科大高等数学（一）”为例，打开课程后浏览器地址栏显示为：
`http://www.icourse163.org/learn/nudt-9004#/learn/announce`,则 url 为 `http://www.icourse163.org/learn/nudt-9004`
* 网易流量时快时慢，时有时无。可以运行两遍，之前没下完的可断线续传。



###清华学堂在线（`xuetangx.com`）       +++待修改+++

    python xuetangx_dl.py  -u <username@xxx.xxx> -p <password>  "url"
    
* 其中 url 是课程课件页面的浏览器地址，比如：`http://www.xuetangx.com/courses/HITx/GO90300700/2014_T2/courseware/`




###网易云课堂（`study.163.com`）       +++Done+++

    python study163_dl.py "url"
    e.g. python study163_dl.py "http://study.163.com/course/introduction/334013.htm"
         python study163_dl.py "http://study.163.com/course/introduction.htm?courseId=1458012"
	 
* 云课堂新增专栏“计算机专业课程”那一部分（mooc.study.163.com）有点特殊，具体看下面。
* 收费课程下不了。
* 网易云课堂不必登录。其中 url 是课程列表页面浏览器地址，比如:
`http://study.163.com/course/introduction/334013.htm`  玩转 C语言 基础课堂
`http://study.163.com/course/introduction.htm?courseId=1458012`  8种风光摄影技巧教学视频（免费）
* 不能续传。




###云课堂计算机专业课程（`mooc.study.163.com`）      +++待修改+++

    python icourse163_dl.py  -u <username@xxx.xxx> -p <password>  "url" 
    
* 云课堂新增专栏“计算机专业课程”，虽然挂在云课堂页面上，但是里面的结构是和“中国大学 MOOC”一样的。所以要用 `icourse163_dl.py` 来下载。
* 其中 url 类似这样： `http://mooc.study.163.com/learn/ZJU-1000002014`


#####--path 用于指定保存文件夹， --overwrite 指定是否覆盖

![](logo/wangyiykt.jpg)

<br>wzxuexizhuanyong@163.com
