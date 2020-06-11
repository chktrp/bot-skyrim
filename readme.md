# Bot plays Skyrim (simple combat)

This is a bot that can perform a simple combat in Skyrim. It uses SSD lite mobilenet v2 to obtain the enemy locations and acts according to the predefined rules.

## Bot description

This is my attempt to create a bot that can perform a simple task in a videogame. Its behavior is simple.

- It'll move backward if the nearest enemy stays too close.
- It'll try to center the crosshair to the nearest enemy.
- It'll try to circle around the enemy
- It'll attack (hold attack key) the enemy if it stays close enough to the crosshair.
- It'll turn around for a moment if no enemy is visible.
- It'll reload a quick-save (press F9 key) if it couldn't find any enemy.

## Prerequisites

1. Skyrim should be run in window-mode with 640x400 resolution, locating in the top-left corner of the screen.

2. Attack key should be set to `X` instead of default `Left-click`

3. Player character should have _Flames_ equipped on their right hand.

4. A quick-save at the location where the enemies are around.

5. Anaconda (or miniconda) as package manager.

## Instructions

1. Install dependencies: `conda install --file requirements.txt`

2. Run the bot: `python play.py`

3. Swap to Skyrim window after the countdown started (5 seconds). __It'll take control the key A, S, D, W, X, F9 and mouse cursor. Be prepared!__

4. It should run for about 30 seconds or until no enemy is detected and terminate itself.

## Video

https://www.youtube.com/watch?v=uNbRt3y6bME

## Reference

This project has a huge inspiration from https://github.com/Sentdex/pygta5
