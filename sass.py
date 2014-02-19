""":mod:`sass` --- Binding of ``libsass``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This simple C extension module provides a very simple binding of ``libsass``,
which is written in C/C++.  It contains only one function and one exception
type.

>>> import sass
>>> sass.compile(string='a { b { color: blue; } }')
'a b {\n  color: blue; }\n'

"""
import collections
import os.path

from _sass import (OUTPUT_STYLES, compile_dirname, compile_filename,
                   compile_string)

__all__ = 'MODES', 'OUTPUT_STYLES', 'CompileError', 'and_join', 'compile'
__version__ = '0.3.0'


#: (:class:`collections.Mapping`) The dictionary of output styles.
#: Keys are output name strings, and values are flag integers.
OUTPUT_STYLES = OUTPUT_STYLES

#: (:class:`collections.Set`) The set of keywords :func:`compile()` can take.
MODES = set(['string', 'filename', 'dirname'])


class CompileError(ValueError):
    """The exception type that is raised by :func:`compile()`.
    It is a subtype of :exc:`exceptions.ValueError`.

    """


def compile(**kwargs):
    """There are three modes of parameters :func:`compile()` can take:
    ``string``, ``filename``, and ``dirname``.

    The ``string`` parameter is the most basic way to compile SASS.
    It simply takes a string of SASS code, and then returns a compiled
    CSS string.

    :param string: SASS source code to compile.  it's exclusive to
                   ``filename`` and ``dirname`` parameters
    :type string: :class:`str`
    :param output_style: an optional coding style of the compiled result.
                         choose one of: ``'nested'`` (default), ``'expanded'``,
                         ``'compact'``, ``'compressed'``
    :type output_style: :class:`str`
    :param include_paths: an optional list of paths to find ``@import``\ ed
                          SASS/CSS source files
    :type include_paths: :class:`collections.Sequence`, :class:`str`
    :param image_path: an optional path to find images
    :type image_path: :class:`str`
    :returns: the compiled CSS string
    :rtype: :class:`str`
    :raises sass.CompileError: when it fails for any reason
                               (for example the given SASS has broken syntax)

    The ``filename`` is the most commonly used way.  It takes a string of
    SASS filename, and then returns a compiled CSS string.

    :param filename: the filename of SASS source code to compile.
                     it's exclusive to ``string`` and ``dirname`` parameters
    :type filename: :class:`str`
    :param output_style: an optional coding style of the compiled result.
                         choose one of: ``'nested'`` (default), ``'expanded'``,
                         ``'compact'``, ``'compressed'``
    :type output_style: :class:`str`
    :param include_paths: an optional list of paths to find ``@import``\ ed
                          SASS/CSS source files
    :type include_paths: :class:`collections.Sequence`, :class:`str`
    :param image_path: an optional path to find images
    :type image_path: :class:`str`
    :returns: the compiled CSS string
    :rtype: :class:`str`
    :raises sass.CompileError: when it fails for any reason
                               (for example the given SASS has broken syntax)
    :raises exceptions.IOError: when the ``filename`` doesn't exist or
                                cannot be read

    The ``dirname`` is useful for automation.  It takes a pair of paths.
    The first of the ``dirname`` pair refers the source directory, contains
    several SASS source files to compiled.  SASS source files can be nested
    in directories.  The second of the pair refers the output directory
    that compiled CSS files would be saved.  Directory tree structure of
    the source directory will be maintained in the output directory as well.
    If ``dirname`` parameter is used the function returns :const:`None`.

    :param dirname: a pair of ``(source_dir, output_dir)``.
                    it's exclusive to ``string`` and ``filename``
                    parameters
    :type dirname: :class:`tuple`
    :param output_style: an optional coding style of the compiled result.
                         choose one of: ``'nested'`` (default), ``'expanded'``,
                         ``'compact'``, ``'compressed'``
    :type output_style: :class:`str`
    :param include_paths: an optional list of paths to find ``@import``\ ed
                          SASS/CSS source files
    :type include_paths: :class:`collections.Sequence`, :class:`str`
    :param image_path: an optional path to find images
    :type image_path: :class:`str`
    :raises sass.CompileError: when it fails for any reason
                               (for example the given SASS has broken syntax)

    """
    modes = set()
    for mode_name in MODES:
        if mode_name in kwargs:
            modes.add(mode_name)
    if not modes:
        raise TypeError('choose one at least in ' + and_join(MODES))
    elif len(modes) > 1:
        raise TypeError(and_join(modes) + ' are exclusive each other; '
                        'cannot be used at a time')
    try:
        output_style = kwargs.pop('output_style')
    except KeyError:
        output_style = 'nested'
    if not isinstance(output_style, basestring):
        raise TypeError('output_style must be a string, not ' +
                        repr(output_style))
    try:
        output_style = OUTPUT_STYLES[output_style]
    except KeyError:
        raise CompileError('{0} is unsupported output_style; choose one of {1}'
                           ''.format(output_style, and_join(OUTPUT_STYLES)))
    try:
        include_paths = kwargs.pop('include_paths')
    except KeyError:
        include_paths = ''
    else:
        if isinstance(include_paths, collections.Sequence):
            include_paths = ':'.join(include_paths)
        elif not isinstance(include_paths, basestring):
            raise TypeError('include_paths must be a sequence of strings, or '
                            'a colon-separated string, not ' +
                            repr(include_paths))
    try:
        image_path = kwargs.pop('image_path')
    except KeyError:
        image_path = '.'
    else:
        if not isinstance(image_path, basestring):
            raise TypeError('image_path must be a string, not ' +
                            repr(image_path))
    if 'string' in modes:
        string = kwargs.pop('string')
        s, v = compile_string(string, output_style, include_paths, image_path)
    elif 'filename' in modes:
        filename = kwargs.pop('filename')
        if not os.path.isfile(filename):
            raise IOError('{0!r} seems not a file'.format(filename))
        s, v = compile_filename(filename,
                                output_style, include_paths, image_path)
    elif 'dirname' in modes:
        try:
            search_path, output_path = kwargs.pop('dirname')
        except ValueError:
            raise ValueError('dirname must be a pair of (source_dir, '
                             'output_dir)')
        s, v = compile_dirname(search_path, output_path,
                               output_style, include_paths, image_path)
    else:
        raise TypeError('something went wrong')
    if s:
        return v
    raise CompileError(v)


def and_join(strings):
    """Join the given ``strings`` by commas with last `' and '` conjuction.

    >>> and_join(['Korea', 'Japan', 'China', 'Taiwan'])
    'Korea, Japan, China, and Taiwan'

    :param strings: a list of words to join
    :type string: :class:`collections.Sequence`
    :returns: a joined string
    :rtype: :class:`str`, :class:`basestring`

    """
    last = len(strings) - 1
    if last == 0:
        return strings[0]
    elif last < 0:
        return ''
    iterator = enumerate(strings)
    return ', '.join('and ' + s if i == last else s for i, s in iterator)
