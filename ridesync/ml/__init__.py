"""M6 models: demand forecast (``demand``), fare fit (``fare``), ETA correction (``eta``).

Everything is trained on NYC TLC March 2024 by ``python -m ridesync.ml.train`` and saved under
``data/models``. The modules import scikit-learn and pandas lazily, so the package stays importable
without them (and on PyFlink's Python 3.10).
"""
