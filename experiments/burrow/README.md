# Burrow experiment map

Place the experiment map in this directory as `burrows.csv`. Use a rectangular,
semicolon-delimited CSV with these cell values:

- `0`: open space
- `1`: wall
- `9`: burrow

The center cell must be open (`0`). The experiment starts the selected creature
there with a random heading on every run. A run is counted as successful after
the creature remains in a burrow continuously for the configured number of
ticks. A run ends as `entered_then_left` when the creature leaves a burrow before
meeting that duration, or as `never_entered` when it never reaches one before
the run timeout. The experiment performs 1000 runs; the default timeout is 2000
ticks per run (extended to one tick beyond the configured stay duration when
that duration is longer).
