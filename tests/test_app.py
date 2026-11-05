from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_demo_pages():
    app=AppTest.from_file(str(Path(__file__).parents[1]/'app.py')).run(timeout=30)
    assert not app.exception
    for name in ['Campaign comparison','Budget scenario']:
        app.sidebar.radio[0].set_value(name).run(timeout=30)
        assert not app.exception
    app.sidebar.selectbox[0].set_value('Alternative demo').run(timeout=30)
    assert not app.exception
    app.sidebar.selectbox[0].set_value('Upload CSV files').run(timeout=30)
    assert not app.exception
