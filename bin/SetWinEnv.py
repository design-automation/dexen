import os
import platform
import ctypes
# --------------------------------------------------------------------------------
# SetEnv tool
# --------------------------------------------------------------------------------
#http://www.codeproject.com/Articles/12153/SetEnv

# --------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------
def fix_path(path):
    path = os.path.expandvars(path)
    path = os.path.normcase(path)
    #I found that if there is a ~ in the path, it does not work
    #http://stackoverflow.com/questions/2738473/compare-two-windows-paths-one-containing-tilde-in-python
    if "~" in path:
        path = unicode(path)
        GetLongPathName = ctypes.windll.kernel32.GetLongPathNameW
        buffer = ctypes.create_unicode_buffer(GetLongPathName(path, 0, 0))
        GetLongPathName(path, buffer, len(buffer))
        path = buffer.value
    return path

def setenv_add_paths(name, paths, prepend = True):
    name = name.upper()
    if type(paths) == str:
        paths = [paths]
    paths = [fix_path(i) for i in paths]
    for path in paths:
        if prepend:
            os.system('SetWinEnv -uap ' + name + ' %"' + path + '"')
        else:
            os.system('SetWinEnv -ua ' + name + ' %"' + path + '"')
        print
        print "Added '" + path + "'"
        print "to the '" + name + "' environment variable."
        
def setenv_add_values(name, values, prepend = True):
    name = name.upper()
    for value in values:
        if prepend:
            os.system('SetWinEnv -uap ' + name + ' %"' + value + '"')
        else:
            os.system('SetWinEnv -ua ' + name + ' %"' + value + '"')
        print
        print "Added '" + value + "'"
        print "to the '" + name + "' environment variable."
        
def is_houdini_dir(path):
    if os.path.isdir(path):
        dir_contents = os.listdir(path)
        if "houdini" in dir_contents:
            return True
    return False
    
# --------------------------------------------------------------------------------
# MAIN SCRIPT
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Get paths
# --------------------------------------------------------------------------------

dexen_dir =  os.path.split(os.getcwd())[0] #go back one dir
platform = platform.architecture()[0]

# --------------------------------------------------------------------------------
# Set up Dexen paths
# --------------------------------------------------------------------------------

setenv_add_paths("DEXEN", [dexen_dir])

libs_dir = dexen_dir + "\\libs"
setenv_add_paths("PYTHONPATH", [dexen_dir, libs_dir])

bin_dir = dexen_dir + "\\bin"
setenv_add_paths("PATH", [bin_dir])

# --------------------------------------------------------------------------------
#print
#raw_input("Press any key to exit...")
#print "Bye..."
