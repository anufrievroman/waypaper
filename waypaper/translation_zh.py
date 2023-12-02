"""Chinese Simplified translations of the program interface"""

MSG_DESC = (
    "Wayland 和 X11 的 GUI 壁纸设置器。它用作 feh、swaybg、wallutils 和 swww 的前端。"
)
MSG_INFO = "欲了解更多信息，请访问:\nhttps://github.com/anufrievroman/waypaper"

MSG_ARG_HELP = "版本信息"
MSG_ARG_FILL = "指定所选图像填充屏幕"
MSG_ARG_REST = "恢复上个壁纸"
MSG_ARG_BACK = "指定使用哪个后端来设置壁纸"
MSG_ARG_RAND = "设置随机壁纸"

MSG_PATH = "选择的图像路径："
MSG_SELECT = "选择"
MSG_REFRESH = "刷新"
MSG_RANDOM = "随机"
MSG_EXIT = "退出"
MSG_SUBFOLDERS = "子文件夹"
MSG_CHANGEFOLDER = "更改壁纸文件夹"
MSG_CHOOSEFOLDER = "请选择一个文件夹"
MSG_CACHING = "缓存壁纸..."
MSG_SETWITH = "发送设置壁纸的命令是用"

MSG_HELP = "Waypaper 的热键：\n\nhjkl -导航 (←↓↑→)\nf -更改壁纸文件夹\n"
MSG_HELP += "g -滚动到顶部\nG -滚动到底部\nR -设置随机壁纸\nr -重新缓存壁纸\n"
MSG_HELP += "s -包含/排除子文件夹中的图像\n？ -帮助\nq -退出\n\n"
MSG_HELP += MSG_INFO

ERR_CACHE = "删除缓存时出错"
ERR_BACKEND = "系统中似乎没有安装壁纸后端。\n"
ERR_BACKEND += "使用包管理器安装至少以下后端之一：\n\n"
ERR_BACKEND += "-swaybg (用于 Wayland)\n-swww (用于 Wayland)\n"
ERR_BACKEND += "-feh (对于 Xorg)\n-wallutils (对于 Xorg 和 Wayland)\n\n"
ERR_BACKEND += MSG_INFO
ERR_WALL = "更改壁纸时出错："
ERR_NOTSUP = "不支持后端："
ERR_DISP = "确定监视器名称时出错："
ERR_KILL = "与killall相关的警告："

TIP_SUBFOLDER = "在子文件夹中包含/排除图像"
TIP_REFRESH = "重新缓存图像文件夹"
TIP_FILL = "选择填充类型"
TIP_BACKEND = "选择后端"
TIP_SORTING = "选择排序类型"
TIP_DISPLAY = "选择显示"
TIP_COLOR = "选择背景颜色"
TIP_RANDOM = "设置随机壁纸"
TIP_EXIT = "退出应用程序"
