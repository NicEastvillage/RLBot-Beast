<p align="center" >
    <img src="https://raw.githubusercontent.com/NicEastvillage/RLBot-Beast/master/beastbot/logo.png" height="100px" 
    alt="Beast from the East" 
    title="Beast from the East">
</p>

# Beast from the East
An offline bot for Rocket League using the framework [RLBot](https://github.com/RLBot/RLBot).

Designed for 1v1 soccer.

Beast from the East uses a utility system to decide what to do, and a set of controllers to execute that.
In terms of skill Beast can easily beat one Psyonix AllStar.

## How to run

1. Make sure you've installed [Python 3.6 64 bit](https://www.python.org/ftp/python/3.6.5/python-3.6.5-amd64.exe). During installation:
   - Select "Add Python to PATH"
   - Make sure pip is included in the installation
2. Open Rocket League
3. Download or clone this repository
3. In the files from the previous step, find and double click on run-gui.bat
4. Click the 'Run' button

The match configuration can be changed in rlbot.cfg

## Tournament Participation

Beast from the East participated in:
* [RLBot Wintertide Tournament 2019](https://braacket.com/tournament/wintertide)
  * got **4th place** in 1v1
  * eliminated in the 2v2 **quarterfinals** with NV Derevo by jeroen11dijk as teammate
  * also eliminated in the 2v2 **quarterfinals** with Zoomlette by Jonas as teammate
* [Snowbot Showdown](https://braacket.com/tournament/69BF67CC-54A5-4212-B108-1677922358C9/match/6670A22A-17FF-4398-AF76-6DF2DA8B8EFD), hosted by jeroen11dijk
  * eliminated in the **qualifier round**
* [Titan Tournament](https://braacket.com/tournament/tinytourney2), hosted by jeroen11dijk
  * got a **5th place**
* [Tiny Tournament](https://braacket.com/tournament/0661561E-BA13-49E9-80BF-ABD953579CED/match), hosted by jeroen11dijk
  * got a **2nd place**
* [Rocket League Bot Tournament August 2018](https://braacket.com/tournament/527AAEBD-D323-455A-90EB-9AFFA8C92B34/dashboard)
  * got **9th place** in 1v1
  * got **5th place** in 2v2 with random teammates

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