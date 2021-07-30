import functools
import tempfile
import inspect
import atexit
import sys
import os


def remote_ipc_stub(source):
    file = 'SI_IPC_' + str(os.getpid()) + '.py'
    file = os.path.join(tempfile.gettempdir(), file)
    with open(file, 'a') as f:
        if source[-1:] != '\n':
            source = source + '\n'
        f.write(source + '===\n')

    if not hasattr(remote_ipc_stub, '_si_did'):
        remote_ipc_stub._si_did = '_Did'
        atexit.register(os.unlink, file)


def remote_findsourcelines(object):
    file = 'SI_IPC_' + str(os.getppid() if 'idlelib' in sys.modules else os.getpid()) + '.py'
    file = os.path.join(tempfile.gettempdir(), file)
    if not os.path.exists(file):
        message = remote_get_error_message()
        (message)
        raise IOError(f'Cannot find file {file}!' + message)

    with open(file, 'r') as f:
        lines = f.read()
    return lines.split('===\n')


def remote_findsource(object):
    try:
        module = object.__module__
        assert module[0] == '<' and module[-1] == '>' or module in ['__console__', '__main__']
    except:
        raise IOError(f'Object `{repr(object)}` does not come from console')

    lines = remote_findsourcelines(object)
    for lnum, line in reversed(list(enumerate(lines))):
        try:
            name = line.split('def ', 1)[1]
            name = name.split(':', 1)[0]
            name = name.split('(', 1)[0]
            if name == object.__name__:
                break
        except IndexError:
            pass
    else:
        raise IOError(f'Cannot find source of object `{repr(object)}`')

    return lines, lnum


def remote_get_error_message():
    name = 'SourceInspect'
    if 'taichi' in sys.modules:
        name = 'Taichi'
    return f'''
To make {name} functional in IDLE, please append the following line:

__import__("sourceinspect").remote_hack(globals())

to file "{__import__("code").__file__}".
'''


def remote_hack(globals):
    old_runsource = globals['InteractiveInterpreter'].runsource

    @functools.wraps(old_runsource)
    def new_runsource(self, source, *args, **kwargs):
        remote_ipc_stub(source)
        return old_runsource(self, source, *args, **kwargs)

    globals['InteractiveInterpreter'].runsource = new_runsource


def blender_get_text_name(file):
    import os
    if file.startswith(os.path.sep) and file.count(os.path.sep) == 1:
        return file[1:]      # untitled blender file, "/Text"

    i = file.rfind('.blend' + os.path.sep)
    if i != -1:
        return file[i + 7:]  # saved blender file, "hello.blend/Text"

    return None


def blender_findsourcetext(object):
    try:
        import bpy
    except ImportError:
        raise IOError('Not in Blender environment!')

    file = inspect.getfile(object)
    text_name = blender_get_text_name(file)
    if text_name is None:
        raise IOError(f'Object `{repr(object)}` not defined Blender file mode!')

    lines = bpy.data.texts[text_name].as_string()
    return lines, text_name


def blender_findsource(object):
    lines, text_name = blender_findsourcetext(object)

    try:
        filename = blender_findsource._si_cache[lines]
    except KeyError:
        fd, filename = tempfile.mkstemp(prefix='SI_Blender_', suffix=f'_{text_name}.py')
        os.close(fd)
        with open(filename, 'w') as f:
            f.write(lines)

        blender_findsource._si_cache[lines] = filename

    def hooked_getfile(o):
        if id(o) == id(object):
            return filename
        return inspect._si_old_getfile(o)

    inspect._si_old_getfile = inspect.getfile
    inspect.getfile = hooked_getfile
    ret = inspect.findsource(object)
    inspect.getfile = inspect._si_old_getfile
    del inspect._si_old_getfile
    return ret

blender_findsource._si_cache = {}


def dill_findsource(object):
    try:
        import dill.source
    except ImportError:
        raise IOError(
            'Run `python3 -m pip install dill` to make SourceInspect functional in Python native shell. '
            'Additionally you should run `python3 -m pip install pyreadline` if you are on Windows.'
            )
    return dill.source.findsource(object)


def our_findsource(object):
    try:
        return inspect._si_old_findsource(object)
    except IOError:
        try:
            return blender_findsource(object)
        except IOError:
            try:
                return remote_findsource(object)
            except IOError:
                try:
                    return dill_findsource(object)
                except IOError:
                    raise IOError(f'Could not get source code for object: {repr(object)}')


class InspectMock():
    def __enter__(self):  # TODO: ensure this won't be re-entered
        inspect._si_old_findsource = inspect.findsource
        inspect.findsource = our_findsource
        return self

    def __exit__(self, *_):
        inspect.findsource = inspect._si_old_findsource
        del inspect._si_old_findsource


def getfile(object):
    with InspectMock():
        return inspect.getfile(object)

def findsource(object):
    with InspectMock():
        return inspect.findsource(object)

def getsource(object):
    with InspectMock():
        return inspect.getsource(object)

def getcomments(object):
    with InspectMock():
        return inspect.getcomments(object)

def getsourcelines(object):
    with InspectMock():
        return inspect.getsourcelines(object)

def getsourcefile(object):
    with InspectMock():
        ret = inspect.getsourcefile(object)
        if ret is None:  # Make Taichi happy
            try:
                ret = inspect.getfile(object)
            except:
                pass
        return ret

def getfile(object):
    with InspectMock():
        return inspect.getfile(object)

def stack(context=1):
    with InspectMock():
        return inspect.getouterframes(sys._getframe(1), context)


__all__ = [
    'InspectMock',
    'getfile',
    'findsource',
    'getsource',
    'getcomments',
    'getsourcelines',
    'getsourcefile',
    'getfile',
    'stack',
]