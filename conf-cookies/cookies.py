# -*- coding: utf-8 -*-

from glob import glob
import os
import sys
import threading
import time
import datetime
import functools

# sys.path.append(os.path.join(sys.path[0], '../../'))
import schedule
from instabot import Bot
from random import randint
from tqdm import tqdm

import config
import signal
import sys

bot = Bot(max_likes_per_day=config.MAX_LIKES_PER_DAY,
			max_unlikes_per_day=config.MAX_UNLIKES_PER_DAY,
			max_follows_per_day=config.MAX_FOLLOWS_PER_DAY,
			max_unfollows_per_day=config.MAX_UNFOLLOWS_PER_DAY,
			min_followers_to_follow=config.MIN_FOLLOWERS_TO_FOLLOW,
			min_media_count_to_follow=config.MIN_MEDIA_COUNT_TO_FOLLOW,
			max_following_to_block=config.MAX_FOLLOWING_TO_BLOCK)
bot.login(username=config.USERNAME)
bot.logger.info("Cookies account 24/7!")

# ==== Startup specials ====

# ==== Convert from friends to whitelist ids in a proper way ====
if not os.path.isfile("whitelist_cached.txt"):
	open("whitelist_cached.txt", 'a').close()

whitelist = []
reject = []
whitelist_cache = {}
with open("whitelist_cached.txt", "r") as f:
	for line in f:
		(key, val) = line.rstrip().split("|")
		whitelist_cache[key] = val
		
whitelist_to_del = []		
for id, value in whitelist_cache.items():
	if value == "None":
		whitelist_to_del.append(id)

for to_del in whitelist_to_del:		
	del whitelist_cache[to_del]
	 
friends = bot.read_list_from_file("friends.txt")
for friend in tqdm(friends):
	if friend not in whitelist_cache:
		user_id = bot.get_user_id_from_username(friend)
		if user_id is not None:
			whitelist_cache[friend] = user_id
		else:
			reject.append(friend)
		bot.small_delay()
	
	# in all case append to whitelist
	if friend in whitelist_cache:
		whitelist.append(whitelist_cache[friend])

# Write cache
with open('whitelist_cached.txt', 'w') as file:  # rewrite file
	for id, value in whitelist_cache.items():
		file.write(id + "|" + str(value) + "\n")
		
with open('whitelist.txt', 'w') as file:  # rewrite file
	for value in whitelist:
		file.write(value + "\n")
		
with open('reject.txt', 'w') as file:  # reject file
	for value in reject:
		file.write(value + "\n")
		
		
# ==== Unban and follow whitelist ====
#users_to_follow = bot.whitelist
#your_following = bot.following
#rest_users = list(set(users_to_follow) - set(your_following))
#print("Found %d users in file." % len(rest_users))
#bot.follow_users(rest_users)

#exit(18)

def signal_handler(sig, frame):
	bot.logout()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# This decorator can be applied to
def with_wait(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		# Random wait of 0-120 minutes
		rndWait = randint(0, 120)
		bot.logger.info(func.__name__ + " in " + str(rndWait) + " minutes.")
		time.sleep(rndWait*60)
		result = func(*args, **kwargs)
		return result
	return wrapper
	
def likeNFollow_hashtag(hashtags, namount=3):
	for hashtag in hashtags:
		medias = bot.get_total_hashtag_medias(hashtag, amount=namount, filtration=True)
		bot.like_medias(medias)
		
		for media in medias:
			userid = bot.get_media_owner(media)
			bot.follow(userid)
	
def like_timeline():
	# max timeline like divided by max occurences in one day
	# timeline like = max like * timeline percent
	# max occurences : from 7H to 00H = 17
	maxLike = int(bot.max_per_day['likes'] * config.TIMELINE_LIKE_RATIO)
	maxRoundLike = int(maxLike // 17)
	bot.logger.info("Max timeline like: " + str(maxLike))
	bot.logger.info("Max timeline round like: " + str(maxRoundLike))
	bot.like_timeline(amount=maxRoundLike)

@with_wait
def likeNFollow_media_likers():	
	medias = bot.get_user_medias(config.USERNAME, filtration=False)
	if len(medias):
		likers = bot.get_media_likers(medias[0])
		for liker in tqdm(likers):
			bot.like_user(liker, amount=3)
			bot.follow(liker)
	
@with_wait
def unfollow_non_followers():
	bot.unfollow_non_followers()

@with_wait
def block_bots():
	bot.block_bots()

@with_wait
def morning_hashtag():
	random_hashtag_file = bot.read_list_from_file(config.HASHTAGS_07H)
	random_hashtag_file = random_hashtag_file[:config.NB_HASHTAGS_07H]
	
	likeNFollow_hashtag(random_hashtag_file, config.NB_HASHTAGS_LIKENFOL_07H)
		
@with_wait
def noon_hashtag():
	random_hashtag_file = bot.read_list_from_file(config.HASHTAGS_13H)
	random_hashtag_file = random_hashtag_file[:config.NB_HASHTAGS_13H]
	
	likeNFollow_hashtag(random_hashtag_file, config.NB_HASHTAGS_LIKENFOL_13H)
		
@with_wait
def apero_hashtag():
	random_hashtag_file = bot.read_list_from_file(config.HASHTAGS_17H)
	random_hashtag_file = random_hashtag_file[:config.NB_HASHTAGS_17H]
	
	likeNFollow_hashtag(random_hashtag_file, config.NB_HASHTAGS_LIKENFOL_17H)
		
@with_wait
def nigth_hashtag():
	random_hashtag_file = bot.read_list_from_file(config.HASHTAGS_22H)
	random_hashtag_file = random_hashtag_file[:config.NB_HASHTAGS_22H]
	
	likeNFollow_hashtag(random_hashtag_file, config.NB_HASHTAGS_LIKENFOL_22H)
				
def stats():
	bot.logger.info("Saving stats")
	bot.save_user_stats(bot.user_id)

def run_threaded(job_fn):
	job_thread = threading.Thread(target=job_fn)
	job_thread.start()	
	
schedule.every(1).hours.do(run_threaded, stats)	
#schedule.every(2).to(4).days.at("10:20").do(run_threaded, block_bots)	
schedule.every(2).to(3).days.at("07:15").do(run_threaded, unfollow_non_followers)	
schedule.every(1).to(3).hours.do(run_threaded, like_timeline)	


schedule.every().day.at("07:21").do(run_threaded, likeNFollow_media_likers)
schedule.every().day.at("13:50").do(run_threaded, likeNFollow_media_likers)
schedule.every().day.at("17:10").do(run_threaded, likeNFollow_media_likers)
schedule.every().day.at("21:20").do(run_threaded, likeNFollow_media_likers)

schedule.every().day.at("08:01").do(run_threaded, morning_hashtag)
schedule.every().day.at("12:00").do(run_threaded, noon_hashtag)
schedule.every().day.at("16:00").do(run_threaded, apero_hashtag)
schedule.every().day.at("20:00").do(run_threaded, nigth_hashtag)

while True:
	current_time = datetime.datetime.now()
	start_day = datetime.datetime(hour=7, minute=0, second=0, year=current_time.year, month=current_time.month, day=current_time.day)
	end_day = datetime.datetime(hour=23, minute=59, second=59, microsecond=999999, year=current_time.year, month=current_time.month, day=current_time.day)
	
	if start_day < current_time < end_day:
		schedule.run_pending()
		waittime = schedule.idle_seconds()
		waittime = waittime if waittime > 0 else 0
		bot.logger.info("Waiting for: " + str(waittime))
		time.sleep(waittime)
	else:
		if current_time < start_day:
			newstart = start_day
		else:
			newstart = start_day + datetime.timedelta(days=1)
		waittime = (newstart-current_time).total_seconds()
		waittime = waittime if waittime > 0 else 0
		if waittime > 86400:
			bot.logger.warn("New day calc error! ")

		bot.logger.info("Waiting tomorrow for: " + str(waittime))
		time.sleep(waittime)
	