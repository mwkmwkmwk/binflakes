project = 'binflakes'
copyright = '2018, Marcin Kościelnicki'  # noqa: A001
author = 'Marcin Kościelnicki'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
]
source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'sphinx'
html_theme = 'nature'
autoclass_content = 'both'
autodoc_default_flags = ['members', 'special-members', 'show-inheritance']
