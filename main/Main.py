from Twitter.TwitterInterface import TwitterInterface
from Twitter.Account import Account

# Tweets to pull
numberToPull = 10

# Companies of interest
companies = [
    Account("Wendys", "@Wendys"),
    Account("Mcdonalds", "@McDonalds"),
    Account("BurgerKing", "@BurgerKing"),
    Account("TacoBell", "@tacobell")]

people = [
    Account("vomit", "🤮")]

# TwitterInterface Objects to pull from
queryList = []

# Raw Tweet Objects
rawTweets = []

# List companies to search
def companiesToSearch():
    for entity in companies:
        queryList.append(TwitterInterface(numberToPull, entity.screenName, entity.name+".txt"))


# List people to search
def peopleToSearch():
    for entity in people:
        queryList.append(TwitterInterface(numberToPull, entity.screenName, entity.name+".txt"))


# Execute queries contained in list
def collectData():
    for query in queryList:
        raw = query.searchTweets()
        query.filterTweets(raw)
        rawTweets.append(raw)


def main():
    peopleToSearch()
    collectData()


main()