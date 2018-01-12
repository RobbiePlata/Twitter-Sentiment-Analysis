import twitter
import emoji
#  (3.3.1 supports 280 characters)


class TwitterInterface(object):

    # Twitter API keys apps.twitter.com
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    ACCESS_TOKEN_KEY = ''
    ACCESS_TOKEN_SECRET = ''

    # Initialize api class containing pull functions
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN_KEY,
                      access_token_secret=ACCESS_TOKEN_SECRET,
                      tweet_mode='extended',
                      sleep_on_rate_limit=True)

    def __init__(self, numberToPull, query, textFile):
        """
        :param numberToPull: Tweets to be saved
        :param query: Term to be searched
        :param textFile: Text file in which tweets are saved in form of RAWtextFile.txt and FilteredtextFile.txt
        """
        self.numberToPull = numberToPull
        self.query = query
        self.textFile = textFile
        self.rawTextFile = 'RAW'+textFile
        self.filteredTextFile = 'Filtered'+textFile

    def searchTweets(self):
        """
        :return results: List of tweet objects
        """
        #  w+ create & write - a+ append - r reads - w write
        file = open(self.rawTextFile, "w+", encoding='utf-8')
        # ID of last fetched tweet ID
        batchID = 0
        # Unique Tweets that have been analyzed
        listOfTweets = []
        # Count of Tweets saved
        numTweets = 0
        # Tweet objects to be returned
        results = []
        while numTweets <= self.numberToPull:
            try:
                search = self.api.GetSearch(term=self.query, count=100, since_id=batchID, include_entities=True)
                for tweet in search:
                    if tweet.full_text[:3] != 'RT ' and tweet.full_text not in listOfTweets and tweet.lang == 'en':
                        urls = tweet.urls
                        media = tweet.media
                        users = tweet.user_mentions
                        temp = tweet.full_text
                        # Checks for array of url objects that contains urls to remove
                        if urls:
                            for object in urls:
                                temp = temp.replace(object.url, "URL")
                                print(object.url, "changed to URL")
                        # Checks for array of media objects for various media urls to remove
                        if media:
                            for object in media:
                                print('media.url ' + object.url)
                                temp = temp.replace(object.url, "")
                                if object.media_url:
                                    temp = temp.replace(object.media_url, "")
                                if object.media_url_https:
                                    temp = temp.replace(object.media_url_https, "")
                        # Checks for array of user mention objects that contain screen names to remove
                        if users:
                            for user in users:
                                print('user.screen_name ' + user.screen_name)
                                temp = temp.replace('@' + user.screen_name, "")
                        # Checks if ONLY emojis and or hyperlinks are contained within tweet text
                        for character in temp:
                            if character in emoji.UNICODE_EMOJI:
                                temp = temp.replace(character, "")
                        # Checks for newline
                        temp = temp.replace("\n", "")
                        # Removes all whitespace
                        temp = temp.replace(" ", "")
                        # Check if tweet doesn't contain pure text character
                        if temp == "":
                            print("Pointless Tweet")
                            break
                        results.append(tweet)
                        listOfTweets.append(tweet.full_text)
                        print(tweet.full_text)
                        print("********************************************************************************************************************************************\n")
                        file.write(tweet.full_text + '\n')
                        file.write('********************************************************************************************************************************************\n')  # 180 stars for length of Tweet/Tweet Separator
                        numTweets+=1
                        print("Tweet #" + str(numTweets))
                    batchID = tweet.id
                print('Last BatchID: ', batchID)
            except Exception as ex:
                print(ex)
        file.close()
        return results

    def filterTweets(self, rawTweets):
        """
        :param rawTweets: Parsed tweets to be filtered
        """
        removeCharacters = ['\r','\n',',','*','"','`',"'"]
        spaceCharacters = ['_','-',',',':',';','(',')','[',']','{','}','/']
        file = open(self.filteredTextFile, "w+", encoding='utf-8')
        numTweets = 0
        for tweet in rawTweets:
            print(type(tweet))
            urls = tweet.urls
            media = tweet.media
            users = tweet.user_mentions
            hashtags = tweet.hashtags
            print("RAW TWEET:")
            print(tweet.full_text)
            filteredTweet = tweet.full_text
            filteredTweet = filteredTweet.replace(self.query, "COMPANY")  # Company
            if urls:
                for object in urls:
                    filteredTweet = filteredTweet.replace(object.url, "URL")
                    print(object.url, "changed to URL")
            if media:
                for object in media:
                    print('media.url ' + object.url)
                    filteredTweet = filteredTweet.replace(object.url, "")
                    if object.media_url:
                        filteredTweet = filteredTweet.replace(object.media_url, "")
                    if object.media_url_https:
                        filteredTweet = filteredTweet.replace(object.media_url_https, "")
            if users:
                count = 0
                for user in users:
                    print('user.screen_name ' + user.screen_name)
                    if count == 0:
                        filteredTweet = filteredTweet.replace('@' + user.screen_name, "SOMEONE")
                    if count > 0:
                        filteredTweet = filteredTweet.replace('@' + user.screen_name, "")
            if hashtags:
                for hashtag in hashtags:
                    print('hashtag ' + hashtag.text)
                    filteredTweet = filteredTweet.replace('#' + hashtag.text, "")
            for c in removeCharacters:
                filteredTweet = filteredTweet.replace(c, "")
            for c in spaceCharacters:
                filteredTweet = filteredTweet.replace(c, " ")
            filteredTweet = filteredTweet.replace("!", ".")
            filteredTweet = filteredTweet.replace("?", ".")
            filteredTweet = filteredTweet.replace("@", "at")
            filteredTweet = filteredTweet.replace("&amp", "and")
            filteredTweet = filteredTweet.replace("%", "percent")
            filteredTweet = filteredTweet.replace("$", "dollar")
            filteredTweet = filteredTweet.replace("+", "plus")

            for i, character in enumerate(filteredTweet):
                if character in emoji.UNICODE_EMOJI:
                    filteredTweet = filteredTweet.replace(character, " EMOJI ")
            # Remove adjacent duplicate words "SOMEONE"
            print(filteredTweet)
            words = filteredTweet.split()
            i = 0
            while i < len(words)-1:
                if words[i+1] == words[i] and words[i] == "SOMEONE":
                    words.pop(i)
                else:
                    i+=1
            # Remove adjacent duplicate words "EMOJI"
            i = 0
            while i < len(words) - 1:
                if words[i+1] == words[i] and words[i] == "EMOJI":
                    words.pop(i)
                else:
                    i+=1
            filteredTweet = " ".join(words)
            # emoji.emojize can be used to convert the unicode into emoji description, (:grinning:) semicolons have to be removed though
            print("FILTERED TWEET:")
            print(filteredTweet)
            print("********************************************************************************************************************************************\n")
            file.write(filteredTweet + '\n')
            file.write('********************************************************************************************************************************************\n')
            numTweets += 1
            print("Tweet #" + str(numTweets))
        file.close()
