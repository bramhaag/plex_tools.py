import argparse
import sys
from plexapi.myplex import MyPlexAccount
from plexapi.library import ShowSection
from plexapi.library import MovieSection
from plexapi.video import Show
from plexapi.video import Movie
from plexapi.exceptions import NotFound
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("email", metavar="email", help="Email address")
parser.add_argument("password", metavar="password", help="Password")

parser.add_argument('--list', help="List all your Plex servers", action="store_true")
parser.add_argument('--stats', help="Return watch-time statistics", action="store_true")
parser.add_argument('--sync', help="Sync watched content across all servers (excluding ignored servers)", action="store_true")

parser.add_argument("--ignore", help="List of servers to ignore", nargs="+", default=[])
parser.add_argument("-V", "--verbose", help="Enable verbose output", action="store_true")

args = parser.parse_args()


def debug(message):
    if args.verbose:
        print(message)

account = MyPlexAccount(args.email, args.password)
debug(f"Connected to plex account: {account}")

servers = list(filter(lambda a: a.product == 'Plex Media Server' and a.name not in args.ignore, account.resources()))
connections = list(map(lambda s: s.connect(), servers))

if args.list:
    print(f"Found {len(connections)} servers: {list(map(lambda s: s.friendlyName, connections))}")

if not args.stats and not args.sync:
    sys.exit(0)

watched_shows = defaultdict(set)
watched_movies = set([])

debug("Gathering watched content...")

# Populate watched_shows and watched_movies
for conn in connections[1:]:
    for section in conn.library.sections():
        if (isinstance(section, ShowSection)):
            for show in section.all():
                for episode in show.watched():
                    watched_shows[show.title].add(episode.title)
        elif (isinstance(section, MovieSection)):
            for movie in section.search(unwatched=False):
                watched_movies.add((movie.title, movie.year))

if args.stats:
    print(f"You've watched {len(watched_shows)} show(s) ({sum(map(len, watched_shows.values()))} episodes) and {len(watched_movies)} movie(s)")

if args.sync:
    debug(f"Syncing watched content...")
    marked = 0
    for conn in connections:
        for section in conn.library.sections():
            if (isinstance(section, ShowSection)):
                for show_title, watched_episodes in watched_shows.items():
                    try:
                        show = section.get(show_title)
                        for episode in show.unwatched():
                            if (episode.title in watched_episodes):
                                try:
                                    episode.markWatched()
                                    debug(f"Marked {show_title}: {episode.title} as watched on {conn.friendlyName}")
                                    marked += 1
                                except AttributeError as e:
                                    debug(f"Could not mark {show_title}: {episode.title} as watched on {conn.friendlyName}: {e}")
                    except NotFound:
                        continue
            elif (isinstance(section, MovieSection)):
                for movie_title, year in watched_movies:
                    try:
                        results = section.search(title=movie_title, year=year, unwatched=True)
                        if (len(results) == 0):
                            continue

                        try:
                            results[0].markWatched()
                            debug(f"Marked {movie_title} ({year}) as watched on {conn.friendlyName}")
                            marked += 1
                        except AttributeError as e:
                            debug(f"Could not mark {movie_title} ({year}) as watched on {conn.friendlyName}: {e}")
                    except NotFound:
                        continue

    debug(f"Marked {marked} items as watched")
    debug(f"Done")
