# Расчётный и навигационный стенд ECONA

Установка и проверки: **10 октября 2026**, Ubuntu 24.04 x86_64.
Программы работают на исследовательском компьютере. Подключение к физическому
рулю, моторам, аккумулятору или кайту не выполнялось.

## Установленные программы

| Программа | Версия / среда | Выполненная проверка и применение |
|---|---|---|
| OpenCPN | 5.8.4, Ubuntu | Запущено окно с отдельным тестовым профилем; навигация и маршруты. Морские карты для района плавания ещё не выбраны |
| ParaView | 5.11.2, Ubuntu, Python API | Прочитан настоящий результат CFD: 400 ячеек, поле скорости, PNG и состояние `.pvsm` |
| OpenFOAM | Основная: OpenCFD **v2512**, официальный комплект 2512.0-2, включая исходники, wmake и tutorials | Учебный cavity рассчитан; эта версия выбрана для CfdOF. Ранее установленный Ubuntu 1912 остаётся отдельным учебным комплектом, не используется CfdOF |
| GNU Octave | 8.4.0 | Аналитическая RC-ОДУ: ошибка менее 5×10⁻¹¹; инерция ватерлинии двух раздельных прямоугольных поплавков |
| KiCad | 7.0.11 | GUI запущен; плата 30×20 мм сохранена/прочитана, слой и контур экспортированы в SVG. Это геометрический эталон, не схема привода |
| pypilot | 0.71, отдельный Python 3.12 | Собраны C++/SWIG-модули, RTIMULib 8.1.0, UI, web и Signal K зависимости; 37 тестов upstream прошли, окно Autopilot Control запущено |
| OpenPlotter Settings | 4.2.9, Debian 12 через PRoot | Установка пакета, Python import и окно Settings проверены. Это среда конфигурирования; бортовые службы и GPIO-пакеты не развёрнуты |
| Julia / KiteModels | 1.12.6 / 0.11.17 | Все зависимости скомпилированы; KPS4: 80 шагов по 0,05 с, конечные силы и высота. Зафиксирован `Manifest.toml` |
| PYLEECAN | 1.5.2, отдельный Python 3.8.20 | GUI, построение сечения, массы и геометрия учебной IPMSM; зависимости согласованы |
| FEMM / Wine | 4.2, сборка 22Oct2023 x64 / Wine 9 | PYLEECAN `_FEMMHandler` решает магнитную задачу: B≈(1;0) Тл совпадает с аналитикой с ошибкой менее 10⁻⁶ Тл |

Также установлены системные CalculiX 2.21, Gmsh 4.12.1, GetDP 3.2, Pandoc,
SWIG, библиотеки сборки, Xvfb и утилиты. Основной FEM FreeCAD продолжает использовать
собственные **CalculiX 2.23 / Gmsh 4.15.0**, проектный Gmsh Python — **4.15.2**,
проектный GetDP — **3.5.0**. Разные пути явно фиксируются в расчётах.

## Запуск

Основные системные приложения доступны в меню Ubuntu. Для дополнительных:

```bash
tools/pyleecan
tools/pypilot-client
tools/openplotter
tools/julia calculations/kite-julia/verify_kite.jl
```

В меню добавлены PYLEECAN — ECONA, pypilot — ECONA, OpenPlotter 4 — ECONA
и Julia / KiteModels — ECONA. Общий инженерный порядок —
[дополнения FreeCAD](21_freecad_addons.md).

Для CLI OpenFOAM **сначала** выполнить `source /usr/lib/openfoam/openfoam2512/etc/bashrc`
в отдельном терминале. Рабочие каталоги CFD должны иметь латинские имена без пробелов:
`environment/.local/share/econa-cfd-cases`. Копии результата сохранять в `calculations/`.
Не смешивать окружение v2512 и 1912 в одном процессе.

## Особенности отдельных сред

[Официальная инструкция OpenPlotter 4](https://openplotter.readthedocs.io/latest/getting_started/installing.html)
указывает Debian 12 и Ubuntu 22.04. Поэтому на Ubuntu 24.04 применяется
совместимый Debian userspace в `environment/.local/opt/openplotter-bookworm`.
PRoot не является средством защиты от недоверенного кода. Запускающий wrapper
открывает ему проект как `/workspace`, X11 и необходимые системные интерфейсы.
Службы в госте не включены. В госте заменён только его `sudo` на делегирование
команд при фиктивном uid=0: PRoot не может использовать setuid. Исходный файл
сохранён как `sudo.real`; привилегии и sudoers основного Ubuntu не изменены.

PYLEECAN 1.5.2 требует Python <3.11 и старые версии NumPy/Matplotlib.
Его среда `environment/.local/opt/pyleecan-env` отделена от FreeCAD и проектной `.venv`.
FEMM находится в отдельном Wine-префиксе `environment/.local/share/econa-femm-wine`.
Локальный патч `software/pyleecan-femm-path.patch` исправляет потерю аргументов
пути в `_FEMMHandler` и добавляет `FEMM_PATH`. После обновления повторить тест.
GUI запускается с этим окружением через `tools/pyleecan`.

FEMM извлечён из официального установщика, его SHA-256 совпал с опубликованным
на [странице FEMM](https://www.femm.info/wiki/Download). Включённый Microsoft VC++
runtime установлен внутри собственного Wine-префикса. 32-битный Wine не потребовался.

KiteModels в выполненном примере имеет **неподвижное основание** и примерный кайт.
Перенос на движущийся катамаран, сопряжение кажущегося ветра, троса, лебёдки,
сил/моментов и курса остаётся отдельной инженерной задачей.
Проверка pypilot подтверждает программный стенд, а не управление нашим рулём или кайтом.

## Воспроизводимость

- Версии и результаты: `software/engineering-installation.json`.
- Системные журналы: `software/logs/system-installation.log`, `system-extra-installation.log`, `openfoam2512-installation.log`.
- Окна программ: `calculations/verification/gui/*.json` и `*.png`.
- Численные эталоны: `calculations/verification/`, Julia — `calculations/kite-julia/`.
- Происхождение архивов и контрольные суммы: `software/manifests/`.
- Отдельные Python lock-файлы: `software/manifests/pypilot-requirements.txt`, `pyleecan-requirements.txt`.
- Основная геометрия не изменена; SHA-256 приведён в сводном отчёте установки.

Эталонные задачи проверяют работоспособность связок. Они не заменяют расчёты
обводов ECONA, остойчивости с тягой кайта, прочности сэндвича, винтов,
мощности BLDC, батареи и солнечной генерации.
