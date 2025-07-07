# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

# https://stackoverflow.com/questions/17958987/difference-between-python-getmtime-and-getctime-in-unix-system
#
# The mtime refers to last time the file's contents were changed. This can be altered on unix systems in various
# ways. Often, when you restore files from backup, the mtime is altered to indicate the last time the contents were
# changed before the backup was made.
#
# The ctime indicates the last time the inode was altered. This cannot be changed. In the above example with the
# backup, the ctime will still reflect the time of file restoration. Additionally, ctime is updated when things l
# ike file permissions are changed.
#
# Unfortunately, there's usually no way to find the original date of file creation. This is a limitation of the
# underlying filesystem. I believe the ext4 filesystem has added creation date to the inode, and Apple's HFS also
# supports it, but I'm not sure how you'd go about retrieving it in Python. (The C stat function and the
# corresponding stat command should show you that information on filesystems that support it.)
#

# archive utils - tools for organising aggregates of files and folders - e.g. for doing reliable backup, cleaning, archive, etc in
# the presence of unreliable operations - it's hard (and inefficient) to provide an atomic interface


# NOMENCLATURE
# a path is a string that locates as fs object
# a file is an fs object
# a folder is an fs object


from coppertop.pipe import *
import coppertop.dm.pp
from coppertop.dm.core import drop, startsWith
import glob, os, shutil, datetime, sys, pathlib, stat
from coppertop.dm.core.types import txt, bool
from bones.core.sentinels import Missing
from coppertop.dm.core.types import pylist
from coppertop.dm.pp import JJ

OCTAL_FORMAT = "{0:o}"


class FileNotMovedError(Exception): pass


if not hasattr(sys, '_moveException'): sys._moveException = []


counter = 0

@coppertop
def XX(x):
    global counter
    if counter > 10:
        counter = 0
        print(
            '                                                                                                                                                                                                                                                                                      ',
            end='\r'
        )
        print(x, end='\r')
    counter += 1
    return x


@coppertop
def XX1(x):
    print(
        '                                                                                                                                                                                                                                                                                      ',
        end='\r'
    )
    print(x, end='\r')
    return x


@coppertop
def basename(path: txt):
    return os.path.basename(path)


@coppertop(style=binary)
def deepDeleteFiles(src, pattern):
    try:
        for p in src >> scanFolders:
            src >> joinPath >> p >> deepDeleteFiles >> pattern
        files = glob.glob(src >> joinPath >> pattern)
        if files: f"\\n Deleting files in {src}" >> XX1
        for f in files:
            try:
                f >> deleteFile
            except FileNotMovedError as ex:
                pass
    except FileNotFoundError as ex:
        ex >> PP


@coppertop
def deepDeleteEmptyFolders(src):
    if src >> isFolder:
        for p in src >> scanFolders:
            src >> joinPath >> p >> deepDeleteEmptyFolders
        if src >> isFolderEmpty:
            f"Deleting folder {src}" >> XX1
            src >> deleteEmptyFolder


@coppertop(style=ternary)
def deepDeleteFilesWithinSubfolders(src:txt, pattern:txt, subdirs:pylist):
    for p in src >> scanFolders:
        src >> joinPath >> p >> JJ >> deepDeleteFilesWithinSubfolders >> pattern >> subdirs
    if (src >> basename) in subdirs:
        for p in glob.glob(src >> joinPath >> pattern):
            if (ffn := src >> joinPath >> p) >> isFile:
                ffn >> deleteFile >> JJ


@coppertop(style=binary)
def deepFindFiles(src, pattern):
    ffns = []
    for p in src >> scanFolders:
        src >> joinPath >> p >> deepFindFiles >> pattern
    for p in glob.glob(src >> joinPath >> pattern):
        if (ffn := src >> joinPath >> p) >> isFile:
            ffns.append(ffn)
    return ffns


@coppertop(style=ternary)
def deepFindFilesWithinSubfolders(src: txt, pattern: txt, subdirs: pylist) -> pylist:
    ffns = []
    for p in src >> scanFolders:
        childrenFfns = src >> joinPath >> p >> deepFindFilesWithinSubfolders >> pattern >> subdirs
        ffns.extend(childrenFfns)
    if (src >> basename) in subdirs:
        for p in glob.glob(src >> joinPath >> pattern):
            if (ffn := src >> joinPath >> p) >> isFile:
                ffns.append(ffn)
    return ffns


@coppertop(style=binary)
def deepFindNamedSubfolders(src:txt, folderNames:pylist) -> pylist:
    paths = []
    for p in src >> JJ >> scanFolders:
        if p >> basename in folderNames:
            paths.append(src >> joinPath >> p >> JJ)
        else:
            childPaths = src >> joinPath >> p >> deepFindNamedSubfolders >> folderNames
            paths.extend(childPaths)
    return paths


@coppertop(style=binary)
def deepMoveFiles(src, dst):
    exceptions = []
    for p in src >> scanFolders:
        exceptions.extend(src >> joinPath >> p >> deepMoveFiles >> (dst >> joinPath >> p >> ensureFolderWithXX))
    allFilesMoved = True
    if src >> hasFiles:
        files = src >> scanFiles
        if files: f"\\nMoving \\n   {src}\\n   {dst}" >> XX
        for fn in files:
            # did try not moving files starting with ._ - however scrivener uses this too so didn't move properly
            try:
                src >> joinPath >> fn >> moveFile >> (dst >> joinPath >> fn)
                fn >> XX
            except FileNotMovedError as why:
                f"{why}" >> XX1
                exceptions.append((src >> joinPath >> fn, why))
                allFilesMoved = False
    if allFilesMoved:
        if src >> isFolderEmpty:
            src >> deleteEmptyFolder
    return exceptions


@coppertop
def deleteFile(path):
    try:
        os.remove(path)
    except PermissionError as why:
        try:
            path >> macosUnlock
            os.remove(path)
        except PermissionError as why:
            raise FileNotMovedError(
                f"{path >> basename}   - can't delete ({stat.S_IMODE(os.lstat(path).st_mode) >> mask2perm})")
    return path


@coppertop
def deleteEmptyFolder(path: txt) -> txt:
    os.rmdir(path)
    return path


@coppertop
def ensureFolder(path):
    if path >> isFolder:
        pass
    else:
        os.makedirs(path, exist_ok=True)
    return path


@coppertop
def ensureFolderWithXX(path):
    if path >> isFolder:
        # f"{path} - already exists" >> XX
        pass
    else:
        f"Creating {path}" >> XX
        os.makedirs(path, exist_ok=True)
    return path


@coppertop
def expandUser(path:txt) -> txt:
    return os.path.expanduser(path)


folderEntries = coppertop(style=nullary, name='folderEntries')(lambda path: os.listdir(path))


getCwd = coppertop(style=nullary, name='getCwd')(os.getcwd)


@coppertop
def gid(stats: os.stat_result):
    return stats.st_gid


@coppertop
def hasFiles(path):
    # https://stackoverflow.com/questions/57968829/what-is-the-fastest-way-to-check-whether-a-directory-is-empty-in-python
    for p in os.scandir(path):
        if os.path.isfile(p): return True
    return False


@coppertop
def isFile(path: txt) -> bool:
    return os.path.isfile(path)


@coppertop
def isFolder(path: txt) -> bool:
    return os.path.isdir(path)


@coppertop
def isFolderEmpty(path):
    # https://stackoverflow.com/questions/57968829/what-is-the-fastest-way-to-check-whether-a-directory-is-empty-in-python
    (os.path.isfile(path) for x in os.scandir(path))
    with os.scandir(path) as it:
        return not any(it)


@coppertop(style=binary)
def joinPath(p1, p2):
    return os.path.normpath(os.path.join(p1, p2))


@coppertop
def macosUnlock(path):
    # https://stackoverflow.com/questions/48675286/how-do-i-unlock-locked-files-and-folders-mac-with-python
    # https://www.pythonfixing.com/2022/01/fixed-how-do-i-unlock-locked-files-and.html
    # https://superuser.com/questions/40749/command-to-unlock-locked-files-on-os-x
    os.system('chflags nouchg {}'.format(path))
    return path


@coppertop
def mask2perm(mask):
    assert mask >= 0 and mask < 2048, 'Bad mask'
    answer = ''
    answer += 'r' if mask & stat.S_IRUSR else '-'
    answer += 'w' if mask & stat.S_IWUSR else '-'
    answer += 's' if mask & (stat.S_IXUSR | stat.S_ISUID) else ('x' if mask & stat.S_IXUSR else '-')
    answer += 'r' if mask & stat.S_IRGRP else '-'
    answer += 'w' if mask & stat.S_IWGRP else '-'
    answer += 's' if mask & (stat.S_IXGRP | stat.S_ISGID) else ('x' if mask & stat.S_IXGRP else '-')
    answer += 'r' if mask & stat.S_IROTH else '-'
    answer += 'w' if mask & stat.S_IWOTH else '-'
    answer += 't' if mask & (stat.S_IXOTH | stat.S_ISVTX) else ('x' if mask & stat.S_IXOTH else '-')
    return answer


@coppertop
def modTime(stats: os.stat_result):
    return stats.st_mtime_ns


@coppertop(style=binary)
def moveFile(src, dst):
    # check that the dst doesn't exist
    if dst >> isFile or dst >> isFolder:
        # check they are the same - same mod time and same size (same hash later on)
        stSrc, stDst = src >> stats, dst >> stats
        if stDst.st_mtime_ns == stSrc.st_mtime_ns and stDst.st_size == stSrc.st_size:
            # already been copied
            pass
        else:
            raise FileNotMovedError(f"{dst} already exists modtime {'different' if stDst.st_mtime_ns != stSrc.st_mtime_ns else 'same'}, size {'different' if stDst.st_size != stSrc.st_size else 'same'}")
    else:
        shutil.copyfile(src, dst, follow_symlinks=True)
    try:
        shutil.copystat(src, dst, follow_symlinks=True)
    except PermissionError as why:
        pass
    if dst >> isFile:
        # check they are the same - same mod time and same size (same hash later on)
        stSrc, stDst = src >> stats, dst >> stats
        if stDst.st_mtime_ns == stSrc.st_mtime_ns and stDst.st_size == stSrc.st_size:
            try:
                os.remove(src)
            except PermissionError as why:
                try:
                    src >> macosUnlock
                    os.remove(src)
                except PermissionError as why:
                    raise FileNotMovedError(f"{src >> basename}   - copied but can't delete ({stat.S_IMODE(os.lstat(src).st_mode) >> mask2perm})")
        else:
            raise FileNotMovedError(f"Destination {dst} doesn't appear to be the one just copied")
    else:
        raise FileNotMovedError(f"Destination {dst} does not exist")
    return dst


@coppertop
def nanoToDT(ns) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ns / 1000000000)


@coppertop
def perm2mask(p):
    assert len(p) == 9, 'Bad permission length'
    assert all(p[k] in 'rw-' for k in [0, 1, 3, 4, 6, 7]), 'Bad permission format (read-write)'
    assert all(p[k] in 'xs-' for k in [2, 5]), 'Bad permission format (execute)'
    assert p[8] in 'xt-', 'Bad permission format (execute other)'

    m = 0

    if p[0] == 'r': m |= stat.S_IRUSR
    if p[1] == 'w': m |= stat.S_IWUSR
    if p[2] == 'x': m |= stat.S_IXUSR
    if p[2] == 's': m |= stat.S_IXUSR | stat.S_ISUID

    if p[3] == 'r': m |= stat.S_IRGRP
    if p[4] == 'w': m |= stat.S_IWGRP
    if p[5] == 'x': m |= stat.S_IXGRP
    if p[5] == 's': m |= stat.S_IXGRP | stat.S_ISGID

    if p[6] == 'r': m |= stat.S_IROTH
    if p[7] == 'w': m |= stat.S_IWOTH
    if p[8] == 'x': m |= stat.S_IXOTH
    if p[8] == 't': m |= stat.S_IXOTH | stat.S_ISVTX

    return m


@coppertop
def ppDT(dt: datetime.datetime) -> txt:
    return dt.strftime('%Y.%m.%d %H:%M:%S.%f UTC')


@coppertop(style=binary)
def replicateFolders(src, dst):
    for p in src >> scanFolders:
        src >> joinPath >> p \
        >> replicateFolders \
        >> (dst >> joinPath >> p)
    dst >> ensureFolderWithXX


@coppertop
def scanFiles(path):
    answer = []
    for f in os.scandir(path):
        if not f.is_dir():
            answer.append(f.name)
    return answer


@coppertop
def scanFolders(path):
    answer = []
    for f in os.scandir(path):
        if f.is_dir():
            answer.append(f.name)
    answer.sort(key=lambda s: (s.upper(), s))
    return answer


@coppertop
def setCwd(path:txt) -> txt:
    """Sets the current working directory to the given path."""
    os.chdir(path)
    return path


@coppertop
def size(stats: os.stat_result):
    return stats.st_size


@coppertop
def stats(path: txt):
    return os.stat(path)


@coppertop
def uid(stats: os.stat_result):
    return stats.st_uid
