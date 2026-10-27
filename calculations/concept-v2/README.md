# ECONA v2 — воспроизводимость

Миссия: кругосветка и вокруг всех материков; 2 постоянных / до 8 на переходах.
Маршрут пользователь пока не определил. Полярный охват не назначен.

Из корня проекта:

1. `.venv/bin/python tools/concept/prepare_v2.py`
2. `environment/.local/opt/freecad/squashfs-root/AppRun freecadcmd tools/concept/ship_v2_freecad.py`
3. `.venv/bin/python tools/concept/finish_v2.py`
4. `.venv/bin/python tools/concept/annotate_v2.py`
5. Bundled Python: `tools/concept/build_report_v2.py` (ReportLab).

Ship требует основного multihull-патча, section-compatibility и section-sort.
Кеш успешных срезов привязан к BRep и исходному коду Tools; при смене геометрии
или патча удаляется. Не считать exit 0 FreeCADCmd доказательством успеха:
требуется `ship-hydro.json: status=PASS`, независимые проверки и просмотр PDF.

Native AreasCurve нулевые концы заменены сечениями 0.001 мм внутрь границы
для погружённого транца. Независимые моменты ватерлинии проверяются производными
объёмных моментов ∫x²dV и ∫y²dV, с шагом 0.1 мм.

CG/LCG и уровни танков не утверждены; GM и MCT условные. Полные GZ/RAO/FEM
не рассчитаны без физических входных данных. Вода, пища, сопротивление, KPI
и погода — явные сценарии. Исходная сборка не менялась.
