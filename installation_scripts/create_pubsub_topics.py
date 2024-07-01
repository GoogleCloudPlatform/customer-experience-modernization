from google.cloud import pubsub_v1
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--project_id")
parser.add_argument("--topic_id")
args = parser.parse_args()


project_id = args.project_id
topic_id = args.topic_id

def create_topic(project_id,topic_id):

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    topic = publisher.create_topic(request={"name": topic_path})

    print(f"Created topic: {topic.name}")


def get_topics(project_id):
    publisher = pubsub_v1.PublisherClient()
    project_path = f"projects/{project_id}"

    topics_name=[]
    for topic in publisher.list_topics(request={"project": project_path}):
        topics_name.append(topic.name.split('/')[-1])
    return topics_name


topics=get_topics(project_id)

if topic_id in topics:
    print("pubsub Topic already exist")
else:
    print("creating pubsub topic")
    create_topic(project_id,topic_id)