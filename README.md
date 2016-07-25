# osu! Replay Reader

Replay parser for osu!, converts replay file/bytes to python object
https://osu.ppy.sh/wiki/Osr_(file_format)

## Usage

```
r = ReplayParser()
r.load_from_file('replay.osr')

r.get_replay() # Returns python dictionary of the replay
r.to_json() # returns json representation of the replay

```

#### Available Types:
```
type
version
bmMd5Hash
playerName
rMd5Hash
h300
h100
h50
hGekis
hKatus
tScore
tCombo
hMisses
fullClear
mods
lifeBar
time_played
replayByteLength
```



