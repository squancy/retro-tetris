import sys, pygame, pygame.freetype, time, math, random, re
from includes.constants import * 
from includes.helpers import *
from includes.elements import *

pygame.init()
pygame.display.set_caption('Retro Tetris')

startTime = time.time()

def displayText(text, color, pos):
  textSurface, rect = GAME_FONT.render(text, color)
  screen.fill(pygame.Color("black"), (pos[0], pos[1], rect.width, rect.height))
  screen.blit(textSurface, pos) 
  return (textSurface, rect)

def updateTime(color, pos):
  elapsedTimeInSecs = math.floor(time.time() - startTime)
  formattedTime = formatSec(elapsedTimeInSecs) 
  screen.fill(pygame.Color("black"), (35, 50, 75, 18))
  newTextSurface, rect = GAME_FONT.render(formattedTime, color)
  screen.blit(newTextSurface, pos) 

def moveBlockX(currentElement, d):
  """
    Shift the current element horizontally by 1 unit
    Also make sure that the rotation does not place the element out of the map
  """
  # If element is at the very right/left of the map do not allow further X-shift in that dir.
  for sq in currentElement:
    if (d == 'l' and sq.pos.left == 150) or (d == 'r' and sq.pos.left == 425):
      return

  for sq in currentElement:
    screen.blit(background, sq.pos, (150, 0, 26, 26))

  for sq in currentElement:
    sq.moveHorizontally(d)
    screen.blit(sq.image, sq.pos)

def rotateElement(element):
  """
    Rotate 90 deg each square that the tetris element is made up of around a pivot point
    The point is the center of the bounding box
  """
  # Make sure that the rotation will not place the tetromino out of map at the top
  for sq in element:
    if sq.pos[1] <= 0:
      return
  
  for sq in element:
    screen.blit(background, sq.pos, (150, 0, 26, 26))
  
  # Also, make sure that element stays within the map after rotation
  tmpArr = []
  for sq in element:
    sq.rotate()
    tmpArr.append(sq.pos.left)

  leftmostElement = min(tmpArr)
  rightmostElement = max(tmpArr)
  if leftmostElement < 150:
    xShift = 150 - leftmostElement
  elif rightmostElement > 425:
    xShift = 425 - rightmostElement
  else:
    xShift = 0
  
  for sq in element:
    sq.pos.left += xShift
    screen.blit(sq.image, sq.pos)

def displayNextElement(element):
  """
    Display the next element for the player
  """
  screen.fill(pygame.Color("black"), (450, 50, 149, 149))

  # Position the element to the top right of the screen
  # Also make sure that the element is centered
  l = []
  for sq in element:
    l.append(sq.pos[0])
  
  # There is a 150px wide section at both sides of the screen
  minMaxDiff = max(l) - min(l)
  
  # First shift the element to the very right of the map
  diffCorrigated = 425 - max(l)

  # Then add margins to both sides so that it will be centered in the 150px region
  diffCorrigated += 150 - (125 - minMaxDiff) / 2

  for i in range(len(element)):
    element[i].pos = element[i].pos.move(diffCorrigated, 75)
    screen.blit(element[i].image, element[i].pos)

def getTextWidth(text):
  hsTxt, _ = GAME_FONT.render(text, BLACK)
  return hsTxt.get_width()

def updateScore(currentScore, highScore):
  """
    Update current score and high score on the screen & also make sure they're centered
  """
  screen.fill(pygame.Color("black"), (10, 210, 130, 20))
  hsWidth = getTextWidth(str(highScore))
  hsPos = (150 - hsWidth) // 2, 210
  displayText(str(highScore), GOLD, hsPos)

  screen.fill(pygame.Color("black"), (10, 130, 130, 20))
  csWidth = getTextWidth(str(currentScore))
  csPos = (150 - csWidth) // 2, 130
  displayText(str(currentScore), GOLD, csPos)

def getNextElements():
  (nextShape, nextColor) = selectRandomElement(extra = True)
  nextElementGroup = nextShape(nextColor, ex = False)
  nextElement = nextElementGroup.squares
  nextElementDisplay = nextShape(nextColor, ex = False).squares
  return [nextElementGroup, nextElement, nextElementDisplay]

def updateBothScores(currentScore, highScore, n):
  currentScore += n
  if currentScore > highScore:
    highScore = currentScore
    updateHighScore(highScore)
  updateScore(currentScore, highScore)
  return [currentScore, highScore]

def displayGameOver():
  """
    When the game is over clear the screen and display a game over message
  """
  screen.fill(pygame.Color('black'), (0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]))
  goText, rect1 = GAME_FONT.render('Game Over', WHITE)
  paText, rect2 = GAME_FONT.render('Press [Enter] to play again', WHITE)
  width1 = goText.get_width()
  height1 = goText.get_height()
  width2 = paText.get_width()
  height2 = paText.get_height()
  posX1 = (SCREEN_SIZE[0] - width1) / 2
  posY1 = (SCREEN_SIZE[1] - height1) / 2
  posX2 = (SCREEN_SIZE[0] - width2) / 2
  posY2 = (SCREEN_SIZE[1] - height2) / 2 + 30
  screen.blit(goText, (posX1, posY1))
  screen.blit(paText, (posX2, posY2))

# Create display and set screen size
screen = pygame.display.set_mode(SCREEN_SIZE)
background = pygame.image.load('sprites/bgImage.png').convert()

def graphicsInit():
  """
    Display graphical elements and text on the screen
  """
  screen.blit(background, (round((SCREEN_SIZE[0] - 300) / 2), 0))

  hsWidth = getTextWidth(str(getHighScore()))
  hsPos = (150 - hsWidth) // 2, 210

  # Initialize font, display elapsed time, current score and high score
  (timeLabel, x) = displayText('Time', WHITE, (50, 20))
  (elapsedTime, x) = displayText('00:00:00', GOLD, (35, 50))
  (currentScoreLabel, x) = displayText('Current Score', WHITE, (10, 100))
  (cs, x) = displayText('0', GOLD, (70, 130))
  (highScoreLabel, x) = displayText('High Score', WHITE, (25, 180))
  (highScore, x) = displayText(str(getHighScore()), GOLD, hsPos)
  (linesLabel, x) = displayText('Lines', WHITE, (50, 260))
  (linesCount, x) = displayText('0', GOLD, (70, 290))
  (nextLabel, x) = displayText('Next', WHITE, (500, 20))

graphicsInit()

def soundInit():
  """
    Initialize sounds, set volumes
  """
  # Play background music forever
  pygame.mixer.music.set_volume(0.5)
  pygame.mixer.music.load('sounds/bgMusic.mp3')
  pygame.mixer.music.play(-1)

  lineSound = pygame.mixer.Sound('sounds/success.wav')
  lineSound.set_volume(0.9)
  gameOverSound = pygame.mixer.Sound('sounds/gameover.wav')
  gameOverSound.set_volume(0.9)
  return [lineSound, gameOverSound]
 
lineSound, gameOverSound = soundInit()

def main():
  """
    Main event loop of the game
  """

  prevMoveSec = 0
  precision = 0
  currentScore = 0 
  lines = 0
  gameOver = False
  highScore = getHighScore()
  currentElementGroup = selectRandomElement()
  currentElement = currentElementGroup.squares

  (nextElementGroup, nextElement, nextElementDisplay) = getNextElements()

  # Move the image of the next element to the top right corner
  displayNextElement(nextElementDisplay)
  while True:
    if not gameOver:
      posBefore = []
      for sq in currentElement:
        posBefore.append((sq.pos[0], sq.pos[1]))

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          sys.exit()

        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
          # Move the current element left/right by one unit (if not already at the sides)
          if (event.key == pygame.K_LEFT and
            not checkCollision(currentElement, Game.tetrominos.copy(), -25, 0)):
            moveBlockX(currentElement, 'l')
          elif (event.key == pygame.K_RIGHT and not checkCollision(currentElement,
            Game.tetrominos.copy(), 25, 0)):
            moveBlockX(currentElement, 'r')
          # Rotate the current element in clockwise direction
          elif (event.key == pygame.K_UP and not checkCollision(currentElement,
            Game.tetrominos.copy(), 0, 0, rotate = True)):
            rotateElement(currentElement)
          # Speed up the falling of a tetromino
          elif event.key == pygame.K_DOWN:
            precision = 1
        elif event.type == pygame.KEYUP:
          if event.key == pygame.K_DOWN:
            precision = 0

      eTime = round(time.time() - startTime, precision)
      
      # At every second move current tetromino down by 1 unit
      if eTime > prevMoveSec:
        if precision:
          currentScore, highScore = updateBothScores(currentScore, highScore, 1)
          
        for sq in currentElement:
          screen.blit(background, sq.pos, (150, 0, 26, 26))
        
        for sq in currentElement:
          sq.move()
          screen.blit(sq.image, sq.pos)
        
        # Check if there is a filled row
        posYs = Game.checkForRows()
        if posYs and currentElementGroup.didCollide():
          pygame.mixer.Channel(0).play(lineSound)
          Game.clearRow(posYs, screen, background) 
          Game.shiftRows(posYs, screen, background)

          # Update number of filled lines and current score
          lines += len(posYs)
          displayText(str(lines), GOLD, (70, 290))  
          
          n = len(posYs) * (len(posYs) - 1) * 100
          currentScore, highScore = updateBothScores(currentScore, highScore, n)

        prevMoveSec = eTime
   
      # Check if the current tetromino reached the bottom of the map
      if currentElementGroup.didCollide():
        # Check for game end: if the player cannot move the current element anymore
        posAfter = []
        for sq in currentElement:
          posAfter.append((sq.pos[0], sq.pos[1]))
          
        # Game over, reset states
        if posAfter == posBefore:
          pygame.mixer.Sound.play(gameOverSound)
          pygame.mixer.music.stop()
          Game.tetrominos = []
          displayGameOver()
          gameOver = True
        
        if not gameOver:
          currentElementGroup = nextElementGroup
          currentElement = currentElementGroup.squares
          (nextElementGroup, nextElement, nextElementDisplay) = getNextElements()
          displayNextElement(nextElementDisplay)
          Game.tetrominos.extend(currentElement)

      if not gameOver:
        updateTime(GOLD, (35, 50))

      pygame.display.update()
    else:
      # Listen for [Enter] -> play again
      # Also reset states
      for event in pygame.event.get(): 
        if event.type == pygame.KEYDOWN:
          if event.type == pygame.QUIT:
            sys.exit()

          if event.key == pygame.K_RETURN:
            gameOver = False
            prevMoveSec = 0
            precision = 0
            currentScore = 0 
            lines = 0
            graphicsInit()
            currentElementGroup = selectRandomElement()
            currentElement = currentElementGroup.squares
            (nextElementGroup, nextElement, nextElementDisplay) = getNextElements()
            displayNextElement(nextElementDisplay)

            soundInit()

if __name__ == '__main__':
  tetris = main() 
