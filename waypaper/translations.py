"""Module with translation into various languages. To add a new language, add a new class"""


class English:
    def __init__(self):
        self.msg_desc = "GUI wallpaper setter for Wayland and X11. It works as a frontend for feh, swaybg, wallutils, hyprpaper, and swww."
        self.msg_info = "For more information, visit:\nhttps://github.com/anufrievroman/waypaper"

        self.msg_arg_help = "print version of the program"
        self.msg_arg_fill = "specify how to fill the screen with chosen image"
        self.msg_arg_rest = "restore last wallpaper"
        self.msg_arg_back = "specify which backend to use to set wallpaper"
        self.msg_arg_rand = "set a random wallpaper"
        self.msg_arg_list = "list wallpapers in json to standard out"
        self.msg_arg_wall = "set the specified wallpaper"

        self.msg_path = "Selected image path:"
        self.msg_select = "Select"
        self.msg_refresh = "Refresh"
        self.msg_random = "Random"
        self.msg_exit = "Exit"
        self.msg_subfolders = "Show subfolders"
        self.msg_hidden = "Show hidden"
        self.msg_gifs = "Show gifs only"
        self.msg_changefolder = "Change wallpaper folder"
        self.msg_choosefolder = "Please choose a folder"
        self.msg_caching = "Caching wallpapers..."
        self.msg_setwith = "Sent command to set wallpaper was set with"

        self.msg_help = "Waypaper's hotkeys:\n\nhjkl - Navigation (←↓↑→)\nEnter - Set selected wallpaper\nf - Change wallpaper folder\n"
        self.msg_help += "g - Scroll to top\nG - Scroll to bottom\nR - Set random wallpaper\nr - Recache wallpapers\n"
        self.msg_help += ". - Toggle hidden images\ns - Toggle images in subfolders\n? - Help\nq - Exit\n\n"
        self.msg_help += self.msg_info

        self.err_cache = "Error deleting cache"
        self.err_backend = "Looks like none of the wallpaper backends is installed in the system.\n"
        self.err_backend += "Use your package manager to install at least one of these backends:\n\n"
        self.err_backend += "- swaybg (for Wayland)\n- swww (for Wayland)\n"
        self.err_backend += "- hyprpaper (for Wayland)\n- feh (for Xorg)\n- wallutils (for Xorg & Wayland)\n\n"
        self.err_backend += self.msg_info
        self.err_wall = "Error changing wallpaper:"
        self.err_notsup = "The backend is not supported:"
        self.err_disp = "Error determining monitor names:"

        self.tip_refresh = "Recache the folder of images"
        self.tip_fill = "Choose fill type"
        self.tip_backend = "Choose backend"
        self.tip_sorting = "Choose sorting type"
        self.tip_display = "Choose display"
        self.tip_color = "Choose background color"
        self.tip_random = "Set random wallpaper"
        self.tip_exit = "Exit the application"


class German:
    def __init__(self):
        self.msg_desc = "Grafisches Hintergrundbild-Auswahlwerkzeug für Wayland und X11. Es dient als Frontend für feh, swaybg, wallutils, hyprpaper und swww."
        self.msg_info = "Weitere Informationen finden Sie unter:\nhttps://github.com/anufrievroman/waypaper"

        self.msg_arg_help = "gibt die Programmversion aus"
        self.msg_arg_fill = "legt fest, wie das Bild skaliert werden soll, um den gesamten Bildschirm auszufüllen"
        self.msg_arg_rest = "stellt das zuletzt verwendete Hintergrundbild wieder her"
        self.msg_arg_back = "legt das Backend fest, welches zum Setzen des Hintergrundbildes verwendet werden soll"
        self.msg_arg_rand = "wählt ein zufälliges Hintergrundbild aus"
        self.msg_arg_list = "list wallpapers in json to standard out"
        self.msg_arg_wall = "set the specified wallpaper"

        self.msg_path = "Pfad zum ausgewählten Bild:"
        self.msg_select = "Auswählen"
        self.msg_refresh = "Aktualisieren"
        self.msg_random = "Zufällig"
        self.msg_exit = "Beenden"
        self.msg_subfolders = "Unterordner"
        self.msg_hidden = "Hidden"
        self.msg_gifs = "Show only gifs"
        self.msg_changefolder = "Hintergrundbild-Ordner ändern"
        self.msg_choosefolder = "Bitte wählen Sie einen Ordner aus"
        self.msg_caching = "Hintergrundbilder werden zwischengespeichert..."
        self.msg_setwith = "Hintergrundbild wurde mit folgendem Befehl gesetzt"

        self.msg_help = "Waypapers Tastenkürzel:\n\nhjkl - Navigation (←↓↑→)\nf - Hintergrundbild-Ordner ändern\n"
        self.msg_help += "g - Zum Anfang scrollen\nG - Zum Ende scrollen\nR - Zufälliges Hintergrundbild\nr - Hintergrundbilder zwischenspeichern\n"
        self.msg_help += ". - Versteckte Bilder einbeziehen/ausschließen\ns - Unterordner mit einbeziehen\n? - Hilfe\nq - Beenden\n\n"
        self.msg_help += self.msg_info

        self.err_cache = "Fehler beim Löschen des Zwischenspeichers"
        self.err_backend = "Es konnte kein Hintergrundbild-Backend gefunden werden.\n"
        self.err_backend += "Installieren Sie mindestens eines der folgenden Backends:\n\n"
        self.err_backend += "- swaybg (für Wayland)\n- swww (für Wayland)\n"
        self.err_backend += "- hyprpaper (fur Wayland)\n- feh (für Xorg)\n- wallutils (für Xorg & Wayland)\n\n"
        self.err_backend += self.msg_info
        self.err_wall = "Fehler beim Ändern des Hintergrundbildes:"
        self.err_notsup = "Das folgende Backend wird nicht unterstützt:"
        self.err_disp = "Fehler beim Ermitteln der Monitor-Namen:"

        self.tip_refresh = "Erneutes einlesen des Hintergrundbild-Ordners"
        self.tip_fill = "Skalierungsart auswählen"
        self.tip_backend = "Backend auswählen"
        self.tip_sorting = "Sortierungsart auswählen"
        self.tip_display = "Bildschirm auswählen"
        self.tip_color = "Hintergrundfarbe auswählen"
        self.tip_random = "Ein zufälliges Hintergrundbild auswählen"
        self.tip_exit = "Das Programm beenden"


class French:
    def __init__(self):
        self.msg_desc = "Sélecteur de papier peint graphique pour Wayland et X11. Il fonctionne comme une interface pour feh, swaybg, wallutils, hyprpaper, et swww."
        self.msg_info = "Pour plus d'informations, visitez :\nhttps://github.com/anufrievroman/waypaper"

        self.msg_arg_help = "afficher la version du programme"
        self.msg_arg_fill = "spécifier comment remplir l'écran avec l'image choisie"
        self.msg_arg_rest = "restaurer le dernier papier peint"
        self.msg_arg_back = "spécifier quel backend utiliser pour définir le papier peint"
        self.msg_arg_rand = "définir un papier peint aléatoire"
        self.msg_arg_list = "list wallpapers in json to standard out"
        self.msg_arg_wall = "set the specified wallpaper"

        self.msg_path = "Chemin de l'image sélectionnée :"
        self.msg_select = "Sélectionner"
        self.msg_refresh = "Actualiser"
        self.msg_random = "Aléatoire"
        self.msg_exit = "Quitter"
        self.msg_subfolders = "Sous-dossiers"
        self.msg_hidden = "Hidden"
        self.msg_gifs = "Show only gifs"
        self.msg_changefolder = "Changer de dossier de papier peint"
        self.msg_choosefolder = "Veuillez choisir un dossier"
        self.msg_caching = "Mise en cache des papiers peints..."
        self.msg_setwith = "La commande envoyée pour définir le papier peint a été définie avec"

        self.msg_help = "Raccourcis clavier de Waypaper :\n\nhjkl - Navigation (←↓↑→)\nf - Changer de dossier de papier peint\n"
        self.msg_help += "g - Faire défiler vers le haut\nG - Faire défiler vers le bas\nR - Définir un papier peint aléatoire\nr - Recréer le cache des papiers peints\n"
        self.msg_help += ". - Inclure/exclure les images cachées\ns - Inclure/exclure les images des sous-dossiers\n? - Aide\nq - Quitter\n\n"
        self.msg_help += self.msg_info

        self.err_cache = "Erreur lors de la suppression du cache"
        self.err_backend = "Il semble qu'aucun des backends de papier peint ne soit installé sur le système.\n"
        self.err_backend += "Utilisez votre gestionnaire de paquets pour installer au moins l'un de ces backends :\n\n"
        self.err_backend += "- swaybg (pour Wayland)\n- swww (pour Wayland)\n"
        self.err_backend += "- hyprpaper (pour Wayland)\n- feh (pour Xorg)\n- wallutils (pour Xorg & Wayland)\n\n"
        self.err_backend += self.msg_info
        self.err_wall = "Erreur lors du changement de papier peint :"
        self.err_notsup = "Le backend n'est pas pris en charge :"
        self.err_disp = "Erreur lors de la détermination des noms des moniteurs :"

        self.tip_refresh = "Recréer le dossier d'images"
        self.tip_fill = "Choisir le type de remplissage"
        self.tip_backend = "Choisir le backend"
        self.tip_sorting = "Choisir le type de tri"
        self.tip_display = "Choisir l'affichage"
        self.tip_color = "Choisir la couleur de fond"
        self.tip_random = "Définir un papier peint aléatoire"
        self.tip_exit = "Quitter l'application"


class Polish:
    def __init__(self):
        self.msg_desc = "Graficzne ustawiacz tapet dla Wayland i X11. Działa jako interfejs dla feh, swaybg, wallutils, hyprpaper, i swww."
        self.msg_info = "Aby uzyskać więcej informacji, odwiedź:\nhttps://github.com/anufrievroman/waypaper"

        self.msg_arg_help = "wyświetl wersję programu"
        self.msg_arg_fill = "określ, jak wypełnić ekran wybranym obrazem"
        self.msg_arg_rest = "przywróć ostatnią tapetę"
        self.msg_arg_back = "określ, który backend użyć do ustawienia tapety"
        self.msg_arg_rand = "ustaw losową tapetę"
        self.msg_arg_list = "list wallpapers in json to standard out"
        self.msg_arg_wall = "set the specified wallpaper"

        self.msg_path = "Wybrana ścieżka obrazu:"
        self.msg_select = "Wybierz"
        self.msg_refresh = "Odśwież"
        self.msg_random = "Losowo"
        self.msg_exit = "Wyjście"
        self.msg_subfolders = "Podkatalogi"
        self.msg_hidden = "Hidden"
        self.msg_gifs = "Show only gifs"
        self.msg_changefolder = "Zmień folder z tapetami"
        self.msg_choosefolder = "Proszę wybrać folder"
        self.msg_caching = "Kasowanie tapet..."
        self.msg_setwith = "Wysłano polecenie ustawienia tapety z"

        self.msg_help = "Skróty klawiszowe Waypaper:\n\nhjkl - Nawigacja (←↓↑→)\nf - Zmień folder z tapetami\n"
        self.msg_help += "g - Przewiń do góry\nG - Przewiń na dół\nR - Ustaw losową tapetę\nr - Odśwież katalog z tapetami\n"
        self.msg_help += ". - Załącz/Wyłącz ukryte obrazy\ns - Dołącz/wyłącz obrazy z podkatalogów\n? - Pomoc\nq - Wyjście\n\n"
        self.msg_help += self.msg_info

        self.err_cache = "Błąd podczas usuwania pamięci podręcznej"
        self.err_backend = "Wygląda na to, że żaden z backendów tapet nie jest zainstalowany w systemie.\n"
        self.err_backend += "Użyj menedżera pakietów, aby zainstalować co najmniej jeden z tych backendów:\n\n"
        self.err_backend += "- swaybg (dla Wayland)\n- swww (dla Wayland)\n"
        self.err_backend += "- hyprpaper (dla Wayland)\n- feh (dla Xorg)\n- wallutils (dla Xorg i Wayland)\n\n"
        self.err_backend += self.msg_info
        self.err_wall = "Błąd podczas zmiany tapety:"
        self.err_notsup = "Backend nie jest obsługiwany:"
        self.err_disp = "Błąd podczas określania nazw monitorów:"

        self.tip_refresh = "Odśwież folder z obrazami"
        self.tip_fill = "Wybierz typ wypełnienia"
        self.tip_backend = "Wybierz backend"
        self.tip_sorting = "Wybierz typ sortowania"
        self.tip_display = "Wybierz wyświetlacz"
        self.tip_color = "Wybierz kolor tła"
        self.tip_random = "Ustaw losową tapetę"
        self.tip_exit = "Wyjdź z aplikacji"


class Russian:
    def __init__(self):
        self.msg_desc = "Графический интерфейс для установки обоев на Wayland и X11. Работает как фронтенд для feh, swaybg, wallutils, hyprpaper, и swww."
        self.msg_info = "Для получения дополнительной информации посетите:\nhttps://github.com/anufrievroman/waypaper"

        self.msg_arg_help = "вывести версию программы"
        self.msg_arg_fill = "указать, как заполнить экран выбранным изображением"
        self.msg_arg_rest = "восстановить последние обои"
        self.msg_arg_back = "указать бэкенд для установки обоев"
        self.msg_arg_rand = "установить случайные обои"
        self.msg_arg_list = "вывести обои и мотиноры в формате json"
        self.msg_arg_wall = "указать путь к изображению"

        self.msg_path = "Выбранный путь к изображению:"
        self.msg_select = "Выбрать"
        self.msg_refresh = "Обновить"
        self.msg_random = "Случайно"
        self.msg_exit = "Выход"
        self.msg_subfolders = "Показать подпапки"
        self.msg_hidden = "Показать скрытые"
        self.msg_gifs = "Показать только gif"
        self.msg_changefolder = "Изменить папку с обоями"
        self.msg_choosefolder = "Пожалуйста, выберите папку"
        self.msg_caching = "Кэширование обоев..."
        self.msg_setwith = "Отправлена команда на установку обоев с использованием"

        self.msg_help = "Горячие клавиши Waypaper:\n\nhjkl - Навигация (←↓↑→)\nf - Изменить папку с обоями\n"
        self.msg_help += "g - Прокрутка в начало\nG - Прокрутка в конец\nR - Установить случайные обои\nr - Обновить кэш обоев\n"
        self.msg_help += ". - Показать/скрыть скрытые файлы \ns - Показать/скрыть вложенные папки\n? - Справка\nq - Выход\n\n"
        self.msg_help += self.msg_info

        self.err_cache = "Ошибка при удалении кэша"
        self.err_backend = "Похоже, что ни один из бэкендов для установки обоев не установлен в системе.\n"
        self.err_backend += "Используйте менеджер пакетов для установки хотя бы одного из следующих бэкендов:\n\n"
        self.err_backend += "- swaybg (для Wayland)\n- swww (для Wayland)\n"
        self.err_backend += "- hyprpaper (для Wayland)\n- feh (для Xorg)\n- wallutils (для Xorg и Wayland)\n\n"
        self.err_backend += self.msg_info
        self.err_wall = "Ошибка при смене обоев:"
        self.err_notsup = "Бэкенд не поддерживается:"
        self.err_disp = "Ошибка определения названий мониторов:"

        self.tip_refresh = "Обновить папку с изображениями"
        self.tip_fill = "Выбрать тип заполнения"
        self.tip_backend = "Выбрать бэкенд"
        self.tip_sorting = "Выбрать тип сортировки"
        self.tip_display = "Выбрать дисплей"
        self.tip_color = "Выбрать цвет фона"
        self.tip_random = "Установить случайные обои"
        self.tip_exit = "Выйти из приложения"


class Chinese:
    def __init__(self):
        self.msg_desc = "Wayland 和 X11 的 GUI 壁纸设置器。它用作 feh、swaybg、hyprpaper、wallutils 和 swww 的前端。"
        self.msg_info = "欲了解更多信息，请访问:\nhttps://github.com/anufrievroman/waypaper"

        self.msg_arg_help = "版本信息"
        self.msg_arg_fill = "指定所选图像填充屏幕"
        self.msg_arg_rest = "恢复上个壁纸"
        self.msg_arg_back = "指定使用哪个后端来设置壁纸"
        self.msg_arg_rand = "设置随机壁纸"
        self.msg_arg_list = "list wallpapers in json to standard out"
        self.msg_arg_wall = "set the specified wallpaper"

        self.msg_path = "选择的图像路径："
        self.msg_select = "选择"
        self.msg_refresh = "刷新"
        self.msg_random = "随机"
        self.msg_exit = "退出"
        self.msg_subfolders = "子文件夹"
        self.msg_hidden = "Show hidden"
        self.msg_gifs = "Show only gifs"
        self.msg_changefolder = "更改壁纸文件夹"
        self.msg_choosefolder = "请选择一个文件夹"
        self.msg_caching = "缓存壁纸..."
        self.msg_setwith = "发送设置壁纸的命令是用"

        self.msg_help = "Waypaper 的热键：\n\nhjkl -导航 (←↓↑→)\nf -更改壁纸文件夹\n"
        self.msg_help += "g -滚动到顶部\nG -滚动到底部\nR -设置随机壁纸\nr -重新缓存壁纸\n"
        self.msg_help += ". - 包括/排除隐藏图像\ns -包含/排除子文件夹中的图像\n？ -帮助\nq -退出\n\n"
        self.msg_help += self.msg_info

        self.err_cache = "删除缓存时出错"
        self.err_backend = "系统中似乎没有安装壁纸后端。\n"
        self.err_backend += "使用包管理器安装至少以下后端之一：\n\n"
        self.err_backend += "-swaybg (用于 Wayland)\n-swww (用于 Wayland)\n"
        self.err_backend += "- hyprpaper (对于 Wayland)\n-feh (对于 Xorg)\n-wallutils (对于 Xorg 和 Wayland)\n\n"
        self.err_backend += self.msg_info
        self.err_wall = "更改壁纸时出错："
        self.err_notsup = "不支持后端："
        self.err_disp = "确定监视器名称时出错："

        self.tip_refresh = "重新缓存图像文件夹"
        self.tip_fill = "选择填充类型"
        self.tip_backend = "选择后端"
        self.tip_sorting = "选择排序类型"
        self.tip_display = "选择显示"
        self.tip_color = "选择背景颜色"
        self.tip_random = "设置随机壁纸"
        self.tip_exit = "退出应用程序"

class Spanish:
    def __init__(self):
        self.msg_desc = 'Cambiador de imagen de fondo gráfico para "Wayland" y "X11". Trabaja como una astricción para "feh", "swaybg", "wallutils", "swww" y "hyprpaper".'
        self.msg_info = "Para mas información, visita:\nhttps://github.com/anufrievroman/waypaper"

        self.msg_arg_help = "imprime la versión del programa"
        self.msg_arg_fill = "especifica cual es el relleno de la pantalla con la imagen escogida"
        self.msg_arg_rest = "restaura la ultima imagen de fondo"
        self.msg_arg_back = "especifica cual es el programa se va a utilizar para cambiar la imagen de fondo"
        self.msg_arg_rand = "aplica una imagen de fondo aleatoria"
        self.msg_arg_list = 'imprime un listado de las imágenes de fondo al terminal en formato "JSON"'
        self.msg_arg_wall = "set the specified wallpaper"

        self.msg_path = "Donde esta ubicado la imagen en disco"
        self.msg_select = "Selecciona"
        self.msg_refresh = "Actualizar"
        self.msg_random = "Aleatorio"
        self.msg_exit = "Salir"
        self.msg_subfolders = "Enseñar carpetas enlazadas"
        self.msg_hidden = "Ver archivos ocultos"
        self.msg_gifs = 'Ver solamente imágenes tipo "GIF"'
        self.msg_changefolder = "Cambiar carpeta de imágenes"
        self.msg_choosefolder = "Por favor, selecciona una carpeta"
        self.msg_caching = "Almacenando en el caché..."
        self.msg_setwith = "El comando para actualizar la imagen de fondo fue ejecutado por"

        self.msg_help = 'Controles para el teclado para "Waypaper":\n\nhjkl - Navegación (←↓↑→)\n"Enter" (⏎) - Actualizar imagen de fondo a la imagen seleccionada\nf - Cambiar carpeta de images\n'
        self.msg_help += "g - Ir a la parte de arriba\nG - Ir a la parte de abajo\nR - Cambiar imagen de fondo a una imagen aleatoria\nr - Recrear caché de images\n"
        self.msg_help += ". - Ver/Omitir archivos ocultos\ns - Ver/Omitir imágenes en carpetas enlazadas\n? - Ayuda\nq - Cerrar aplicación\n\n"
        self.msg_help += self.msg_info

        self.err_cache = "Error borrando el caché"
        self.err_backend = "Parece ser que ningún programa para actualizar la imagen de fondo esta instalado en su sistema.\n"
        self.err_backend += "Por favor instalar uno de los siguientes programas para poder cambiar la imagen de fondo:\n\n"
        self.err_backend += '- swaybg (para "Wayland")\n- swww (para "Wayland"")\n- hyprpaper (para "Wayland")\n'
        self.err_backend += '- hyprpaper (para "Wayland")\n- feh (para "Xorg")\n- wallutils (para "Xorg" y "Wayland")\n\n'
        self.err_backend += self.msg_info
        self.err_wall = "Error cambiando imagen de fondo:"
        self.err_notsup = "El programa para cambiar imagen de fondo no tiene soporte:"
        self.err_disp = "Error buscando nombre de monitores"

        self.tip_refresh = "Volver a almacenar la carpeta de imágenes"
        self.tip_fill = "Escoja el tipo de relleno"
        self.tip_backend = "Escoja el programa para cambiar imagen de fondo"
        self.tip_sorting = "Escoja métrica de ordenamiento"
        self.tip_display = "Escoja nombre de pantalla"
        self.tip_color = "Escoja color de fondo"
        self.tip_random = "Actualizar imagen de fondo a una imagen aleatoria"
        self.tip_exit = "Cerrar la aplicación"
