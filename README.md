# pyHonGo

pyHonGo is a [pygame](https://www.pygame.org)-based french-japanese vocabulary quizz. It features :

* Efficient learning with the [flashcard](https://en.wikipedia.org/wiki/Flashcard) method,
* Merging of the quizz choices by identical [word class](https://en.wikipedia.org/wiki/Part-of-speech),
* Three independant saving profiles,
* Possibility to use the TV remote control over HDMI with the [CEC](https://en.wikipedia.org/wiki/Consumer_Electronics_Control) protocol.

Table of contents
=================

1. [Installation](#installation)
2. [Usage](#usage)
3. [Remarks](#remarks)
3. [Credits](#credits)
4. [License](#license)

Installation
============

Simply copy all the contents to an individual folder, then to start the game simply run `pyHonGo.py` with a Python 2 interpreter:
```
python2 ./pyHonGo.py
```
The dependency **pygame** should be installed on the system. You can get some informations on the [installation details](https://www.pygame.org/wiki/GettingStarted#Pygame%20Installation) on the official pygame website, or if you are running under a debian-based distribution (e.g. Ubuntu) you can simply type:
```
sudo apt-get install python-pygame
```
To use the HDMI CEC protocol to control the game with a TV remote control, the command-line tool **cec-client** should be installed. On Ubuntu you can type:
```
sudo apt-get install cec-utils
```
Note however that TV remote control is not mandatory and is deactivated by default.

Usage
=====

#### Launching the game

To launch the game, go the folder where you installed the files and run:
```
python2 ./pyHonGo.py
```

#### Game manual

![Game screenshot](./imgs/screenshot.png)

#### Changing default settings

#### Using the TV remote control

Remarks
=======

Credits
=======

License
=======

