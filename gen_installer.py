import os
import subprocess
import sys
import bzt
import configparser


def run_cmd(label, cmdline, **kwargs):
    print(label + " " + str(cmdline))
    subprocess.run(cmdline, check=True, **kwargs)


# ["apiritif==0.6.3",
#  "astunparse==1.5.0",
#  "colorama==0.3.9",
#   "colorlog==3.1.4",
#      "hdrpy==0.3.1",
#   "lxml==4.2.1",
#                                   "nose==1.3.7",
#                                   "progressbar33==2.4",
#                                   "psutil==5.4.5",
#                                   "pytest==3.5.1",
#                                   "PyVirtualDisplay==0.2.1",
#                                   "pyyaml==3.12",
#                                   "requests==2.18.4",
#                                   "selenium==3.11.0",
#                                   "Appium-Python-Client==0.26",
#                                   "urwid==2.0.1"]

def generate_pynsist_config(dependencies, wheel_dir, cfg_location):
    print("Generating pynsist config")
    cfg = configparser.ConfigParser()
    cfg['Application'] = {
        'name': 'Taurus',
        'version': bzt.VERSION,
        'entry_point': 'bzt.cli:main',
        'console': 'true',
        'icon': 'site/img/taurus.ico',
    }

    cfg['Command bzt'] = {
        'entry_point': 'bzt.cli:main',
    }

    cfg['Command jmx2yaml'] = {
        'entry_point': 'bzt.jmx2yaml:main',
    }

    cfg['Command soapui2yaml'] = {
        'entry_point': 'bzt.soapui2yaml:main',
    }

    cfg['Python'] = {
        'bitness': 64,
        'version': '3.5.4',
    }

    wheels_list = ["%s==%s" % (package_name, version) for package_name, version in dependencies]
    cfg['Include'] = {
        'packages': '\n'.join(['tkinter', '_tkinter']),
        'pypi_wheels': "\n".join(wheels_list),
        'extra_wheel_sources': wheel_dir,
        'files': '\n'.join(['README.md',
                            r'installers\win32\_tkinter.pyd > $INSTDIR\pkgs',
                            r'installers\win32\tcl86t.dll > $INSTDIR\pkgs',
                            r'installers\win32\tk86t.dll > $INSTDIR\pkgs',
                            r'installers\win32\lib',
                            ])
    }

    with open(cfg_location, 'w') as fds:
        cfg.write(fds)


def run_pynsist(cfg_location):
    run_cmd("Running pynsist", ["pynsist", cfg_location])


def fetch_all_wheels(for_package, wheel_dir):
    run_cmd("Fetching wheels", [
        "pip-custom-platform", "wheel", "--wheel-dir", wheel_dir, "--platform", "win_amd64", for_package
    ])


def extract_all_dependencies(wheel_dir):
    """Extract all (package, version) pairs from a directory with wheels"""
    print("Extracting dependent package list")
    packages = []
    for filename in os.listdir(wheel_dir):
        if filename.endswith('.whl'):
            parts = filename.split('-')
            package_name, version = parts[0], parts[1]
            packages.append((package_name, version))
    return packages


def main():
    if len(sys.argv) < 2:
        print("Usage: %s <bzt-wheel>" % sys.argv[0])
        sys.exit(1)
    bzt_dist = sys.argv[1]
    pynsist_config = "installer-gen.cfg"
    wheel_dir = "build/wheels"
    fetch_all_wheels(bzt_dist, wheel_dir)
    dependencies = extract_all_dependencies(wheel_dir)
    generate_pynsist_config(dependencies, wheel_dir, pynsist_config)
    run_pynsist(pynsist_config)


if __name__ == '__main__':
    main()
