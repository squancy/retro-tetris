import re

# Helper functions
def formatSec(secs):
  """
    Given some elapsed time in seconds output time in AB:CD:EF format
  """
  def zeroPrefix(n):
    if n < 10:
      return '0' + str(n)
    return str(n)

  output = ''
  
  hrs = secs // 3600
  if hrs > 0:
    output += zeroPrefix(hrs) + ':'
    secs -= hrs * 3600
  else:
    output += '00:'

  mins = secs // 60
  if mins > 0:
    output += zeroPrefix(mins) + ':'
    secs -= mins * 60
  else:
    output += '00:'

  output += zeroPrefix(secs)
  return output

def getData():
  with open('data.txt', 'r') as f:
    return f.read()

def getHighScore():
  """
    Get current high score saved in file
  """
  with open('data.txt', 'r') as f:
    s = f.read()    
    dataArr = [x for x in s.split(';;;') if '=' in x]
    for el in dataArr:
      (k, v) = el.split('=')
      if k == 'hs':
        return int(v)

def updateHighScore(highScore):
  """
    Write a new high score to file
  """
  s = getData()
  hsText = 'hs=' + str(highScore)
  with open('data.txt', 'w') as f:
    d = re.sub(r'hs=\d+', hsText, s)
    f.write(d)

def checkCollision(currentElement, elements, xShift, yShift, rotate = False):
  """
    Check that if the player moves the current tetromino to left, right or down will it collide
    with other tetromino elements already on the map
  """
  # Simulate a movement to L/R/D or rotation
  elementsPos = []
  size = currentElement[0].size;
  if rotate:
    for sq in currentElement:
      xOld = sq.pos.left
      newX = sq.pos.top + sq.pivotPoint[0] - sq.pivotPoint[1]
      newY = sq.pivotPoint[0] + sq.pivotPoint[1] - xOld - size
      elementsPos.append((newX, newY))
  else:
    for sq in currentElement:
      elementsPos.append((sq.pos[0] + xShift, sq.pos[1] + yShift)) 

  # Filter out the current element from all elements
  for sq2 in currentElement:
    for sq1 in elements:
      if sq1 is sq2:
        elements.remove(sq1)

  # Check for collision
  othersPos = []
  for sq in elements:
    othersPos.append((sq.pos[0], sq.pos[1]))

  for (x1, y1) in othersPos:
    for (x2, y2) in elementsPos:
      if abs(x1 - x2) < size and abs(y1 - y2) < size:
        return True 
  return False
