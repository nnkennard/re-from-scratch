import collections
import json
import openreview
import tqdm


# Change these values according to your needs
INVITATION = 'ICLR.cc/2019/Conference/-/Blind_Submission'
LIMIT = 10 # Number of papers to build timelines for


def main():

  guest_client = openreview.Client(baseurl='https://api.openreview.net')
  forum_notes = []
  for i, forum_note in enumerate(openreview.tools.iterget_notes(
        guest_client, invitation=INVITATION)):
    forum_notes.append(forum_note)

  review_text_map = {}
  forum_map = collections.defaultdict(list)

  for forum_note in tqdm.tqdm(forum_notes[:50]):
    this_forum_notes = guest_client.get_notes(forum=forum_note.id)
    for note in this_forum_notes:
        if 'review' in note.content:
          forum_map[forum_note.id].append(note.id)
          review_text_map[note.id] = note.content['review']

  with open('iclr2019_reviews.json', 'w') as f:
    json.dump({
      "forums": forum_map,
      "reviews": review_text_map
    }, f)


if __name__ == "__main__":
  main()

