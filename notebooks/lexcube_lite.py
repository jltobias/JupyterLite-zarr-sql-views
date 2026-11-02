"""Load upstream LexCube in Pyodide; native Python uses the installed package.

The upstream wheel stays unmodified on disk. Two explicit in-memory filesystem
patches make its optional process-memory diagnostic portable. The patched
LexCube module remains GPL-3.0-or-later. See public/vendor/lexcube/README.md.
"""
import sys


async def setup_lexcube():
    if sys.platform == 'emscripten' and 'lexcube' not in sys.modules:
        import piplite
        import micropip
        from pathlib import Path
        await piplite.install(['ipywidgets','xarray','dask',
                               'cachey','fsspec','bottleneck','cftime','numcodecs','opencv-python'])
        wheel=Path('wheels/lexcube-2.0.1-py3-none-any.whl').resolve()
        await micropip.install('emfs:'+str(wheel), deps=False)
        import importlib.util
        location=Path(importlib.util.find_spec('lexcube').origin).parent
        target=location/'lexcube_server/src/tile_server.py'
        text=target.read_text()
        assert text.count('import psutil\n')==1
        text=text.replace('import psutil\n',
            '# JupyterLite adaptation (2026): process diagnostics unavailable in WebAssembly.\n'
            'psutil = None\n')
        text=text.replace('def get_current_memory_usage(s: str = ""):\n',
            'def get_current_memory_usage(s: str = ""):\n'
            '    if psutil is None:\n'
            '        return "Process memory diagnostics are unavailable in WebAssembly"\n')
        target.write_text(text)
    import lexcube
    return lexcube


def cube_sliders(cube, data):
    """Course controls with stop-exclusive bounds, including the last cell.

    LexCube 2.0.1's bundled Sliders caps endpoints at size-1, although the
    selection API slices at stop. Use an independent ipywidgets control here
    so an initial whole-window selection does not silently lose the last cell.
    """
    import ipywidgets as widgets
    sliders=[];links=[]
    for axis,dimension in [('x',2),('y',1),('z',0)]:
        name=axis+'lim'
        slider=widgets.IntRangeSlider(value=getattr(cube,name),min=0,max=data.shape[dimension],
            description=str(data.dims[dimension])+':',continuous_update=False,
            style={'description_width':'80px'},layout=widgets.Layout(width='480px'))
        links.append(widgets.link((cube,name),(slider,'value')))
        sliders.append(slider)
    box=widgets.VBox(sliders)
    box._course_links=links
    return box
