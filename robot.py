from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

__pragma__('iconv')
__pragma__('tconv')
#__pragma__('opov')

# don't try to use global variables!!
class MyRobot(BCAbstractRobot):
    step = -1
    crusaders = 1
    pilgrims = 1

    def turn(self):
        self.step += 1
        self.log("START TURN " + self.step)
        if self.me['unit'] == SPECS['CRUSADER']:
            self.log("Crusader health: " + str(self.me['health']))
            # The directions: North, NorthEast, East, SouthEast, South, SouthWest, West, NorthWest
            choices = [(0,-1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
            choice = random.choice(choices)
            self.log('TRYING TO MOVE IN DIRECTION ' + str(choice))
            return self.move(*choice)

        elif self.me['unit'] == SPECS['CASTLE']:
            if self.step < 20:
                randir = [-1, 0, 1]
                firstdir = random.choice(randir)
                seconddir = random.choice(randir)
                if self.crusaders / self.pilgrims <= .5:
                    self.log("Building a crusader at " + str(self.me['x']+1) + ", " + str(self.me['y']+1))
                    return self.build_unit(SPECS['CRUSADER'], firstdir, seconddir)
                else:
                    self.log("building a pilgrim at " + str(self.me['x']+1) + ", " + str(self.me['y']+1))
                    return self.build_unit(SPECS['PILGRIM'], firstdir, seconddir)
            else:
                self.log("Castle health: " + self.me['health'])
        
        elif self.me['unit'] ==SPECS['PILGRIM']:
            choices = [(0,-1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
            choice = random.choice(choices)
            self.log('TRYING TO MOVE IN DIRECTION ' + str(choice))
            return self.move(*choice)

robot = MyRobot()
