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

import config

bot = Bot(max_likes_per_day=config.MAX_LIKES_PER_DAY,
			max_unlikes_per_day=config.MAX_UNLIKES_PER_DAY,
			max_follows_per_day=config.MAX_FOLLOWS_PER_DAY,
			max_unfollows_per_day=config.MAX_UNFOLLOWS_PER_DAY,
			min_followers_to_follow=config.MIN_FOLLOWERS_TO_FOLLOW,
			min_media_count_to_follow=config.MIN_MEDIA_COUNT_TO_FOLLOW,
			max_following_to_block=config.MAX_FOLLOWING_TO_BLOCK)
bot.login(username=config.USERNAME)
bot.logger.info("Herba account 24/7!")

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
	
def likeNFollow_hashtag(hashtags, amount=3):
	medias = bot.get_total_hashtag_media(hashtags, amount, true)
	bot.like_medias(medias)
	
	for media in medias:
		userid = bot.get_media_owner(media)
		bot.follow(userid)
	
def like_timeline():
	# max timeline like divided by max occurences in one day
	# timeline like = max like * timeline percent
	# max occurences : from 7H to 00H = 17
	maxLike = bot.max_per_day['likes'] * config.TIMELINE_LIKE_RATIO
	maxRoundLike = maxLike // 17
	bot.logger.info("Max timeline like: " + str(maxLike))
	bot.logger.info("Max timeline round like: " + str(maxRoundLike))
	bot.like_timeline(amount=maxRoundLike)

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
schedule.every(2).to(4).days.at("10:50").do(run_threaded, block_bots)	
schedule.every(2).to(3).days.at("07:45").do(run_threaded, unfollow_non_followers)	
schedule.every(1).to(3).hours.do(run_threaded, like_timeline)	

schedule.every().day.at("07:01").do(run_threaded, morning_hashtag)
schedule.every().day.at("13:00").do(run_threaded, noon_hashtag)
schedule.every().day.at("17:00").do(run_threaded, apero_hashtag)
schedule.every().day.at("22:00").do(run_threaded, nigth_hashtag)

while True:
	current_time = datetime.datetime.now()
	start_day = datetime.datetime(hour=7, minute=0, second=0, year=current_time.year, month=current_time.month, day=current_time.day)
	end_day = datetime.datetime(hour=23, minute=59, second=59, microsecond=999999, year=current_time.year, month=current_time.month, day=current_time.day)
	
	if start_day < current_time < end_day:
		schedule.run_pending()
		waittime = schedule.idle_seconds()
		bot.logger.info("Waiting for: " + str(waittime))
		time.sleep(waittime)
	else:
		newstart = start_day + datetime.timedelta(days=1)
		waittime = (newstart-current_time).total_seconds()
		bot.logger.info("Waiting tomorrow for: " + str(waittime))
		time.sleep(waittime)
	