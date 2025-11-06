# Chess - Self Learning AI (Qt frontend)

This repository contains a chess engine, a self-learning AI, and two frontends: the original pygame-based `ChessMain.py` and a new PySide6-based GUI `ChessQt.py`.

Goal: provide a professional desktop UI similar to chess.com with integrated self-learning AI, move log, timers, promotion dialog, and PGN export.

Quick start (PowerShell on Windows):

```powershell
python -m pip install -r requirements.txt
python .\ChessQt.py
```

Notes:
- `ChessEngine.py` contains the game logic and `Move` class.
- `SelfLearningAI.py` contains the learning brain and move-finding logic.
- `ChessMain.py` is the original pygame frontend (kept for compatibility).
- `ChessQt.py` is a newer Qt frontend (recommended for a professional UI).

If you want me to further refine the Qt UI to match your screenshot pixel-perfect (left sidebar icons, right ad panel, exact fonts and spacing), I can continue iterating and add assets and styling.
