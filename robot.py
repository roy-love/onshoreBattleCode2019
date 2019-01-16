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
    mapHeight = 0
    defenceGrid = []

    isCrusader = False

    # target location hard coded to 16,16 for now. set to None here to disable pathfinding until a target is set
    targetLocation = None
    resourceInSight = False
    failedResourceSearchCount = 0
    randomMovementCount = 0
    spawnLocation = None
    spawnCastleLocation = None

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

        if self.step == 0:
            self.mapLength = len(self.map)
            self.mapHeight = len(self.map[0])
            self.log("map length is " + str(self.mapLength) + " map height is " + str(self.mapHeight))
            if self.me['unit'] != SPECS['PILGRIM']:
                self.setDefenseGrid()
                self.targetLocation = self.getStation()
                self.log("my station is " + str(self.targetLocation))

            # self.log("map length is " + str(self.mapLength) + " map height is " + str(self.mapHeight))

        if self.step % 1 == 0:
            # self.log("START STEP " + self.step)

            if self.me['unit'] == SPECS['CRUSADER']:
                        # ensure that target location is not none and not equal to the current location
                #myCurrentLocation = (self.me['x'], self.me['y'])
                #if not (self.targetLocation and not myCurrentLocation == self.targetLocation):
                    #self.log("Setting new target because old one was bad")
                    #self.targetLocation = self.getRandomPassableLocation()

                if not self.isCrusader:
                    self.isCrusader = True
                    # self.targetLocation = self.getRandomPassableLocation()

            #    self.log("Crusader health: " + str(self.me['health']))

                # Attack closest target if possible
                targets = self.getTargetRobots()
                if len(targets) > 0:
                    target = self.findClosestTarget(targets)
                    engage = self.engageEnemyRobots(target)
                    if engage:
                        self.log("engaging robot " + str(target['bot']))
                        return self.attack(target['location']['x'] - self.me.x, target['location']['y'] - self.me.y)

                # move to target if possible
                movement = self.getMovement()
                if movement != (0,0):
                  #  self.log("Moving in direction: " + str(movement))
                    return self.move(*movement)

            elif self.me['unit'] == SPECS['CASTLE']:
                if self.karbonite >= 20:
                    randir = [-1, 0, 1]
                    ranChance = [False, True]
                    firstdir = random.choice(randir)
                    seconddir = random.choice(randir)
                    if self.pilgrims <= 2:
                     #   self.log("building a pilgrim at " + str(self.me['x']+1) + ", " + str(self.me['y']+1))
                        self.pilgrims += 1
                        return self.build_unit(SPECS['PILGRIM'], firstdir, seconddir)
                    elif self.crusaders / self.pilgrims <= .5:
                       # self.log("Building a crusader at " + str(self.me['x']+1) + ", " + str(self.me['y']+1))
                        self.crusaders += 1
                        return self.build_unit(SPECS['CRUSADER'], firstdir, seconddir)
                    elif self.prophets <= 2:
                        # self.log("building a prophet at " + str(self.me['x']+1) + ", " + str(self.me['y']+1))
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
                currentLocation = (self.me['x'], self.me['y'])
                returningHome = False            

                if self.step == 0:
                    self.spawnLocation = currentLocation
                    for robot in self.get_visible_robots():
                        if robot['unit'] == SPECS['CASTLE']:
                            self.spawnCastleLocation = (robot['x'], robot['y'])

                if self.failedResourceSearchCount == 10:
                    returningHome = False    
                    self.targetLocation = self.getRandomPassableLocation()
                    self.randomMovementCount += 1

                    if self.randomMovementCount < 12:
                        self.failedResourceSearchCount = 0

                elif self.targetLocation is None or not self.resourceInSight:
                    returningHome = False    
                    # find nearest vacant karbonite or fuel
                    self.targetLocation = self.find_nearest(self.karbonite_map, currentLocation)
                    if self.targetLocation != (-1, -1):
                        self.resourceInSight = True
                        self.failedResourceSearchCount = 0
                    else:
                        self.targetLocation = self.find_nearest(self.fuel_map, currentLocation)
                        if self.targetLocation != (-1, -1):
                            self.resourceInSight = True
                            self.failedResourceSearchCount = 0
                        else:
                            self.failedResourceSearchCount += 1                
                if self.me['karbonite'] == SPECS['UNITS'][SPECS["PILGRIM"]]['KARBONITE_CAPACITY']:
                    returningHome = True
                    # set target back to the castle and unload
                    self.targetLocation = self.spawnLocation
                    if self.spawnLocation == currentLocation:
                        directionToCastle = self.getDirection(currentLocation, self.spawnCastleLocation)
                        self.resourceInSight = False
                        self.targetLocation = None
                        return self.give(directionToCastle[0], directionToCastle[1], self.me['karbonite'], self.me['fuel'])
                elif self.me['fuel'] == SPECS['UNITS'][SPECS["PILGRIM"]]['FUEL_CAPACITY']:
                    returningHome = True
                    # set target back to the castle and unload
                    self.targetLocation = self.spawnLocation
                    if self.spawnLocation == currentLocation:
                        directionToCastle = self.getDirection(currentLocation, self.spawnCastleLocation)
                        self.resourceInSight = False
                        self.targetLocation = None
                        return self.give(directionToCastle[0], directionToCastle[1], self.me['karbonite'], self.me['fuel'])
                elif self.karbonite_map[currentLocation[1]][currentLocation[0]] or self.fuel_map[currentLocation[1]][currentLocation[0]]:
                    return self.mine()

                # move to target if possible
                movement = self.getMovement()
                if movement != (0,0):
                    return self.move(*movement)

            elif self.me['unit'] == SPECS['PROPHET']:
                #myCurrentLocation = (self.me['x'], self.me['y'])
                #if not (self.targetLocation and not myCurrentLocation == self.targetLocation):
                    #self.log("Setting new target because old one was bad")
                    #self.targetLocation = self.getRandomPassableLocation()
                if self.step == 0:
                    currentLocation = (self.me['x'], self.me['y'])
                    centerPoint = math.ceil(self.mapLength / 2)
                    centerLocation = (centerPoint, centerPoint)
                    direction = self.getDirection(currentLocation, centerLocation)
                    # self.targetLocation = self.getTargetInDirection(currentLocation, direction, 5)
                    # self.targetLocation = self.getRandomPassableLocation()
                # Attack closest target if possible
                targets = self.getTargetRobots()
                if len(targets) > 0:
                    target = self.findClosestTarget(targets)
                    engage = self.engageEnemyRobots(target)
                    if engage:
                        #self.log("engaging robot " + str(target['target']['id']))
                        return self.attack(target['location']['x'] - self.me['x'], target['location']['y'] - self.me['y'])
                # move to target if possible
                movement = self.getMovement()
                if movement != (0,0):
                    if self.me.fuel > 100:
                        self.log("Moving in direction: " + str(movement))
                        return self.move(*movement)
        else:
            return False

    def getTargetInDirection(self, location, direction, amount):
        x = location[0] + direction[0] * amount
        y = location[1] + direction[1] * amount
        return (x, y)

    def getMovement(self):
        """Will return the number of x and y blocks the robot will move, as a set of coordinates"""
        # store the robot's current location and set the directional movement to 0,0 so that the robot won't move by default
        currentLocation = (self.me['x'], self.me['y'])
        directionalMovement = (0,0)

        # ensure that target location is not none and not equal to the current location
        if self.targetLocation and not currentLocation == self.targetLocation:

            # store the direction, directional movement, and the new map location we will trying to move the robot to this round
            direction = self.getDirection(currentLocation, self.targetLocation)
            directionalMovement = self.getDirectionalMovement(currentLocation, direction)
            newLocation = self.getNewLocation(currentLocation, directionalMovement)

            # store the current direction for use later
            initialDirection = direction

            # by default, the robot is ready to move in the event that the new map location is already passable
            readyToMove = True

            # while the new map location is not passable
            while not self.isPassable(newLocation):
                # if unit is a crusader moving diagonally at their fastest pace, set their directional movement to (1,1)
                if self.isCrusader and directionalMovement[0] == 2 and directionalMovement[1] == 2:
                    directionalMovement[0] = 1
                    directionalMovement[1] = 1
                # or if the unit is traveling faster than 1 block East
                elif directionalMovement[0] > 1:
                    # lower the unit's movement East by 1 block
                    directionalMovement[0] -= 1
                # or if the unit is traveling faster than 1 block West
                elif directionalMovement[0] < -1:
                    # lower the unit's movement West by 1 block
                    directionalMovement[0] += 1
                # or if the unit is traveling faster than 1 block South
                elif directionalMovement[1] > 1:
                    # lower the unit's movement South by 1 block
                    directionalMovement[1] -= 1
                # or if the unit is traveling faster than 1 block North
                elif directionalMovement[1] < -1:
                    # lower the unit's movement North by 1 block
                    directionalMovement[1] += 1
                # else the unit is already moving the shortest distance they can in the current direction
                else:
                    # rotate the robots direction clockwise and proceed
                    direction = self.getRotatedDirection(direction, 1)

                    # if we ened up facing the same direction we started in
                    if direction == initialDirection:
                        # let the code know we're not ready to move
                        readyToMove = False
                        # break out of the while loop
                        break

                    # overwrite the directional movement with a new one based on the direction we just got
                    directionalMovement = self.getDirectionalMovement(currentLocation, direction)

                # overwrite the new location with the location we get from the directional movement we just got
                newLocation = self.getNewLocation(currentLocation, directionalMovement)

            # if the robot ended up not being ready to move
            if not readyToMove:
                # change the directional movement back to (0,0) so that it doesn't move
                directionalMovement = (0,0)
        else :
            self.targetLocation = self.getRandomPassableLocation()
        # return the directional movement
        return directionalMovement

    def getDirection(self, location, target):
        """Will return the direction as a set of coordinates"""
        # store the distance from the target to the location as dx and dy
        dx = target[0] - location[0]
        dy = target[1] - location[1]

        # if the x distance is less than 0, face West
        if dx < 0:
            dx = -1
        # or if the x distance is greater than 0, face East
        elif dx > 0:
            dx = 1

        # if the y distance is less than 0, face North
        if dy < 0:
            dy = -1
        # or if the y distance is greater than 0, face South
        elif dy > 0:
            dy = 1

        # return the direction as a set of coordinates
        return (dx, dy)

    def getDirectionalMovement(self, currentLocation, direction):
        """Will return the number of x and y blocks the unit can move in the specified direction as a set of coordinates"""
        # get the maximum diagonal vs single line movements based on the robot type
        if self.isCrusader:
            # Crusader can move a maximum of 3 blocks in a single line and 2 blocks in a diagonal line
            singleLineMovementSpeed = 3
            diagonalMovementSpeed = 2
        else:
            # all other units can move a maximum of 2 blocks in a single line and 1 block in a diagonal line
            singleLineMovementSpeed = 2
            diagonalMovementSpeed = 1

        # set the x and y directional movements to the current direction's x and y. These will be used to store the maximum movement speed of the robot in a given direction
        xDirectionalMovement = direction[0]
        yDirectionalMovement = direction[1]

        # if neither x or y are 0, then the unit is traveling diagonally so we multiply the values by the diagonal movement speed
        if xDirectionalMovement != 0 and yDirectionalMovement != 0:
            xDirectionalMovement *= diagonalMovementSpeed
            yDirectionalMovement *= diagonalMovementSpeed
        else:
            # else we multiply the movement values by the single line movement speed
            xDirectionalMovement *= singleLineMovementSpeed
            yDirectionalMovement *= singleLineMovementSpeed

        # store the values of how far the current location is from the target location
        xOffset = self.targetLocation[0] - currentLocation[0]
        yOffset = self.targetLocation[1] - currentLocation[1]

        # if the distance from 
        if self.isCrusader:
            if xDirectionalMovement != 0:
                if (xOffset > 0 and xOffset < 3) or (xOffset < 0 and xOffset > -3):
                    xDirectionalMovement = xOffset

            if yDirectionalMovement != 0:
                if (yOffset > 0 and yOffset < 3) or (yOffset < 0 and yOffset > -3):
                    yDirectionalMovement = yOffset
        else:
            if xDirectionalMovement != 0 and (xOffset == 1 or xOffset == -1):
                xDirectionalMovement = xOffset

            if yDirectionalMovement != 0 and (yOffset == 1 or yOffset == -1):
                yDirectionalMovement = yOffset

        return (xDirectionalMovement, yDirectionalMovement)

    def getNewLocation(self, currentLocation, directionalMovement):
        """Will return the coordinates of the location reached after moving"""
        x = currentLocation[0] + directionalMovement[0]
        y = currentLocation[1] + directionalMovement[1]
        return (x, y)

    def isPassable(self, newLocation, includeRobots=True):
        """Will return whether a set of coordinates is on the map, passable, and not occupied by another robot"""
        passable = True

        if newLocation[0] < 0 or newLocation[0] > len(self.map):
            passable = False
        elif newLocation[1] < 0 or newLocation[1] > len(self.map):
            passable = False
        elif not self.map[newLocation[1]][newLocation[0]]:
            passable = False
        elif includeRobots and self.get_visible_robot_map()[newLocation[1]][newLocation[0]] > 0:
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

    def getRandomPassableLocation(self):
        randomX = random.randint(1, self.mapLength - 1)
        randomY = random.randint(1, self.mapLength - 1)

        while not self.isPassable((randomX, randomY), False):
            randomX = random.randint(1, self.mapLength - 1)
            randomY = random.randint(1, self.mapLength - 1)

        return (randomX, randomY)

    def find_nearest(self, m, loc):
        closest_loc = (-1, -1)
        best_dist_sq = 64 * 64 + 64 * 64 + 1
        for x in range(len(m)):
            if (x - loc[0])**2 > best_dist_sq:
                continue
            for y in range(len(m[0])):
                if (y - loc[1])**2 > best_dist_sq:
                    continue
                d = (x-loc[0]) ** 2 + (y-loc[1]) **2
                if self.get_visible_robot_map()[y][x] == 0 and m[y][x] and d < best_dist_sq:
                    best_dist_sq = d
                    closest_loc = (x,y)
        return closest_loc

    def getTargetRobots(self):
        """will return a list of visable enemy robots."""
        # self.log("find targets")
        robots = self.get_visible_robots()
        enemyRobots = []
        if len(robots) > 0:
            for bot in robots:
                # self.log("target bot team " + str(bot['team']))
                # self.log("my team " + str(self.me['team']))
                if bot['team'] != self.me['team']:
                    self.log("adding bot to enemy list")
                    enemyRobots.append(bot)
        return enemyRobots

    def getRangeToTarget(self, startPosition, targetPosition):
        """will return the radius squared distance |X1-X2|^2 + |Y1-Y2|^2 from the startPosition {'x': 1, 'y': 2} to the TargetPosition {'x': 4, 'y': 9}"""
        return (startPosition['x'] - targetPosition['x'])**2 + (startPosition['y']-targetPosition['y'])**2

    def findClosestTarget(self, enemyRobots):
        """will return the closest robot in the list of robots"""
        # self.log("finding closest target")
        closest = {'target': None}
        myLoc = {'x': self.me['x'], 'y': self.me['y']}
        for bot in enemyRobots:
            enemyLoc = {'x':bot['x'], 'y': bot['y']}
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
        # self.log("engaging enemys")
        enemyEngaged = False
        if  SPECS.UNITS[self.me.unit].ATTACK_RADIUS[0] <= targetRobot['distance'] <= SPECS.UNITS[self.me.unit].ATTACK_RADIUS[1]: 
            enemyEngaged = True
        return enemyEngaged

    def setDefenseGrid(self):
        horizontal = -2
        vertical = -2
        if self.me.x < self.mapHeight - self.me['x']:
            horizontal = 2
        if self.me.y < self.mapLength - self.me['y']:
            vertical = 2
        gridSize = 2
        x = self.me['x']
        y = self.me['y']
        self.log("My coords are " + str(x) + " " + str(y))
        maxX = x + 10
        minX = x - 10
        maxY = y + 10
        minY = y - 10
        if maxX > self.mapHeight:
            maxX = self.mapHeight
        if minX < 0:
            minX = 0
        if maxY > self.mapLength:
            maxY = self.mapLength
        if minY < 0:
            minY = 0
        self.log("horizontal is " + str(horizontal))
        newHorizontal = horizontal
        self.log("New Horizontal is ************************ " + str(newHorizontal))
        while gridSize < 8:
            self.log("minx is " + str(minX))
            self.log("newHorizontal 2 is " + str(newHorizontal))
            x = (minX + newHorizontal)
            #self.log("x is " + str(x))
            newHorizontal += horizontal
            yGrid = 2
            gridSize += 2
            newVertical = vertical
            while yGrid < 8:
                y = (minY + newVertical)
                self.log("x is " + str(x))
                if x == x:
                    self.defenceGrid.append((x,y))
                yGrid += 2
                newVertical += 2
        #self.log("Final Gridsizes " + str(gridSize) + ' ' + yGrid)
        self.log("Defense Grid " + str(self.defenceGrid))

    def getStation(self):
        return random.choice(self.defenceGrid)



robot = MyRobot()
