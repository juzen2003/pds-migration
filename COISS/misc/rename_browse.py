import os, sys

for start in ('/Volumes/Migration/holdings/previews/COISS_2xxx/',
              '/Volumes/Migration/holdings/previews/COISS_1xxx/'):

    prev_root = ''
    for root, dirs, files in os.walk(start):
      for name in files:
        if not name.endswith('_full.png'):
            continue

        if root != prev_root:
            print root
            prev_root = root

        oldpath = os.path.join(root, name)
        newdir = '/Volumes/Migration/pds4/COISS_xxxx/browse_raw/%sxxxxx/' % name[1:6]
        if not os.path.exists(newdir):
            os.makedirs(newdir)

        newname = name[1:11] + name[0].lower() + '-full.png'
        newpath = newdir + newname
    #     print oldpath, newpath
        os.rename(oldpath, newpath)

