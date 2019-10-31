import config
import numpy as np
import math
import os
import sys
from PIL import Image, ImageDraw, ImageOps, ImageFont
from experience_replay import load_replays

font = ImageFont.truetype("ariblk.ttf", 30)	
large_font = ImageFont.truetype("ariblk.ttf", 80)	

def draw_text(image, x, y, angle, text, shade, transparent, font):
	width, height = font.getsize(text)
	width = math.ceil(width)
	height = math.ceil(height)
	
	size = max(width, height)*2

	# Render text
	txt=Image.new('RGBA', (size, size), (0, 0, 0, 0))
	d = ImageDraw.Draw(txt)
	px = size/2-width/2
	py = size/2-3
	
	# Draw outline
	outline = (0, 0, 0, 255) # Black
	d.text((px-2, py), text, font=font, fill=outline)
	d.text((px-1, py-1), text, font=font, fill=outline)
	d.text((px, py-2), text, font=font, fill=outline)
	d.text((px+1, py+1), text, font=font, fill=outline)
	d.text((px+2, py), text, font=font, fill=outline)
	d.text((px-1, py+1), text, font=font, fill=outline)
	d.text((px, py+1), text, font=font, fill=outline)
	d.text((px+2, py-2), text, font=font, fill=outline)
	
	# Draw main text
	d.text((px, py), text, font=font, fill=(255, shade, shade, 255))
	
	w=txt.rotate(angle)
	
	if transparent:
		mask = w.copy()
		pixels = mask.load()
		for mx in range(size):
			for my in range(size):
				r, g, b, a = pixels[mx, my]
				pixels[mx, my] = (r, g, b, int(a/6))
	else:
		mask = w
	
	image.paste(w, box=(int(x-size/2), int(y-size/2)), mask=mask)

def get_option(opt, default):
	if opt in sys.argv and sys.argv.index(opt) < len(sys.argv) - 1:
		return int(sys.argv[sys.argv.index(opt)+1])
	else:
		return default
	
DrawEvery = get_option('--every', 12)
MaxKarts = get_option('--max', 1000000)

print('Drawing 1 in every {0} karts'.format(DrawEvery))

# Conversion table from in-game course IDs
Course = {
	7: 1,
	19: 2,
	16: 3,
	17: 4,
	15: 5,
}

Checkpoints = {
	1: 30,
	2: 37,
	3: 33,
	4: 35,
	5: 35,
}

def log(s):
	print(s)
	return

replay_buffer = load_replays(config.get_checkpoint_file('experience_replay'), log, 200 if '--test' in sys.argv else 1000000000)

# Merge replay_buffer into a single compact array of position data
compact = []
for replay in replay_buffer:
	screens = replay[0]
	if len(replay) < 5:
		print("Replay files don't include coordinate information. Make sure Emulator/track_position is set to 'true' in the config file.")
		exit()
	positions = replay[4]
	rewards = replay[2]

	# Extract the position data from each frame
	for frame in range(len(screens)):
		course = Course[np.argmax(screens[frame][225:245])]
		x, y, angle = positions[frame]
		reward = rewards[frame]
		
		x, y, angle = int(x), int(y), int(angle)
		compact.append((x, y, angle, course, reward))

# Free replay buffer RAM		
replay_buffer = None

# Draw every course
for course_filter in range(1, 6):
	start_indices = []

	# Find list of time stamps for the beginning of each course
	prevCourse = -1	
	for i in range(len(compact)):
		x, y, angle, course, reward = compact[i]
		
		if prevCourse != course_filter and course == course_filter:
			start_indices.append(i)
			
		prevCourse = course

	# Filter out unused runs
	start_indices = start_indices[::DrawEvery]
	start_indices = start_indices[:MaxKarts]
	
	# Create directory
	directory = config.get_checkpoint_file('multikart')
	if not os.path.exists(directory):
		os.makedirs(directory)
		
	checkpoints_per_lap = Checkpoints[course_filter]	
	total_reward = np.zeros(len(start_indices))
	lap = 1
	
	template = picFile = Image.open("./CoursePics/Course{0}.png".format(course_filter), "r")
		
	# Generate individual frames
	print('Generating images for course {0}...'.format(course_filter))
	for frame in range(config.get_steps_per_second() * config.get_seconds_per_course()):
		picFile = template.copy()
		picFile = picFile.convert()
		draw = ImageDraw.Draw(picFile)
		
		# Draw each kart
		kart_num = 1
		for i in range(len(start_indices)):
			start = start_indices[i]
			
			# Make sure we didn't run off the end of the list
			if start + frame >= len(compact):
				continue
				
			x, y, angle, course, reward = compact[start+frame]
			
			# Make sure it's still on the same course
			if course != course_filter:
				continue
				
			total_reward[i] += reward
			
			if total_reward[i] > lap * checkpoints_per_lap * 100:
				lap += 1

			x, y = int(x/4), int(y/4)
			shade = min(int(kart_num * 255 / len(start_indices)), 255)
			transparent = False if total_reward[i] > (lap - 1) * checkpoints_per_lap * 100 else True
			#draw.ellipse((x-10, y-10, x+10, y+10), fill=(int(shade/2), int(shade/2), int(shade)), outline='black')
			draw_text(picFile, x, y, -angle * 360 / 256, str(kart_num), shade, transparent, font)
			kart_num += 1

		lap_text = 'Lap {0}'.format(lap)
		draw_text(picFile, 512, 0, 0, lap_text, 255, False, large_font)
			
		picFile.save(config.get_checkpoint_file(config.get_checkpoint_file('multikart\\{0:04}.png'.format(frame))))

	# Run ffmpeg to create the video file
	cwd = os.getcwd()
	os.chdir(config.get_checkpoint_dir())
	os.system('ffmpeg -start_number 0 -i .\multikart\%04d.png -c:v libx264 -r 30 -pix_fmt yuv420p multikart_course{0}.mp4 -y'.format(course_filter))
	print('Finished writing {0}\\multikart_course{1}.mp4'.format(os.getcwd(), course_filter))
	os.chdir(cwd)
