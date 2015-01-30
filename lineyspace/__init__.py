#!/usr/bin/python

import game
import sys

def main():
    universe = game.Game()

    universe.run()
    universe.quit()

if __name__ == "__main__":
    sys.exit(main())

