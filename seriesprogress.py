import xml.etree.ElementTree as etree
import urllib2
import time
import config


def wait_one_second(start_time):
	'''Called to ensure time between API calls is one second or greater.'''
	end_time = time.time()
	while (end_time - start_time < 1):
		end_time = time.time()

user_id = raw_input("Please enter a Goodreads ID: ")
API_KEY = config.API_KEY
url = "https://www.goodreads.com/review/list.xml?v=2&id=%s&shelf=read&per_page=40&sort=date_read&key=%s" % (user_id, API_KEY)
read_shelf = etree.parse(urllib2.urlopen(url)).getroot() # XML for read shelf of user
number_of_reviews = int(read_shelf[1].attrib['end']) - int(read_shelf[1].attrib['start']) + 1
book_ids = list() # list of book ids on shelf
for i in range(number_of_reviews):
	id = read_shelf[1][i][1][0].text # reviews->review->book->id
	title = read_shelf[1][i][1][4].text # reviews->review->book->title
	print id.encode('utf-8'), title.encode('utf-8') # encode prevents UnicodeEncodeError (?) with foreign characters
	book_ids.append(id)

series_ids = {} # dictionary of series ids - key is numeric id, corresponds to number of read books in series
series_id_set = set() # set of series ids used to determine if a series is already in series_ids
for i in range(len(book_ids)):
	start_time = time.time()
	url = "https://www.goodreads.com/book/show.xml?id=%s&key=%s" % (book_ids[i], API_KEY)
	book = etree.parse(urllib2.urlopen(url)).getroot() # XML for book in book_ids
	try:
		series_id = book[1][27][0][2][0].text # book->series_works->series_work->series->title (only gets first series)
		user_position = book[1][27][0][1].text # series_work->user_position (numerical place of work in series)
		number_of_books = 1 # default number of books
		if user_position is not None:
			if '-' in user_position: # if book is multiple books e.g. 1-3
				dash_position = user_position.find('-')
				start_position = ""
				for i in range(dash_position): # start position is everything before dash
					start_position += user_position[i] 
				end_position = ""
				remaining_length = len(user_position) - dash_position - 1 # remaining characters past dash
				for i in range(remaining_length): # end position is everything after dash
					end_position += user_position[i + dash_position + 1]
				number_of_books = int(end_position) - int(start_position) + 1
		print series_id
		if (series_id in series_ids): # if id already in series_ids, add number_of_books to value
			series_ids[series_id] += number_of_books
		else: # otherwise value is number_of_books
			series_ids[series_id] = number_of_books
	except IndexError: # if there are no series
		print "No series"
	wait_one_second(start_time)
	
for id in series_ids:
	start_time = time.time()
	url = "https://www.goodreads.com/series/show/%s.xml?key=%s" % (id, API_KEY)
	series = etree.parse(urllib2.urlopen(url)).getroot() # XML for series in series_ids
	series_title = series[1][1].text # series->title
	series_number_of_works = series[1][5].text # series->primary_work_count
	print series_title.encode('utf-8'), str(series_ids[id]), "/", series_number_of_works # e.g. The Lord of the Rings 2/3
	wait_one_second(start_time)

