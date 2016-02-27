import pygame.draw
import pygame.image
import pygame.surface
import numpy, os

goodColors = [[255, 0, 0, 255], [255, 165, 0, 255], [0, 255, 0, 255], [40, 255, 150, 255], [40, 150, 255, 255], [0, 0, 255, 255], [172, 0, 175, 255], [223, 0, 99, 255]]

def fform(nper, weights, phases, resolution=1024):
    if nper != len(weights) or nper != len(phases) or len(weights) != len(phases):
        raise ArgumentError, 'Arguments not of equal length!'
    
    theta = numpy.arange(0, 2.0*numpy.pi, (2.0 / resolution)*numpy.pi)
    form = numpy.zeros((resolution))
    
    for n in xrange(nper):
        form += weights[n] * numpy.exp(numpy.cos((n+1) * (theta + phases[n])))
    
    return theta, form

def makeStim(alpha, phases, randPhases, size, col = [128, 128, 128, 255], resolution=1024, fname = None):
    '''
    Create a blob stimulus and return it as a pygame surface.
    
    alpha - Exponent for the weight given to each frequency component of the
        figure.
    phases - The non-random (fixed) phases of each frequency component
    randPhases - Sequence of indices for the frequency components that are to
        have random phases.
    size - The number of pixels to a side of the final figure.
    col - The color (in RGBA) the figure should be filled with.
    resolution - The number of points along the edge of the figure (more points
        means higher fidelity)
    fname - Optional filename if you want to save the final figure to a file.
    '''
    # Create pygame surface to draw to
    surf = pygame.Surface((size, size))
    surf.fill([0, 0, 0, 0]) # [255, 255, 255, 0]
    
    # Compute the phases and weights of each frequency component
    nper = len(phases)
    weights = numpy.arange(1.0, nper+1.0)**alpha
    thisPhases = numpy.copy(phases)
    for p in randPhases: thisPhases[p] = numpy.random.rand() * 2.0 * numpy.pi
    
    # Create the resulting blob figure, in polar coordinates (theta, radius)
    t, r = fform(nper, weights, thisPhases, resolution)
    
    # Normalize the figure to take up 1/4 the area of the entire surface
    area = numpy.sum(.5 * r**2.0 * (t[1] - t[0]))
    targetArea = size**2.0 / 4.0
    r *= numpy.sqrt(targetArea / area)
    
    # Convert to Cartesian coordinates (x, y), center, and draw the surface, with a black outline
    x = r * numpy.cos(t) + size / 2.0
    y = r * numpy.sin(t) + size / 2.0
    
    xSum = 0.0
    ySum = 0.0
    xTotal = 0.0
    yTotal = 0.0
    xRound = numpy.round(x)
    yRound = numpy.round(y)
    for xVal in xRound:
        yVals = numpy.sort(yRound[xRound==xVal])
        if len(yVals) > 1:
            height = numpy.sum(numpy.diff(yVals)[numpy.arange(len(yVals)-1) % 2 == 0])
            xSum += xVal * height
            xTotal += height
    for yVal in yRound:
        xVals = numpy.sort(xRound[yRound==yVal])
        if len(xVals) > 1:
            width = numpy.sum(numpy.diff(xVals)[numpy.arange(len(xVals)-1) % 2 == 0])
            ySum += yVal * width
            yTotal += width
        
    cMass = tuple([xSum / xTotal, ySum / yTotal])
    #print cMass
    x -= cMass[0] - 0.5 * float(size)
    y -= cMass[1] - 0.5 * float(size)
    points = zip(x,y)
    pygame.draw.polygon(surf, col, points)
    #pygame.draw.aalines(surf, [255,255,255,255], True, points) # [0,0,0,255]
    
    # Optionally, save the figure to a file for later use
    if fname != None: pygame.image.save(surf, fname)
    
    return surf

def makeCategories(nCat, nExemplars, nper = 12, alpha = -1.5, catPhases = [2,4], catCol = [[180, 180, 180, 255]], size = 70, resolution = 512, root=None):
    objects = []
    #initPhases = numpy.random.rand(nper) * 2.0 * numpy.pi
    #phaseIncr = (2.0 * numpy.pi) / float(nCat)
    catPhaseIncr = (2.0 * numpy.pi) / float(nExemplars)
    
    if len(catCol) < nCat: catCol = [catCol[0]] * nCat
    
    if root != None and not os.path.isdir(os.path.join(os.getcwd(), root)):
        os.makedirs(os.path.join(os.getcwd(), root))
    
    for c in xrange(nCat):
        thisCat = []
        #phases = numpy.copy(initPhases)
        phases = numpy.random.rand(nper) * 2.0 * numpy.pi
        
        for n in xrange(nExemplars):
            if root == None:
                thisCat.append(makeStim(alpha, phases, [], size, catCol[c], resolution))
            else:
                thisCat.append(makeStim(alpha, phases, [], size, catCol[c], resolution, os.path.join(os.getcwd(), root, 'blob_'+str(c)+'_'+str(n)+'.jpg')))
            
            for p in catPhases: phases[p] += catPhaseIncr
        
        objects.append(thisCat)
        #initPhases += phaseIncr
    
    return objects
