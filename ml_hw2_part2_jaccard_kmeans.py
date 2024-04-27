import re
import os
import random

def preprocess_tweet(tweet):
    """
    Cleans a single tweet using various regex operations:
    - Removes tweet ID and timestamp.
    - Removes anything starting with @.
    - Removes URLs.
    - Converts hashtags to plain text.
    - Converts text to lowercase.
    """
    # Remove the tweet ID and timestamp
    tweet = tweet.split('|', 2)[-1]
    # Remove any word tht starts with @
    tweet = re.sub(r'@\w+', '', tweet)
    # Remove URLs
    tweet = re.sub(r'http\S+', '', tweet)
    # Convert hashtags to plain text
    tweet = tweet.replace('#', '')
    # Remove 'rt :'
    tweet = re.sub(r'\brt\s*:\s*', '', tweet, flags=re.IGNORECASE)
    # Convert text to lowercase
    tweet = tweet.lower()
    return tweet

def pre_process_tweets(input_file_path, output_file_path):
    """
    Pre_processes all tweets in the given file, writes the cleaned tweets to a new file, and returns a list of the cleaned tweets.
    """
    pre_processed_tweets = []
    # Open the input file and the output file
    with open(input_file_path, 'r', encoding='utf-8') as infile, \
         open(output_file_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            pre_processed_line = preprocess_tweet(line)
            outfile.write(pre_processed_line + '\n')
            pre_processed_tweets.append(pre_processed_line)

    return pre_processed_tweets

def jaccard_distance(tweet1, tweet2):
    """
    Calculate the Jaccard distance between two tweets.
    The tweets are provided as strings of words.
    """
    # Split the tweets into sets of words
    words_in_tweet1 = set(tweet1.split())
    words_in_tweet2 = set(tweet2.split())

    # Calculate the intersection and union of the two sets
    intersection = words_in_tweet1.intersection(words_in_tweet2)
    union = words_in_tweet1.union(words_in_tweet2)

    # Calculate Jaccard distance
    jaccard_distance = 1 - len(intersection) / len(union) if union else 0

    return jaccard_distance

def k_means_clustering(k, tweets):
    """Perform K-means clustering on a list of pre-processed tweets using Jaccard distance."""
    # Initialize centroids to the first k tweets (not random)
    centroids = random.sample(tweets, k)
    
    while True:
        clusters = {i: [] for i in range(k)}  # Create a dictionary to store clusters
        sse = 0
        
        # Assign tweets to the closest centroid
        for tweet in tweets:
            distances = [jaccard_distance(tweet, centroids[i]) for i in range(k)]
            closest_centroid = distances.index(min(distances))
            closest_distance = distances[closest_centroid]
            clusters[closest_centroid].append(tweet)
            sse += closest_distance ** 2
        
        # Update centroids by finding the tweet that minimizes the sum of distances within each cluster
        new_centroids = []
        for i in range(k):
            if clusters[i]:  # Ensure the cluster is not empty
                min_distance = float('inf')
                for candidate_centroid in clusters[i]:
                    total_distance = sum(jaccard_distance(candidate_centroid, other_tweet) for other_tweet in clusters[i])
                    if total_distance < min_distance:
                        min_distance = total_distance
                        best_candidate = candidate_centroid
                new_centroids.append(best_candidate)
            else:
                # If a cluster is empty, reuse the old centroid
                new_centroids.append(centroids[i])

        # Check if centroids have changed, if not, break the loop
        if set(new_centroids) == set(centroids):
            break
        else:
            centroids = new_centroids

    return clusters, sse

def main():
    # Specify the path to the input file relative to the .py file's location
    input_path = os.path.join(os.path.dirname(__file__), 'health+news+in+twitter', 'Health-Tweets', 'usnewshealth.txt')
    # Specify the path to the output file
    output_path = os.path.join(os.path.dirname(__file__), 'usnewshealth_processed.txt')

    # Process the tweets
    pre_processed_tweets = pre_process_tweets(input_path, output_path)

    print("Number of pre-processed tweets:", len(pre_processed_tweets))

    k = int(input("Please enter the number of clusters (k): "))
    print("You entered: k = ", k)
    clusters, sse = k_means_clustering(k, pre_processed_tweets)
    print("sse = {:.2f}".format(sse))
    print("CLUSTER SIZES:")
    for cluster_id, tweets in clusters.items():
        print(f"{cluster_id+1}: {len(tweets)}", "tweets")#cluster size


if __name__ == "__main__":
    main()