import sys
import meaningcloud
import config
import random
import wikipedia

license_key = config.LICENCE_KEY


def get_topics(text, language):
    result = []

    language = 'ru' if language == 'ru-RU' else 'en'

    try:
        topics_response = meaningcloud.TopicsResponse(meaningcloud.TopicsRequest(license_key, txt=text,
                                                      lang=language, topicType='e').sendReq())

        if topics_response.isSuccessful():
            entities = topics_response.getEntities()

            for entity in entities:
                result.append(
                    (topics_response.getTopicForm(entity),
                     topics_response.getTypeLastNode(topics_response.getOntoType(entity)))
                )

        else:
            if topics_response.getResponse() is None:
                print("\nOh no! The request sent did not return a Json\n")
            else:
                print("\nOh no! There was the following error: " + topics_response.getStatusMsg() + "\n")

    except:
        print('Something went wrong when making a meaningCloud request', file=sys.stderr)

    finally:
        return result


def get_topic(text, language):
    topics = get_topics(text, language)
    if not topics:
        return None
    else:
        return random.choice(topics)


successful_reply_starters = (
    'Well, I\'ve heard just a few things of $. ',
    'Yeah, I know about $. ',
    'Talking about $, did you know, that ',
    'Would you like to talk about $',
    'Uh, I don\'t know much about $, is that somehow related to ',
    'Shall we change the theme please? I only know that $ is something about ',
    'Unfortunately, I don\'t know a lot about $, will you please tell me more? Is that about '
)


def get_wiki_answer(topic):
    try:
        wiki_summary = wikipedia.summary(topic, 3)
        return wiki_summary
    except:
        pass

    try:
        wiki_keyword = wikipedia.search(topic)
        if not wiki_keyword:
            return None
        else:
            return wikipedia.summary(wiki_keyword, 3)
    except:
        pass

    return None


def get_reply(text, language):
    topic = get_topic(text, language)
    if topic is None:
        return None
    else:
        reply_starter = random.choice(successful_reply_starters)
        reply_starter = reply_starter.replace('$', topic[0])

        wiki_answer = get_wiki_answer(topic[0])

        if wiki_answer is not None:
            return reply_starter + wiki_answer
        else:
            return None
