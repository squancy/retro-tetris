import pygame, random, copy
from includes.constants import *
from includes.helpers import * 

class Game:
  # Represents all the tetris blocks that are visible on the map
  tetrominos = []
  
  @staticmethod
  def checkForRows():
    """
      Check for filled rows
    """
    filledRowPos = []
    elementsPos = [(sq.pos[0], sq.pos[1]) for sq in Game.tetrominos]
    for i in range(24):
      flag = True
      for j in range(12):
        rPos = (150 + j * 25, i * 25)
        if rPos not in elementsPos:
          flag = False
      if flag:
        filledRowPos.append(i * 25)

    return filledRowPos

  @staticmethod
  def clearRow(posYs, screen, background):
    """
      If the row is completely filled then clear it 
    """
    localTetrominos = Game.tetrominos.copy()
    toRemove = []
    for sq in Game.tetrominos:
      if sq.pos[1] in posYs:
        localTetrominos.remove(sq)
        screen.blit(background, sq.pos, (150, 0, 26, 26))

    Game.tetrominos = localTetrominos

  @staticmethod
  def shiftRows(posYs, screen, background):
    """
      If a row has been cleared shift every block down by 1
    """
    verticalShift = len(posYs)
    for sq in Game.tetrominos:
      if sq.pos[1] < max(posYs):
        screen.blit(background, sq.pos, (150, 0, 26, 26))

    for sq in Game.tetrominos:
      if sq.pos[1] < max(posYs):
        for i in range(verticalShift):
          sq.move()
        screen.blit(sq.image, sq.pos)

class TetrisBlock:
  """
    Builds 1 square block; more of these can be grouped together to form an L, Z, etc. shaped
    element
    Each square has its own velocity, position and image source
  """
  def __init__(self, color, pos, pivotPoint):
    self.size = 24
    self.image = pygame.image.load('sprites/' + color + 'Block.png').convert()
    self.pos = self.image.get_rect().move(pos)
    self.speed = 25
    self.pivotPoint = pivotPoint

  def move(self):
    """
      Vertical movemenet of a tetris block by 1 unit at a time
    """
    if not(self.pos.top + self.size >= SCREEN_SIZE[1]):
      self.pos = self.pos.move(0, self.speed)

      # Also update the pivot point of the element
      px = self.pivotPoint[0]
      py = self.pivotPoint[1]
      self.pivotPoint = (px, py + self.speed)

  def moveHorizontally(self, d):
    """
      Move the current tetris element left/right by 1 unit (if not already at the sides)
    """
    if d == 'l':
      xShift = -(self.speed)
    else:
      xShift = self.speed

    self.pos = self.pos.move(xShift, 0)

    # Also update the pivot point of the element
    px = self.pivotPoint[0]
    py = self.pivotPoint[1]
    self.pivotPoint = (px + xShift, py)

  def rotate(self):
    """
      Rotate an square around a pivot point (center of bounding box)
      Also make sure that the rotation does not place the element out of the map
    """
    # Perform simple rotation by 90 deg
    xOld = self.pos.left
    self.pos.left = self.pos.top + self.pivotPoint[0] - self.pivotPoint[1]
    self.pos.top = self.pivotPoint[0] + self.pivotPoint[1] - xOld - self.size

def randomXCoord(elementType):
  """
    Generate a random X coordinate for the first square block of a tetris element
  """
  if elementType == 'L' or elementType == 'square':
    return random.randrange(150, 400, 25)
  elif elementType == 'I':
    return random.randrange(150, 325, 25)
  elif elementType == 'Z' or elementType == 'T':
    return random.randrange(150, 350, 25)

class TetrominoMethods:
  def __init__(self, color, elementType):
    self.isFixed = False
    self.color = color
    self.elementType = elementType

  def didCollide(self):
    """
      Check if the current tetromino has reached the bottom of the map or the top of another
      tetromino
      If yes, then do not move it further down
    """
    # Check if the bottom of the map is reached
    for sq in self.squares:
      if sq.pos.bottom >= SCREEN_SIZE[1] - sq.size:
        self.isFixed = True
        return True

    # Check if the top of another tetromino is reached
    return checkCollision(self.squares, Game.tetrominos.copy(), 0, 25)

class LShapedElement(TetrominoMethods):
  """
    An L-shaped tetris element that is made up of 1x1 squares; represented as an array
  """
  def __init__(self, color, ex = True):
    """
      |1|
      |2|
      |3|4|
    """
    # Also, randomly select the x coordinate when creating a new element
    super().__init__(color, 'L')
    xCoord = randomXCoord('L')
    pp = (xCoord + 37, 12)
    self.squares = [TetrisBlock(color, (xCoord, -25), pp),
                    TetrisBlock(color, (xCoord, 0), pp),
                    TetrisBlock(color, (xCoord, 25), pp),
                    TetrisBlock(color, (xCoord + 25, 25), pp)] 
    if ex: Game.tetrominos.extend(self.squares)                    

class LShapedElementInv(TetrominoMethods):
  """
    An L-shaped tetris element that is made up of 1x1 squares; represented as an array
  """
  def __init__(self, color, ex = True):
    """
        |4|
        |3|
      |1|2|
    """
    # Also, randomly select the x coordinate when creating a new element
    super().__init__(color, 'LInv')
    xCoord = randomXCoord('L')
    pp = (xCoord + 37, 12)
    self.squares = [TetrisBlock(color, (xCoord, 25), pp),
                    TetrisBlock(color, (xCoord + 25, 25), pp),
                    TetrisBlock(color, (xCoord + 25, 0), pp),
                    TetrisBlock(color, (xCoord + 25, -25), pp)] 
    if ex: Game.tetrominos.extend(self.squares)                    

class IShapedElement(TetrominoMethods):
  """
    An I-shaped tetris element that is made up of 1x1 squares
  """
  def __init__(self, color, ex = True):
    """
      |1|2|3|4|
    """
    super().__init__(color, 'I')
    xCoord = randomXCoord('I')
    pp = (xCoord + 50, -0.5)
    self.squares = []
    for i in range(4):
      self.squares.append(TetrisBlock(color, (xCoord + i * 25, -25), pp))
    if ex: Game.tetrominos.extend(self.squares)                    

class BigSquareElement(TetrominoMethods):
  """
    A 2x2 square tetris element that is made up of 1x1 squares
  """
  def __init__(self, color, ex = True):
    """
      |1|2|
      |3|4|
    """
    super().__init__(color, 'square')
    xCoord = randomXCoord('square')
    pp = (xCoord + 25, -0.5)
    self.squares = [TetrisBlock(color, (xCoord, -25), pp),
                    TetrisBlock(color, (xCoord + 25, -25), pp),
                    TetrisBlock(color, (xCoord, 0), pp),
                    TetrisBlock(color, (xCoord + 25, 0), pp)] 
    if ex: Game.tetrominos.extend(self.squares)                    

class ZShapedElement(TetrominoMethods):
  """
    A Z-shaped tetris element that is made up of 1x1 squares
  """
  def __init__(self, color, ex = True):
    """
      |1|2|
        |3|4|
    """
    super().__init__(color, 'Z')
    xCoord = randomXCoord('Z')
    pp = (xCoord + 37, 12)
    self.squares = [TetrisBlock(color, (xCoord, -25), pp),
                    TetrisBlock(color, (xCoord + 25, -25), pp),
                    TetrisBlock(color, (xCoord + 25, 0), pp),
                    TetrisBlock(color, (xCoord + 50, 0), pp)]
    if ex: Game.tetrominos.extend(self.squares)                    

class ZShapedElementInv(TetrominoMethods):
  """
    A Z-shaped tetris element that is made up of 1x1 squares
  """
  def __init__(self, color, ex = True):
    """
        |3|4|
      |1|2|
    """
    super().__init__(color, 'ZInv')
    xCoord = randomXCoord('Z')
    pp = (xCoord + 37, 12)
    self.squares = [TetrisBlock(color, (xCoord, 0), pp),
                    TetrisBlock(color, (xCoord + 25, 0), pp),
                    TetrisBlock(color, (xCoord + 25, -25), pp),
                    TetrisBlock(color, (xCoord + 50, -25), pp)]
    if ex: Game.tetrominos.extend(self.squares)                    

class TShapedElement(TetrominoMethods):
  """
    A Z-shaped tetris element that is made up of 1x1 squares
  """
  def __init__(self, color, ex = True):
    """
      |1|2|3|
        |4|
    """
    super().__init__(color, 'T')
    xCoord = randomXCoord('T')
    pp = (xCoord + 37, 12)
    self.squares = [TetrisBlock(color, (xCoord, -25), pp),
                    TetrisBlock(color, (xCoord + 25, -25), pp),
                    TetrisBlock(color, (xCoord + 50, -25), pp),
                    TetrisBlock(color, (xCoord + 25, 0), pp)]
    if ex: Game.tetrominos.extend(self.squares)                    

def selectRandomElement(extra = False):
  """
    Select a tetris element with a random color and shape
    Also return the color and shape on request
  """
  color = random.choice(['red', 'cyan', 'yellow', 'orange', 'green', 'blue'])
  shape = random.choice([LShapedElement,
                         LShapedElementInv,
                         IShapedElement,
                         BigSquareElement,
                         ZShapedElement,
                         ZShapedElementInv,
                         TShapedElement
                       ])
  if extra:
    return [shape, color]
  return shape(color)
