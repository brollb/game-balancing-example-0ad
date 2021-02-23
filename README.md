# Game Balancing Example in 0 A.D.
This repository contains a simple example of exploring game balance using 0 A.D. More detail can be found in the [demo video](https://youtu.be/zAAXbTYPNcM)!

## Quick Start
First, we will need to start 0 AD with our custom scenarios (available in a mod [here](https://github.com/brollb/zero_ad_rl)). Then, we can start 0 AD with the RL interface (and the mods):
```
pyrogenesis --rl-interface=127.0.0.1:6000 --mod=rl-scenarios --mod=public
```

Next, we will install the required Python dependencies:
```
python -m pip install -r requirements.txt
```
You may need to install `zero_ad` manually from [here](https://github.com/brollb/0ad/tree/main/source/tools/rlclient/python).

Finally, we can run the example with:
```
python find_speed_range.py
```

## Related Resources
- [0 AD w/ game balance support](https://github.com/brollb/0ad). The game balancing features require an endpoint which did not make it in before the feature freeze. The linked game version is 0.24b with the required patch for game balancing support. As soon as 0.25 is released, this should no longer be an issue! :)
- [Scenarios, environments, and utilities for RL in 0 AD](https://github.com/brollb/zero_ad_rl)
- [Player replay data](https://drive.google.com/file/d/1lzQkUi9HFKWcbp-6L6MVynhEOnasTAZa/view?usp=sharing) retrieved from the [0 A.D. forums](https://wildfiregames.com/forum/topic/25610-public-domain-dataset-for-machine-learning/)
