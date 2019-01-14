from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import math
import random

# __pragma__('iconv')
# __pragma__('tconv')
#__pragma__('opov')

# don't try to use global variables!!
class MyRobot(BCAbstractRobot):
    step = -1
    crusaders = 1
    pilgrims = 1
    prophets = 1

    mapLength = 0

    isCrusader = False

    # target location hard coded to 16,16 for now. set to None here to disable pathfinding until a target is set
    targetLocation = (16,16)

    direction_to_string = {
        (0,0): "C",
        (0,1): "S",
        (1,1): "SE",
        (1,0): "E",
        (1,-1): "NE",
        (0,-1): "N",
        (-1,-1): "NW",
        (-1,0): "W",
        (-1,1): "SW"
    }

    string_to_direction = {
        "C": (0,0),
        "S": (0,1),
        "SE": (1,1),
        "E": (1,0),
        "NE": (1,-1),
        "N": (0,-1),
        "NW": (-1,-1),
        "W": (-1,0),
        "SW": (-1,1)
    }

    # rotation values are strings because Python cannot easily get the index of a list of Tuples
    rotate_ccw = ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]
    rotate_cw = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]

    # robot min/max attack ranges
    attackRanges = {'crusaderMin': 1, 'crusaderMax': 16, 'prophetMin': 16, 'prophetMax': 64, 'preacherMin': 1, 'preacherMax': 16 }

    def turn(self):
        self.step += 1

<<<<<<< HEAD
=======
        if self.step == 1:
            self.mapLength = len(self.map)
>>>>>>> 0b63492a7a6248aa5a1c12661a790ef2613664ee

        if self.step % 1 == 0:
            #self.log("START TURN " + self.step)

            if self.me['unit'] == SPECS['CRUSADER']:
                if not self.isCrusader:
                    self.isCrusader = True

            #    self.log("Crusader health: " + str(self.me['health']))

                # Attack closest target if possible
                targets = self.getTargetRobots()
                if len(targets) > 0:
                    target = self.findClosestTarget(targets)
                    engage = self.engageEnemyRobots(target)
                    if engage:
                        self.log("engaging robot " + str(target['bot']))
                        return self.attack(self.me.x - target['location']['x'], self.me.y - target['location']['y'])

                # move to target if possible
                movement = self.getMovement()
                if movement != (0,0):
                  #  self.log("Moving in direction: " + str(movement))
                    return self.move(*movement)

            elif self.me['unit'] == SPECS['CASTLE']:
                if self.step < 20:
                    randir = [-1, 0, 1]
                    firstdir = random.choice(randir)
                    seconddir = random.choice(randir)
                    if self.crusaders / self.pilgrims <= .5:
                       # self.log("Building a crusader at " + str(self.me['x']+1) + ", " + str(self.me['y']+1))
                        self.crusaders += 1
                        return self.build_unit(SPECS['CRUSADER'], firstdir, seconddir)
                    elif self.prophets <= 1:
                        self.log("building a prophet at " + str(self.me['x']+1) + ", " + str(self.me['y']+1))
                        self.prophets += 1
                        return self.build_unit(SPECS['PROPHET'], firstdir, seconddir)
                    else:
                     #   self.log("building a pilgrim at " + str(self.me['x']+1) + ", " + str(self.me['y']+1))
                        self.pilgrims += 1
                        return self.build_unit(SPECS['PILGRIM'], firstdir, seconddir)
                else:
                  #  self.log("Castle health: " + self.me['health'])
                    pass
            
            elif self.me['unit'] == SPECS['PILGRIM']:
                # move to target if possible
                movement = self.getMovement()
                if movement != (0,0):
                  #  self.log("Moving in direction: " + str(movement))
                    return self.move(*movement)

            elif self.me['unit'] == SPECS['PROPHET']:
                if self.step == 1:
                    currentLocation = (self.me['x'], self.me['y'])
                    centerPoint = math.ceil(self.mapLength / 2)
                    centerLocation = (centerPoint, centerPoint)
                    direction = self.getDirection(currentLocation, centerLocation)
                    self.targetLocation = self.getTargetInDirection(currentLocation, direction, 5)
                # move to target if possible
                movement = self.getMovement()
                if movement != (0,0):
                    self.log("Moving in direction: " + str(movement))
                    return self.move(*movement)
        else:
            return False

    def getTargetInDirection(self, location, direction, amount):
        x = location[0] + direction[0] * amount
        y = location[1] + direction[1] * amount
        return (x, y)

    # will return (0,0) if there is no target location set, no available spaces within movement range, or if robot is already at the target location
    def getMovement(self):
        currentLocation = (self.me['x'], self.me['y'])
        directionalMovement = (0,0)

        if self.targetLocation and not currentLocation == self.targetLocation:

            direction = self.getDirection(currentLocation, self.targetLocation)
            directionalMovement = self.getDirectionalMovement(currentLocation, direction)
            newLocation = self.getNewLocation(currentLocation, directionalMovement)
            initialDirection = direction
            readyToMove = True

            while not self.isPassable(newLocation):
                # rotate the robots direction clockwise and proceed
                #TO DO determine when it makes more sense to go clockwise vs counter clockwise
                direction = self.getRotatedDirection(direction, 1)

                if direction == initialDirection:
                 #   self.log("Was unable to find a direction to move in")
                    readyToMove = False
                    break

                directionalMovement = self.getDirectionalMovement(currentLocation, direction)
                newLocation = self.getNewLocation(currentLocation, directionalMovement)

            if not readyToMove:
                directionalMovement = (0,0)

        return directionalMovement

    def getDirection(self, location, target):
        # get direction to target
        dx = target[0] - location[0]
        dy = target[1] - location[1]

        if dx < 0:
            dx = -1
        elif dx > 0:
            dx = 1

        if dy < 0:
            dy = -1
        elif dy > 0:
            dy = 1

        return (dx, dy)

    def getDirectionalMovement(self, currentLocation, direction):
        # get directional movement allowed towards target        
        if self.isCrusader:
            singleLineMovementSpeed = 3
            diagonalMovementSpeed = 2
        else:
            singleLineMovementSpeed = 2
            diagonalMovementSpeed = 1

        xDirectionalMovement = direction[0]
        yDirectionalMovement = direction[1]

        if xDirectionalMovement != 0 and yDirectionalMovement != 0:
            xDirectionalMovement *= diagonalMovementSpeed
            yDirectionalMovement *= diagonalMovementSpeed
        else:
            xDirectionalMovement *= singleLineMovementSpeed
            yDirectionalMovement *= singleLineMovementSpeed

        # limit the directional movement if target is closer than max movement range
        xOffset = self.targetLocation[0] - currentLocation[0]
        yOffset = self.targetLocation[1] - currentLocation[1]

        if self.isCrusader:
            # TO DO Add logic to enhance Crusader movements
            pass
        else:
            if xDirectionalMovement != 0:
                directionalMovement = (xDirectionalMovement, yDirectionalMovement)
                xDirectionalMovement = self.checkForShorterAxisMovement(xOffset, xDirectionalMovement, directionalMovement, currentLocation)
                    
            if yDirectionalMovement != 0:
                directionalMovement = (xDirectionalMovement, yDirectionalMovement)
                yDirectionalMovement = self.checkForShorterAxisMovement(yOffset, yDirectionalMovement, directionalMovement, currentLocation)                

        return (xDirectionalMovement, yDirectionalMovement)

    def checkForShorterAxisMovement(self, Offset, axisDirectionalMovement, directionalMovement, currentLocation):
        # shorten directional movement by single increment if possible
        if Offset == 1 or Offset == -1:
            axisDirectionalMovement = Offset                                
        elif axisDirectionalMovement > 1:
            newLocation = self.getNewLocation(currentLocation, directionalMovement)
            if not self.isPassable(newLocation):
                axisDirectionalMovement = 1
        elif axisDirectionalMovement < -1:
            newLocation = self.getNewLocation(currentLocation, directionalMovement)
            if not self.isPassable(newLocation):
                axisDirectionalMovement = -1
        
        return axisDirectionalMovement

    def getNewLocation(self, currentLocation, directionalMovement):
        x = currentLocation[0] + directionalMovement[0]
        y = currentLocation[1] + directionalMovement[1]
        return (x, y)

    def isPassable(self, newLocation):
        passable = True

        if newLocation[0] < 0 or newLocation[0] > len(self.map):
            passable = False
        elif newLocation[1] < 0 or newLocation[1] > len(self.map):
            passable = False
        elif not self.map[newLocation[1]][newLocation[0]]:
            passable = False
        elif self.get_visible_robot_map()[newLocation[1]][newLocation[0]] > 0:
            passable = False

        return passable

    def getRotatedDirection(self, direction, amount, clockwise=True):
        #rotate direction
        directionString = self.direction_to_string[direction]

        if clockwise:
            rotatedDirectionString = self.rotate_cw[(self.rotate_cw.index(directionString) + amount) % 8]
        else:
            rotatedDirectionString = self.rotate_ccw[(self.rotate_cw.index(directionString) + amount) % 8]

        rotatedDirection = self.string_to_direction[rotatedDirectionString]

        return rotatedDirection

    def getTargetRobots(self):
        """will return a list of visable enemy robots."""
        self.log("find targets")
        robots = self.get_visible_robots()
        enemyRobots = []
        if len(robots) > 0:
            for bot in robots:
                self.log("target bot team " + str(bot.team))
                self.log("my team " + str(self.me['team']))
                if bot.team != self.me['team']:
                    self.log("adding bot to enemy list")
                    enemyRobots.append(bot)
        return enemyRobots

    def getRangeToTarget(self, startPosition, targetPosition):
        """will return the radius squared distance |X1-X2|^2 + |Y1-Y2|^2 from the startPosition {'x': 1, 'y': 2} to the TargetPosition {'x': 4, 'y': 9}"""
        return abs(startPosition['x'] - targetPosition['x'])**2 + abs(startPosition['y']-targetPosition['y'])**2

    def findClosestTarget(self, enemyRobots):
        """will return the closest robot in the list of robots"""
        self.log("finding closest target")
        closest = {'target': None}
        myLoc = {'x': self.me.x, 'y': self.me.y}
        for bot in enemyRobots:
            enemyLoc = {'x':bot.x, 'y': bot.y}
            distance = self.getRangeToTarget(myLoc, enemyLoc)
            if closest['target'] is None:
                closest['target'] = bot 
                closest['distance'] = distance
                closest['location'] = enemyLoc
            else:
                if distance < closest['distance']:
                    closest['target'] = bot
                    closest['distance'] = distance
                    closest['location'] = enemyLoc
        self.log(str(closest['target']))
        self.log(str(closest['distance']))
        return closest

    def engageEnemyRobots(self, targetRobot):
        """Will engage the enemy if it is within robots range."""
        self.log("engaging enemys")
        enemyEngaged = False
        if self.me['unit'] == SPECS['CRUSADER']:
            if  self.attackRanges['crusaderMin'] <= targetRobot['distance'] <= self.attackRanges['crusaderMax']: 
                enemyEngaged = True
        return enemyEngaged

robot = MyRobot()
