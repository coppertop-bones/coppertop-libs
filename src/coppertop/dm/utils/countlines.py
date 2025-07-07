
import os


def ffn_linecount(ffn, opts, line_excls):
    lines = 0
    skipBlanks = "--skipblank" in opts
    try:
        with open(ffn, encoding='utf-8-sig') as f:
            for line in f:
                if line := line.strip():
                    include = True
                    for excl in line_excls:
                        if line.startswith(excl):
                            include = False
                            break
                    if include:  lines += 1
                else:
                    if not skipBlanks:  lines += 1

    except Exception as ex:
        if '-oe' in opts:
            print(f'Error reading "{ffn}"')

    if '-ofn' in opts:
        print("%6d lines in %s" % (lines, ffn))
    return lines


def folder_linecount(folder, opts, exts, line_excls, path_excls):
    # derived from https://github.com/mhalitk/line-counter/blob/master/linecounter.py

    lines, files = 0, 0
    folder = os.path.expanduser(folder)
    for fn in os.listdir(folder):
        ffn = os.path.join(folder, fn)
        include = True
        for excl in path_excls:
            if excl in ffn:
                include = False
                break
        include = include and (not exts or os.path.splitext(os.path.join(folder, fn))[1] in exts)
        include = include and os.path.isfile(ffn)
        if include:
            lines += ffn_linecount(ffn, opts, line_excls)
            files += 1
    if lines and '-of' in opts: print("%6d lines, %4d files, in %s" % (lines, files, folder))

    if "-r" in opts:
        for cf in os.listdir(folder):
            cf = os.path.join(folder, cf)
            if os.path.isdir(cf):
                l, f = folder_linecount(cf, opts, exts, line_excls, path_excls)
                lines += l
                files += f

    return lines, files


def print_my_stuff():
    opts = ['-r', '-of', '--skipblank']
    c_comments = ['//']
    py_comments = ['#']

    dm_all = folder_linecount('~/arwen/dm', opts, ['.py'], py_comments, [])
    dm_src = folder_linecount('~/arwen/dm/src', ['-r', '--skipblank'], ['.py'], py_comments, [])
    print(f'----------------- src: {dm_src} tests: {dm_all[0]-dm_src[0], dm_all[1]-dm_src[1]}')

    cp = folder_linecount('~/arwen/coppertop/src', opts, ['.py', '.g4'], py_comments, ['TypeLang', 'pygments'])
    print(f'----------------- {cp}')

    bones = folder_linecount('~/arwen/bones', opts, ['.py'], py_comments, [])
    print(f'----------------- {bones}')

    mybones = folder_linecount('~/arwen/my-bones', opts, ['.py'], py_comments, [])
    print(f'----------------- {mybones}')

    pondering = folder_linecount('~/arwen/pondering', opts, ['.py'], py_comments, ['projects/S/'])
    print(f'----------------- {pondering}')

    bk = folder_linecount('~/arwen/coppertop/bk', opts, ['.c', '.h', '.tmplt'], c_comments, [])
    print(f'----------------- {bk}')

    bkw = folder_linecount('~/arwen/bones-kernel-wip', opts, ['.c', '.h'], c_comments, [])
    bkw += folder_linecount('~/arwen/bones-kernel-wip', opts, ['.py'], py_comments, [])
    print(f'----------------- {bkw}')

    qbe = folder_linecount('~/arwen/IR/qbe', opts, ['.c', '.h'], c_comments, [])
    print(f'----------------- {qbe}')

    mir = folder_linecount('~/arwen/IR/mir', opts, ['.c', '.h'], c_comments, [])
    print(f'----------------- {mir}')

    cproc = folder_linecount('~/arwen/IR/cproc', opts, ['.c', '.h'], c_comments, [])
    print(f'----------------- {cproc}')

    print('dm_src: ', dm_src, 'dm_tests:', (dm_all[0]-dm_src[0], dm_all[1]-dm_src[1]))
    print('cp', cp)
    print('bones', bones)
    print('mybones', mybones)
    print('pondering', pondering)
    print('bk', bk)
    print('bkw', bkw)
    print(dm_all + cp + bones + mybones + pondering + bk + bkw)
    print('qbe', qbe)
    print('mir', mir)
    print('cproc', cproc)

    folder_linecount('~/arwen/coppertop/src/bones/lang', ['-r', '-ofn', '--skipblank'], ['.py'], py_comments, ['TypeLang'])



if __name__ == '__main__':
    print_my_stuff()
