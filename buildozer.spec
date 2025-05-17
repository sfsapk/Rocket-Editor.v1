[app]

# (str) Название вашего приложения
title = RocketEditor

# (str) Имя пакета
package.name = rocketeditor

# (str) Домен пакета (нужен для упаковки Android/iOS)
package.domain = org.kivy

# (str) Исходный код, где находится main.py
source.dir = .

# (list) Исходные файлы для включения
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Директории для включения
source.include_dirs = data,rocket_data

# (list) Исходные файлы для исключения
source.exclude_exts = spec,md,yml,yaml

# (list) Директории для исключения
source.exclude_dirs = tests, bin, venv, .github, attached_assets

# (str) Версия приложения
version = 1.0

# (list) Требования к приложению
requirements = python3,kivy==2.0.0,pillow

# (str) Поддерживаемые ориентации
orientation = portrait

#
# Android specifics
#

# (bool) Указывает, должно ли приложение быть полноэкранным
fullscreen = 0

# (int) Android API для использования
android.api = 31

# (int) Минимальный API, который будет поддерживать ваш APK
android.minapi = 21

# (int) Android SDK версия для использования
android.sdk = 25

# (str) Android NDK версия для использования
android.ndk = 23b

# (int) Android NDK API для использования
android.ndk_api = 21

# (list) Android архитектуры для сборки
android.archs = arm64-v8a, armeabi-v7a

# (list) Разрешения
android.permissions = android.permission.READ_EXTERNAL_STORAGE, android.permission.WRITE_EXTERNAL_STORAGE

# (bool) Включить поддержку AndroidX
android.enable_androidx = True

# (bool) Если True, пропускать попытку обновления Android SDK
android.skip_update = False

# (bool) Если True, автоматически принимать лицензию SDK
android.accept_sdk_license = True

# (str) Java опции компиляции для поддержки Android 8+
android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (bool) Указывает, должен ли экран оставаться включенным
android.wakelock = False

# (str) Фильтры Android logcat для использования
android.logcat_filters = *:S python:D

# (bool) Копировать библиотеку вместо создания libpymodules.so
android.copy_libs = 1

# (str) Android тема приложения
android.apptheme = @android:style/Theme.NoTitleBar

#
# Python for android (p4a) specific
#

# (str) Bootstrap для использования при сборке Android
p4a.bootstrap = sdl2

#
# iOS specific
#

# (str) iOS целевая версия для развертывания, т.е. 9.0 для 9.0+
# ios.deployment_target = 9.0

# (bool) Указывает, должно ли приложение быть полноэкранным
ios.fullscreen = 0

# (list) Разрешения
# ios.permissions =

[buildozer]
# (int) Уровень логирования (0 = только ошибки, 1 = инфо, 2 = дебаг с выводом команд)
log_level = 2

# (int) Отображать предупреждение, если buildozer запущен от root
warn_on_root = 1

# (str) Путь к хранилищу артефактов сборки, абсолютный или относительно файла spec
build_dir = ./.buildozer

# (str) Путь к хранилищу результатов сборки (т.е. .apk, .aab, .ipa)
bin_dir = ./bin
