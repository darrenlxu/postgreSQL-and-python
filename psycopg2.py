
# ****************************************************************************************************************************************

import sys
import psycopg2

# define any local helper functions here

# set up some globals

usage = "Usage: q1.py [N]"
db = None

# process command-line args

argc = len(sys.argv)

# manipulate database

try:
	db = psycopg2.connect("dbname=imdb")
	cursor = db.cursor()

	query = """select count(CR.movie_id) as cnt, N.name as name from Crew_Roles CR join Names N on (CR.name_id = N.id) where CR.role = 'director' group by N.name order by cnt desc, name limit %s"""
	
	# when N is not specified, defaults to N = 10
	if argc == 1:
		cursor.execute(query, [str(10)])
		for tuple in cursor.fetchall():
			cnt, name = tuple
			result = "{} {}".format(cnt, name)
			print(result)

	# when N is specified 
	elif argc == 2:
		# when N is not numeric or N <= 0
		if sys.argv[1].isnumeric() == False or int(sys.argv[1]) <= 0:
			print(usage)

		# when N is numeric or N > 0
		elif sys.argv[1].isnumeric() == True or int(sys.argv[1]) > 0:
			cursor.execute(query, [sys.argv[1]])
			for tuple in cursor.fetchall():
				cnt, name = tuple
				result = "{} {}".format(cnt, name)
				print(result)

		# all other erroneous cases will return usage
		else:
			print(usage)

	# when the number of command-line arguments isn't 1 nor 2 
	else:
		print(usage)

except psycopg2.Error as err:
	print("DB error: ", err)
finally:
	if db:
		db.close()

# ****************************************************************************************************************************************

import sys
import psycopg2

# define any local helper functions here

# set up some globals

usage = "Usage: q2.py 'PartialMovieTitle'"
db = None

# process command-line args

argc = len(sys.argv)

# manipulate database

try:
    db = psycopg2.connect("dbname=imdb")
    cursor = db.cursor()

    # when no partial/whole movie name or pattern is supplied
    if argc == 1:
        print(usage)

    # when a partial/whole movie name or pattern is supplied (includes non-matching name/patterns)
    elif argc == 2: 

        query = """select rating, title, start_year, id from Movies where title ilike %s group by rating, title, start_year, id order by rating desc, start_year, title"""

        cursor.execute(query, ["%" + sys.argv[1] + "%"])
        num_of_rows = len(cursor.fetchall())

        # when the partial-name matches to exactly one movie
        if num_of_rows == 1:
            cursor.execute(query, ["%" + sys.argv[1] + "%"])
            for tuple in cursor.fetchall():
                rating, title, start_year, id = tuple
                result = "{} ({})".format(title, start_year)

                query1 = """select A.local_title, A.region, A.language, A.extra_info from Aliases A join Movies M on (A.movie_id = M.id) where M.id = %s group by A.local_title, A.region, A.language, A.ordering, A.extra_info order by A.ordering"""

                cursor.execute(query1, [id])
                alias_num_of_rows = len(cursor.fetchall())
                
                if alias_num_of_rows > 0:
                    print(result + " was also released as")
                else:
                    print(sys.argv[1] + " (" + str(start_year) + ") has no alternative releases")

            query2 = """select A.local_title, A.region, A.language, A.extra_info from Aliases A join Movies M on (A.movie_id = M.id) where M.id = %s group by A.local_title, A.region, A.language, A.ordering, A.extra_info order by A.ordering"""
            
            cursor.execute(query2, [id])
            for tuple in cursor.fetchall():
                local_title, region, language, extra_info = tuple
                if region is None and language is None:
                    result = "'{}' ({})".format(local_title, extra_info)
                elif region is not None and language is None:
                    region = region.rstrip()
                    result = "'{}' (region: {})".format(local_title, region)
                elif region is None and language is not None:
                    language = language.rstrip()
                    result = "'{}' (language: {})".format(local_title, language)
                elif region is None and language is None and extra_info is None:
                    result = "'{}'".format(local_title)
                else:
                    region = region.rstrip()
                    language = language.rstrip()
                    result = "'{}' (region: {}, language: {})".format(local_title, region, language)
                print(result)

        # when the partial-name matches to multiple movies
        elif num_of_rows > 1:
            cursor.execute(query, ["%" + sys.argv[1] + "%"])
            print("Movies matching " + "'" + sys.argv[1] + "'")
            print("===============")
            for tuple in cursor.fetchall():
                rating, title, start_year, id = tuple 
                result = "{} {} ({})".format(rating, title, start_year)
                print(result)
        
        # when the partial-name does not match to any movie/s
        elif num_of_rows == 0:
            cursor.execute(query, ["%" + sys.argv[1] + "%"])
            print("No movie matching " + "'" + sys.argv[1] + "'")

        # all other erroneous cases will return usage
        else:
            print(usage)

    # when the number of command-line arguments isn't 1 nor 2 
    else:
        print(usage)
        
except psycopg2.Error as err:
	print("DB error: ", err)
finally:
	if db:
		db.close()

# ****************************************************************************************************************************************

import sys
import psycopg2

# define any local helper functions here

# set up some globals

usage = "Usage: q3.py 'MovieTitlePattern' [Year]"
db = None

# process command-line args

argc = len(sys.argv)

# manipulate database

try:
	db = psycopg2.connect("dbname=imdb")
	cursor = db.cursor()
	
	# when no partial/whole movie name or pattern is supplied
	if argc == 1:
		print(usage)

	# when a partial/whole movie name or pattern is supplied (includes non-matching name/patterns) - optional year is not supplied
	elif argc == 2:
		
		first = "^"
		last = "$"
		if first in sys.argv[1] and last in sys.argv[1]:
			sys.argv[1] = sys.argv[1][1:len(sys.argv[1]) - 1] 

		query = """select rating, title, start_year, id from Movies where title ilike %s group by rating, title, start_year, id order by rating desc, start_year, title"""

		cursor.execute(query, ["%" + sys.argv[1] + "%"])
		num_of_rows = len(cursor.fetchall())

		if num_of_rows == 0:
			print("No movie matching " + "'" + sys.argv[1] + "'")

		elif num_of_rows == 1:
			cursor.execute(query, ["%" + sys.argv[1] + "%"])
			for tuple in cursor.fetchall():
				rating, title, start_year, id = tuple
				print(str(title) + " (" + str(start_year) + ")")
				print("===============")

			query1 = """select N.name, AR.played from Acting_Roles AR join Names N on (AR.name_id = N.id) join Movies M on (AR.movie_id = M.id) join Principals P on (AR.movie_id = P.movie_id and AR.name_id = P.name_id) where M.title ilike %s group by N.name, AR.played, P.ordering order by P.ordering"""

			cursor.execute(query1, ["%" + sys.argv[1] + "%"])
			print("Starring")
			for tuple in cursor.fetchall():
				name, played = tuple 
				result = " {} as {}".format(name, played)
				print(result)

			query2 = """select N.name, CR.role from Crew_Roles CR join Names N on (CR.name_id = N.id) join Movies M on (CR.movie_id = M.id) join Principals P on (CR.movie_id = P.movie_id and CR.name_id = P.name_id) where M.title ilike %s group by N.name, CR.role, P.ordering order by P.ordering"""		

			cursor.execute(query2, ["%" + sys.argv[1] + "%"])
			print("and with")
			for tuple in cursor.fetchall():
				name, role = tuple 
				role = role.capitalize()
				result = " {}: {}".format(name, role)
				print(result)

		elif num_of_rows > 1:
			cursor.execute(query, ["%" + sys.argv[1] + "%"])
			print("Movies matching " + "'" + sys.argv[1] + "'")
			print("===============")
			for tuple in cursor.fetchall():
				rating, title, start_year, id = tuple
				result = "{} {} ({})".format(rating, title, start_year)
				print(result)

	# when a partial/whole movie name or pattern is supplied (includes non-matching name/patterns) - optional year is supplied and input is numeric
	elif argc == 3 and sys.argv[2].isnumeric() == True:
		first = "^"
		last = "$"
		if first in sys.argv[1] and last in sys.argv[1]:
			sys.argv[1] = sys.argv[1][1:len(sys.argv[1]) - 1] 

			query0 = """select rating, title, start_year, id from Movies where title = %s and start_year = %s group by rating, title, start_year, id order by rating desc, start_year, title"""
			
			cursor.execute(query0, [sys.argv[1], sys.argv[2]])
			for tuple in cursor.fetchall():
				rating, title, start_year, id = tuple 
				print(str(title) + " (" + str(start_year) + ")")
				print("===============")
			
			query00 = """select N.name, AR.played from Acting_Roles AR join Names N on (AR.name_id = N.id) join Movies M on (AR.movie_id = M.id) join Principals P on (AR.movie_id = P.movie_id and AR.name_id = P.name_id) where M.title = %s and M.start_year = %s group by N.name, AR.played, P.ordering order by P.ordering"""

			cursor.execute(query00, [sys.argv[1], sys.argv[2]])
			print("Starring")
			for tuple in cursor.fetchall():
				name, played = tuple 
				result = " {} as {}".format(name, played)
				print(result)

			query000 = """select N.name, CR.role from Crew_Roles CR join Names N on (CR.name_id = N.id) join Movies M on (CR.movie_id = M.id) join Principals P on (CR.movie_id = P.movie_id and CR.name_id = P.name_id) where M.title = %s and M.start_year = %s group by N.name, CR.role, P.ordering order by P.ordering"""		
			
			cursor.execute(query000, [sys.argv[1], sys.argv[2]])
			print("and with")
			for tuple in cursor.fetchall():
					name, role = tuple 
					role = role.capitalize()
					result = " {}: {}".format(name, role)
					print(result)

		else:
			query3 = """select rating, title, start_year, id from Movies where title ilike %s and start_year = %s group by rating, title, start_year, id order by rating desc, start_year, title"""
			_title = "%" + sys.argv[1] + "%"
			_year = sys.argv[2]
			cursor.execute(query3, [_title, _year])
			num_of_rows = len(cursor.fetchall()) 		

			if num_of_rows == 0:
				print("No movie matching " + "'" + sys.argv[1] + "' " + sys.argv[2])

			elif num_of_rows == 1:
				cursor.execute(query3, [_title, _year])
				for tuple in cursor.fetchall():
					rating, title, start_year, id = tuple 
					print(str(title) + " (" + str(start_year) + ")")
					print("===============")

				query4 = """select N.name, AR.played from Acting_Roles AR join Names N on (AR.name_id = N.id) join Movies M on (AR.movie_id = M.id) join Principals P on (AR.movie_id = P.movie_id and AR.name_id = P.name_id) where M.title ilike %s and M.start_year = %s group by N.name, AR.played, P.ordering order by P.ordering"""

				cursor.execute(query4, [_title, _year])
				print("Starring")
				for tuple in cursor.fetchall():
					name, played = tuple 
					result = " {} as {}".format(name, played)
					print(result)

				query5 = """select N.name, CR.role from Crew_Roles CR join Names N on (CR.name_id = N.id) join Movies M on (CR.movie_id = M.id) join Principals P on (CR.movie_id = P.movie_id and CR.name_id = P.name_id) where M.title ilike %s and M.start_year = %s group by N.name, CR.role, P.ordering order by P.ordering"""		

				cursor.execute(query5, [_title, _year])
				print("and with")
				for tuple in cursor.fetchall():
					name, role = tuple 
					role = role.capitalize()
					result = " {}: {}".format(name, role)
					print(result)

			elif num_of_rows > 1:
				cursor.execute(query3, [_title, _year])
				print("Movies matching " + "'" + sys.argv[1] + "' " + sys.argv[2])
				print("===============")
				for tuple in cursor.fetchall():
					rating, title, start_year, id = tuple
					result = "{} {} ({})".format(rating, title, start_year)
					print(result)	

	# when a partial/whole movie name or pattern is supplied (includes non-matching name/patterns) - optional year is supplied but input is not numeric
	elif argc == 3 and sys.argv[2].isnumeric() == False:
		print(usage)

	# when the number of command-line arguments isn't 1, 2 nor 3
	else:
		print(usage)
	
except psycopg2.Error as err:
	print("DB error: ", err)
finally:
	if db:
		db.close()

# ****************************************************************************************************************************************

import sys
import psycopg2

# define any local helper functions here

# set up some globals

usage = "Usage: q4.py 'NamePattern' [Year]"
db = None

# process command-line args

argc = len(sys.argv)

# manipulate database

try:
	db = psycopg2.connect("dbname=imdb")
	cursor = db.cursor()

    # when no partial/whole name or pattern is supplied
	if argc == 1:
		print(usage)

	# when partial/whole name or pattern is supplied - optional year has not been supplied 
	elif argc == 2: 

		first = "^"
		last = "$"
		if first in sys.argv[1] and last in sys.argv[1]:
			sys.argv[1] = sys.argv[1][1:len(sys.argv[1]) - 1] 
		
		query = """select * from Names where name ilike %s order by name, birth_year, id"""

		cursor.execute(query, ["%" + sys.argv[1] + "%"])
		num_of_rows = len(cursor.fetchall())

		if num_of_rows == 0:
			print("No name matching " + "'" + sys.argv[1] + "'")
		
		elif num_of_rows == 1:
			cursor.execute(query, ["%" + sys.argv[1] + "%"])
			for tuple in cursor.fetchall():
				id, name, birth_year, death_year = tuple 
				
				if birth_year is None:
					result = "Filmography for {} (???)".format(name)
					print(result)
					print("===============")

				elif birth_year is not None and death_year is None:
					result = "Filmography for {} ({}-)".format(name, birth_year)
					print(result)
					print("===============")

				elif birth_year is not None and death_year is not None:
					result = "Filmography for {} ({}-{})".format(name, birth_year, death_year)
					print(result)
					print("===============")

			query1 = """select round(avg(cast(M.rating as numeric)), 1) as rded from Movies M join Principals P on (M.id = P.movie_id) join Names N on (P.name_id = N.id) where N.name ilike %s"""

			cursor.execute(query1, ["%" + sys.argv[1] + "%"])
			for tuple in cursor.fetchall():
				rounded_rating = tuple 

				if rounded_rating[0] is None:
					print("Personal Rating: 0")
				else:
					rounded_rating = float(rounded_rating[0])
					print("Personal Rating: " + str(rounded_rating))

			query2 = """select MG.genre, count(MG.genre) as cnt from Movie_genres MG join Movies M on (MG.movie_id = M.id) join Principals P on (M.id = P.movie_id) join Names N on (P.name_id = N.id) where N.name ilike %s group by MG.genre order by cnt desc, MG.genre limit 3"""
	
			cursor.execute(query2, ["%" + sys.argv[1] + "%"])
			print("Top 3 Genres:")
			for tuple in cursor.fetchall():
				genre, cnt = tuple 
				result = " {}".format(genre)
				print(result)
			print("===============")

			query3 = """select M.title, M.start_year from Movies M join Principals P on (M.id = P.movie_id) join Names N on (P.name_id = N.id) where N.name ilike %s group by M.start_year, M.title order by M.start_year, M.title"""

			cursor.execute(query3, ["%" + sys.argv[1] + "%"])
			for tuple in cursor.fetchall():
				title, start_year = tuple 
				result = "{} ({})".format(title, start_year)
				print(result)

				query4 = """select AR.played, M.title, M.start_year from Acting_Roles AR join Movies M on (AR.movie_id = M.id) join Names N on (AR.name_id = N.id) join Principals P on (M.id = P.movie_id and N.id = P.name_id) where N.name ilike %s group by M.start_year, M.title, AR.played order by M.start_year, M.title, AR.played"""

				cursor.execute(query4, ["%" + sys.argv[1] + "%"])
				for tuple in cursor.fetchall():
					played, title1, start_year1 = tuple 

					if title1 == title and start_year1 == start_year:
						result1 = " playing {}".format(played)
						print(result1)

				query5 = """select CR.role, M.title, M.start_year from Crew_Roles CR join Movies M on (CR.movie_id = M.id) join Names N on (CR.name_id = N.id) join Principals P on (M.id = P.movie_id and N.id = P.name_id) where N.name ilike %s group by M.start_year, M.title, CR.role order by M.start_year, M.title, CR.role"""

				cursor.execute(query5, ["%" + sys.argv[1] + "%"])
				for tuple in cursor.fetchall():
					role, title2, start_year2 = tuple

					if title2 == title and start_year2 == start_year:
						role = role.capitalize()
						role = role.replace("_", " ")
						result2 = " as {}".format(role)
						print(result2)
		
		elif num_of_rows > 1:
			cursor.execute(query, ["%" + sys.argv[1] + "%"])
			print("Names matching " + "'" + sys.argv[1] + "'")
			print("===============")
			for tuple in cursor.fetchall():
				id, name, birth_year, death_year = tuple 
				
				if birth_year is None:
					result = "{} (???)".format(name)
					print(result)

				elif birth_year is not None and death_year is None:
					result = "{} ({}-)".format(name, birth_year)
					print(result)

				elif birth_year is not None and death_year is not None:
					result = "{} ({}-{})".format(name, birth_year, death_year)
					print(result)

	# when partial/whole name or pattern is supplied - optional year has been supplied and year is numeric
	elif argc == 3 and sys.argv[2].isnumeric() == True:

		first = "^"
		last = "$"
		if first in sys.argv[1] and last in sys.argv[1]:
			sys.argv[1] = sys.argv[1][1:len(sys.argv[1]) - 1] 

		query6 = """select * from Names where name ilike %s and birth_year = %s order by name, birth_year, id"""

		name_ = "%" + sys.argv[1] + "%"
		year_ = sys.argv[2]
		cursor.execute(query6, [name_, year_])
		num_of_rows = len(cursor.fetchall())

		if num_of_rows == 0:
			print("No name matching " + "'" + sys.argv[1] + "' " + str(sys.argv[2]))
		
		elif num_of_rows == 1:
			cursor.execute(query6, [name_, year_])
			for tuple in cursor.fetchall():
				id, name, birth_year, death_year = tuple 
				
				if birth_year is None:
					result = "Filmography for {} (???)".format(name)
					print(result)
					print("===============")

				elif birth_year is not None and death_year is None:
					result = "Filmography for {} ({}-)".format(name, birth_year)
					print(result)
					print("===============")

				elif birth_year is not None and death_year is not None:
					result = "Filmography for {} ({}-{})".format(name, birth_year, death_year)
					print(result)
					print("===============")

			query7 = """select round(avg(cast(M.rating as numeric)), 1) as rded from Movies M join Principals P on (M.id = P.movie_id) join Names N on (P.name_id = N.id) where N.name ilike %s and N.birth_year = %s"""

			cursor.execute(query7, [name_, year_])
			for tuple in cursor.fetchall():
				rounded_rating = tuple 

				if rounded_rating[0] is None:
					print("Personal Rating: 0")
				else:
					rounded_rating = float(rounded_rating[0])
					print("Personal Rating: " + str(rounded_rating))

			query8 = """select MG.genre, count(MG.genre) as cnt from Movie_genres MG join Movies M on (MG.movie_id = M.id) join Principals P on (M.id = P.movie_id) join Names N on (P.name_id = N.id) where N.name ilike %s and N.birth_year = %s group by MG.genre order by cnt desc, MG.genre limit 3"""
	
			cursor.execute(query8, [name_, year_])
			print("Top 3 Genres:")
			for tuple in cursor.fetchall():
				genre, cnt = tuple 
				result = " {}".format(genre)
				print(result)
			print("===============")

			query9 = """select M.title, M.start_year from Movies M join Principals P on (M.id = P.movie_id) join Names N on (P.name_id = N.id) where N.name ilike %s and N.birth_year = %s group by M.start_year, M.title order by M.start_year, M.title"""

			cursor.execute(query9, [name_, year_])
			for tuple in cursor.fetchall():
				title, start_year = tuple 
				result = "{} ({})".format(title, start_year)
				print(result)

				query10 = """select AR.played, M.title, M.start_year from Acting_Roles AR join Movies M on (AR.movie_id = M.id) join Names N on (AR.name_id = N.id) join Principals P on (M.id = P.movie_id and N.id = P.name_id) where N.name ilike %s and N.birth_year = %s group by M.start_year, M.title, AR.played order by M.start_year, M.title, AR.played"""

				cursor.execute(query10, [name_, year_])
				for tuple in cursor.fetchall():
					played, title1, start_year1 = tuple 

					if title1 == title and start_year1 == start_year:
						result1 = " playing {}".format(played)
						print(result1)

				query11 = """select CR.role, M.title, M.start_year from Crew_Roles CR join Movies M on (CR.movie_id = M.id) join Names N on (CR.name_id = N.id) join Principals P on (M.id = P.movie_id and N.id = P.name_id) where N.name ilike %s and N.birth_year = %s group by M.start_year, M.title, CR.role order by M.start_year, M.title, CR.role"""

				cursor.execute(query11, [name_, year_])
				for tuple in cursor.fetchall():
					role, title2, start_year2 = tuple

					if title2 == title and start_year2 == start_year:
						role = role.capitalize()
						role = role.replace("_", " ")
						result2 = " as {}".format(role)
						print(result2)
		
		elif num_of_rows > 1:
			cursor.execute(query6, [name_, year_])
			print("Names matching " + "'" + sys.argv[1] + "'")
			print("===============")
			for tuple in cursor.fetchall():
				id, name, birth_year, death_year = tuple 
				
				if birth_year is None:
					result = "{} (???)".format(name)
					print(result)

				elif birth_year is not None and death_year is None:
					result = "{} ({}-)".format(name, birth_year)
					print(result)

				elif birth_year is not None and death_year is not None:
					result = "{} ({}-{})".format(name, birth_year, death_year)
					print(result)

	# when partial/whole name or pattern is supplied - optional year has been supplied and year is not numeric
	elif argc == 3 and sys.argv[2].isnumeric() == False:
		print(usage)

	# when the number of command-line arguments isn't 1, 2 nor 3
	else:
		print(usage)

except psycopg2.Error as err:
	print("DB error: ", err)
finally:
	if db:
		db.close()
