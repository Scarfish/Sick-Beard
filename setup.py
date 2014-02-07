import urllib, ConfigParser
from distutils.core import setup
import py2exe, sys, os, shutil, datetime, zipfile, subprocess, fnmatch
import json, PathLocator
from glob import glob

# mostly stolen from the SABnzbd package.py file
name = 'SickBeard'
version = '0.1'

release = name + '-' + version

Win32ConsoleName = 'SickBeard-console.exe'
Win32WindowName = 'SickBeard.exe'

githubRepoUser = 'Scarfish'
githubRepoBranch = 'Dutch'

def findLatestBuild():

    latestBuild = 0
    releases = json.load(urllib.urlopen("https://api.github.com/repos/" + githubRepoUser + "/Sick-Beard/releases"))    

    if 'message' in releases and 'API rate limit exceeded' in releases['message']:
        raise Exception('Too many GitHub API calls were fired in the last 60 minutes. Please try again later.')

    for release in releases:
        build = int(release['name'].rpartition('-')[2])
        latestBuild = build if build > latestBuild else latestBuild

    return latestBuild

def recursive_find_data_files(root_dir, allowed_extensions=('*'), new_root_dir=None):
    
    to_return = {}
    for (dirpath, dirnames, filenames) in os.walk(root_dir):
        if not filenames:
            continue

        newdirpath = dirpath if not new_root_dir else os.path.join(new_root_dir, dirpath)
        
        for cur_filename in filenames:
            
            matches_pattern = False
            for cur_pattern in allowed_extensions:
                if fnmatch.fnmatch(cur_filename, '*.'+cur_pattern):
                    matches_pattern = True
            if not matches_pattern:
                continue
            
            cur_filepath = os.path.join(dirpath, cur_filename)
            to_return.setdefault(newdirpath, []).append(cur_filepath)
            
    return sorted(to_return.items())


def find_all_libraries(root_dirs):
    
    libs = []
    
    for cur_root_dir in root_dirs:
        for (dirpath, dirnames, filenames) in os.walk(cur_root_dir):
            if '__init__.py' not in filenames:
                continue
            
            libs.append(dirpath.replace(os.sep, '.')) 
    
    return libs


def allFiles(dir):
    files = []
    for file in os.listdir(dir):
        fullFile = os.path.join(dir, file)
        if os.path.isdir(fullFile):
            files += allFiles(fullFile)
        else:
            files.append(fullFile) 

    return files

# save the original arguments and replace them with the py2exe args
oldArgs = []
if len(sys.argv) > 1:
    oldArgs = sys.argv[1:]
    del sys.argv[1:]

sys.argv.append('py2exe')

# clear the dist dir
if os.path.isdir('dist'):
    shutil.rmtree('dist')

# root source dir
compile_dir = os.path.dirname(os.path.normpath(os.path.abspath(sys.argv[0])))

if not 'nopull' in oldArgs:
    # pull new source from git
    print 'Updating source from git'
    p = subprocess.Popen('git pull origin master', shell=True, cwd=compile_dir)
    o,e = p.communicate()

# figure out what build this is going to be
latestBuild = findLatestBuild()
if 'test' in oldArgs:
    currentBuildNumber = str(latestBuild)+'a'
else:
    currentBuildNumber = latestBuild+1

# write the version file before we compile
versionFile = open("sickbeard/version.py", "w")
versionFile.write("SICKBEARD_VERSION = \"" + githubRepoBranch + " build "+str(currentBuildNumber)+"\"")
versionFile.close()

# set up the compilation options
data_files = recursive_find_data_files('gui', ['gif', 'png', 'jpg', 'ico', 'js', 'css', 'tmpl'])
# Also incorporate the txt and dll files from the libraries as some are necessary (e.g. guessit, unrar2)
data_files.extend(recursive_find_data_files('lib', ['dll', 'txt'], 'lib'))
# Incorporate assemblies from the redist package so that it doesn't have to be installed
data_files.append(('.', glob(r'C:\\Program Files/Microsoft Visual Studio 9.0/VC/redist/x86/Microsoft.VC90.CRT/*.*')))

packages = find_all_libraries(['sickbeard', 'lib'])

options = dict(
    name=name,
    version=release,
    author='Nic Wolfe',
    author_email='nic@wolfeden.ca',
    description=name + ' ' + release,
    scripts=['SickBeard.py'],
    packages=list(packages),
)

packages.append('Cheetah');

# set up py2exe to generate the console app
program = [ {'script': 'SickBeard.py' } ]
options['options'] = {'py2exe':
                        {
                         'bundle_files': 3,
                         'packages': packages,
                         'excludes': ['Tkconstants', 'Tkinter', 'tcl'],
                         'optimize': 2,
                         'compressed': 0,
#Archive cannot be used because of files that modules depend on (eg. unrar2 depends on unrar.dll)
                         'skip_archive': 1
                        }
                     }
options['zipfile'] = 'lib/sickbeard.zip'
options['console'] = program
options['data_files'] = data_files

# compile sickbeard-console.exe
setup(**options)

# rename the exe to sickbeard-console.exe
try:
    if os.path.exists("dist/%s" % Win32ConsoleName):
        os.remove("dist/%s" % Win32ConsoleName)
    os.rename("dist/%s" % Win32WindowName, "dist/%s" % Win32ConsoleName)
except:
    print "Cannot create dist/%s" % Win32ConsoleName
    #sys.exit(1)

# we don't need this stuff when we make the 2nd exe
del options['console']
del options['data_files']
options['windows'] = program

# compile sickbeard.exe
setup(**options)

# compile sabToSickbeard.exe using the existing setup.py script
auto_process_dir = os.path.join(compile_dir, 'autoProcessTV')
p = subprocess.Popen([ sys.executable, os.path.join(auto_process_dir, 'setup.py') ], cwd=auto_process_dir, shell=True)
o,e = p.communicate()

# copy autoProcessTV files to the dist dir
auto_process_files = ['autoProcessTV/sabToSickBeard.py',
                      'autoProcessTV/hellaToSickBeard.py',
                      'autoProcessTV/autoProcessTV.py',
                      'autoProcessTV/autoProcessTV.cfg.sample',
                      'autoProcessTV/sabToSickBeard.exe']
 
os.makedirs('dist/autoProcessTV')
 
for curFile in auto_process_files:
    newFile = os.path.join('dist', curFile)
    print "Copying file from", curFile, "to", newFile
    shutil.copy(curFile, newFile)

# compile updater.exe
setup(
      options = {'py2exe': {'bundle_files': 1}},
      zipfile = None,
      console = ['updater.py'],
)

if 'test' in oldArgs:
    print "Ignoring changelog for test build"
else:
    # start building the CHANGELOG.txt
    print 'Creating changelog'
    
    # read the old changelog and find the last commit from that build
    lastCommit = ""
    try:
        cl = open("CHANGELOG.txt", "r")
        lastCommit = cl.readlines()[0].strip()
        cl.close()
    except:
        print "I guess there's no changelog"
    
    newestCommit = ""
    changeString = ""

    # cycle through all the git commits and save their commit messages
    commits = json.load(urllib.urlopen("https://api.github.com/repos/" + githubRepoUser + "/Sick-Beard/commits"))

    if 'message' in commits and 'API rate limit exceeded' in commits['message']:
        raise Exception('Too many GitHub API calls were fired in the last 60 minutes. Please try again later.')

    for curCommit in commits:
        if curCommit['sha'] == lastCommit:
            break;

    
        if newestCommit == "":
            newestCommit = curCommit['sha']
        
        changeString += curCommit['commit']['message'] + "\n\n"
    
    # if we didn't find any changes don't make a changelog file
    if newestCommit != "":
        newChangelog = open("CHANGELOG.txt", "w")
        newChangelog.write(newestCommit+"\n\n")
        newChangelog.write("Changelog for build "+str(currentBuildNumber)+"\n\n")
        newChangelog.write(changeString)
        newChangelog.close()
    else:
        print "No changes found, keeping old changelog"

# put the changelog in the compile dir
if os.path.exists("CHANGELOG.txt"):
    shutil.copy('CHANGELOG.txt', 'dist/')

# figure out what we're going to call the zip file
print 'Zipping files...'
zipFilename = 'SickBeard-' + githubRepoBranch + '-win32-alpha-build-'+str(currentBuildNumber)
if os.path.isfile(zipFilename + '.zip'):
    zipNum = 2
    while os.path.isfile(zipFilename + '.{0:0>2}.zip'.format(str(zipNum))):
        zipNum += 1
    zipFilename = zipFilename + '.{0:0>2}'.format(str(zipNum))

# get a list of files to add to the zip
zipFileList = allFiles('dist/')

# add all files to the zip
z = zipfile.ZipFile(zipFilename + '.zip', 'w', zipfile.ZIP_DEFLATED)
for file in zipFileList:
    z.write(file, file.replace('dist/', zipFilename + '/'))
z.close()

print "Created zip at", zipFilename

# leave version file as it is in source
print "Reverting version file to master"
versionFile = open("sickbeard/version.py", "w")
versionFile.write("SICKBEARD_VERSION = \"" + githubRepoBranch + "\"")
versionFile.close()
