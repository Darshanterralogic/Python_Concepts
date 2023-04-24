import os
import pandas as pd
import pymongo
import requests

class Movies:
    def create_mongodb_connection(self):
        try:
            # Create MongoDB client
            client = pymongo.MongoClient()
            db = client['testdb']

            # Create "movies" collection
            movies_collection = db['movies']

            # Create "comments" collection
            comments_collection = db['comments']

            # Insert sample data into "movies" collection
            movies_data = [
                {'movie_title': 'Movie A', 'runtime': 90, 'imdb_rating': 9.0, 'release_year': 2005, 'awards': 5,
                 'released_country': 'USA'},
                {'movie_title': 'Movie B', 'runtime': 120, 'imdb_rating': 8.5, 'release_year': 2000, 'awards': 4,
                 'released_country': 'UK'},
                {'movie_title': 'Movie C', 'runtime': 45, 'imdb_rating': 7, 'release_year': 2003, 'awards': 2,
                 'released_country': 'France'},
                {'movie_title': 'Movie D', 'runtime': 70, 'imdb_rating': 8.7, 'release_year': 2015, 'awards': 7,
                 'released_country': 'Canada'}
            ]
            movies_ids = movies_collection.insert_many(movies_data).inserted_ids

            # Insert sample data into "comments" collection
            comments_data = [
                {'movie_id': movies_ids[0], 'comment_text': 'Comment 1'},
                {'movie_id': movies_ids[1], 'comment_text': 'Comment 2'},
                {'movie_id': movies_ids[2], 'comment_text': 'Comment 3'}
            ]
            comments_collection.insert_many(comments_data)

            # Create a foreign key relationship between "movies" and "comments" collections
            movies_collection.create_index('_id', name='movies_id_pk')
            comments_collection.create_index('_id', name='comments_id_pk')
            comments_collection.create_index('movie_id', name='comments_movie_id_fk')
            print('Movies and Comments Sample Data Inserted')
            return True
        except pymongo.errors.PyMongoError as error_message:
            return str(error_message)
    def movie_comments(self):
        try:
            client = pymongo.MongoClient()
            db = client['testdb']

            # Read "movies" collection
            movies_collection = db['movies']
            movies_data = list(movies_collection.find())
            movies = pd.DataFrame(movies_data)

            # Read "comments" collection
            comments_collection = db['comments']
            comments_data = list(comments_collection.find())
            comments = pd.DataFrame(comments_data)
            # Merge movies and comments dataframes on '_id' and 'movie_id' columns to create movies_with_comments
            movies_with_comments = movies.merge(comments, left_on='_id', right_on='movie_id', how='inner')

            # Drop redundant columns
            movies_with_comments.drop(['_id_y'], axis=1, inplace=True)
            movies_with_comments.rename(columns={'_id_x': '_id'}, inplace=True)

            # Create movies_with_no_comments dataframe by finding movies that are not in movies_with_comments
            movies_with_no_comments = movies[~movies['_id'].isin(movies_with_comments['_id'])]

            # Reset index for movies_with_no_comments dataframe
            movies_with_no_comments.reset_index(drop=True, inplace=True)

            # Create a folder named "movies" if it does not exist
            if not os.path.exists('movies'):
                os.makedirs('movies')

            # Save movies_with_no_comments dataframe to a CSV file
            movies_with_no_comments.to_csv('movies/movies_with_no_comments.csv', index=False)
            # Rename movies_with_comments dataframe to movies_with_comments
            movies_with_comments.name = 'movies_with_comments'
            print('function1 : movies_with_no_comments.csv generated')
            return movies_with_comments
        except Exception as e:
            print("An error occurred:", str(e))
    def movie_runtime(self, movies_with_comments):
        try:
            # Add low_runtime and high_runtime columns to the dataframe
            movies_with_comments['low_runtime'] = movies_with_comments['runtime'].apply(
                lambda x: 'yes' if x > 50 else 'no')
            movies_with_comments['high_runtime'] = movies_with_comments['runtime'].apply(
                lambda x: 'no' if x > 50 else 'yes')

            # Save the updated dataframe to a CSV file
            movies_with_comments.to_csv('movies/movies_with_comments.csv', index=False)

            print('function2 : movies_with_comments.csv generated')
        except Exception as e:
            print(f"An error occurred: {e}")
    def fetch_movies(self):
        try:
            client = pymongo.MongoClient()
            db = client['testdb']

            # Fetch movies from "movies" collection
            movies_collection = db['movies']
            movies_data = list(movies_collection.find({
                'imdb_rating': {'$gt': 8},
                'release_year': {'$gte': 2000},
                'awards': {'$gt': 3}
            }).sort('release_year', pymongo.ASCENDING))
            movies = pd.DataFrame(movies_data)

            # Save movies dataframe to a CSV file
            movies.to_csv('movies/movies_rating_8_released_aft_2000.csv', index=False)

            print("function3 : movies_rating_8_released_aft_2000.csv  generated")
            return movies
        except Exception as e:
            print(f"An error occurred: {e}")
    def fetch_theatre_data(self):
        try:
            # Sample data from the theatre collection
            theatre = [
                {
                    'theaterId': 1,
                    'location': {
                        'address': {
                            'street1': '123 Main St',
                            'city': 'New York',
                            'street2': 'Apt 4B'
                        }
                    },
                    'geo': [40.7128, -74.0060]
                },
                {
                    'theaterId': 2,
                    'location': {
                        'address': {
                            'street1': '456 Elm St',
                            'city': 'Los Angeles',
                            'street2': 'Unit 8C'
                        }
                    },
                    'geo': [34.0522, -118.2437]
                }
            ]

            # Connect to MongoDB
            client = pymongo.MongoClient()
            db = client['testdb']
            collection = db['theatre']

            # Insert theatre data into MongoDB
            collection.insert_many(theatre)

            # Convert list of dictionaries to DataFrame
            theatre_data = pd.DataFrame(list(collection.find()))

            # Extract required columns from nested arrays
            theatre_data['street1'] = theatre_data['location'].apply(lambda x: x.get('address', {}).get('street1', ''))
            theatre_data['city'] = theatre_data['location'].apply(lambda x: x.get('address', {}).get('city', ''))
            theatre_data['street2'] = theatre_data['location'].apply(lambda x: x.get('address', {}).get('street2', ''))
            theatre_data['0'] = theatre_data['geo'].apply(lambda x: x[0] if x else None)
            theatre_data['1'] = theatre_data['geo'].apply(lambda x: x[1] if x else None)

            # Select required columns for final DataFrame
            theatre_simplified = theatre_data[['theaterId', 'street1', 'city', 'street2', '0', '1']]
            # Save the DataFrame to a CSV file
            theatre_simplified.to_csv('movies/theatre_simplified.csv', index=False)

            print("function 4 & 5 : theatre_simplified.csv generated")
            return theatre_simplified
        except Exception as e:
            print(f"An error occurred: {e}")
    def theatre_simplified_with_lat_long(self, theatre_simplified):
        # OpenCageData API endpoint
        url = "https://api.opencagedata.com/geocode/v1/json"

        # API key
        api_key = "36f4b41df10a476aa55cdefdd3d5ddf3"

        # Create empty lists to store lat and long values
        latitudes = []
        longitudes = []

        # Loop through cities in theatre_simplified dataframe
        for city in theatre_simplified['city']:
            try:
                # Send GET request to OpenCageData API with city name as query parameter
                params = {
                    "q": city,
                    "key": api_key
                }
                response = requests.get(url, params=params)
                data = response.json()

                # Extract lat and long values from API response
                if data['results']:
                    lat = data['results'][0]['geometry']['lat']
                    lon = data['results'][0]['geometry']['lng']
                else:
                    lat = None
                    lon = None

                # Append lat and long values to respective lists
                latitudes.append(lat)
                longitudes.append(lon)
            except Exception as e:
                print(f"Error occurred for city '{city}': {e}")
                latitudes.append(None)
                longitudes.append(None)

        # Add lat and long values as new columns to theatre_simplified dataframe
        theatre_simplified['lat'] = latitudes
        theatre_simplified['long'] = longitudes

        # Rearrange columns in the desired order
        theatre_simplified = theatre_simplified[['theaterId', 'street1', 'city', 'street2', 'lat', 'long']]

        # Save dataframe to CSV
        theatre_simplified.to_csv("movies/theatre_simplified_with_lat_long.csv", index=False)
        print("function6 : theatre_simplified_with_lat_long.csv generated")
        return theatre_simplified
    def filter_and_save_movies(self):
        try:
            # Connect to MongoDB
            client = pymongo.MongoClient()

            # Access the movies collection
            db = client['testdb']
            movies = db['movies']

            # Filter movies where countries value is not equal to "USA"
            released_outside_usa = movies.find({"released_country": {"$ne": "USA"}})

            # Convert cursor to DataFrame
            released_outside_usa_df = pd.DataFrame(list(released_outside_usa))
            # Save the filtered DataFrame to a CSV file
            released_outside_usa_df.to_csv("movies/released_outside_usa.csv", index=False)
            print("function7 : released_outside_usa.csv generated")
            return True
        except Exception as e:
            print(f"Error occurred while filtering and saving movies: {e}")
            return False

if __name__ == "__main__":
    m = Movies()
    #create mongodb data
    data=m.create_mongodb_connection()
    #data=True
    if data is True:
        # function1
        task1 = m.movie_comments()
        # function2
        task2=m.movie_runtime(task1)
        # function3
        task3=m.fetch_movies()
        #function 4 & 5
        task4=m.fetch_theatre_data()
        #function6
        task5=m.theatre_simplified_with_lat_long(task4)
        #function7
        task6 = m.filter_and_save_movies()

    else:
        print(data)
