# RL World Drop 
# Description: all objects abs value of 10, 1 or 2 categories of blobs
# George Kachergis & Greg Cox, Mar 26, 2011
# modified from Ian Mallett's Objects 2: The Vector! - v.2.0.0 (asteroids2.py)
# http://www.pygame.org/project/649/   http://www.geometrian.com/
# Up Arrow, ENTER = Fire, Left Arrow = Go Left, Right Arrow = Go Right
# 8 items
# mass study vs. sequential study (1x or 2x) - same total time
# - maybe no pause4space between trials?
# fixed starting height and separation
# dropspeed=.5 for half the trials, .8 for half
# v4: no inertia - 1 pixel per button press (per time step)
# also, all positive or all negative value distributions (just like flat distros)

import pygame, random, sys, os, copy
from pygame.locals import *
if sys.platform == 'win32' or sys.platform == 'win64':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
from math import *
from socket import gethostname
from time import localtime, strftime
from textwrap import wrap
import make_blobs

#### COLORS
white = (255, 255, 255)
grey = (102,102,102)
ltgrey = (211,211,211)
black = (0, 0, 0)
blue = (0, 0, 175) 
orange = (255, 165, 0) 
green = (0,175,0)
red = (255, 0, 0)

Bullets = []
Fire = 0

BULLETSPEED = 4.0 # was 2.0
DROPSPEED = 2 #.8 # 0.5 - .8 # how fast objects drop 
THRUST = 4 #.3 #.4 #0.08 # was .003 # agent acceleration
#SLOWING = .9 #1 #.98 # proportion of agent speed to retain at each time step

# red, orange, yellow, green, light blue, dark blue, grey, brown, pink, purple
colors = [(255,0,0), (255,102,0), (255,255,0), (0,153,0), (0,153,255), (0,0,255), grey, (102,51,0), (255,102,204), (102,0,204)]
sides = [3,4,5,6,7,8,9,12,100]

pygame.init()
Screen = (800,600) #(640,480)
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
Surface = pygame.display.set_mode(Screen, HWSURFACE | FULLSCREEN)# | DOUBLEBUF
clock = pygame.time.Clock()

Score = 0
Level = 1
NewLevelTextBrightness = 255

font_size = 32
Font = pygame.font.SysFont(None,16)
Font2 = pygame.font.SysFont(None,64)
Font3 = pygame.font.SysFont(None,font_size)

def goodbye(logFile):
	logFile.write('End Time: %s\n' % (strftime("%a, %b %d, %Y %H:%M:%S", localtime() )))
	finalize(logFile)
	blank_screen()
	pygame.event.clear()
	endScript = '''Thanks for participating!  \
Please let the experimenter know that you are finished.  \
If you have any questions, please ask the experimenter.'''
	DisplayText(endScript)
	pygame.display.flip()
	while 1:
		event = pygame.event.poll()
		if pygame.key.get_pressed()[pygame.K_ESCAPE]:
			break
	pygame.quit()
	raw_input('Press enter to exit.')
	sys.exit()

def finalize(logFile):
    logFile.close()

def exit(logFile):
    finalize(logFile)
    pygame.quit()
    sys.exit()

def subject_info(rand_seed):
	#subj = raw_input('Enter Subject Number: ')
	#subj = int(subj)
	random.seed(rand_seed)
	if not os.path.isdir(os.path.join(os.getcwd(), 'data')):
		os.mkdir(os.path.join(os.getcwd(), 'data'))
	
	files = os.listdir(os.path.join(os.curdir, 'data'))
	subj = 1
	for fn in files:
		if fn[:6]=='data_s':
			subj += 1
	logFilename = os.path.join(os.getcwd(), 'data', 'data_s') + str(subj) + ".txt"
	
	# Open data files
	logFile = open(logFilename, 'w')
	logFile.write('Participant: %d\n' % (subj))
	logFile.write('MachineID: %s\n' % (gethostname()))
	logFile.write('Start Time: %s\n' % (strftime("%a, %b %d, %Y %H:%M:%S", localtime() )))
	logFile.write('Seed: %s\n' % rand_seed)
	logFile.write('Subject\tBlock\tNcats\tValence\tStudyTime\tStudyType\tTrial\tLObjVal\tRObjVal\tDist\tSeparation\tDropSpeed\tFoilType\tScoreChange\tStartTime\tDuration\n') 
	# 'Subject Block Ncats Valence StudyTime StudyType Trial Obj1Value Obj2Value Distance Separation DropSpeed FoilType ScoreChange StartTime Duration'
	logFile.flush()
	logFile.close()
	pause(1000) # write the file...
	logFile = open(logFilename, 'a')
	
	posFilename = os.path.join(os.getcwd(), 'data', 'pos_s') + str(subj) + ".txt"
	pos_file = open(posFilename, 'w')
	pos_file.write("Subject\tBlock\tTrial\tPlayerX\tObjectY\tDropSpeed\tTime\n")
	pos_file.flush()
	
	keyFilename = os.path.join(os.getcwd(), 'data', 'key_s') + str(subj) + ".txt"
	key_file = open(keyFilename, 'w')
	key_file.write("Subject\tTrial\tKeyPress\tTime\n")
	key_file.flush()
	
	return subj, logFile, pos_file, key_file

class Player:
	def __init__(self):
		self.points	= [[0, 20], [-140, 20], [180, 7.5], [140, 20]]
		self.rotpoints = [[0, 20], [-140, 20], [180, 7.5], [140, 20]]
		self.pos = [Screen[0]/2.0,Screen[1]-100]
		self.speed = [0, 0]
		self.thrust	= THRUST
		self.rot = 180 # orientation
		self.scale = 0.5
		self.thrust_append = 0
		self.invincibility = 1

player1 = Player()

Objects = []
class Object:
	def __init__(self, stim, value=0):
		self.value = value
		self.speed = DROPSPEED
		self.pos = []
		self.stimulus = stim
		self.radius = 30
		#self.update()
	def pointtest(self,point):
		x = point[0]
		y = point[1]
		#if self.pos[0]-x < self.diameter:
		#	if self.pos[1]-y < 15:
		#		return True
		if abs((self.pos[0]+35)-x) < self.radius:
			if abs((self.pos[1]+35)-y) < self.radius:
				return True # yes, close enough
		return False
	def draw(self):
		#print self.pos
		Surface.blit(self.stimulus, self.pos) # (Posx,Posy)

def NewLevel():
	global player1, NewLevelTextBrightness, Bullets, Objects
	Bullets = []
	Objects = []
	player1.speed = [0,0]
	NewLevelTextBrightness = 255

def GetInput2():
	keystate = pygame.key.get_pressed()
	for event in pygame.event.get():
		if event.type==QUIT or (pygame.key.get_pressed()[pygame.K_LCTRL] and pygame.key.get_pressed()[pygame.K_BACKQUOTE]):
			pygame.quit(); sys.exit()
	if keystate[K_RETURN]:
		return "new"

def FireBullet():
    global Fire
    if Fire == 0:
        Pos = [player1.pos[0]+(7.5*cos(radians(-player1.rot+90))),
               player1.pos[1]+(7.5*sin(radians(-player1.rot+90)))]
        Speedx = BULLETSPEED*cos(radians(-player1.rot+90))
        Speedy = BULLETSPEED*sin(radians(-player1.rot+90))
        Speed = [Speedx,Speedy]
        Bullets.append([Pos,Speed,0])
        Fire = 20
    if Fire > 0:
        Fire -= 1

def pause(pause):
	waittime = 0
	time_stamp = pygame.time.get_ticks()
	while waittime < pause:
		pygame.event.clear()
		if pygame.key.get_pressed()[pygame.K_LCTRL] and pygame.key.get_pressed()[pygame.K_BACKQUOTE]:
			pygame.quit(); sys.exit()
		waittime = pygame.time.get_ticks() - time_stamp

def eat_object(obj, feedback):
	toAdd = obj.value
	if feedback:
		text = str(obj.value)
		if obj.value<0:
			col = red
		else:
			col = green
			text = "+"+text
		fbtext = Font3.render(text, True, col)
		Surface.blit(fbtext,(obj.pos[0]-20, obj.pos[1]+45))
	pygame.display.flip()
	pause(1300)
	Objects.remove(obj)
	return toAdd

def CollisionDetect(feedback=True):
	global Level, Score, player1, NewLevelTextBrightness
	elasticity = 0.5
	if   player1.pos[0] > Screen[0]: player1.pos[0]=Screen[0];player1.speed[0]*=-elasticity
	elif player1.pos[0] < 0:		 player1.pos[0]=0;player1.speed[0]*=-elasticity
	for b in Bullets:
		for a in Objects:
			if a.pointtest(b[0]): # player shot object
				Score += eat_object(a, feedback)
				return
	for p in player1.rotpoints:
#		for a in Objects:
#			a.update()
		for a in Objects:
			if a.pointtest(p): # player ate object!
				Score += eat_object(a, feedback)
				return
	if player1.thrust_append > 0:
		player1.thrust_append -= 1
	if NewLevelTextBrightness > 0:
		NewLevelTextBrightness -= 1

def obj_off_bottom():
	global Score
	fbtext = Font3.render("-30 Pick an object!", True, red)
	Surface.blit(fbtext,(Screen[0]/2 - (fbtext.get_width()/2), Screen[1]/2))
	pygame.display.flip()
	pause(1300)
	Score -= 30

def Move(s_num, bl_num, t_num, pos_file):
	global player1, Score, Objects
	pn = 1
	for p in player1.points:
		xp = p[1]*sin(radians(player1.rot+p[0]))*player1.scale
		yp = p[1]*cos(radians(player1.rot+p[0]))*player1.scale
		player1.rotpoints[pn-1] = [int(player1.pos[0]+xp), int(player1.pos[1]+yp)]
		pn += 1
	player1.pos[0] += player1.speed[0] # *random.random() # noisy movement
	#player1.pos[1] += player1.speed[1] # no y movement
	for b in Bullets:
		b[0][0] += b[1][0]
		b[0][1] += b[1][1]
		b[2] += 1
		if b[2] == 1000:
			Bullets.remove(b);continue
	for a in Objects:
		#a.pos[0] += a.speed 
		a.pos[1] += a.speed
		if a.pos[1]>=Screen[1]:
			obj_off_bottom()
			Objects = []
	#if player1.speed[0]!=0: # write data only when moving
	try:
		pos_file.write(str(s_num)+'\t'+str(bl_num)+'\t'+str(t_num)+'\t'+str(player1.pos[0])+'\t'+str(Objects[0].pos[1])+'\t'+str(Objects[0].speed)+'\t'+str(pygame.time.get_ticks())+'\n')
	except IndexError:
		pass

def GetInput(s_num, bl_num, t_num, key_file):
	key = ''
	keystate = pygame.key.get_pressed()
	for event in pygame.event.get():
		if event.type == QUIT or (pygame.key.get_pressed()[pygame.K_LCTRL] and pygame.key.get_pressed()[pygame.K_BACKQUOTE]):
			pygame.quit(); sys.exit()
	if keystate[K_LEFT]:
		#player1.speed[0] -= player1.thrust # was .rot (turning)
		player1.pos[0] -= THRUST
		time = pygame.time.get_ticks()
		key = 'left'
	if keystate[K_RIGHT]:
		#player1.speed[0] += player1.thrust # was rotation -- could be .pos[0]
		player1.pos[0] += THRUST
		time = pygame.time.get_ticks()
		key = 'right'
		if player1.thrust_append == 0:
			player1.thrust_append = 0
			angle = (-player1.rot-90)+((random.random()*12.0)-6.0)
			speed = 1 #0.5*(2*random.random()+1.0)
			PosB = [(6*cos(radians(angle))),(6*sin(radians(angle)))]
			PosB[0] += player1.pos[0]
			PosB[1] += player1.pos[1]
			Speed = [speed*cos(radians(angle)),speed*sin(radians(angle))]
	#if keystate[K_UP] or keystate[K_RETURN]:
	#	FireBullet()
	#	time = pygame.time.get_ticks()
	#	key = 'shoot'
	if key!='':
		key_file.write(str(s_num)+'\t'+str(bl_num)+'\t'+str(t_num)+'\t'+ key +'\t'+str(time)+'\n')
	#player1.speed[0] *= SLOWING # maybe .97?
	#player1.speed[1] *= 0.98
	player1.speed[0] = 0
	

def Draw():
	Surface.fill((0,0,0))
	pygame.draw.polygon(Surface,white,player1.rotpoints)
	pygame.draw.aalines(Surface,white,True,player1.rotpoints,True)
	for a in Objects:
		a.draw()
	ScoreText = Font.render("Score: "+str(Score), True, (255,255,255))
	Surface.blit(ScoreText,(10,20))
	#FPSText = Font.render("FPS: "+str(round(clock.get_fps(),1)), True, (255,255,255))
	#Surface.blit(FPSText,(Screen[0]-120,Screen[1]-10-12))
	for b in Bullets:
		Surface.set_at((int(b[0][0]),int(b[0][1])),(200,200,255))
	pygame.display.flip()

def DisplayText(sText, clrText=white, nFontSize=font_size, nCharPerRow=57):
	sSegText = wrap(sText, nCharPerRow)
	iVLoc = (Screen[1] / 2) - nFontSize * len(sSegText)/2
	for sLine in sSegText:
		Text = Font3.render(sLine, True, clrText)
		Surface.blit(Text,((Screen[0]/2.0)-(Text.get_width()/2.0),iVLoc))
		iVLoc += nFontSize
	pygame.display.flip()

def pause4space():
	pygame.event.clear()
	Text = Font3.render('Press the SPACE BAR to continue.', True, (255,255,255))
	Surface.blit(Text,((Screen[0]/2.0)-(Text.get_width()/2.0),Screen[1]-40))
	#pygame.display.flip()
	while 1:
		event = pygame.event.poll()
		if pygame.key.get_pressed()[pygame.K_SPACE]:
			break
		if pygame.key.get_pressed()[pygame.K_LCTRL] and pygame.key.get_pressed()[pygame.K_BACKQUOTE]:
			pygame.quit()
			sys.exit()    

class Trial:
	def __init__(self, index, obj1, obj2, foil_type):
		self.index = index
		self.obj1 = obj1
		self.obj2 = obj2
		self.foil_type = foil_type
		self.dist = 250 #random.randint(150, Screen[1]/2 - 40) # objs dist from top of screen | (not diag) [100, 235]
		self.sep = 200 #random.randint(120, Screen[1]/2 - 20) # horiz sep: [70, 255]
	def update(self):
		self.obj1.pos = [int(player1.pos[0]-self.sep/2 - 35), player1.pos[1]-self.dist - 35] # upper left
		self.obj2.pos = [int(player1.pos[0]+self.sep/2 - 35), player1.pos[1]-self.dist - 35] # upper right
	def __repr__(self):
		# 'Trial  Obj1Value Obj2Value Distance Separation DropSpeed FoilType'
		return str(self.index)+'\t'+str(self.obj1.value)+'\t'+str(self.obj2.value)+'\t'+str(self.dist)+'\t'+str(self.sep)+'\t'+str(self.obj1.speed)+'\t'+self.foil_type

def blank_screen(delay=500):
	Surface.fill(black)
	pygame.display.flip()
	pause(delay)

def disp_seq_study(study, study_time, reps=1, shuffle=False):
	blank_screen()
	mid = [Screen[0]/2.0, Screen[1]/2.0]
	t_per_item = int(study_time/(len(study)*reps))
	txt_pos = (mid[0]+50, mid[1]+50)
	for r in range(reps): # repeat whole list
		for i in range(len(study)):
			#obj = copy.deepcopy(study[i])
			obj = study[i]
			obj.pos = mid
			obj.draw()
			if obj.value<0:
				colr = red
				text = str(obj.value)
			else:
				colr = green
				text = "+"+str(obj.value)
			fbtext = Font3.render(text, True, white) # colr
			Surface.blit(fbtext,txt_pos)
			pygame.display.flip()
			pause(t_per_item)
			
			blank_screen(250)
			pygame.display.flip() # windows
			blank_screen(250)
		if shuffle:
			random.shuffle(study)

def beginning_instruct():
	p = "Thank you for participating in this experiment!\n\nThis experiment consists of several short blocks.  In each block, you will be asked to remember a set of alien microbes.  These microbes can be identified by their shape.  You will always see these microbes in a standard orientation, so you can directly compare their shapes.\n\nThe microbes also have point values, reflecting how harmful or beneficial they are.  After studying several microbes, you will be asked to choose the most beneficial of a pair of microbes.  The goal is to get as many points as you can, so you should try to remember both the microbes and their point values.\n\nNo microbe will be appear in more than one block, so you do not need to remember any microbes from previous blocks--only those from the current block.\n\nPress the space bar to continue."
	DisplayText(p)
	pygame.display.update() # windows
	pause(8000)
	pause4space()
	Surface.fill(black)
	blank_screen(200)

def study_instruct():
	p = "You will now be shown several microbes and their point values, one at a time.  Try your best to remember the shape of each microbe, as well as its point value.\n\nPress the space bar to continue."
	DisplayText(p)
	pygame.display.update() # windows
	pause(4000)
	pause4space()
	Surface.fill(black)
	blank_screen(200)

def test_instruct():
	p = "Now, you'll need to rely on your memory of the microbes you just saw.  You will see two microbes moving down from the top of the screen.  One microbe will be one you just studied, the other will be new.  The new one is worth zero points (it is neither harmful nor beneficial).  Try to catch the microbe that is worth the most points by using the left and right arrow keys to move your cursor beneath the microbe you want to choose.  Note that the old microbe might be harmful (negative points), in which case you should try to pick the new (neutral) microbe.  Please do your best!\n\nPress the space bar to continue."
	DisplayText(p)
	pygame.display.update() # windows
	pause(8000)
	pause4space()
	Surface.fill(black)
	blank_screen(200)

def get_block_stimuli(num_cats, valence, totExemps=8):
	targets = []
	foils = []
	half = totExemps/2
	if num_cats==0:
		for i in range(totExemps):
			targets.append(make_blobs.makeCategories(1,1)[0][0])
			foils.append(make_blobs.makeCategories(1,1)[0][0])
		foil_types = ["unique"]*totExemps
	elif num_cats==1:
		same = make_blobs.makeCategories(1,totExemps+half)[0] # nCat, nExemplars
		targets = same[:totExemps]
		foils = same[totExemps:]
		for i in range(half):
			foils.append(make_blobs.makeCategories(1,1)[0][0])
		foil_types = ["similar"]*half + ["unique"]*half
	elif num_cats==2 and valence=="pos":
		cats = make_blobs.makeCategories(2,totExemps)
		targets = cats[0][:half] + cats[1][:half]
		unique = make_blobs.makeCategories(2,1)
		foils = cats[0][half:half+2] + cats[1][half:half+1] + unique[0] + cats[1][half+1:half+2] + cats[0][half+2:] + unique[1]
		foil_types = ["similar"]*2 + ["other"] + ["unique"] + ["similar"] + ["other"]*2 + ["unique"]
	elif num_cats==2 and valence=="mixed":
		cats = make_blobs.makeCategories(2,totExemps)
		targets = cats[0][:half] + cats[1][:half]
		foils = cats[0][half:half+2] + cats[1][half:half+2] + cats[0][half+2:] + cats[1][half+2:]
		foil_types = ["same"]*2 + ["other"]*2 + ["same"]*2 + ["other"]*2
	if len(targets)+len(foils)+len(foil_types)!=3*totExemps:
		print "Wrong number of targs or foils or foil_types in get_block_stimuli!!"
	return targets, foils, foil_types

def create_blocks(blocks_per_cond=4):
	blocks = []
	pos = [10]
	neg = [-10]
	for i in range(blocks_per_cond): # 4 blocks of no structure (all pos)
		targets, foils, foil_types = get_block_stimuli(0, "pos") # numcats, valence distro
		blocks.append(Block(0, "pos", targets, foils, foil_types, pos*8))
	for i in range(blocks_per_cond): # 8 same cat, 1 valence -> 4 cat / 4 novel
		targets, foils, foil_types = get_block_stimuli(1, "pos")
		blocks.append(Block(1, "pos", targets, foils, foil_types, pos*8))
	for i in range(blocks_per_cond): # 8 same cat, 2 valence -> 4 similar / 4 novel
		targets, foils, foil_types = get_block_stimuli(1, "mixed")
		vals = pos*2 + neg*2 + pos*2 + neg*2 # 2 neg, 2 pos for sim foils and unique foils
		blocks.append(Block(1, "mixed", targets, foils, foil_types, vals))
	for i in range(blocks_per_cond): # 8 2 cat, same valence -> 3 same / 3 diff / 2 novel 
		targets, foils, foil_types = get_block_stimuli(2, "pos")
		blocks.append(Block(2, "pos", targets, foils, foil_types, pos*8))
	for i in range(blocks_per_cond): # 4 pos cat, 4 neg cat -> 2 same, 2 diff / 2 same, 2 diff
		targets, foils, foil_types = get_block_stimuli(2, "pos")
		vals = pos*4 + neg*4
		blocks.append(Block(2, "mixed", targets, foils, foil_types, vals))
	bl1 = blocks[0]
	blocks = blocks[1:]
	random.shuffle(blocks)
	blocks = [bl1] + blocks
	for i,b in enumerate(blocks):
		b.index = i+1
	print str(len(blocks))+" blocks created"
	return blocks

class Block:
	def __init__(self, ncats, valence, targets, foils, foil_types, vals, reps_per_obj=1, study_time=4000, feedback=1, study_type='seq'):
		self.targets = []
		self.ncats = ncats
		self.valence = valence
		self.study_type = study_type
		self.study_time = study_time
		self.index = -1
		self.vals = vals
		self.reps_per_obj = reps_per_obj
		self.feedback = feedback # feedback at test
		self.trials = self.make_trials(targets, foils, foil_types, vals)
	
	def make_trials(self, targets, foils, foil_types, vals):
		trials = []
		for i in range(len(targets)):
			target = Object(targets[i], vals[i])
			foil = Object(foils[i], 0)
			objs = [target, foil]
			random.shuffle(objs)
			trials.append(Trial(i+1, objs[0], objs[1], foil_types[i]))
			self.targets.append(target)
		random.shuffle(trials)
		for i,tr in enumerate(trials):
			tr.index = i+1
		return(trials)
	
	def __repr__(self):
		# 'Block Ncats Valence StudyTime StudyType'
		return str(self.index)+'\t'+str(self.ncats)+'\t'+self.valence+'\t'+str(self.study_time)+'\t'+self.study_type


def main():
	s_num, logFile, pos_file, key_file = subject_info(random.randint(10000, 99999))
	
	pygame.mouse.set_pos(Screen)
	pygame.mouse.set_visible(0)
	global Objects
	feedback = True
	study_time = 32000 # total
	
	blocks = create_blocks(4) # change to 4 for actual running!
	
	beginning_instruct()
	
	for bl in range(len(blocks)):
		Objects = []
		
		blank_screen(500)
		study_instruct()
		
		disp_seq_study(blocks[bl].targets, study_time=study_time, reps=1)
		
		blank_screen(1000)
		test_instruct()
		
		for tr in blocks[bl].trials:
			tr.update()
			NewLevel()
			Objects = [tr.obj1, tr.obj2]
			#print Objects[0].pos
			t0 = pygame.time.get_ticks()
			stscor = Score # 0? (or cumulative?)
			while len(Objects)>1:
				GetInput(s_num, bl, tr.index, key_file)
				Move(s_num, bl, tr.index, pos_file)
				CollisionDetect(feedback)
				Draw()
				clock.tick(30)
			tot_t = pygame.time.get_ticks() - t0 - 1300 # subtract feedback delay...
			# 'Subject\tTrial\tLObjVal\tRObjVal\tDist\tSeparation\tSpeed\tScoreChange\tStartTime\tDuration\n'
			line = str(s_num)+'\t'+str(blocks[bl])+'\t'+str(tr)+'\t'+str(Score-stscor)+'\t'+str(t0)+'\t'+str(tot_t)+'\n'
			logFile.write(line)
			#pause4space()
			pause(1500)
			#blank_screen(500)
			player1.pos = [Screen[0]/2.0,Screen[1]-80]
			player1.speed = [0,0]
	blank_screen(200)
	goodbye(logFile)

if __name__ == '__main__': main()
