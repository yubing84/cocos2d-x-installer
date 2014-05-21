
# Cocos Engine 安装包生成工具 #

用于生成 Cocos Engine 的工程配置。

## 配置要求 ##

1. 获取安装包所需打包文件的要求：
	* 系统：Mac
	* 软件：python 2.7
2. 生成 Mac Installer 的系统与软件要求：
	* 系统：Mac 
	* 软件：
		* python 2.7
		* Iceberg
3. 生成 Windows Installer 的系统与软件要求：
	* 系统：windows
	* 软件：Inno Setup 

## 准备打包所需引擎与 IDE 文件 ##

### IDE 文件 ###
* 将 Mac 版 IDE 文件放在 `cocos/ide` 目录下
* 将 Windows 版 64bit IDE 文件放在 `cocos-win32/ide-64bit` 目录下
* 将 Windows 版 32bit IDE 文件放在 `cocos-win32/ide-32bit` 目录下

### 引擎文件 ###
* 在 Mac 系统下，使用 python 脚本 `tools/get-engine.py` 自动生成打包所需的引擎文件，参数说明：
	* -x, 指定 cocos2d-x 仓库目录
	* -j, 指定 cocos2d-js 仓库目录
	* -t, 可以为 `win32`或者`mac`，默认为 `mac`。指定生成 `windows installer` 或者 `mac installer` 所需的引擎文件
* 注意事项：
	* 生成引擎文件之前，需要保证 cocos2d-x 仓库与 cocos2d-js 仓库当前指向的 commit 为所需要打包的 commit


## 生成 Mac Installer ##

* 生成 pkg 文件：使用 Iceberg 打开配置文件 `installer/installer-proj-mac/Cocos Engine.packproj`，在 Iceberg 界面中执行 Build 操作。完成后，在 `release` 目录下会生成 `Cocos Engine.pkg`
* 生成 dmg 文件：运行 `tools/gen-dmg.sh` 脚本，完成后，在 `release` 目录下会生成 `Cocos Engine.dmg`
* 注意事项：
	* 如果使用者的机器上有运行 XtraFinder 插件，可能生成的 pkg 文件的 icon 和 dmg 的背景图会有问题，最好将 XtraFinder 关闭后，重新执行上述两个步骤。


## 生成 Windows Installer ##

* 安装 Inno Setup 后，将 Inno Setup 的目录设置到系统的 `path` 环境变量中。
* 运行批处理文件 `tools/gen-exe.bat`，执行完成后，在 `release` 目录会生成 `Cocos Engine-32bit.exe`和`Cocos Engine-64bit.exe`
* 注意事项：
	* 这里的 32bit 和 64bit 指的是与 jre 的对应版本，而不是 windows 系统版本。