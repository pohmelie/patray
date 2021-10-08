# patray
[![Travis status for master branch](https://travis-ci.com/pohmelie/patray.svg?branch=master)](https://travis-ci.com/pohmelie/patray)
[![Pypi version](https://img.shields.io/pypi/v/patray.svg)](https://pypi.org/project/patray/)
[![Pypi downloads count](https://img.shields.io/pypi/dm/patray)](https://pypi.org/project/patray/)

Patray stands for PulseAudioTray. It is "yet another pulseaudio frontend".

## Default view
![](https://github.com/pohmelie/patray/blob/master/gifs/Peek%202020-06-13%2016-57.gif?raw=true)

## Configuring
![](https://github.com/pohmelie/patray/blob/master/gifs/Peek%202020-06-13%2018-09.gif?raw=true)

# Reasons
- Brilliant [yktoo sound switcher](https://github.com/yktoo/indicator-sound-switcher) lacks of volume control
- [pasystray](https://github.com/christophgysin/pasystray) have too much options and heavy interface
- No simple tray for all in one menu:
    - port switching with radio buttons
    - volume control scroll bar

# Features
- Card profile switches
- Profile port switches
- Profile volume slider
- Port filters by mask
- Configurable UI view: combo or radio

# License
`patray` is offered under MIT license.

# Requirements
* python 3.7+

# Installation
``` bash
$ python -m pip install patray
```

# Usage
Common usecase is:
``` bash
$ python -m patray ~/.patray.config.yml
```
Configuration options are built on [`cock`](https://github.com/pohmelie/cock) logic, so you need to run
``` bash
$ python -m patray --help
```
to see all available options. But you can pass all options via command line interface, or even via environemnt vairables.

# Example
For version `0.1.2` help output looks like this:
```
$ python -m patray --help
Usage: patray [OPTIONS] [CONFIGURATION_FILE]

Options:
  --profile-enabled BOOLEAN      [default: True]
  --profile-style [combo|radio]  [default: combo]
  --profile-weight FLOAT         [default: 1.0]
  --port-enabled BOOLEAN         [default: True]
  --port-style [combo|radio]     [default: radio]
  --port-maximum-volume INTEGER  [default: 100]
  --port-hide-by-mask TEXT
  --port-weight FLOAT            [default: 1.0]
  --log-level TEXT               [default: INFO]
  --icon-path FILE
  --icon-color TEXT              Use `random` value for random color on each
                                 click  [default: #fff]

  --version                      Show the version and exit.  [default: False]
  --help                         Show this message and exit.  [default: False]
```
You can see all defaults and all «flat» keys. Your configuration file can look like this:
``` yml
icon-color: random
profile:
  enabled: true
  style: combo
port:
  enabled: true
  style: radio
  weight: 0.95
  maximum-volume: 100
  hide-by-mask:
    - "Front*"
    - "Rear*"
    - "Line In*"
```
You can see, that each `-` in flat cli argument name can be cutted off to create tree-like config.
