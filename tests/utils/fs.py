import os
import os.path as op
import commands


def md5sum(path):
    rc, msg = commands.getstatusoutput("md5sum " + path)
    if rc != 0:
        raise Exception('command error: ' + msg)
    return msg.split()[0]


def equal(dir1, dir2):
    files_1 = os.listdir(dir1)
    files_2 = os.listdir(dir2)

    flag = files_1 == files_2
    if not flag:
        return flag
    for i in xrange(len(files_1)):
        p1, p2 = op.join(dir1, files_1[i]), op.join(dir2, files_2[i])
        if op.isdir(p1) and op.isdir(p2):
            if not equal(p1, p2):
                return False
        elif op.isfile(p1) and op.isfile(p2):
            if md5sum(p1) != md5sum(p2):
                return False
        else:
            return False
    return True

