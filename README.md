# Beast from the East
An offline bot for Rocket League using the framework [RLBot](https://github.com/RLBot/RLBot).

Designed for 1v1 soccer.

It participated in:
* Rocket League Bot Tournament August 2018
  * got #9 place in 1v1
  * got #5 place in 2v2 with random teammates

Beast from the East uses a utility system to decide what to do, and a set of controllers to execute that.
In terms of skill Beast is similar to Psyonix AllStar.

## How to run

1. Make sure you've installed [Python 3.6 64 bit](https://www.python.org/ftp/python/3.6.5/python-3.6.5-amd64.exe). During installation:
   - Select "Add Python to PATH"
   - Make sure pip is included in the installation
2. Open Rocket League
3. Download or clone this repository
3. In the files from the previous step, find and double click on run-gui.bat
4. Click the 'Run' button

The match configuration can be changed in rlbot.cfg

## More

* See www.rlbot.org for getting started with making RLBot bots
* See https://github.com/RLBot/RLBot/wiki for framework documentation and tutorials.
* See [https://braacket.com/league/rlbot/](https://braacket.com/league/rlbot/ranking?rows=100) for ranking of other RLBot bots

## TODO
Things I might add/improve in the future:
* Improve the small jump shots (this probably requires better prediction of *when* Beast can/will hit the ball)
* Add a dribble controller for situations where the ball is close
* Give Beast a better understanding of interceptions and ball trajectories
* Make Beast better at stopping in front of the goal instead of continuing into the goal
* Adaptive kickoffs