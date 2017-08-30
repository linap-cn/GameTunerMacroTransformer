# GameTuner Macro Transformer
## 简介
用于三星游戏游戏调节器的宏命令简化及打包脚本  
将简单命令脚本转化为游戏调节器可以调用的json压缩格式  
因游戏服务功能限制，只有模拟触屏的功能，无法实现分支、循环、找色等其他功能。
* * *

## 命令详解
* move 坐标x,坐标y  
* move 坐标x,坐标y,花费时间  
* down 坐标x,坐标y  
* up  
* tap 坐标x,坐标y  
* delay 等待时间  

支持多点触控，命令分别是move#1-move#15、tap#1-tap#15、down#1-down#15、up#1-up#15,不带#相当于#0。  
  
注意：  
多点触控需自行理清逻辑，如#0点未落下，无法使用#1点。
* * *
## 宏文件格式：
包名  
宽度 高度  
命令1  
命令2  
...  
* * *
## 一般使用方法：
1. 使用宏命令录制器，在需要写宏的程序中录制最简单的宏一个。
2. 在/sdcard/GameTuner文件夹中找到录制的宏，使用pack.py脚本解压，获取应用包名，版本号，分辨率等数据。
3. 编写宏文件。
4. 使用macro2m.py脚本转化打包成游戏调节器能识别的格式。
5. 把宏文件拷入/sdcard/GameTuner。
